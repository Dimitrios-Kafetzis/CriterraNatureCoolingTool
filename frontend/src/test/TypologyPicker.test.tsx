import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { TypologyPicker, assessFit } from '../wizard/TypologyPicker';
import { messages } from '../i18n/en';
import type { DraftInput, MethodologyData, Typology, TypologyLibrary } from '../api/types';
import methodologyFixture from './fixtures/methodology.json';
import typologiesFixture from './fixtures/typologies.json';

const library = typologiesFixture as unknown as TypologyLibrary;
const methodology = methodologyFixture as unknown as MethodologyData;
const ranks = {
  soil: methodology.derived_scores.suitability_sub_indicators!.requirement_match!.soil_ranks!,
  irrigation:
    methodology.derived_scores.suitability_sub_indicators!.requirement_match!.irrigation_ranks!,
};

function typology(nbsType: string): Typology {
  return library.typologies.find((candidate) => candidate.nbs_type === nbsType)!;
}

// A constrained site: small, arid, limited soil, no irrigation.
const constrainedSite: DraftInput = {
  site_area_m2: 400,
  climate_zone: 'arid',
  soil_availability: 'limited',
  irrigation_availability: 'none',
};

describe('assessFit', () => {
  it('never disqualifies from absent information (D-022 reading)', () => {
    // Nothing entered yet: requirements exist but cannot be checked → caution.
    const fit = assessFit({}, typology('street_tree_planting'), ranks);
    expect(fit.kind).toBe('caution');
  });

  it('flags a supplied answer below the requirement as unsuitable', () => {
    const fit = assessFit(constrainedSite, typology('riparian_restoration'), ranks);
    expect(fit.kind).toBe('unsuitable');
  });

  it('marks a met requirement as suited', () => {
    const fit = assessFit(
      {
        site_area_m2: 6000,
        climate_zone: 'temperate',
        soil_availability: 'high',
        irrigation_availability: 'reliable',
      },
      typology('street_tree_planting'),
      ranks,
    );
    expect(fit).toEqual({ kind: 'suited', notes: [] });
  });
});

describe('TypologyPicker', () => {
  it('renders all 14 cards with cooling envelope and evidence from the library', () => {
    render(
      <TypologyPicker
        library={library}
        methodology={methodology}
        draft={constrainedSite}
        onSelect={vi.fn()}
      />,
    );
    const cards = screen.getAllByRole('button');
    expect(cards).toHaveLength(library.typologies.length);
    const street = typology('street_tree_planting');
    expect(
      screen.getAllByText(
        messages.picker.cooling(
          street.temp_reduction_min_c.toLocaleString(),
          street.temp_reduction_max_c.toLocaleString(),
        ),
      ).length,
    ).toBeGreaterThan(0);
  });

  it('sorts unsuitable cards after suitable ones, keeping them selectable (D-019)', async () => {
    const onSelect = vi.fn();
    render(
      <TypologyPicker
        library={library}
        methodology={methodology}
        draft={constrainedSite}
        onSelect={onSelect}
      />,
    );
    const cards = screen.getAllByRole('button');
    const unsuitableFlags = cards.map((card) =>
      card.textContent!.includes(messages.picker.fit.unsuitablePrefix),
    );
    // Once the first unsuitable card appears, every later card is unsuitable too.
    const firstUnsuitable = unsuitableFlags.indexOf(true);
    expect(firstUnsuitable).toBeGreaterThan(-1);
    expect(unsuitableFlags.slice(firstUnsuitable).every(Boolean)).toBe(true);

    // An unsuitable card is annotated but fully selectable.
    const unsuitableCard = cards[firstUnsuitable]!;
    const user = userEvent.setup();
    await user.click(unsuitableCard);
    expect(onSelect).toHaveBeenCalledTimes(1);
  });
});
