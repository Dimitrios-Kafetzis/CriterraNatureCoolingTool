import { screen, within } from '@testing-library/react';
import { Route } from 'react-router';
import { describe, expect, it } from 'vitest';
import { ResultsScreen } from '../screens/ResultsScreen';
import { messages } from '../i18n/en';
import type { AssessmentResult, AssessmentView } from '../api/types';
import { installFetchMock } from './mockFetch';
import { renderAt } from './render';
import assessmentDraft from './fixtures/assessment-draft.json';
import assessmentEvaluated from './fixtures/assessment-evaluated.json';
import assessmentPackage from './fixtures/assessment-package.json';
import meta from './fixtures/meta.json';
import project from './fixtures/project.json';
import resultMinimal from './fixtures/result-minimal.json';
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

  it('uses the neutral wording for non-derived cooling outputs, never the cost sentence', async () => {
    const view: AssessmentView = {
      assessment_id: 'minimal-1',
      label: 'Option M',
      created_at: evaluated.created_at,
      input: {},
      result: resultMinimal,
      methodology_update_available: false,
    };
    renderResults(view, `/projects/${project.project_id}/assessments/minimal-1/results`);
    await screen.findByText(messages.results.heading);
    // Shade potential and time to benefit (D-034): sizing inputs, not cost data.
    expect(screen.getAllByText(messages.results.cooling.notEstimated)).toHaveLength(2);
    // The economic wording remains reserved for the cost outputs.
    const costsBlock = screen
      .getByRole('heading', { name: messages.results.blocks.costs })
      .closest('section') as HTMLElement;
    expect(costsBlock.textContent).toContain(messages.results.statuses.not_estimated);
  });

  it('enables the Export action as two downloads hitting the report endpoints', async () => {
    renderResults(assessmentEvaluated);
    const base = `/api/projects/${project.project_id}/assessments/${evaluated.assessment_id}`;
    const pdf = await screen.findByRole('link', { name: messages.results.actions.exportPdf });
    expect(pdf).toHaveAttribute('href', `${base}/report.pdf`);
    expect(pdf).toHaveAttribute('download');
    const xlsx = screen.getByRole('link', { name: messages.results.actions.exportXlsx });
    expect(xlsx).toHaveAttribute('href', `${base}/report.xlsx`);
    expect(xlsx).toHaveAttribute('download');
  });

  it('offers the questionnaire, not results, for a draft', async () => {
    renderResults(assessmentDraft);
    expect(await screen.findByText(messages.results.draftNotice)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: messages.results.continueDraft })).toBeInTheDocument();
  });

  it('shows no package section for a single-intervention assessment (D-038)', async () => {
    renderResults(assessmentEvaluated);
    await screen.findByText(messages.results.heading);
    expect(result.package.component_count).toBe(1);
    expect(
      screen.queryByRole('region', { name: messages.results.packageSection.heading }),
    ).not.toBeInTheDocument();
  });
});

describe('ResultsScreen — packages (D-038)', () => {
  const view = assessmentPackage as unknown as AssessmentView;
  const packaged = view.result as unknown as AssessmentResult;
  const url = `/projects/${project.project_id}/assessments/${view.assessment_id}/results`;
  const p = messages.results.packageSection;

  it('itemises every component with its own range, evidence class and suitability', async () => {
    renderResults(assessmentPackage, url);
    const section = await screen.findByRole('region', { name: p.heading });
    expect(packaged.components.length).toBeGreaterThan(1);

    for (const component of packaged.components) {
      const item = within(section)
        .getAllByRole('listitem')
        .find((element) => element.textContent!.includes(component.typology.display_name))!;
      expect(item).toBeDefined();
      const text = item.textContent!;
      expect(text).toContain(component.typology.archetype_display_name);
      expect(text).toContain(String(component.cooling.delta_t_min_c));
      expect(text).toContain(String(component.cooling.delta_t_max_c));
      expect(text).toContain(String(component.suitability.score));
    }
  });

  it('marks exactly the component that carries the headline estimate', async () => {
    renderResults(assessmentPackage, url);
    const section = await screen.findByRole('region', { name: p.heading });
    const marks = within(section).getAllByText(p.representative);
    expect(marks).toHaveLength(1);
    const representative = packaged.components.find((component) => component.is_representative)!;
    expect(representative.typology.nbs_type).toBe(packaged.package.representative_nbs_type);
    expect(marks[0]!.closest('li')!.textContent).toContain(representative.typology.display_name);
  });

  it('renders the combination rules as the engine stated them, not restated', async () => {
    renderResults(assessmentPackage, url);
    const section = await screen.findByRole('region', { name: p.heading });
    for (const rule of [
      packaged.package.cooling_rule,
      packaged.package.co_benefit_rule,
      packaged.package.suitability_rule,
      packaged.package.cost_rule,
    ]) {
      expect(within(section).getByText(rule)).toBeInTheDocument();
    }
    expect(
      within(section).getByText(
        (_content, element) =>
          element?.tagName === 'P' &&
          element.textContent ===
            `${p.representativeWhy}: ${packaged.package.representative_reason}`,
      ),
    ).toBeInTheDocument();
  });

  it('names the single component the energy figure was derived from', async () => {
    renderResults(assessmentPackage, url);
    const section = await screen.findByRole('region', { name: p.heading });
    const energyComponent = packaged.components.find(
      (component) => component.typology.nbs_type === packaged.package.energy_component_nbs_type,
    );
    expect(
      within(section).getByText(
        energyComponent
          ? p.energyComponent(energyComponent.typology.display_name)
          : p.energyNoComponent,
      ),
    ).toBeInTheDocument();
  });
});
