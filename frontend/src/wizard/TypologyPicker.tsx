/**
 * The guided typology picker (UX §5, D-019, D-009, D-043, D-044).
 *
 * The catalogue holds 110 entries across fourteen families, and a school site
 * is offered 67 of them, so the picker groups by family, filters by name, and
 * supports selecting several entries as a package (D-038). Every card keeps
 * the fit annotation it has always carried: a comparison of the user's answers
 * against each entry's suitability conditions served by GET /api/typologies,
 * using the ordinal ranks served by GET /api/methodology — no rank, threshold,
 * or requirement originates here.
 *
 * Two boundaries govern this file:
 *
 * * **Availability is asked, never computed.** GET /api/typologies/available
 *   says what the service offers for this site; the picker sorts and labels by
 *   that answer and derives no gating rule of its own (ARCHITECTURE boundary
 *   1). While the answer is unavailable — no scale entered yet, or the request
 *   failed — every entry is simply offered, which is the pre-v2 behaviour.
 * * **Availability guides, it never blocks (D-019).** An entry the service
 *   does not offer stays fully selectable, visually separated and labelled, so
 *   a professional deliberately testing a hypothesis is never overridden. The
 *   engine records the choice with its own honest flags (D-009).
 */

import { useId, useMemo, useState } from 'react';
import { FieldExplainer } from '../components/FieldExplainer';
import { ExampleImageDialog } from './ExampleImageDialog';
import { messages, optionLabel } from '../i18n/en';
import type {
  AvailableTypologies,
  DraftInput,
  MethodologyData,
  NbsImage,
  Typology,
  TypologyLibrary,
} from '../api/types';

type FitKind = 'suited' | 'caution' | 'unsuitable';

export interface Fit {
  kind: FitKind;
  notes: string[];
}

const FIT_ORDER: Record<FitKind, number> = { suited: 0, caution: 1, unsuitable: 2 };

/**
 * Compare entered site data against one typology's suitability conditions.
 *
 * Mirrors the reading of D-022 (and D-009's flags): a disqualification is
 * asserted only from a *supplied* answer strictly below the requirement —
 * never from absent information, which yields a caution instead.
 */
export function assessFit(
  site: DraftInput,
  typology: Typology,
  ranks: { soil: Record<string, number>; irrigation: Record<string, number> },
): Fit {
  const conditions = typology.suitability;
  const unsuitable: string[] = [];
  const cautions: string[] = [];

  if (site.site_area_m2 != null && site.site_area_m2 < conditions.minimum_site_area_m2) {
    unsuitable.push(
      messages.picker.fit.belowMinimumArea(conditions.minimum_site_area_m2.toLocaleString()),
    );
  }

  if (
    site.climate_zone != null &&
    (conditions.unsuitable_climate_zones ?? []).includes(site.climate_zone)
  ) {
    unsuitable.push(messages.picker.fit.unsuitableClimate);
  }

  const soilRequired = ranks.soil[conditions.requires_soil] ?? 0;
  if (soilRequired > 0) {
    const supplied = site.soil_availability != null && site.soil_availability !== 'unknown';
    if (!supplied) {
      cautions.push(
        messages.picker.fit.needsSoil(optionLabel(conditions.requires_soil).toLowerCase()),
      );
    } else if ((ranks.soil[site.soil_availability as string] ?? 0) < soilRequired) {
      unsuitable.push(
        messages.picker.fit.insufficientSoil(optionLabel(conditions.requires_soil).toLowerCase()),
      );
    }
  }

  const irrigationRequired = ranks.irrigation[conditions.requires_irrigation] ?? 0;
  if (irrigationRequired > 0) {
    const supplied =
      site.irrigation_availability != null && site.irrigation_availability !== 'unknown';
    if (!supplied) {
      cautions.push(
        messages.picker.fit.needsIrrigation(
          optionLabel(conditions.requires_irrigation).toLowerCase(),
        ),
      );
    } else if (
      (ranks.irrigation[site.irrigation_availability as string] ?? 0) < irrigationRequired
    ) {
      unsuitable.push(
        messages.picker.fit.insufficientIrrigation(
          optionLabel(conditions.requires_irrigation).toLowerCase(),
        ),
      );
    }
  }

  if (unsuitable.length > 0) return { kind: 'unsuitable', notes: unsuitable };
  if (cautions.length > 0) return { kind: 'caution', notes: cautions };
  return { kind: 'suited', notes: [] };
}

