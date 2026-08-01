import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { TypologyPicker, assessFit } from '../wizard/TypologyPicker';
import { messages } from '../i18n/en';
import type {
  AvailableTypologies,
  DraftInput,
  MethodologyData,
  Typology,
  TypologyLibrary,
} from '../api/types';
import methodologyFixture from './fixtures/methodology.json';
import typologiesFixture from './fixtures/typologies.json';
import availableFixture from './fixtures/typologies-available.json';
import availableCityFixture from './fixtures/typologies-available-city.json';

const library = typologiesFixture as unknown as TypologyLibrary;
const methodology = methodologyFixture as unknown as MethodologyData;
const available = availableFixture as unknown as AvailableTypologies;
const availableCity = availableCityFixture as unknown as AvailableTypologies;
const resolved = library.resolved!;
const ranks = {
  soil: methodology.derived_scores.suitability_sub_indicators!.requirement_match!.soil_ranks!,
  irrigation:
    methodology.derived_scores.suitability_sub_indicators!.requirement_match!.irrigation_ranks!,
};

function typology(nbsType: string): Typology {
  return resolved.find((candidate) => candidate.nbs_type === nbsType)!;
}

// A constrained site: small, arid, limited soil, no irrigation.
const constrainedSite: DraftInput = {
  site_area_m2: 400,
  climate_zone: 'arid',
  soil_availability: 'limited',
  irrigation_availability: 'none',
};

function renderPicker(props: Partial<Parameters<typeof TypologyPicker>[0]> = {}) {
  const onChange = vi.fn();
  render(
    <TypologyPicker
      library={library}
      methodology={methodology}
      availability={null}
      draft={constrainedSite}
      onChange={onChange}
      {...props}
    />,
  );
  return { onChange };
}

/** Every card, regardless of which family disclosure it sits in. */
function cards(): HTMLElement[] {
  return screen
    .getAllByRole('button')
    .filter((element) => element.className.includes('picker__card'));
}

describe('assessFit', () => {
  it('never disqualifies from absent information (D-022 reading)', () => {
    // Nothing entered yet: requirements exist but cannot be checked → caution.
    const fit = assessFit({}, typology('strategic_individual_tree_planting'), ranks);
    expect(fit.kind).toBe('caution');
  });

  it('flags a supplied answer below the requirement as unsuitable', () => {
    const fit = assessFit(constrainedSite, typology('urban_woodland_site'), ranks);
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
      typology('strategic_individual_tree_planting'),
      ranks,
    );
    expect(fit).toEqual({ kind: 'suited', notes: [] });
  });
});

