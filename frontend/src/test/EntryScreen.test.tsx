import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Route } from 'react-router';
import { describe, expect, it } from 'vitest';
import { EntryScreen } from '../screens/EntryScreen';
import { messages } from '../i18n/en';
import { installFetchMock } from './mockFetch';
import { renderAt } from './render';
import assessmentDraft from './fixtures/assessment-draft.json';
import meta from './fixtures/meta.json';
import project from './fixtures/project.json';

describe('EntryScreen', () => {
  it('states the premise before asking anything, and links the methodology', () => {
    installFetchMock([{ method: 'GET', path: '/api/meta', response: meta }]);
    renderAt('/', <Route index element={<EntryScreen />} />);
    expect(screen.getByText(messages.entry.partialAnswers)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: messages.entry.startNew })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: messages.entry.openSaved })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: messages.entry.methodologyLink })).toBeInTheDocument();
  });

  it('creates a project and its first assessment, then opens the wizard', async () => {
    const { calls } = installFetchMock([
      { method: 'GET', path: '/api/meta', response: meta },
      { method: 'POST', path: '/api/projects', response: { ...project, assessments: [] } },
      {
        method: 'POST',
        path: `/api/projects/${project.project_id}/assessments`,
        response: assessmentDraft,
        status: 201,
      },
    ]);
    renderAt(
      '/',
      <>
        <Route index element={<EntryScreen />} />
        <Route
          path="projects/:projectId/assessments/:assessmentId/edit"
          element={<div>wizard-probe</div>}
        />
      </>,
    );

    const user = userEvent.setup();
    await user.click(screen.getByRole('button', { name: messages.entry.startNew }));
    await user.type(
      screen.getByLabelText(messages.entry.newProjectName),
      'Riverside school quarter',
    );
    await user.click(screen.getByRole('button', { name: messages.entry.create }));

    expect(await screen.findByText('wizard-probe')).toBeInTheDocument();
    const createProject = calls.find(
      (call) => call.method === 'POST' && call.url === '/api/projects',
    );
    expect(createProject?.body).toEqual({ name: 'Riverside school quarter' });
    const createAssessment = calls.find(
      (call) =>
        call.method === 'POST' && call.url === `/api/projects/${project.project_id}/assessments`,
    );
    expect(createAssessment?.body).toEqual({
      label: messages.project.defaultFirstLabel,
      input: { project_name: 'Riverside school quarter' },
    });
  });
});