function ranksOf(methodology: MethodologyData): {
  soil: Record<string, number>;
  irrigation: Record<string, number>;
} {
  const match = methodology.derived_scores.suitability_sub_indicators?.requirement_match;
  return { soil: match?.soil_ranks ?? {}, irrigation: match?.irrigation_ranks ?? {} };
}

const FIT_MARK: Record<FitKind, string> = { suited: '✓', caution: '!', unsuitable: '✕' };

interface Card {
  typology: Typology;
  fit: Fit;
  offered: boolean;
  /** A verified example photo for exactly this zone, if one exists (D-051). */
  example: NbsImage | undefined;
}

interface FamilyGroup {
  family: string;
  cards: Card[];
}

/** The library's flat scoring view, which is the shape the picker renders. */
function resolvedEntries(library: TypologyLibrary): Typology[] {
  return library.resolved ?? [];
}

/**
 * Group cards by family in the catalogue's own order, elements before
 * composites, with any family the catalogue adds later appended rather than
 * dropped.
 */
function groupByFamily(cards: Card[]): FamilyGroup[] {
  const byFamily = new Map<string, Card[]>();
  for (const card of cards) {
    const bucket = byFamily.get(card.typology.family);
    if (bucket) bucket.push(card);
    else byFamily.set(card.typology.family, [card]);
  }
  const ordered = [...messages.families.order].filter((family) => byFamily.has(family));
  const extra = [...byFamily.keys()].filter((family) => !ordered.includes(family));
  return [...ordered, ...extra].map((family) => ({ family, cards: byFamily.get(family) ?? [] }));
}

function familyLabel(family: string): string {
  return messages.families.labels[family] ?? family;
}

/**
 * The example image for one entry, under the strict zone match of D-051.5.
 *
 * The lookup mirrors the library's own inheritance (D-044.3, D-051.1): a
 * per-typology override outranks the archetype image, and the archetype image
 * serves every entry inheriting it. No climate zone answered, or no verified
 * image for exactly this zone → `undefined`, and no affordance renders —
 * absence is the honest state, never a placeholder or a cross-zone
 * substitute.
 */
export function exampleImageFor(
  typology: Typology,
  images: NbsImage[] | null,
  climateZone: string | null | undefined,
): NbsImage | undefined {
  if (images == null || climateZone == null) return undefined;
  let inherited: NbsImage | undefined;
  for (const image of images) {
    if (image.zone !== climateZone) continue;
    if (image.nbs_type === typology.nbs_type) return image;
    if (image.nbs_type == null && image.archetype === typology.archetype) inherited = image;
  }
  return inherited;
}

