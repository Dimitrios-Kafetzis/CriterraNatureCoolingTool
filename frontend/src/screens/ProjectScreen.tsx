import { useCallback, useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router';
import { api } from '../api/client';
import type { AssessmentView, ProjectView } from '../api/types';
import { messages } from '../i18n/en';

/**
 * One project: its assessments (drafts and evaluated), with the OQ-15
 * methodology-update surfacing and the D-021 duplicate action.
 */
export function ProjectScreen() {
  const { projectId } = useParams<'projectId'>();
  const navigate = useNavigate();
  const [project, setProject] = useState<ProjectView | null>(null);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(() => {
    if (!projectId) return;
    api
      .getProject(projectId)
      .then(setProject)
      .catch(() => setError(messages.app.apiError));
  }, [projectId]);

  useEffect(reload, [reload]);

  if (error) return <p className="notice notice--error">{error}</p>;
  if (!project || !projectId) return <p className="muted">{messages.app.loading}</p>;

  const evaluated = project.assessments.filter((assessment) => assessment.result != null);

  async function newAssessment() {
    const label = nextLabel(project?.assessments ?? []);
    const created = await api.createAssessment(projectId ?? '', label, {
      project_name: project?.name,
    });
    void navigate(`/projects/${projectId}/assessments/${created.assessment_id}/edit`);
  }

  async function duplicate(assessmentId: string) {
    const created = await api.duplicateAssessment(projectId ?? '', assessmentId);
    void navigate(`/projects/${projectId}/assessments/${created.assessment_id}/edit?step=5`);
  }

  async function removeAssessment(assessmentId: string) {
    if (!window.confirm(messages.project.deleteAssessmentConfirm)) return;
    await api.deleteAssessment(projectId ?? '', assessmentId);
    reload();
  }

  return (
    <div>
      <h1>{project.name}</h1>
      <h2>{messages.project.assessments}</h2>
      {project.assessments.length === 0 ? (
        <p className="muted">{messages.project.empty}</p>
      ) : (
        <table className="data">
          <tbody>
            {project.assessments.map((assessment) => (
              <tr key={assessment.assessment_id}>
                <td>
                  {assessment.label}
                  {assessment.methodology_update_available ? (
                    <>
                      {' '}
                      <span className="badge badge--warn">
                        {messages.project.methodologyUpdate}
                      </span>
                    </>
                  ) : null}
                </td>
                <td>
                  <span className={assessment.result ? 'badge badge--accent' : 'badge'}>
                    {assessment.result ? messages.project.evaluated : messages.project.draft}
                  </span>
                </td>
                <td className="num">{new Date(assessment.created_at).toLocaleDateString()}</td>
                <td>
                  {assessment.result ? (
                    <Link
                      className="button button--quiet"
                      to={`/projects/${projectId}/assessments/${assessment.assessment_id}/results`}
                    >
                      {messages.project.viewResults}
                    </Link>
                  ) : (
                    <Link
                      className="button button--quiet"
                      to={`/projects/${projectId}/assessments/${assessment.assessment_id}/edit`}
                    >
                      {messages.project.continueDraft}
                    </Link>
                  )}
                </td>
                <td>
                  <button
                    type="button"
                    className="button button--quiet"
                    onClick={() => void duplicate(assessment.assessment_id)}
                  >
                    {messages.project.duplicate}
                  </button>
                </td>
                <td>
                  <button
                    type="button"
                    className="button button--danger"
                    onClick={() => void removeAssessment(assessment.assessment_id)}
                  >
                    {messages.project.deleteAssessment}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <div className="actions-row" style={{ marginTop: '1.5rem' }}>
        <button type="button" className="button" onClick={() => void newAssessment()}>
          {messages.project.newAssessment}
        </button>
        {evaluated.length >= 2 ? (
          <Link className="button button--secondary" to={`/projects/${projectId}/compare`}>
            {messages.project.compare}
          </Link>
        ) : (
          <span className="muted small">{messages.project.compareHint}</span>
        )}
      </div>
    </div>
  );
}

/** Option A, Option B, … following the existing count. */
function nextLabel(assessments: AssessmentView[]): string {
  const letter = String.fromCharCode('A'.charCodeAt(0) + assessments.length);
  return `Option ${letter}`;
}
