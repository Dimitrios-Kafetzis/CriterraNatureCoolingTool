import { useState } from 'react';
import { Link, useNavigate } from 'react-router';
import { api } from '../api/client';
import { messages } from '../i18n/en';

/**
 * Entry (UX §2): states what the tool does, what it will ask, and that
 * partial answers are acceptable — before requesting anything. Two actions:
 * start a new assessment, open a saved project. The methodology is linked
 * from here (and from every screen via the header).
 */
export function EntryScreen() {
  const navigate = useNavigate();
  const [creating, setCreating] = useState(false);
  const [name, setName] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function createProject(event: React.FormEvent) {
    event.preventDefault();
    if (!name.trim()) return;
    setBusy(true);
    setError(null);
    try {
      const project = await api.createProject(name.trim());
      const assessment = await api.createAssessment(
        project.project_id,
        messages.project.defaultFirstLabel,
        { project_name: name.trim() },
      );
      void navigate(`/projects/${project.project_id}/assessments/${assessment.assessment_id}/edit`);
    } catch {
      setError(messages.app.apiError);
      setBusy(false);
    }
  }

  return (
    <div className="entry">
      <div className="page-intro">
        <h1>{messages.entry.heading}</h1>
        <p>{messages.entry.what}</p>
        <p>{messages.entry.whatItAsks}</p>
        <p>{messages.entry.partialAnswers}</p>
      </div>

      {creating ? (
        <form className="card" onSubmit={createProject}>
          <div className="field">
            <label className="field__label" htmlFor="new-project-name">
              {messages.entry.newProjectName}
            </label>
            <p className="field__help" id="new-project-name-help">
              {messages.entry.newProjectHelp}
            </p>
            <input
              id="new-project-name"
              type="text"
              value={name}
              aria-describedby="new-project-name-help"
              onChange={(event) => setName(event.target.value)}
            />
          </div>
          {error ? <p className="error-text">{error}</p> : null}
          <div className="actions-row">
            <button type="submit" className="button" disabled={busy || !name.trim()}>
              {busy ? messages.entry.creating : messages.entry.create}
            </button>
          </div>
        </form>
      ) : (
        <div className="entry__actions">
          <button type="button" className="button" onClick={() => setCreating(true)}>
            {messages.entry.startNew}
          </button>
          <Link to="/projects" className="button button--secondary">
            {messages.entry.openSaved}
          </Link>
        </div>
      )}

      <p>
        <Link to="/methodology">{messages.entry.methodologyLink}</Link>
      </p>
    </div>
  );
}
