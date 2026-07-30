import { useEffect, useState } from 'react';
import { Link } from 'react-router';
import { api } from '../api/client';
import type { ProjectSummary } from '../api/types';
import { messages } from '../i18n/en';

/** Saved projects, most recently updated first (D-020). */
export function ProjectsScreen() {
  const [projects, setProjects] = useState<ProjectSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  function reload() {
    api
      .listProjects()
      .then(setProjects)
      .catch(() => setError(messages.app.apiError));
  }

  useEffect(reload, []);

  async function remove(projectId: string) {
    if (!window.confirm(messages.projects.deleteConfirm)) return;
    await api.deleteProject(projectId);
    reload();
  }

  if (error) return <p className="notice notice--error">{error}</p>;
  if (projects === null) return <p className="muted">{messages.app.loading}</p>;

  return (
    <div>
      <h1>{messages.projects.heading}</h1>
      {projects.length === 0 ? (
        <p className="muted">{messages.projects.empty}</p>
      ) : (
        <table className="data">
          <thead>
            <tr>
              <th scope="col">{messages.entry.newProjectName}</th>
              <th scope="col">{messages.projects.updated}</th>
              <th scope="col"></th>
              <th scope="col"></th>
            </tr>
          </thead>
          <tbody>
            {projects.map((project) => (
              <tr key={project.project_id}>
                <td>
                  <Link to={`/projects/${project.project_id}`}>{project.name}</Link>
                  <span className="muted small">
                    {' '}
                    · {messages.projects.assessmentCount(project.assessment_count)}
                  </span>
                </td>
                <td className="num">{new Date(project.updated_at).toLocaleString()}</td>
                <td>
                  <Link className="button button--quiet" to={`/projects/${project.project_id}`}>
                    {messages.projects.open}
                  </Link>
                </td>
                <td>
                  <button
                    type="button"
                    className="button button--danger"
                    onClick={() => void remove(project.project_id)}
                  >
                    {messages.projects.delete}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <p style={{ marginTop: '1.5rem' }}>
        <Link to="/">{messages.projects.backToEntry}</Link>
      </p>
    </div>
  );
}
