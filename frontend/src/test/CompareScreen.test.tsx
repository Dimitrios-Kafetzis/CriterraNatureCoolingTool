import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
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

function renderCompare(fixture: unknown = project) {
  installFetchMock([
    { method: 'GET', path: '/api/meta', response: meta },
    { method: 'GET', path: `/api/projects/${project.project_id}`, response: fixture },
  ]);
  return renderAt(
    `/projects/${project.project_id}/compare`,
    <Route path="projects/:projectId/compare" element={<CompareScreen />} />,
  );
}

/** The recorded project with one evaluated option moved to another scale. */
function crossScaleFixture(): ProjectView {
  const clone = JSON.parse(JSON.stringify(project)) as ProjectView;
  const other = clone.assessments.find((assessment) => assessment.result != null);
  other!.input.assessment_scale = 'district';
  return clone;
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

  it('offers the comparison export in the on-screen column order (v2.4)', async () => {
    renderCompare();
    await screen.findByRole('heading', { name: messages.compare.heading });

    const pdf = screen.getByRole('link', { name: messages.compare.exportPdf });
    const xlsx = screen.getByRole('link', { name: messages.compare.exportXlsx });
    const query = evaluated
      .slice(0, 3)
      .map((option) => `assessments=${option.assessment_id}`)
      .join('&');
    expect(pdf).toHaveAttribute(
      'href',
      `/api/projects/${project.project_id}/report/comparison.pdf?${query}`,
    );
    expect(xlsx).toHaveAttribute(
      'href',
      `/api/projects/${project.project_id}/report/comparison.xlsx?${query}`,
    );
  });

  it('states the assessment scale and stays silent when it is uniform', async () => {
    renderCompare();
    await screen.findByRole('heading', { name: messages.compare.heading });

    const scaleRow = screen.getByRole('row', { name: new RegExp(messages.compare.row.scale) });
    expect(scaleRow.className).toBe('identical');
    expect(screen.queryByText(messages.compare.crossScale)).not.toBeInTheDocument();
  });

  it('flags a cross-scale comparison instead of tabulating it silently (v2.4)', async () => {
    renderCompare(crossScaleFixture());
    await screen.findByRole('heading', { name: messages.compare.heading });

    expect(screen.getByText(messages.compare.crossScale)).toBeVisible();
    const scaleRow = screen.getByRole('row', { name: new RegExp(messages.compare.row.scale) });
    expect(scaleRow.className).toBe('differs');
    expect(scaleRow).toHaveTextContent(messages.options.assessment_scale.district);
  });

  it('withholds the export above four options and says why', async () => {
    const wide = JSON.parse(JSON.stringify(project)) as ProjectView;
    const source = wide.assessments.find((assessment) => assessment.result != null)!;
    for (let index = 0; index < 2; index += 1) {
      wide.assessments.push({
        ...(JSON.parse(JSON.stringify(source)) as typeof source),
        assessment_id: `00000000-0000-0000-0000-00000000000${index}`,
        label: `Extra ${index + 1}`,
      });
    }
    renderCompare(wide);
    await screen.findByRole('heading', { name: messages.compare.heading });

    // Five evaluated options selected: the on-screen table still renders,
    // the export does not pretend it can.
    const user = userEvent.setup();
    for (const label of ['Extra 1', 'Extra 2']) {
      await user.click(screen.getByRole('checkbox', { name: new RegExp(label) }));
    }
    expect(screen.getByText(messages.compare.exportLimit)).toBeVisible();
    expect(
      screen.queryByRole('link', { name: messages.compare.exportPdf }),
    ).not.toBeInTheDocument();
  });
});
