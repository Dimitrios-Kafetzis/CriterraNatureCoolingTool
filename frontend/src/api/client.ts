/**
 * The thin typed fetch client (D-030): no data-fetching or global-state
 * library — the app talks to a local API measured in milliseconds. Every
 * request/response type traces to the generated OpenAPI schema.
 */

import type {
  AssessmentInput,
  AssessmentResult,
  AssessmentView,
  AutofillSources,
  AvailabilityQuery,
  AvailableTypologies,
  BasemapDocument,
  DraftInput,
  GeoLookupRequest,
  GeoLookupResponse,
  MetaResponse,
  MethodologyData,
  NbsImageManifest,
  PlaceSearchResponse,
  ProjectSummary,
  ProjectView,
  TypologyLibrary,
  ValidateResponse,
} from './types';

export class ApiError extends Error {
  readonly status: number;
  readonly detail: unknown;

  constructor(status: number, detail: unknown) {
    super(typeof detail === 'string' ? detail : `API error ${status}`);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    headers: init?.body != null ? { 'Content-Type': 'application/json' } : undefined,
    ...init,
  });
  if (!response.ok) {
    let detail: unknown = null;
    try {
      detail = ((await response.json()) as { detail?: unknown }).detail ?? null;
    } catch {
      // non-JSON error body; status alone will have to do
    }
    throw new ApiError(response.status, detail);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}

const json = (body: unknown): RequestInit => ({ method: 'POST', body: JSON.stringify(body) });
const patch = (body: unknown): RequestInit => ({ method: 'PATCH', body: JSON.stringify(body) });

/**
 * Serialise an availability query, dropping unanswered conditions entirely.
 *
 * An unanswered condition is omitted rather than sent as a value the service
 * would have to interpret: the gating rules are the service's (D-044.1), and
 * a query string is not the place to decide what "not answered" means.
 */
function availabilityParams(query: AvailabilityQuery): string {
  const params = new URLSearchParams();
  params.set('assessment_scale', query.assessment_scale);
  if (query.land_use != null) params.set('land_use', query.land_use);
  if (query.waterfront_type != null) params.set('waterfront_type', query.waterfront_type);
  if (query.includes_railway !== undefined) {
    params.set('includes_railway', String(query.includes_railway));
  }
  if (query.existing_woodland !== undefined) {
    params.set('existing_woodland', String(query.existing_woodland));
  }
  for (const governance of query.productive_governance ?? []) {
    params.append('productive_governance', governance);
  }
  return params.toString();
}

export const api = {
  meta: () => request<MetaResponse>('/api/meta'),

  typologies: () => request<TypologyLibrary>('/api/typologies'),

  /**
   * The entries the service offers for this site (D-043, D-044.1).
   *
   * Availability guides selection and never blocks it (D-019): an entry
   * absent from this list stays fully selectable in the picker.
   */
  availableTypologies: (query: AvailabilityQuery) =>
    request<AvailableTypologies>(`/api/typologies/available?${availabilityParams(query)}`),

  methodology: () => request<MethodologyData>('/api/methodology'),

  /**
   * The bundled example images (v2.3, D-051): one request tells the picker
   * every (archetype-or-override, climate zone) pair a verified photograph
   * exists for. Pairs absent from the answer render no affordance at all.
   */
  imageManifest: () => request<NbsImageManifest>('/api/images/manifest'),

  /** The bundled country outlines the offline map draws (D-047.1). */
  basemap: () => request<BasemapDocument>('/api/geo/basemap'),

  /**
   * The three inputs a location can honestly answer (D-047).
   *
   * Returns suggestions, not answers: the caller applies each only where the
   * user has not already answered, and marks what it applies as autofilled.
   */
  geoLookup: (body: GeoLookupRequest) => request<GeoLookupResponse>('/api/geo/lookup', json(body)),

  /**
   * Offline navigation by name (v2.2, D-049.6): somewhere for the map to move
   * to. Selecting a result fills in no answer.
   */
  places: (query: string) =>
    request<PlaceSearchResponse>(`/api/geo/places?query=${encodeURIComponent(query)}`),

  /** Dry-run validation of a partial questionnaire state (D-028). */
  validate: (draft: DraftInput) =>
    request<ValidateResponse>('/api/assessments/validate', json(draft)),

  /** Stateless evaluation (kept for completeness; the app evaluates stored drafts). */
  evaluate: (input: AssessmentInput) =>
    request<AssessmentResult>('/api/assessments/evaluate', json(input)),

  listProjects: () => request<ProjectSummary[]>('/api/projects'),

  createProject: (name: string) => request<ProjectView>('/api/projects', json({ name })),

  getProject: (projectId: string) => request<ProjectView>(`/api/projects/${projectId}`),

  patchProject: (projectId: string, body: { name?: string }) =>
    request<ProjectView>(`/api/projects/${projectId}`, patch(body)),

  deleteProject: (projectId: string) =>
    request<void>(`/api/projects/${projectId}`, { method: 'DELETE' }),

  createAssessment: (projectId: string, label: string, input: DraftInput = {}) =>
    request<AssessmentView>(`/api/projects/${projectId}/assessments`, json({ label, input })),

  getAssessment: (projectId: string, assessmentId: string) =>
    request<AssessmentView>(`/api/projects/${projectId}/assessments/${assessmentId}`),

  /** Auto-save target (D-020): replaces the stored draft input. */
  patchAssessment: (
    projectId: string,
    assessmentId: string,
    body: { label?: string; input?: DraftInput; autofilled?: AutofillSources },
  ) =>
    request<AssessmentView>(`/api/projects/${projectId}/assessments/${assessmentId}`, patch(body)),

  deleteAssessment: (projectId: string, assessmentId: string) =>
    request<void>(`/api/projects/${projectId}/assessments/${assessmentId}`, { method: 'DELETE' }),

  /** Explicit evaluation of a stored draft (OQ-15): results enter storage only from the engine. */
  evaluateAssessment: (projectId: string, assessmentId: string) =>
    request<AssessmentView>(`/api/projects/${projectId}/assessments/${assessmentId}/evaluate`, {
      method: 'POST',
    }),

  /** Comparison draft (D-021): carries the site, blanks intervention + cost/energy. */
  duplicateAssessment: (projectId: string, assessmentId: string, label?: string) =>
    request<AssessmentView>(
      `/api/projects/${projectId}/assessments/${assessmentId}/duplicate`,
      json(label === undefined ? {} : { label }),
    ),
};