export function TypologyPicker(props: {
  library: TypologyLibrary;
  methodology: MethodologyData;
  availability: AvailableTypologies | null;
  images: NbsImage[] | null;
  draft: DraftInput;
  onChange: (nbsTypes: string[]) => void;
}) {
  const [filter, setFilter] = useState('');
  // The open example dialog, if any: the image plus the evidence-class name
  // of the card it was opened from (the dialog states the inheritance).
  const [example, setExample] = useState<{ image: NbsImage; archetype: string } | null>(null);
  const filterId = useId();
  const { library, methodology, availability, draft } = props;
  const selected = draft.nbs_type ?? [];
  const entries = resolvedEntries(library);

  const offeredSet = useMemo(
    () => (availability ? new Set(availability.nbs_types) : null),
    [availability],
  );

  const cards = useMemo<Card[]>(() => {
    const ranks = ranksOf(methodology);
    return entries
      .map((typology) => ({
        typology,
        fit: assessFit(draft, typology, ranks),
        // Without a served answer nothing is "not offered": an unasked
        // question is not a negative one.
        offered: offeredSet === null || offeredSet.has(typology.nbs_type),
        example: exampleImageFor(typology, props.images, draft.climate_zone),
      }))
      .sort((a, b) => FIT_ORDER[a.fit.kind] - FIT_ORDER[b.fit.kind]);
  }, [entries, offeredSet, draft, methodology, props.images]);

  const needle = filter.trim().toLowerCase();
  const matching = needle
    ? cards.filter(
        (card) =>
          card.typology.display_name.toLowerCase().includes(needle) ||
          card.typology.archetype_display_name.toLowerCase().includes(needle),
      )
    : cards;

  const offeredGroups = groupByFamily(matching.filter((card) => card.offered));
  const withheldGroups = groupByFamily(matching.filter((card) => !card.offered));

  function toggle(nbsType: string) {
    // Selection order is the user's own and is preserved: the engine reports
    // components in the order they were proposed.
    props.onChange(
      selected.includes(nbsType)
        ? selected.filter((candidate) => candidate !== nbsType)
        : [...selected, nbsType],
    );
  }

  const byType = new Map(entries.map((typology) => [typology.nbs_type, typology]));
  const composesPackages = props.availability?.composes_packages ?? false;
  const warnAbove = props.availability?.warn_above_components;

  return (
    <div className="picker-shell">
      {/* The intervention is a questionnaire parameter like any other, so it
          carries the same D-041 explanation as every field. */}
      <div className="field__label-row">
        <span className="field__label">{messages.fields.nbs_type?.label}</span>
        <FieldExplainer field="nbs_type" />
      </div>
      <p className="muted">
        {composesPackages ? messages.picker.introPackage : messages.picker.intro}
      </p>

      <SelectionList
        selected={selected}
        byType={byType}
        warnAbove={warnAbove}
        onRemove={(nbsType) =>
          props.onChange(selected.filter((candidate) => candidate !== nbsType))
        }
      />

      <div className="field picker__filter">
        <label className="field__label" htmlFor={filterId}>
          {messages.picker.filterLabel}
        </label>
        <input
          id={filterId}
          type="search"
          value={filter}
          placeholder={messages.picker.filterPlaceholder}
          onChange={(event) => setFilter(event.target.value)}
        />
        {filter !== '' ? (
          <button type="button" className="button button--quiet" onClick={() => setFilter('')}>
            {messages.picker.clearFilter}
          </button>
        ) : null}
      </div>

      {matching.length === 0 ? <p className="notice">{messages.picker.filterNoMatch}</p> : null}

      {offeredGroups.length > 0 ? (
        <section aria-label={messages.picker.offeredHeading}>
          {offeredSet !== null ? (
            <>
              <h4 className="picker__section-heading">{messages.picker.offeredHeading}</h4>
              <p className="muted small">
                {messages.picker.offeredIntro(props.availability?.count ?? 0)}
              </p>
            </>
          ) : null}
          {offeredGroups.map((group) => (
            <FamilySection
              key={group.family}
              group={group}
              selected={selected}
              defaultOpen={offeredGroups.length <= 3 || needle !== ''}
              onToggle={toggle}
              onShowExample={setExample}
            />
          ))}
        </section>
      ) : null}

      {withheldGroups.length > 0 ? (
        <section className="picker__withheld" aria-label={messages.picker.notOfferedHeading}>
          <h4 className="picker__section-heading">{messages.picker.notOfferedHeading}</h4>
          <p className="muted small">{messages.picker.notOfferedIntro}</p>
          {withheldGroups.map((group) => (
            <FamilySection
              key={group.family}
              group={group}
              selected={selected}
              defaultOpen={needle !== ''}
              onToggle={toggle}
              onShowExample={setExample}
            />
          ))}
        </section>
      ) : null}

      <p className="muted small">{messages.picker.evidenceClassNote}</p>

      {example !== null ? (
        <ExampleImageDialog
          image={example.image}
          archetypeDisplayName={example.archetype}
          onClose={() => setExample(null)}
        />
      ) : null}
    </div>
  );
}

/** The current package: a removable, ordered list of what has been chosen. */
function SelectionList(props: {
  selected: string[];
  byType: Map<string, Typology>;
  warnAbove: number | undefined;
  onRemove: (nbsType: string) => void;
}) {
  const overSize = props.warnAbove !== undefined && props.selected.length > props.warnAbove;
  return (
    <div className="picker__selection">
      <h4 className="picker__section-heading">
        {messages.picker.selectionHeading}
        {props.selected.length > 0 ? (
          <>
            {' '}
            <span className="badge badge--accent">
              {messages.picker.selectionCount(props.selected.length)}
            </span>
          </>
        ) : null}
      </h4>
      {props.selected.length === 0 ? (
        <p className="muted small">{messages.picker.selectionEmpty}</p>
      ) : (
        <>
          <ol className="picker__selection-list">
            {props.selected.map((nbsType) => {
              const typology = props.byType.get(nbsType);
              return (
                <li key={nbsType}>
                  <span>
                    {typology ? (
                      <>
                        {typology.display_name}{' '}
                        <span className="muted small">
                          · {messages.picker.evidenceClass(typology.archetype_display_name)}
                        </span>
                      </>
                    ) : (
                      // A migrated draft can name an entry the current library
                      // no longer holds (D-044.2); it is shown, never hidden.
                      <span className="error-text">{messages.picker.unknownEntry(nbsType)}</span>
                    )}
                  </span>
                  <button
                    type="button"
                    className="button button--quiet"
                    aria-label={messages.picker.removeLabel(typology?.display_name ?? nbsType)}
                    onClick={() => props.onRemove(nbsType)}
                  >
                    {messages.picker.remove}
                  </button>
                </li>
              );
            })}
          </ol>
          <p className="muted small">{messages.picker.representativeHint}</p>
        </>
      )}
      {overSize && props.warnAbove !== undefined ? (
        <p className="notice notice--warn" role="status">
          {messages.picker.sizeWarning(props.warnAbove)}
        </p>
      ) : null}
    </div>
  );
}

