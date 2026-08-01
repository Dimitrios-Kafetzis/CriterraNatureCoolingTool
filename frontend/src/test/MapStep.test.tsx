/**
 * The map step (v2.1, D-047).
 *
 * The behaviours under test are the ones the rulings turn on, not the drawing:
 * the step is skippable in one action and the questionnaire works without it;
 * exactly three inputs are offered; an offer never overwrites an answer the
 * user has already given; and an autofilled answer is marked where it is asked
 * and loses its mark the moment the user edits it.
 */

import { describe, expect, it } from 'vitest';
import { Route } from 'react-router';
import { screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { WizardScreen } from '../screens/WizardScreen';
import { installFetchMock, type Route as MockRoute } from './mockFetch';
import { renderAt } from './render';
import { STEPS, stepNumber } from '../wizard/steps';

import meta from './fixtures/meta.json';
import typologies from './fixtures/typologies.json';
import available from './fixtures/typologies-available.json';
import methodology from './fixtures/methodology.json';
import project from './fixtures/project.json';
import assessmentDraft from './fixtures/assessment-draft.json';
import validatePartial from './fixtures/validate-partial.json';
import basemap from './fixtures/basemap.json';
import geoLookup from './fixtures/geo-lookup.json';
import geoLookupOcean from './fixtures/geo-lookup-ocean.json';

const editUrl = `/projects/${project.project_id}/assessments/${assessmentDraft.assessment_id}/edit`;
const mapUrl = `${editUrl}?step=${String(stepNumber('map'))}`;

function routes(options: { stored?: unknown; lookup?: unknown } = {}): MockRoute[] {
  const stored = options.stored ?? assessmentDraft;
  return [
    { method: 'GET', path: '/api/meta', response: meta },
    { method: 'GET', path: '/api/typologies', response: typologies },
    { method: 'GET', path: '/api/typologies/available', response: available },
    { method: 'GET', path: '/api/methodology', response: methodology },
    { method: 'GET', path: '/api/geo/basemap', response: basemap },
    { method: 'POST', path: '/api/geo/lookup', response: options.lookup ?? geoLookup },
    {
      method: 'GET',
      path: new RegExp(`^/api/projects/${project.project_id}/assessments/[^/]+$`),
      response: stored,
    },
    {
      method: 'PATCH',
      path: new RegExp(`^/api/projects/${project.project_id}/assessments/[^/]+$`),
      response: (body: unknown) => ({ ...stored, ...(body as object) }),
    },
    { method: 'POST', path: '/api/assessments/validate', response: validatePartial },
  ];
}

function renderWizard(url = mapUrl) {
  return renderAt(
    url,
    <Route path="projects/:projectId/assessments/:assessmentId/edit" element={<WizardScreen />} />,
  );
}

/**
 * Click the map canvas as a user would.
 *
 * jsdom performs no layout, so every element reports a zero-sized box and the
 * component — correctly — refuses to turn a click on a zero-sized map into a
 * location. The box is supplied here because a browser supplies one; nothing
 * about the component's behaviour is stubbed.
 */
async function clickMap(user: ReturnType<typeof userEvent.setup>, fx = 0.5, fy = 0.5) {
  const canvas = await screen.findByRole('application');
  const box = { x: 0, y: 0, top: 0, left: 0, right: 800, bottom: 450, width: 800, height: 450 };
  canvas.getBoundingClientRect = () => ({ ...box, toJSON: () => box });
  await user.pointer({ target: canvas, coords: { clientX: 800 * fx, clientY: 450 * fy } });
  await user.click(canvas);
}

describe('MapStep', () => {
  it('is the first step, and the questionnaire has one more step than fields to fill', () => {
    // The map asks no questions of its own; it offers answers to three that
    // other steps ask, which is why its `fields` list is empty.
    expect(STEPS[0]?.id).toBe('map');
    expect(STEPS[0]?.fields).toEqual([]);
  });

  it('is skippable in one action', async () => {
    installFetchMock(routes());
    const user = userEvent.setup();
    renderWizard();

    await user.click(await screen.findByRole('button', { name: /skip the map/i }));

    // One click and the user is on the first real question.
    expect(await screen.findByRole('heading', { name: /project information/i })).toBeVisible();
  });

  it('offers exactly the three inputs a map can honestly fill in (D-047)', async () => {
    installFetchMock(routes());
    const user = userEvent.setup();
    renderWizard();

    await clickMap(user);

    const found = await screen.findByRole('heading', { name: /what this location tells us/i });
    const panel = found.closest('.card');
    expect(panel).not.toBeNull();
    const offered = within(panel as HTMLElement).getAllByRole('listitem');
    expect(offered).toHaveLength(3);

    const text = (panel as HTMLElement).textContent ?? '';
    expect(text).toMatch(/Site area/i);
    expect(text).toMatch(/Country code/i);
    expect(text).toMatch(/Climate zone/i);
    // And nothing that would need satellite or census data (D-002, D-016).
    expect(text).not.toMatch(/canopy/i);
    expect(text).not.toMatch(/impervious/i);
    expect(text).not.toMatch(/land.surface temperature|LST/i);
  });

  it('states where the classification came from and how coarse it is', async () => {
    installFetchMock(routes());
    const user = userEvent.setup();
    renderWizard();
    await clickMap(user);

    await screen.findByRole('heading', { name: /what this location tells us/i });
    // The citation and the resolution caveat are the service's own words,
    // rendered verbatim rather than restated in the interface's voice.
    expect(screen.getByText(/Köppen.Geiger class at this location/i)).toBeVisible();
    expect(screen.getByText(/11 km/)).toBeVisible();
  });

  it('applies the answers and marks them where they are asked', async () => {
    installFetchMock(routes());
    const user = userEvent.setup();
    renderWizard();
    await clickMap(user);

    await user.click(await screen.findByRole('button', { name: /use these answers/i }));

    // The country is asked on the project step; it arrives filled in and marked.
    await user.click(screen.getByRole('button', { name: /project information/i }));
    const country = await screen.findByRole('textbox', { name: /country code/i });
    expect(country).toHaveValue('GR');
    expect(screen.getByText(/^from the map$/i)).toBeVisible();
  });

  it('never overwrites an answer the user has already given (D-047.2)', async () => {
    const answered = {
      ...assessmentDraft,
      input: { ...assessmentDraft.input, climate_zone: 'arid' },
    };
    installFetchMock(routes({ stored: answered }));
    const user = userEvent.setup();
    renderWizard();
    await clickMap(user);

    await screen.findByRole('heading', { name: /what this location tells us/i });
    // The conflict is named rather than resolved silently.
    expect(screen.getByText(/you have answered this/i)).toBeVisible();

    await user.click(screen.getByRole('button', { name: /^use these answers$/i }));

    await user.click(screen.getByRole('button', { name: /climate and heat exposure/i }));
    const zone = await screen.findByRole('combobox', { name: /climate zone/i });
    expect(zone).toHaveValue('arid');
  });

  it('replaces an existing answer only through a separate, explicit action', async () => {
    const answered = {
      ...assessmentDraft,
      input: { ...assessmentDraft.input, climate_zone: 'arid' },
    };
    installFetchMock(routes({ stored: answered }));
    const user = userEvent.setup();
    renderWizard();
    await clickMap(user);

    const replace = await screen.findByRole('button', { name: /replace my 1 existing answer/i });
    await user.click(replace);

    await user.click(screen.getByRole('button', { name: /climate and heat exposure/i }));
    const zone = await screen.findByRole('combobox', { name: /climate zone/i });
    expect(zone).toHaveValue('temperate');
  });

  it('drops the mark as soon as the user edits the answer themselves', async () => {
    installFetchMock(routes());
    const user = userEvent.setup();
    renderWizard();
    await clickMap(user);
    await user.click(await screen.findByRole('button', { name: /use these answers/i }));

    await user.click(screen.getByRole('button', { name: /climate and heat exposure/i }));
    const zone = await screen.findByRole('combobox', { name: /climate zone/i });
    expect(screen.getByText(/^from the map$/i)).toBeVisible();

    await user.selectOptions(zone, 'arid');
    await waitFor(() => {
      expect(screen.queryByText(/^from the map$/i)).toBeNull();
    });
  });

  it('says plainly when a location tells it nothing, and fills in nothing', async () => {
    installFetchMock(routes({ lookup: geoLookupOcean }));
    const user = userEvent.setup();
    renderWizard();
    await clickMap(user);

    expect(await screen.findByText(/nothing could be identified here/i)).toBeVisible();
    expect(screen.queryByRole('button', { name: /use these answers/i })).toBeNull();
  });

  it('sends the whole autofill as one save rather than one save per field', async () => {
    const mock = installFetchMock(routes());
    const user = userEvent.setup();
    renderWizard();
    await clickMap(user);
    await user.click(await screen.findByRole('button', { name: /use these answers/i }));

    await waitFor(() => {
      expect(mock.calls.some((call) => call.method === 'PATCH')).toBe(true);
    });
    const patches = mock.calls.filter((call) => call.method === 'PATCH');
    const last = patches[patches.length - 1]?.body as {
      input: Record<string, unknown>;
      autofilled: Record<string, string>;
    };
    expect(last.input.country).toBe('GR');
    expect(last.input.climate_zone).toBe('temperate');
    expect(last.input.site_area_m2).toBe(9745);
    // The provenance travels with the answers, naming the dataset behind each.
    expect(last.autofilled).toEqual({
      country: 'naturalearth',
      climate_zone: 'beck2023',
      site_area_m2: 'drawn_polygon',
    });
  });
});

describe('MapStep, when the map itself is unavailable', () => {
  it('degrades to a notice and leaves the questionnaire fully usable', async () => {
    // The map is optional infrastructure. If the bundled outlines cannot be
    // loaded the step says so and points at the alternative, rather than
    // stranding the user on a broken first step (v2.1 scope item 1).
    const withoutBasemap = routes().filter((route) => route.path !== '/api/geo/basemap');
    installFetchMock([
      ...withoutBasemap,
      { method: 'GET', path: '/api/geo/basemap', response: 'nope', status: 500 },
    ]);
    const user = userEvent.setup();
    renderWizard();

    expect(await screen.findByText(/the map could not be loaded/i)).toBeVisible();
    expect(screen.queryByRole('application')).toBeNull();

    await user.click(screen.getByRole('button', { name: /skip the map/i }));
    expect(await screen.findByRole('heading', { name: /project information/i })).toBeVisible();
  });
});

describe('MapStep, external tiles (D-047.1)', () => {
  it('requests no tiles at all until a user names a source and enables one', async () => {
    const mock = installFetchMock(routes());
    const user = userEvent.setup();
    renderWizard();
    await screen.findByRole('application');
    await clickMap(user);
    await screen.findByRole('heading', { name: /what this location tells us/i });

    // The default build makes no third-party request. Every call went to this
    // application's own API, and no tile element exists to make one.
    for (const call of mock.calls) {
      expect(call.url).toMatch(/^\/api\//);
    }
    expect(document.querySelectorAll('.sitemap__tiles img')).toHaveLength(0);
  });

  it('names no tile source of its own, so enabling one is the user naming it', async () => {
    installFetchMock(routes());
    renderWizard();
    await screen.findByRole('application');

    await userEvent.setup().click(screen.getByText(/use an external map service/i));
    const input = screen.getByRole('textbox', { name: /tile url template/i });
    expect(input).toHaveValue('');
    // A placeholder shows the shape of a template without naming a provider:
    // naming one would make it the obvious choice and quietly turn an informed
    // decision back into a default.
    expect(input.getAttribute('placeholder')).not.toMatch(/openstreetmap|osm|mapbox|google/i);
    expect(screen.getByRole('button', { name: /enable this tile service/i })).toBeDisabled();
  });

  it('explains what enabling tiles discloses before it can be enabled', async () => {
    installFetchMock(routes());
    const user = userEvent.setup();
    renderWizard();
    await screen.findByRole('application');

    // The disclosure is behind the same disclosure widget as the control, so a
    // user cannot reach the switch without passing the explanation.
    await user.click(screen.getByText(/use an external map service/i));

    const explanation = screen.getByText(/makes no third-party requests/i);
    expect(explanation).toBeVisible();
    expect(explanation.textContent).toMatch(/IP address/i);
  });
});
