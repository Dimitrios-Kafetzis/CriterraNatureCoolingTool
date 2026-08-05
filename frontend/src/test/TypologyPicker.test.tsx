import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { TypologyPicker, assessFit, exampleImageFor } from '../wizard/TypologyPicker';
import { exampleCaption, suitabilityConditions } from '../wizard/TypologyDetailDialog';
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
const resolved = library.resolved;
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

/** The card buttons inside one container, excluding the detail affordances
 * that sit beside them in each card shell since v2.6. */
function cardsWithin(container: HTMLElement): HTMLElement[] {
  return within(container)
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
      expect(cardsWithin(group)).toHaveLength(count);
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
    const inFamily = cardsWithin(group);
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
    const card = cardsWithin(group).find(
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
 * per entry, which is quadratic over 121 cards and has timed out CI before. */
function affordances(): HTMLElement[] {
  return [...document.querySelectorAll<HTMLElement>('.picker__details')];
}

/** Open one entry's detail dialog through its affordance. */
async function openDetails(user: ReturnType<typeof userEvent.setup>, nbsType: string) {
  await user.click(
    screen.getByRole('button', {
      name: messages.picker.details.affordance(typology(nbsType).display_name),
    }),
  );
  return screen.getByRole('dialog');
}

describe('the detail dialog (v2.6)', () => {
  it('offers one detail affordance per card, as a sibling of the card button (D-051.2)', () => {
    renderPicker({ images, draft: temperateSite });
    // Every entry has details to show, so every card carries exactly one
    // affordance — never two dialogs on the same card.
    expect(affordances()).toHaveLength(resolved.length);
    for (const affordance of affordances()) {
      expect(affordance.closest('.picker__card')).toBeNull();
      expect(affordance.parentElement!.className).toContain('picker__card-shell');
    }
  });

  it('states identity: name, family, kind, catalogue id, and cooling mechanism', async () => {
    renderPicker({ images, draft: temperateSite });
    const user = userEvent.setup();
    const entry = typology('depaving');
    const dialog = await openDetails(user, 'depaving');

    expect(within(dialog).getByRole('heading', { name: entry.display_name })).toBeInTheDocument();
    expect(
      within(dialog).getByText(new RegExp(messages.families.labels[entry.family]!)),
    ).toBeInTheDocument();
    expect(
      within(dialog).getByText(
        new RegExp(messages.picker.details.catalogueEntry(entry.nbs_id).replace('.', '\\.')),
      ),
    ).toBeInTheDocument();
    expect(
      within(dialog).getByText(messages.picker.details.mechanism(entry.primary_cooling_mechanism)),
    ).toBeInTheDocument();
  });

  it('renders every citation with its finding, full reference and link inline, never behind an expand', async () => {
    renderPicker({ images, draft: temperateSite });
    const user = userEvent.setup();
    // tree_avenue inherits street_tree_canopy, the library's longest citation
    // list (five sources): the worst case renders whole, by design.
    const entry = typology('tree_avenue');
    expect(entry.sources.length).toBe(5);
    const dialog = await openDetails(user, 'tree_avenue');

    expect(
      within(dialog).getByText(messages.picker.details.inherits(entry.archetype_display_name)),
    ).toBeInTheDocument();
    const items = dialog.querySelectorAll('.detail-dialog__sources li');
    expect(items).toHaveLength(entry.sources.length);
    for (const [index, source] of entry.sources.entries()) {
      const item = items[index]!;
      expect(item.textContent).toContain(source.key);
      expect(item.textContent).toContain(source.finding);
      // A key like "ziter2019" says nothing on its own: the served
      // bibliography entry renders beneath it — the full citation, with the
      // DOI resolver as a link the user may follow.
      const reference = library.bibliography[source.key]!;
      expect(item.textContent).toContain(reference.reference);
      if (reference.url != null) {
        const link = within(item as HTMLElement).getByRole('link');
        expect(link).toHaveAttribute('href', reference.url);
        if (reference.doi != null) expect(link.textContent).toBe(reference.doi);
      }
    }
  });

  it('shows the curation reason served with the library, verbatim', async () => {
    renderPicker({ images, draft: temperateSite });
    const user = userEvent.setup();
    const entry = typology('depaving');
    const reason = library.curation_reasons[entry.nbs_id]!;
    const dialog = await openDetails(user, 'depaving');
    expect(within(dialog).getByText(reason)).toBeInTheDocument();
  });

  it('states the numbers of a failed area condition: requirement beside the answer', async () => {
    renderPicker({ images, draft: constrainedSite });
    const user = userEvent.setup();
    const dialog = await openDetails(user, 'urban_woodland_site');
    // 400 m² described, 2,000 m² required: both numbers are served or
    // user-entered — the dialog restates them, it computes nothing.
    const failed = dialog.querySelector('.detail-dialog__condition--failed')!;
    expect(failed.textContent).toBe(
      messages.picker.details.conditions.area((2000).toLocaleString()) +
        messages.picker.details.conditions.areaAnswer((400).toLocaleString()),
    );
    await user.click(within(dialog).getByRole('button', { name: messages.picker.details.close }));
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('folds the example image into the same dialog, attribution rendered (D-051.3, D-051.6)', async () => {
    renderPicker({ images, draft: temperateSite });
    const user = userEvent.setup();
    const image = images.find((candidate) => candidate.nbs_type === 'water_square')!;
    const dialog = await openDetails(user, 'water_square');

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
  });

  it('says an archetype-level photo is from the evidence class, not the card that opened it', async () => {
    renderPicker({ images, draft: temperateSite });
    const user = userEvent.setup();
    const entry = typology('tree_avenue');
    const dialog = await openDetails(user, 'tree_avenue');
    // The caption names what the photograph depicts (the archetype subject),
    // and the inheritance is stated — a Tree Avenue card showing a street
    // tree canopy photo says so rather than implying a photo of itself.
    expect(
      within(dialog).getByText(
        messages.picker.example.evidenceClassNote(entry.archetype_display_name),
      ),
    ).toBeInTheDocument();
  });

  it('renders no image section when no verified image matches the zone — absence is the honest state (D-051.4, D-051.5)', async () => {
    // Only temperate images offered to an arid site: no cross-zone
    // substitution, and no placeholder — the section simply does not exist.
    const temperateOnly = images.filter((image) => image.zone === 'temperate');
    renderPicker({ images: temperateOnly, draft: constrainedSite });
    const user = userEvent.setup();
    const dialog = await openDetails(user, 'tree_avenue');
    expect(within(dialog).queryByRole('img')).not.toBeInTheDocument();
    expect(within(dialog).queryByText(messages.picker.example.illustrativeNote)).toBeNull();
  });
});

describe('example image resolution (v2.3, D-051)', () => {
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
});

describe('suitabilityConditions', () => {
  it('mirrors assessFit: a supplied answer strictly below the requirement fails, with numbers', () => {
    const rows = suitabilityConditions(constrainedSite, typology('urban_woodland_site'), ranks);
    const area = rows[0]!;
    expect(area.status).toBe('failed');
    expect(area.text).toContain((2000).toLocaleString());
    expect(area.text).toContain((400).toLocaleString());
  });

  it('leaves an unanswered condition open rather than failing it (D-022 reading)', () => {
    const rows = suitabilityConditions({}, typology('urban_woodland_site'), ranks);
    expect(rows.every((row) => row.status === 'unanswered')).toBe(true);
  });

  it('renders no row for a condition the entry does not assert — absence renders nothing', () => {
    // water_square requires no soil, no irrigation, and lists no unsuitable
    // zone: the area minimum is its only condition, so one row exists.
    const rows = suitabilityConditions(temperateSite, typology('water_square'), ranks);
    expect(rows).toHaveLength(1);
    expect(rows[0]!.status).toBe('met');
  });

  it('states the climate constraint with the zones named and the site answer beside it', () => {
    // mangrove_restoration carries the library's one climate override
    // ("tropical and subtropical climates only" per its source).
    const entry = typology('mangrove_restoration');
    const zones = entry.suitability.unsuitable_climate_zones ?? [];
    expect(zones.length).toBeGreaterThan(0);

    const failed = suitabilityConditions(constrainedSite, entry, ranks);
    const climate = failed[failed.length - 1]!;
    expect(climate.status).toBe('failed');
    expect(climate.text).toContain(messages.options.climate_zone.arid);

    const open = suitabilityConditions({ site_area_m2: 6000 }, entry, ranks);
    expect(open[open.length - 1]!.status).toBe('unanswered');
  });
});
