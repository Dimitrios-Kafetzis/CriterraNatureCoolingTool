/**
 * The thin typed fetch client (D-030): no data-fetching or global-state
 * library — the app talks to a local API measured in milliseconds. Every
 * request/response type traces to the generated OpenAPI schema.
 */

import type {
  AssessmentInput,
  AssessmentResult,
  AssessmentView,
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

export const api = {
  meta: () => request<MetaResponse>('/api/meta'),

  typologies: () => request<TypologyLibrary>('/api/typologies'),

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
