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
import projectMigrated from './fixtures/project-migrated.json';

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
    // Three evaluated (A, B, and the package D) and one draft (C), as recorded.
    const evaluated = project.assessments.filter((a) => a.result != null).length;
    expect(screen.getAllByText(messages.project.evaluated)).toHaveLength(evaluated);
    expect(screen.getAllByText(messages.project.draft)).toHaveLength(
      project.assessments.length - evaluated,
    );
    // More than one evaluated option: comparison is offered.
    expect(screen.getByRole('link', { name: messages.project.compare })).toBeInTheDocument();
  });

  it('surfaces what a storage migration changed, itemised (D-029, D-044.2)', async () => {
    installFetchMock([
      { method: 'GET', path: '/api/meta', response: meta },
      {
        method: 'GET',
        path: `/api/projects/${projectMigrated.project_id}`,
        response: projectMigrated,
      },
    ]);
    renderAt(
      `/projects/${projectMigrated.project_id}`,
      <Route path="projects/:projectId" element={<ProjectScreen />} />,
    );

    expect(await screen.findByText(messages.project.migratedHeading)).toBeInTheDocument();
    expect(projectMigrated.migrated_notes.length).toBeGreaterThan(0);
    for (const note of projectMigrated.migrated_notes) {
      expect(screen.getByText(note)).toBeInTheDocument();
    }
  });

  it('says nothing about migration when a project was not migrated', async () => {
    installFetchMock([
      { method: 'GET', path: '/api/meta', response: meta },
      { method: 'GET', path: `/api/projects/${project.project_id}`, response: project },
    ]);
    renderAt(projectUrl, <Route path="projects/:projectId" element={<ProjectScreen />} />);

    await screen.findByRole('heading', { name: project.name });
    expect(screen.queryByText(messages.project.migratedHeading)).not.toBeInTheDocument();
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
