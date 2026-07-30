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
    for (const typology of library.typologies) {
      expect(
        within(section).getByRole('heading', { name: typology.display_name }),
      ).toBeInTheDocument();
    }
    // Citations are rendered as key + finding pairs.
    expect(within(section).getAllByText('keravec2026').length).toBeGreaterThan(0);
  });
});