describe('TypologyPicker', () => {
  it('renders every catalogue entry, grouped by family with counts', () => {
    renderPicker();
    expect(cards()).toHaveLength(resolved.length);

    // Each family the library holds is a disclosure naming its own count.
    const families = new Map<string, number>();
    for (const entry of resolved) {
      families.set(entry.family, (families.get(entry.family) ?? 0) + 1);
    }
    for (const [family, count] of families) {
      const label = messages.families.labels[family]!;
      const group = screen.getByRole('group', { name: label });
      expect(within(group).getAllByRole('button')).toHaveLength(count);
      // The disclosure that owns this group states its own count.
      const summary = group.closest('details')!.querySelector('summary')!;
      expect(summary.textContent).toContain(messages.picker.groupCount(count));
      expect(summary.textContent).toContain(label);
    }
  });

  it('shows the cooling envelope and the inherited evidence class on every card (D-044)', () => {
    renderPicker();
    const entry = typology('strategic_individual_tree_planting');
    expect(
      screen.getAllByText(
        messages.picker.cooling(
          entry.temp_reduction_min_c.toLocaleString(),
          entry.temp_reduction_max_c.toLocaleString(),
        ),
      ).length,
    ).toBeGreaterThan(0);
    expect(
      screen.getAllByText(messages.picker.evidenceClass(entry.archetype_display_name)).length,
    ).toBeGreaterThan(0);
  });

  it('sorts unsuitable cards after suitable ones, keeping them selectable (D-019)', async () => {
    const { onChange } = renderPicker();
    // Within one family, the annotated-unsuitable cards come last.
    const group = screen.getByRole('group', {
      name: messages.families.labels.tree_based!,
    });
    const inFamily = within(group).getAllByRole('button');
    const unsuitable = inFamily.map((card) =>
      card.textContent!.includes(messages.picker.fit.unsuitablePrefix),
    );
    const firstUnsuitable = unsuitable.indexOf(true);
    expect(firstUnsuitable).toBeGreaterThan(-1);
    expect(unsuitable.slice(firstUnsuitable).every(Boolean)).toBe(true);

    const user = userEvent.setup();
    await user.click(inFamily[firstUnsuitable]!);
    expect(onChange).toHaveBeenCalledTimes(1);
  });

  it('accumulates a multi-component package, preserving selection order (D-038)', async () => {
    const onChange = vi.fn();
    const { rerender } = render(
      <TypologyPicker
        library={library}
        methodology={methodology}
        availability={available}
        draft={{ ...constrainedSite, nbs_type: ['rain_garden'] }}
        onChange={onChange}
      />,
    );
    const user = userEvent.setup();
    const group = screen.getByRole('group', { name: messages.families.labels.green_roof! });
    // Several entries inherit the "Extensive green roof" evidence class, so
    // the card is located by its own name, not by any text it carries.
    const card = within(group)
      .getAllByRole('button')
      .find(
        (element) =>
          element.querySelector('.picker__name')!.textContent ===
          typology('extensive_green_roof').display_name,
      )!;
    await user.click(card);
    expect(onChange).toHaveBeenCalledWith(['rain_garden', 'extensive_green_roof']);

    // Both appear in the removable selection list, in the order selected.
    rerender(
      <TypologyPicker
        library={library}
        methodology={methodology}
        availability={available}
        draft={{ ...constrainedSite, nbs_type: ['rain_garden', 'extensive_green_roof'] }}
        onChange={onChange}
      />,
    );
    const items = document.querySelectorAll('.picker__selection-list li');
    expect(items).toHaveLength(2);
    expect(items[0]!.textContent).toContain(typology('rain_garden').display_name);
    expect(items[1]!.textContent).toContain(typology('extensive_green_roof').display_name);
  });

  it('removes a component from the selection', async () => {
    const onChange = vi.fn();
    render(
      <TypologyPicker
        library={library}
        methodology={methodology}
        availability={available}
        draft={{ ...constrainedSite, nbs_type: ['rain_garden', 'extensive_green_roof'] }}
        onChange={onChange}
      />,
    );
    const user = userEvent.setup();
    await user.click(
      screen.getByRole('button', {
        name: messages.picker.removeLabel(typology('rain_garden').display_name),
      }),
    );
    expect(onChange).toHaveBeenCalledWith(['extensive_green_roof']);
  });

  it('separates and labels entries the service does not offer, keeping them selectable (D-019)', () => {
    renderPicker({ availability: available });
    const withheld = screen.getByRole('region', { name: messages.picker.notOfferedHeading });
    expect(withheld).toBeInTheDocument();

    // Every card in that section is labelled and none is disabled.
    const withheldCards = within(withheld)
      .getAllByRole('button')
      .filter((element) => element.className.includes('picker__card'));
    expect(withheldCards.length).toBe(resolved.length - available.nbs_types.length);
    for (const card of withheldCards) {
      expect(card).not.toBeDisabled();
    }
    expect(within(withheld).getAllByText(messages.picker.notOfferedBadge).length).toBe(
      withheldCards.length,
    );

    // Offered entries are rendered first, in their own labelled section.
    const offered = screen.getByRole('region', { name: messages.picker.offeredHeading });
    expect(
      offered.compareDocumentPosition(withheld) & Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy();
  });

  it('filters across display names and evidence classes', async () => {
    renderPicker({ availability: available });
    const user = userEvent.setup();
    await user.type(screen.getByLabelText(messages.picker.filterLabel), 'wetland');
    const shown = cards();
    expect(shown.length).toBeGreaterThan(0);
    expect(shown.length).toBeLessThan(resolved.length);
    for (const card of shown) {
      expect(card.textContent!.toLowerCase()).toContain('wetland');
    }
  });

  it('says the user is composing a package when the service says so (D-043.2)', () => {
    renderPicker({ availability: availableCity });
    expect(screen.getByText(messages.picker.introPackage)).toBeInTheDocument();
    expect(screen.queryByText(messages.picker.intro)).not.toBeInTheDocument();
  });

  it('warns above the served component limit, stating what a further component does not do (D-044.4)', () => {
    const over = resolved.slice(0, available.warn_above_components + 1).map((e) => e.nbs_type);
    renderPicker({
      availability: available,
      draft: { ...constrainedSite, nbs_type: over },
    });
    expect(
      screen.getByText(messages.picker.sizeWarning(available.warn_above_components)),
    ).toBeInTheDocument();
  });

  it('does not warn at or below the served limit', () => {
    const atLimit = resolved.slice(0, available.warn_above_components).map((e) => e.nbs_type);
    renderPicker({
      availability: available,
      draft: { ...constrainedSite, nbs_type: atLimit },
    });
    expect(
      screen.queryByText(messages.picker.sizeWarning(available.warn_above_components)),
    ).not.toBeInTheDocument();
  });

  it('offers every entry while the service has not answered, inventing no gating rule', () => {
    renderPicker({ availability: null });
    expect(cards()).toHaveLength(resolved.length);
    expect(
      screen.queryByRole('region', { name: messages.picker.notOfferedHeading }),
    ).not.toBeInTheDocument();
  });

  it('names a stored entry the current library no longer holds rather than dropping it (D-044.2)', () => {
    renderPicker({
      availability: available,
      draft: { ...constrainedSite, nbs_type: ['schoolyard_greening'] },
    });
    expect(
      screen.getByText(messages.picker.unknownEntry('schoolyard_greening')),
    ).toBeInTheDocument();
  });
});
