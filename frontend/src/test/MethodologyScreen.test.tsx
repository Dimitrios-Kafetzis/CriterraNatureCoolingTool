import { screen, within } from '@testing-library/react';
import { Route } from 'react-router';
import { describe, expect, it } from 'vitest';
import { MethodologyScreen } from '../screens/MethodologyScreen';
import { messages } from '../i18n/en';
import type { MethodologyData, TypologyLibrary } from '../api/types';
import { installFetchMock } from './mockFetch';
import { renderAt } from './render';
import meta from './fixtures/meta.json';
import methodologyFixture from './fixtures/methodology.json';
import typologiesFixture from './fixtures/typologies.json';

const methodology = methodologyFixture as unknown as MethodologyData;
const library = typologiesFixture as unknown as TypologyLibrary;

function renderMethodology() {
  installFetchMock([
    { method: 'GET', path: '/api/meta', response: meta },
    { method: 'GET', path: '/api/methodology', response: methodology },
    { method: 'GET', path: '/api/typologies', response: typologiesFixture },
  ]);
  return renderAt('/methodology', <Route path="methodology" element={<MethodologyScreen />} />);
}

describe('MethodologyScreen', () => {
  it('stamps the live methodology version', async () => {
    renderMethodology();
    expect(
      await screen.findByText(messages.methodology.version(methodology.version)),
    ).toBeInTheDocument();
  });

  it('renders the score bands from configuration, not constants', async () => {
    renderMethodology();
    const scores = await screen.findByRole('region', {
      name: messages.methodology.sections.scores,
    });
    for (const band of methodology.derived_scores.score_bands!.opportunity!) {
      expect(
        within(scores).getAllByRole('row', { name: new RegExp(band.label, 'i') }).length,
      ).toBeGreaterThan(0);
    }
  });

  it('derives the effective-weights table visibly from the served weights (D-007)', async () => {
    renderMethodology();
    const weights = await screen.findByRole('region', {
      name: messages.methodology.sections.weights,
    });
    const final = methodology.weights.final_opportunity_score as Record<string, number>;
    const hpi = methodology.weights.heat_priority_index as Record<string, number>;
    const effectiveVulnerability =
      final.vulnerability! + final.heat_priority_index! * hpi.vulnerability!;
    const row = within(weights).getByRole('row', { name: /^vulnerability/ });
    // The derivation itself is displayed alongside its product.
    expect(row).toHaveTextContent(
      `${final.vulnerability} + ${final.heat_priority_index} × ${hpi.vulnerability}`,
    );
    expect(row).toHaveTextContent(String(effectiveVulnerability));
  });

  it('renders every typology with citations from the library', async () => {
    renderMethodology();
    const section = await screen.findByRole('region', {
      name: messages.methodology.sections.typologies,
    });

    // The heading names are collected ONCE and then checked by membership.
    // Querying `getByRole('heading', { name })` per typology re-computes the
    // accessible name of every heading in the section on each call, which is
    // quadratic — tolerable at the 14 typologies this test was written for,
    // and 1.6s at 121. The assertion is unchanged: every typology in the
    // served library must have a heading in the typologies section.
    const rendered = new Set(
      within(section)
        .getAllByRole('heading')
        .map((heading) => heading.textContent?.trim()),
    );
    const missing = library.typologies
      .map((typology) => typology.display_name)
      .filter((name) => !rendered.has(name));
    expect(missing).toEqual([]);

    // Citations are rendered as key + finding pairs.
    expect(within(section).getAllByText('keravec2026').length).toBeGreaterThan(0);
  });
});
