import { screen, waitFor, within } from '@testing-library/react';
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
import assessmentDuplicate from './fixtures/assessment-duplicate.json';
import project from './fixtures/project.json';
import typologies from './fixtures/typologies.json';
import available from './fixtures/typologies-available.json';
import imagesManifest from './fixtures/images-manifest.json';
import validateCapped from './fixtures/validate-capped.json';
import validateEmpty from './fixtures/validate-empty.json';
import validatePartial from './fixtures/validate-partial.json';

import { stepNumber, type StepId } from '../wizard/steps';

const draftUrl = `/projects/${project.project_id}/assessments/${assessmentDraft.assessment_id}/edit`;

function baseRoutes(
  validateResponse: unknown,
  storedAssessment: unknown = assessmentDraft,
): MockRoute[] {
  return [
    { method: 'GET', path: '/api/meta', response: meta },
    { method: 'GET', path: '/api/typologies', response: typologies },
    { method: 'GET', path: '/api/typologies/available', response: available },
    { method: 'GET', path: '/api/methodology', response: methodology },
    {
      method: 'GET',
      path: new RegExp(`^/api/projects/${project.project_id}/assessments/[^/]+$`),
      response: storedAssessment,
    },
    {
      method: 'PATCH',
      path: new RegExp(`^/api/projects/${project.project_id}/assessments/[^/]+$`),
      response: assessmentDraft,
    },
    { method: 'POST', path: '/api/assessments/validate', response: validateResponse },
    { method: 'GET', path: '/api/images/manifest', response: imagesManifest },
  ];
}

/**
 * The URL of one step, by id.
 *
 * These tests used to name steps by number, which was correct until v2.1 put a
 * map step in front of them and turned every `?step=5` into a different
 * question. Naming the step is the fix that keeps working.
 */
