import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Route } from 'react-router';
import { describe, expect, it } from 'vitest';
import { WizardScreen } from '../screens/WizardScreen';
import { messages } from '../i18n/en';
import { installFetchMock, type Route as MockRoute } from './mockFetch';
import { renderAt } from './render';
import assessmentDraft from './fixtures/assessment-draft.json';
import assessmentEvaluated from './fixtures/assessment-evaluated.json';
import meta from './fixtures/meta.json';
import methodology from './fixtures/methodology.json';
import project from './fixtures/project.json';
import typologies from './fixtures/typologies.json';
import validateCapped from './fixtures/validate-capped.json';
import validateEmpty from './fixtures/validate-empty.json';
import validatePartial from './fixtures/validate-partial.json';

const draftUrl = `/projects/${project.project_id}/assessments/${assessmentDraft.assessment_id}/edit`;

function baseRoutes(validateResponse: unknown): MockRoute[] {
  return [
    { method: 'GET', path: '/api/meta', response: meta },
    { method: 'GET', path: '/api/typologies', response: typologies },
    { method: 'GET', path: '/api/methodology', response: methodology },
    {
      method: 'GET',
      path: new RegExp(`^/api/projects/${project.project_id}/assessments/[^/]+$`),
      response: assessmentDraft,
    },
    {
      method: 'PATCH',
      path: new RegExp(`^/api/projects/${project.project_id}/assessments/[^/]+$`),
      response: assessmentDraft,
    },
    { method: 'POST', path: '/api/assessments/validate', response: validateResponse },
  ];
}

function renderWizard(url = draftUrl, extraRoutes: React.ReactNode = null) {
  return renderAt(
    url,
    <>
      <Route path="projects/:projectId/assessments/:assessmentId/edit" element={<WizardScreen />} />
      {extraRoutes}
    </>,
  );
}

describe('WizardScreen', () => {
  it('filters validation errors to the active step and blocks Continue (OQ-08)', async () => {
    installFetchMock(baseRoutes(validateEmpty));
    renderWizard();

    expect(
      await screen.findByRole('heading', { name: messages.wizard.steps.project.title }),
    ).toBeInTheDocument();
    // validate-empty carries four required-field errors; only step 1's
    // (assessment_scale) may appear here.
    const alerts = await screen.findAllByRole('alert');
    expect(alerts).toHaveLength(1);
    expect(screen.getByRole('button', { name: messages.wizard.continue })).toBeDisabled();
    expect(screen.getByText(messages.wizard.blockedByErrors)).toBeInTheDocument();
  });

  it('renders the confidence panel from the engine preview, with the missing-field hint', async () => {
    installFetchMock(baseRoutes(validateEmpty));
    renderWizard();

    const expectedHint =
      messages.confidence.hintNext(messages.fields.existing_tree_canopy_percent!.label) +
      messages.confidence.stepRef(messages.wizard.steps.site.title);
    expect(await screen.findByText(`→ ${expectedHint}`)).toBeInTheDocument();
  });

  it('auto-saves the draft with a debounced PATCH (D-020)', async () => {
    const { calls } = installFetchMock(baseRoutes(validateEmpty));
    renderWizard();

    const user = userEvent.setup();
    // Scoped to the control: the field's explanation button (D-041) also
    // carries the field label in its accessible name, by design.
    const scaleSelect = await screen.findByLabelText(
      new RegExp(messages.fields.assessment_scale!.label),
      { selector: 'select' },
    );
    await user.selectOptions(scaleSelect, 'neighbourhood');

    await waitFor(
      () => {
        const patch = calls.find((call) => call.method === 'PATCH');
        expect(patch).toBeDefined();
        expect((patch?.body as { input: Record<string, unknown> }).input).toMatchObject({
          project_name: 'Riverside school quarter',
          assessment_scale: 'neighbourhood',
        });
      },
      { timeout: 3000 },
    );
    expect(await screen.findByText(messages.wizard.saved)).toBeInTheDocument();
  });

  it('shows warnings without ever blocking (OQ-08)', async () => {
    installFetchMock(baseRoutes(validatePartial));
    renderWizard();

    for (const warning of validatePartial.warnings) {
      expect(await screen.findByText(warning)).toBeInTheDocument();
    }
    expect(screen.getByText(messages.wizard.warningsNeverBlock)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: messages.wizard.continue })).toBeEnabled();
  });

  it('explains the evidence-confidence cap when the engine reports it (D-031)', async () => {
    installFetchMock(baseRoutes(validateCapped));
    renderWizard();
    expect(await screen.findByText(messages.confidence.evidenceCap)).toBeInTheDocument();
  });

  it('renders all 14 typology cards on the intervention step (D-019)', async () => {
    installFetchMock(baseRoutes(validatePartial));
    renderWizard(`${draftUrl}?step=5`);

    expect(
      await screen.findByRole('heading', { name: messages.wizard.steps.intervention.title }),
    ).toBeInTheDocument();
    const cards = await screen.findAllByRole('button', { pressed: false });
    expect(cards.filter((card) => card.className.includes('picker__card')).length).toBe(
      typologies.typologies.length,
    );
  });

  it('evaluates explicitly from the last step and navigates to results (OQ-15)', async () => {
    const { calls } = installFetchMock([
      ...baseRoutes(validatePartial),
      {
        method: 'POST',
        path: new RegExp(`/assessments/${assessmentDraft.assessment_id}/evaluate$`),
        response: assessmentEvaluated,
      },
    ]);
    renderWizard(
      `${draftUrl}?step=6`,
      <Route
        path="projects/:projectId/assessments/:assessmentId/results"
        element={<div>results-probe</div>}
      />,
    );

    const user = userEvent.setup();
    await user.click(await screen.findByRole('button', { name: messages.wizard.runAssessment }));

    expect(await screen.findByText('results-probe')).toBeInTheDocument();
    expect(calls.some((call) => call.method === 'POST' && call.url.endsWith('/evaluate'))).toBe(
      true,
    );
  });

  it('redirects to results when the assessment is already evaluated (frozen input, D-029)', async () => {
    installFetchMock([
      { method: 'GET', path: '/api/meta', response: meta },
      { method: 'GET', path: '/api/typologies', response: typologies },
      { method: 'GET', path: '/api/methodology', response: methodology },
      {
        method: 'GET',
        path: new RegExp(`^/api/projects/${project.project_id}/assessments/[^/]+$`),
        response: assessmentEvaluated,
      },
    ]);
    renderWizard(
      `/projects/${project.project_id}/assessments/${assessmentEvaluated.assessment_id}/edit`,
      <Route
        path="projects/:projectId/assessments/:assessmentId/results"
        element={<div>results-probe</div>}
      />,
    );
    expect(await screen.findByText('results-probe')).toBeInTheDocument();
  });
});
