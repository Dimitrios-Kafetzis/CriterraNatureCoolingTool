/**
 * The thin typed fetch client (D-030): no data-fetching or global-state
 * library — the app talks to a local API measured in milliseconds. Every
 * request/response type traces to the generated OpenAPI schema.
 */

import type {
  AssessmentInput,
  AssessmentResult,
  AssessmentView,
  AvailabilityQuery,
  AvailableTypologies,
  DraftInput,
  MetaResponse,
  MethodologyData,
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
    body: { label?: string; input?: DraftInput },
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
