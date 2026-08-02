import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { TypologyPicker, assessFit, exampleImageFor } from '../wizard/TypologyPicker';
import { exampleCaption } from '../wizard/ExampleImageDialog';
import { messages } from '../i18n/en';
import type {
  AvailableTypologies,
  DraftInput,
  MethodologyData,
  NbsImage,
  Typology,
  TypologyLibrary,
} from '../api/types';
import methodologyFixture from './fixtures/methodology.json';
import typologiesFixture from './fixtures/typologies.json';
import availableFixture from './fixtures/typologies-available.json';
import availableCityFixture from './fixtures/typologies-available-city.json';
import imagesFixture from './fixtures/images-manifest.json';

const library = typologiesFixture as unknown as TypologyLibrary;
const methodology = methodologyFixture as unknown as MethodologyData;
const available = availableFixture as unknown as AvailableTypologies;
const availableCity = availableCityFixture as unknown as AvailableTypologies;
const images = imagesFixture.images as NbsImage[];
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
      images={null}
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
        images={null}
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
        images={null}
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
        images={null}
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

// A site whose climate zone matches the fixture images (all temperate).
const temperateSite: DraftInput = { site_area_m2: 6000, climate_zone: 'temperate' };

/** Affordance buttons are queried by class in one pass — never by role+name
 * per entry, which is quadratic over 110 cards and has timed out CI before. */
function affordances(): HTMLElement[] {
  return [...document.querySelectorAll<HTMLElement>('.picker__photo')];
}

describe('example images (v2.3, D-051)', () => {
  it('resolves strictly by zone, with the override outranking the archetype', () => {
    // water_square has a per-typology override in its zone, which outranks
    // the archetype-level image its siblings inherit…
    const override = exampleImageFor(typology('water_square'), images, 'temperate');
    expect(override?.file).toBe('water_square--temperate.webp');
    // …while a sibling of the same archetype inherits the archetype image.
    expect(exampleImageFor(typology('retention_pond'), images, 'temperate')?.file).toBe(
      'small_constructed_water--temperate.webp',
    );
    // An entry inheriting street_tree_canopy gets the archetype image.
    expect(exampleImageFor(typology('tree_avenue'), images, 'temperate')?.file).toBe(
      'street_tree_canopy--temperate.webp',
    );
    // Strict zone match (D-051.5): no cross-zone substitution, and no zone
    // answered means no image at all.
    expect(exampleImageFor(typology('tree_avenue'), images, 'arid')).toBeUndefined();
    expect(exampleImageFor(typology('tree_avenue'), images, null)).toBeUndefined();
    expect(exampleImageFor(typology('tree_avenue'), null, 'temperate')).toBeUndefined();
  });

  it('shows an affordance only where a verified image matches the zone exactly', () => {
    renderPicker({ images, draft: temperateSite });
    const withImage = resolved.filter(
      (entry) => exampleImageFor(entry, images, 'temperate') !== undefined,
    );
    expect(withImage.length).toBeGreaterThan(0);
    expect(affordances()).toHaveLength(withImage.length);
  });

  it('shows no affordance for a zone with no verified image — no cross-zone substitution (D-051.5)', () => {
    // Only temperate images offered to an arid site: nothing renders, because
    // an arid implementation shown to a temperate user (or vice versa) is the
    // misleading substitution this rule exists to refuse.
    const temperateOnly = images.filter((image) => image.zone === 'temperate');
    renderPicker({ images: temperateOnly, draft: constrainedSite });
    expect(affordances()).toHaveLength(0);
  });

  it('shows no affordance while the zone is unanswered', () => {
    renderPicker({ images, draft: { site_area_m2: 6000 } });
    expect(affordances()).toHaveLength(0);
  });

  it('opens a dialog whose caption states place and zone, with the attribution rendered (D-051.3, D-051.6)', async () => {
    renderPicker({ images, draft: temperateSite });
    const user = userEvent.setup();
    const image = images.find((candidate) => candidate.nbs_type === 'water_square')!;

    await user.click(
      screen.getByRole('button', {
        name: messages.picker.example.affordance(typology('water_square').display_name),
      }),
    );

    const dialog = screen.getByRole('dialog');
    const caption = exampleCaption(image);
    // Place and zone, nothing about degrees, performance, or cost — and the
    // alt text is the caption verbatim.
    expect(caption).toBe('A water square (dry state) in Rotterdam, Netherlands (Temperate)');
    const img = within(dialog).getByRole('img', { name: caption });
    expect(img).toHaveAttribute('src', `/api/images/${image.file}`);
    expect(within(dialog).getByText(caption)).toBeInTheDocument();

    // The attribution its licence requires: author, licence name linked to
    // the licence text, and a link to the source page.
    expect(
      within(dialog).getByText(new RegExp(messages.picker.example.credit(image.author))),
    ).toBeInTheDocument();
    expect(within(dialog).getByRole('link', { name: image.licence })).toHaveAttribute(
      'href',
      image.licence_url,
    );
    expect(
      within(dialog).getByRole('link', { name: messages.picker.example.sourceLink }),
    ).toHaveAttribute('href', image.source_page);

    // The example is stated to be illustrative, never evidence (D-051.6).
    expect(within(dialog).getByText(messages.picker.example.illustrativeNote)).toBeInTheDocument();

    await user.click(within(dialog).getByRole('button', { name: messages.picker.example.close }));
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('says an archetype-level photo is from the evidence class, not the card that opened it', async () => {
    renderPicker({ images, draft: temperateSite });
    const user = userEvent.setup();
    const entry = typology('tree_avenue');

    await user.click(
      screen.getByRole('button', {
        name: messages.picker.example.affordance(entry.display_name),
      }),
    );
    const dialog = screen.getByRole('dialog');
    // The caption names what the photograph depicts (the archetype subject),
    // and the inheritance is stated — a Tree Avenue card showing a street
    // tree canopy photo says so rather than implying a photo of itself.
    expect(
      within(dialog).getByText(
        messages.picker.example.evidenceClassNote(entry.archetype_display_name),
      ),
    ).toBeInTheDocument();
  });

  it('keeps the affordance a sibling of the card button, never nested inside it (D-051.2)', () => {
    renderPicker({ images, draft: temperateSite });
    for (const affordance of affordances()) {
      expect(affordance.closest('.picker__card')).toBeNull();
      expect(affordance.parentElement!.className).toContain('picker__card-shell');
    }
  });
});
