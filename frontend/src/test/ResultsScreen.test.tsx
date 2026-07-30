import { screen } from '@testing-library/react';
import { Route } from 'react-router';
import { describe, expect, it } from 'vitest';
import { ResultsScreen } from '../screens/ResultsScreen';
import { messages } from '../i18n/en';
import type { AssessmentResult, AssessmentView } from '../api/types';
import { installFetchMock } from './mockFetch';
import { renderAt } from './render';
import assessmentDraft from './fixtures/assessment-draft.json';
import assessmentEvaluated from './fixtures/assessment-evaluated.json';
import meta from './fixtures/meta.json';
import project from './fixtures/project.json';
import resultUnsuitable from './fixtures/result-unsuitable.json';

const evaluated = assessmentEvaluated as unknown as AssessmentView;
const result = evaluated.result as unknown as AssessmentResult;
const resultsUrl = `/projects/${project.project_id}/assessments/${evaluated.assessment_id}/results`;

function renderResults(fixture: unknown, url = resultsUrl) {
  installFetchMock([
    { method: 'GET', path: '/api/meta', response: meta },
    {
      method: 'GET',
      path: new RegExp(`^/api/projects/${project.project_id}/assessments/[^/]+$`),
      response: fixture,
    },
  ]);
  return renderAt(
    url,
    <Route
      path="projects/:projectId/assessments/:assessmentId/results"
      element={<ResultsScreen />}
    />,
  );
}

describe('ResultsScreen', () => {
  it('renders both score cards verbatim from the stored result', async () => {
    renderResults(assessmentEvaluated);
    expect(
      await screen.findByRole('region', { name: messages.results.heatPriority }),
    ).toHaveTextContent(String(result.heat_priority.score));
    expect(screen.getByRole('region', { name: messages.results.opportunity })).toHaveTextContent(
      String(result.opportunity.score),
    );
  });

  it('renders the deterministic recommendation and method note as the engine composed them', async () => {
    renderResults(assessmentEvaluated);
    expect(await screen.findByText(result.recommendation)).toBeInTheDocument();
    expect(screen.getByText(result.method_note)).toBeInTheDocument();
    expect(
      screen.getByText(
        messages.results.versions(result.methodology_version, result.engine_version),
      ),
    ).toBeInTheDocument();
  });

  it('itemises every assumption the engine applied', async () => {
    renderResults(assessmentEvaluated);
    await screen.findByText(messages.results.assumptionsHeading);
    for (const assumption of result.assumptions_applied) {
      expect(screen.getByText(assumption)).toBeInTheDocument();
    }
  });

  it('shows calculated ranges, never point estimates, for energy and payback', async () => {
    renderResults(assessmentEvaluated);
    await screen.findByText(messages.results.heading);
    const min = result.energy.savings_min_kwh_per_year!.toLocaleString(undefined, {
      maximumFractionDigits: 2,
    });
    const max = result.energy.savings_max_kwh_per_year!.toLocaleString(undefined, {
      maximumFractionDigits: 2,
    });
    expect(screen.getByText(new RegExp(`${min}–\\s*${max}`.replace(/\s/g, '\\s*')))).toBeVisible();
  });

  it('renders suitability flags prominently (D-009)', async () => {
    const view: AssessmentView = {
      assessment_id: 'unsuitable-1',
      label: 'Option X',
      created_at: evaluated.created_at,
      input: {},
      result: resultUnsuitable,
      methodology_update_available: false,
    };
    renderResults(view, `/projects/${project.project_id}/assessments/unsuitable-1/results`);
    await screen.findByText(messages.results.flagsHeading);
    for (const flag of (resultUnsuitable as unknown as AssessmentResult).suitability.flags) {
      expect(screen.getByText(flag.message)).toBeInTheDocument();
    }
  });

  it('offers the questionnaire, not results, for a draft', async () => {
    renderResults(assessmentDraft);
    expect(await screen.findByText(messages.results.draftNotice)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: messages.results.continueDraft })).toBeInTheDocument();
  });
});