function stepUrl(id: StepId): string {
  return `${draftUrl}?step=${String(stepNumber(id))}`;
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
    renderWizard(stepUrl('project'));

    expect(
      await screen.findByRole('heading', { name: messages.wizard.steps.project.title }),
    ).toBeInTheDocument();
    // validate-empty carries four required-field errors; only the project
    // step's (assessment_scale) may appear here.
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
    renderWizard(stepUrl('project'));

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

  it('renders every catalogue entry on the intervention step (D-019, D-043)', async () => {
    installFetchMock(baseRoutes(validatePartial));
    renderWizard(stepUrl('intervention'));

    expect(
      await screen.findByRole('heading', { name: messages.wizard.steps.intervention.title }),
    ).toBeInTheDocument();
    const cards = await screen.findAllByRole('button', { pressed: false });
    expect(cards.filter((card) => card.className.includes('picker__card')).length).toBe(
      typologies.resolved.length,
    );
  });

  it('serves the example-image manifest to the picker in one request (v2.3, D-051)', async () => {
    // The duplicate's site answers temperate, which the fixture manifest
    // holds images for, so the affordances render; the draft fixture with no
    // climate zone is covered by the picker's own tests.
    const { calls } = installFetchMock(baseRoutes(validatePartial, assessmentDuplicate));
    renderWizard(stepUrl('intervention'));

    await screen.findByRole('heading', { name: messages.wizard.steps.intervention.title });
    await waitFor(() => {
      expect(document.querySelectorAll('.picker__photo').length).toBeGreaterThan(0);
    });
    // One manifest request — never a per-card lookup over 110 entries.
    expect(calls.filter((call) => call.url === '/api/images/manifest')).toHaveLength(1);
  });

  it('asks the service which entries this site is offered, computing no rule of its own', async () => {
    // The duplicate carries the site: scale, land use, and the four gating
    // answers, which are exactly what the availability query is built from.
    const { calls } = installFetchMock(baseRoutes(validatePartial, assessmentDuplicate));
    renderWizard(stepUrl('intervention'));

    await screen.findByRole('heading', { name: messages.wizard.steps.intervention.title });
    await waitFor(() => {
      const call = calls.find((candidate) => candidate.url.startsWith('/api/typologies/available'));
      expect(call).toBeDefined();
      const query = new URLSearchParams(call!.url.split('?')[1]);
      expect(query.get('assessment_scale')).toBe(assessmentDuplicate.input.assessment_scale);
      expect(query.get('land_use')).toBe(assessmentDuplicate.input.land_use);
      expect(query.get('waterfront_type')).toBe(assessmentDuplicate.input.waterfront_type);
      // yes/no answers reach the service as booleans, and only when answered.
      expect(query.get('includes_railway')).toBe('false');
      expect(query.getAll('productive_governance')).toEqual(
        assessmentDuplicate.input.productive_governance,
      );
    });

    // What the service withheld is separated and labelled, never removed.
    expect(
      await screen.findByRole('region', { name: messages.picker.notOfferedHeading }),
    ).toBeInTheDocument();
  });

  it('asks nothing while the scale is unanswered, and offers every entry', async () => {
    // The bare draft has no assessment_scale, so there is nothing to ask.
    const { calls } = installFetchMock(baseRoutes(validatePartial));
    renderWizard(stepUrl('intervention'));

    await screen.findByRole('heading', { name: messages.wizard.steps.intervention.title });
    await screen.findAllByRole('button', { pressed: false });
    expect(calls.some((call) => call.url.startsWith('/api/typologies/available'))).toBe(false);
    expect(
      screen.queryByRole('region', { name: messages.picker.notOfferedHeading }),
    ).not.toBeInTheDocument();
  });

  it('saves a multi-component package as an ordered list (D-038)', async () => {
    const { calls } = installFetchMock(baseRoutes(validatePartial, assessmentDuplicate));
    renderWizard(stepUrl('intervention'));

    await screen.findByRole('heading', { name: messages.wizard.steps.intervention.title });
    const user = userEvent.setup();
    const chosen = available.nbs_types.slice(0, 2);
    for (const nbsType of chosen) {
      const entry = typologies.resolved.find((candidate) => candidate.nbs_type === nbsType)!;
      const card = screen
        .getAllByRole('button')
        .find(
          (element) =>
            element.className.includes('picker__card') &&
            element.querySelector('.picker__name')?.textContent === entry.display_name,
        )!;
      await user.click(card);
    }

    await waitFor(
      () => {
        const patches = calls.filter((call) => call.method === 'PATCH');
        const last = patches[patches.length - 1];
        expect((last?.body as { input: { nbs_type?: string[] } }).input.nbs_type).toEqual(chosen);
      },
      { timeout: 3000 },
    );
  });

  it('asks the four availability questions on the site step, each stated as feeding no score (D-044.1)', async () => {
    installFetchMock(baseRoutes(validatePartial));
    renderWizard(stepUrl('site'));

    await screen.findByRole('heading', { name: messages.wizard.steps.site.title });
    for (const field of [
      'includes_railway',
      'existing_woodland',
      'waterfront_type',
      'productive_governance',
    ] as const) {
      const meta = messages.fields[field]!;
      expect(screen.getByText(meta.label)).toBeInTheDocument();
      // D-041: the explanation says plainly that the answer feeds no score.
      expect(meta.affects).toMatch(/feeds no score|cannot raise or lower any result/);
    }
  });

  it('records a multi-select answer as a list, and an empty one as unanswered (D-043.3)', async () => {
    const { calls } = installFetchMock(baseRoutes(validatePartial));
    renderWizard(stepUrl('site'));

    await screen.findByRole('heading', { name: messages.wizard.steps.site.title });
    const user = userEvent.setup();
    const group = screen.getByRole('group', {
      name: new RegExp(messages.fields.productive_governance!.label),
    });
    const community = within(group).getByLabelText(
      messages.options.productive_governance.community,
    );
    const commercial = within(group).getByLabelText(
      messages.options.productive_governance.commercial,
    );

    await user.click(community);
    await user.click(commercial);
    await waitFor(
      () => {
        const patches = calls.filter((call) => call.method === 'PATCH');
        const last = patches[patches.length - 1];
        expect(
          (last?.body as { input: { productive_governance?: string[] } }).input
            .productive_governance,
        ).toEqual(['community', 'commercial']);
      },
      { timeout: 3000 },
    );

    // Unticking every box removes the field rather than storing an empty list.
    await user.click(community);
    await user.click(commercial);
    await waitFor(
      () => {
        const patches = calls.filter((call) => call.method === 'PATCH');
        const last = patches[patches.length - 1];
        expect((last?.body as { input: Record<string, unknown> }).input).not.toHaveProperty(
          'productive_governance',
        );
      },
      { timeout: 3000 },
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
      stepUrl('cost'),
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
      { method: 'GET', path: '/api/typologies/available', response: available },
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
