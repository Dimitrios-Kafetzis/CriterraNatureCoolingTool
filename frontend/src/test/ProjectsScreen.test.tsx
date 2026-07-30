import { screen } from '@testing-library/react';
import { Route } from 'react-router';
import { describe, expect, it } from 'vitest';
import { ProjectsScreen } from '../screens/ProjectsScreen';
import { messages } from '../i18n/en';
import { installFetchMock } from './mockFetch';
import { renderAt } from './render';
import meta from './fixtures/meta.json';
import projectList from './fixtures/project-list.json';

describe('ProjectsScreen', () => {
  it('lists saved projects from GET /api/projects', async () => {
    installFetchMock([
      { method: 'GET', path: '/api/meta', response: meta },
      { method: 'GET', path: '/api/projects', response: projectList },
    ]);
    renderAt('/projects', <Route path="projects" element={<ProjectsScreen />} />);

    const first = projectList[0]!;
    expect(await screen.findByRole('link', { name: first.name })).toBeInTheDocument();
    expect(
      screen.getByText(new RegExp(messages.projects.assessmentCount(first.assessment_count))),
    ).toBeInTheDocument();
  });

  it('shows the empty state when nothing is saved', async () => {
    installFetchMock([
      { method: 'GET', path: '/api/meta', response: meta },
      { method: 'GET', path: '/api/projects', response: [] },
    ]);
    renderAt('/projects', <Route path="projects" element={<ProjectsScreen />} />);
    expect(await screen.findByText(messages.projects.empty)).toBeInTheDocument();
  });
});
