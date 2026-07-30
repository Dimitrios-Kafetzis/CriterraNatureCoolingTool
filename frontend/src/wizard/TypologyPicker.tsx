/**
 * The guided typology picker (UX §5, D-019, D-009).
 *
 * All 14 cards render sorted and annotated by fit to the site data already
 * entered. Fit is a comparison of the user's answers against each typology's
 * suitability conditions served by GET /api/typologies, using the ordinal
 * ranks served by GET /api/methodology — no rank, threshold, or requirement
 * originates here. Unsuitable typologies stay fully selectable: a user
 * deliberately testing a hypothesis is never overridden, and the flag
 * follows through to the results (computed there by the engine, D-009).
 */

import { messages, optionLabel } from '../i18n/en';
import type { DraftInput, MethodologyData, Typology, TypologyLibrary } from '../api/types';

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

export function TypologyPicker(props: {
  library: TypologyLibrary;
  methodology: MethodologyData;
  draft: DraftInput;
  onSelect: (nbsType: string) => void;
}) {
  const ranks = ranksOf(props.methodology);
  const cards = props.library.typologies
    .map((typology) => ({ typology, fit: assessFit(props.draft, typology, ranks) }))
    .sort((a, b) => FIT_ORDER[a.fit.kind] - FIT_ORDER[b.fit.kind]);

  return (
    <div className="picker" role="group" aria-label={messages.fields.nbs_type?.label}>
      {cards.map(({ typology, fit }) => {
        const selected = props.draft.nbs_type === typology.nbs_type;
        return (
          <button
            key={typology.nbs_type}
            type="button"
            className="picker__card"
            aria-pressed={selected}
            onClick={() => props.onSelect(typology.nbs_type)}
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
            <span className="picker__meta">
              {messages.picker.evidence(optionLabel(typology.evidence_confidence))}
              {fit.kind === 'unsuitable' ? ` · ${messages.picker.fit.selectable}` : ''}
            </span>
            {selected ? (
              <span className="badge badge--accent">{messages.picker.selected}</span>
            ) : null}
          </button>
        );
      })}
    </div>
  );
}