/** One collapsible family, with its count in the summary. */
function FamilySection(props: {
  group: FamilyGroup;
  selected: string[];
  defaultOpen: boolean;
  onToggle: (nbsType: string) => void;
  onShowExample: (example: { image: NbsImage; archetype: string }) => void;
}) {
  const label = familyLabel(props.group.family);
  const kind = props.group.cards[0]?.typology.kind;
  return (
    <details className="collapsible picker__family" open={props.defaultOpen}>
      <summary>
        {label}{' '}
        <span className="muted small">
          · {messages.picker.groupCount(props.group.cards.length)}
          {kind ? ` · ${messages.families.kinds[kind] ?? kind}` : ''}
        </span>
      </summary>
      <div className="picker" role="group" aria-label={label}>
        {props.group.cards.map((card) => (
          <TypologyCard
            key={card.typology.nbs_type}
            card={card}
            selected={props.selected.includes(card.typology.nbs_type)}
            onToggle={props.onToggle}
            onShowExample={props.onShowExample}
          />
        ))}
      </div>
    </details>
  );
}

function TypologyCard(props: {
  card: Card;
  selected: boolean;
  onToggle: (nbsType: string) => void;
  onShowExample: (example: { image: NbsImage; archetype: string }) => void;
}) {
  const { typology, fit, offered, example } = props.card;
  const card = (
    <button
      type="button"
      className={`picker__card${offered ? '' : ' picker__card--withheld'}`}
      aria-pressed={props.selected}
      onClick={() => props.onToggle(typology.nbs_type)}
    >
      <span className={`picker__fit picker__fit--${fit.kind}`}>
        {FIT_MARK[fit.kind]}{' '}
        {fit.kind === 'suited'
          ? messages.picker.fit.suited
          : fit.kind === 'unsuitable'
            ? `${messages.picker.fit.unsuitablePrefix} — ${fit.notes.join('; ')}`
            : fit.notes.join('; ')}
      </span>
      <span className="picker__name">{typology.display_name}</span>
      <span className="picker__meta">
        {messages.picker.cooling(
          typology.temp_reduction_min_c.toLocaleString(),
          typology.temp_reduction_max_c.toLocaleString(),
        )}
      </span>
      {/* D-044: the entry inherits a cited envelope, and says which one. */}
      <span className="picker__meta">
        {messages.picker.evidenceClass(typology.archetype_display_name)}
      </span>
      <span className="picker__meta">
        {messages.picker.evidence(optionLabel(typology.evidence_confidence))}
        {fit.kind === 'unsuitable' ? ` · ${messages.picker.fit.selectable}` : ''}
      </span>
      {!offered ? (
        <span className="badge badge--warn">{messages.picker.notOfferedBadge}</span>
      ) : null}
      {props.selected ? (
        <span className="badge badge--accent">{messages.picker.selected}</span>
      ) : null}
    </button>
  );
  if (example === undefined) return card;
  // The card is itself a <button>, so the affordance is a positioned SIBLING
  // inside a wrapper, never a nested button — invalid HTML the browser would
  // "fix" by reparenting (D-051.2).
  return (
    <div className="picker__card-shell">
      {card}
      <button
        type="button"
        className="picker__photo"
        aria-label={messages.picker.example.affordance(typology.display_name)}
        title={messages.picker.example.affordance(typology.display_name)}
        onClick={() =>
          props.onShowExample({ image: example, archetype: typology.archetype_display_name })
        }
      >
        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
          <path
            fill="currentColor"
            d="M9.4 5l-1.2 2H4v12h16V7h-4.2l-1.2-2H9.4zM12 9.5a4 4 0 110 8 4 4 0 010-8zm0 1.8a2.2 2.2 0 100 4.4 2.2 2.2 0 000-4.4z"
          />
        </svg>
      </button>
    </div>
  );
}
