import { screen } from '@testing-library/react';
import { Route } from 'react-router';
import { describe, expect, it } from 'vitest';
import { CompareScreen } from '../screens/CompareScreen';
import { messages } from '../i18n/en';
import { storedResult } from '../api/types';
import type { ProjectView } from '../api/types';
import { installFetchMock } from './mockFetch';
import { renderAt } from './render';
import meta from './fixtures/meta.json';
import project from './fixtures/project.json';

const view = project as unknown as ProjectView;
const evaluated = view.assessments.filter((assessment) => assessment.result != null);

function renderCompare() {
  installFetchMock([
    { method: 'GET', path: '/api/meta', response: meta },
    { method: 'GET', path: `/api/projects/${project.project_id}`, response: project },
  ]);
  return renderAt(
    `/projects/${project.project_id}/compare`,
    <Route path="projects/:projectId/compare" element={<CompareScreen />} />,
  );
}

describe('CompareScreen', () => {
  it('places the evaluated options side by side; drafts are not offered', async () => {
    renderCompare();
    expect(await screen.findByRole('heading', { name: messages.compare.heading })).toBeVisible();
    for (const option of evaluated) {
      expect(screen.getByRole('columnheader', { name: option.label })).toBeInTheDocument();
    }
    // Option C is a draft and must not be selectable for comparison.
    expect(screen.queryByRole('checkbox', { name: /Option C/ })).not.toBeInTheDocument();
  });

  it('highlights rows that differ and mutes identical ones, never naming a winner', async () => {
    renderCompare();
    await screen.findByRole('heading', { name: messages.compare.heading });

    // The recorded options differ by typology; the row is emphasised.
    const typologyRow = screen.getByRole('row', {
      name: new RegExp(messages.compare.row.typology),
    });
    expect(typologyRow.className).toBe('differs');
    for (const option of evaluated) {
      expect(typologyRow).toHaveTextContent(storedResult(option)!.typology.display_name);
    }

    // Same site → identical Heat Priority Index: the row is muted, not repeated as signal.
    const hpiRow = screen.getByRole('row', {
      name: new RegExp(messages.compare.row.heatPriority),
    });
    expect(hpiRow.className).toBe('identical');
  });
});
