import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Route } from 'react-router';
import { describe, expect, it } from 'vitest';
import { ProjectScreen } from '../screens/ProjectScreen';
import { messages } from '../i18n/en';
import { installFetchMock } from './mockFetch';
import { renderAt } from './render';
import assessmentDuplicate from './fixtures/assessment-duplicate.json';
import meta from './fixtures/meta.json';
import project from './fixtures/project.json';

const projectUrl = `/projects/${project.project_id}`;

describe('ProjectScreen', () => {
  it('lists assessments with draft/evaluated state and offers comparison', async () => {
    installFetchMock([
      { method: 'GET', path: '/api/meta', response: meta },
      { method: 'GET', path: `/api/projects/${project.project_id}`, response: project },
    ]);
    renderAt(projectUrl, <Route path="projects/:projectId" element={<ProjectScreen />} />);

    expect(await screen.findByRole('heading', { name: project.name })).toBeInTheDocument();
    expect(screen.getByText('Option A')).toBeInTheDocument();
    expect(screen.getByText('Option C')).toBeInTheDocument();
    // Two evaluated (A, B) and one draft (C), as recorded.
    expect(screen.getAllByText(messages.project.evaluated)).toHaveLength(2);
    expect(screen.getAllByText(messages.project.draft)).toHaveLength(1);
    // Two evaluated options: comparison is offered.
    expect(screen.getByRole('link', { name: messages.project.compare })).toBeInTheDocument();
  });

  it('duplicates an assessment (D-021) and opens the wizard at the intervention step', async () => {
    const { calls } = installFetchMock([
      { method: 'GET', path: '/api/meta', response: meta },
      { method: 'GET', path: `/api/projects/${project.project_id}`, response: project },
      {
        method: 'POST',
        path: new RegExp(`^/api/projects/${project.project_id}/assessments/[^/]+/duplicate$`),
        response: assessmentDuplicate,
        status: 201,
      },
    ]);
    renderAt(
      projectUrl,
      <>
        <Route path="projects/:projectId" element={<ProjectScreen />} />
        <Route
          path="projects/:projectId/assessments/:assessmentId/edit"
          element={<div>wizard-probe</div>}
        />
      </>,
    );

    const user = userEvent.setup();
    const duplicateButtons = await screen.findAllByRole('button', {
      name: messages.project.duplicate,
    });
    await user.click(duplicateButtons[0]!);

    expect(await screen.findByText('wizard-probe')).toBeInTheDocument();
    expect(calls.some((call) => call.method === 'POST' && call.url.endsWith('/duplicate'))).toBe(
      true,
    );
  });
});
