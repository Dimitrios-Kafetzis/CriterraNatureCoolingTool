/**
 * The per-entry detail dialog (v2.6): what the tool already knows about one
 * catalogue entry, disclosed at the point of choosing.
 *
 * Four boundaries govern this file:
 *
 * * **Everything rendered is served, nothing originates here.** The identity,
 *   envelope, confidence, provenance and citations are the resolved entry's
 *   own fields from `GET /api/typologies`; the curation reason and the full
 *   reference behind each citation key ride on the same response, served from
 *   the published curation records and the bibliography; the suitability
 *   numbers restate a served requirement beside the user's own answer. No
 *   value, threshold or explanation is computed client-side.
 * * **The citations render inline, with the finding each supports** — never
 *   behind an expand control. The archetype model's promise is that every
 *   number traces to read literature; folding the evidence away would make
 *   that promise optional at exactly the moment a user is choosing.
 * * **Absence renders nothing.** No image → no image section; no unsuitable
 *   climate zones → no climate row; no placeholder, no "not available"
 *   anywhere. A dialog that lists empty sections teaches users to stop
 *   opening it.
 * * **The example image (v2.3, D-051) is one section of this dialog**, not a
 *   second dialog on the same card. Its caption, attribution and
 *   illustrative-not-evidence statement are unchanged from the dialog it
 *   replaces; the image is bundled and served by the app itself, so opening
 *   this dialog adds no request to any third party (D-049.1).
 */

import { useEffect, useRef } from 'react';
import { BibliographyContext, SourceList } from '../components/SourceList';
import { messages, optionLabel } from '../i18n/en';
import type { DraftInput, NbsImage, SourceReference, Typology } from '../api/types';

function zoneLabel(zone: string): string {
  return (messages.options.climate_zone as Record<string, string>)[zone] ?? zone;
}

export function exampleCaption(image: NbsImage): string {
  return messages.picker.example.caption(image.caption_subject, image.place, zoneLabel(image.zone));
}

export type ConditionStatus = 'met' | 'failed' | 'unanswered';

export interface SuitabilityCondition {
  /** The full sentence, requirement first, the site's answer after. */
  text: string;
  status: ConditionStatus;
}

/**
 * The suitability conditions expanded, requirement beside the site's answer.
 *
 * Mirrors `assessFit` exactly — a *supplied* answer strictly below the
 * requirement fails, an absent one is left open — but keeps each condition
 * separate so the dialog can say *why* the card carries its annotation, with
 * the numbers stated: the requirement is served in `Typology.suitability` and
 * the area is the user's own answer, so restating them originates nothing.
 * A condition the entry does not assert (no soil or irrigation requirement,
 * no unsuitable climate zone) yields no row at all.
 */
export function suitabilityConditions(
  site: DraftInput,
  typology: Typology,
  ranks: { soil: Record<string, number>; irrigation: Record<string, number> },
): SuitabilityCondition[] {
  const t = messages.picker.details.conditions;
  const conditions = typology.suitability;
  const rows: SuitabilityCondition[] = [];

  const minimum = conditions.minimum_site_area_m2;
  const area = site.site_area_m2;
  rows.push(
    area == null
      ? { text: t.area(minimum.toLocaleString()) + t.areaUnanswered, status: 'unanswered' }
      : {
          text: t.area(minimum.toLocaleString()) + t.areaAnswer(area.toLocaleString()),
          status: area < minimum ? 'failed' : 'met',
        },
  );

  const soilRequired = ranks.soil[conditions.requires_soil] ?? 0;
  if (soilRequired > 0) {
    const requirement = optionLabel(conditions.requires_soil).toLowerCase();
    const supplied = site.soil_availability != null && site.soil_availability !== 'unknown';
    rows.push(
      supplied
        ? {
            text:
              t.soil(requirement) +
              t.soilAnswer(optionLabel(site.soil_availability as string).toLowerCase()),
            status:
              (ranks.soil[site.soil_availability as string] ?? 0) < soilRequired ? 'failed' : 'met',
          }
        : { text: t.soil(requirement) + t.soilUnanswered, status: 'unanswered' },
    );
  }

  const irrigationRequired = ranks.irrigation[conditions.requires_irrigation] ?? 0;
  if (irrigationRequired > 0) {
    const requirement = optionLabel(conditions.requires_irrigation).toLowerCase();
    const supplied =
      site.irrigation_availability != null && site.irrigation_availability !== 'unknown';
    rows.push(
      supplied
        ? {
            text:
              t.irrigation(requirement) +
              t.irrigationAnswer(optionLabel(site.irrigation_availability as string).toLowerCase()),
            status:
              (ranks.irrigation[site.irrigation_availability as string] ?? 0) < irrigationRequired
                ? 'failed'
                : 'met',
          }
        : { text: t.irrigation(requirement) + t.irrigationUnanswered, status: 'unanswered' },
    );
  }

  const zones = conditions.unsuitable_climate_zones ?? [];
  if (zones.length > 0) {
    const listed = t.climate(zones.map(zoneLabel).join(', '));
    const zone = site.climate_zone;
    rows.push(
      zone == null
        ? { text: listed + t.climateUnanswered, status: 'unanswered' }
        : {
            text: listed + t.climateAnswer(zoneLabel(zone)),
            status: zones.includes(zone) ? 'failed' : 'met',
          },
    );
  }

  return rows;
}

export function TypologyDetailDialog(props: {
  typology: Typology;
  /** The entry's one-line curation reason, served with the library (v2.6). */
  reason: string | undefined;
  /** The full reference behind each citation key, served with the library. */
  bibliography: Record<string, SourceReference>;
  site: DraftInput;
  ranks: { soil: Record<string, number>; irrigation: Record<string, number> };
  /** A verified example photo for exactly this zone, if one exists (D-051). */
  image: NbsImage | undefined;
  onClose: () => void;
}) {
  const { typology, image } = props;
  const t = messages.picker.details;
  const ref = useRef<HTMLDialogElement>(null);

  // A native <dialog>, opened as a modal so focus containment and Escape
  // handling are the platform's, not reimplementations. jsdom implements
  // neither showModal nor close, so both fall back for the test environment:
  // the open attribute here, and onClose directly in close() below.
  useEffect(() => {
    const dialog = ref.current;
    if (!dialog || dialog.open) return;
    if (typeof dialog.showModal === 'function') dialog.showModal();
    else dialog.setAttribute('open', '');
  }, []);

  const close = () => {
    const dialog = ref.current;
    if (dialog && typeof dialog.close === 'function') dialog.close();
    else props.onClose();
  };

  const provenance = t.provenance[typology.evidence_provenance];
  const conditions = suitabilityConditions(props.site, typology, props.ranks);

  return (
    <dialog
      ref={ref}
      className="detail-dialog"
      aria-label={typology.display_name}
      onClose={props.onClose}
      onClick={(event) => {
        // Clicking the backdrop closes; the backdrop is the dialog element
        // itself, while every visible child sits inside the inner div.
        if (event.target === ref.current) close();
      }}
    >
      <div className="detail-dialog__body">
        <header>
          <h3 className="detail-dialog__name">{typology.display_name}</h3>
          <p className="muted small">
            {messages.families.labels[typology.family] ?? typology.family}
            {' · '}
            {messages.families.kinds[typology.kind] ?? typology.kind}
            {' · '}
            {t.catalogueEntry(typology.nbs_id)}
          </p>
          <p className="small">{t.mechanism(typology.primary_cooling_mechanism)}</p>
        </header>

        <section aria-label={t.evidenceHeading}>
          <h4 className="detail-dialog__heading">{t.evidenceHeading}</h4>
          <p className="small">{t.inherits(typology.archetype_display_name)}</p>
          <p className="small">
            {messages.picker.cooling(
              typology.temp_reduction_min_c.toLocaleString(),
              typology.temp_reduction_max_c.toLocaleString(),
            )}
            {' · '}
            {messages.picker.evidence(optionLabel(typology.evidence_confidence))}
          </p>
          {provenance !== undefined ? <p className="muted small">{provenance}</p> : null}
          {/* Every citation, with its finding and its full reference, inline:
              the evidence is the disclosure, so it is never folded behind an
              expand control, and no key renders without the work it names. */}
          <p className="muted small">{t.sourcesLabel}</p>
          <div className="detail-dialog__sources small">
            <BibliographyContext.Provider value={props.bibliography}>
              <SourceList sources={typology.sources} />
            </BibliographyContext.Provider>
          </div>
        </section>

        {props.reason !== undefined ? (
          <section aria-label={t.reasonHeading}>
            <h4 className="detail-dialog__heading">{t.reasonHeading}</h4>
            <p className="small">{props.reason}</p>
          </section>
        ) : null}

        <section aria-label={t.suitabilityHeading}>
          <h4 className="detail-dialog__heading">{t.suitabilityHeading}</h4>
          <ul className="detail-dialog__conditions small">
            {conditions.map((condition) => (
              <li
                key={condition.text}
                className={`detail-dialog__condition detail-dialog__condition--${condition.status}`}
              >
                {condition.text}
              </li>
            ))}
          </ul>
        </section>

        {image !== undefined ? (
          <section aria-label={exampleCaption(image)}>
            <figure>
              <img
                src={`/api/images/${image.file}`}
                alt={exampleCaption(image)}
                width={image.width}
                height={image.height}
              />
              <figcaption>{exampleCaption(image)}</figcaption>
            </figure>
            {image.nbs_type == null ? (
              <p className="muted small">
                {messages.picker.example.evidenceClassNote(typology.archetype_display_name)}
              </p>
            ) : null}
            <p className="muted small">{messages.picker.example.illustrativeNote}</p>
            <p className="detail-dialog__credit small">
              {messages.picker.example.credit(image.author)}
              {' · '}
              {messages.picker.example.licenceLabel}{' '}
              {image.licence_url != null ? (
                <a href={image.licence_url} target="_blank" rel="noreferrer">
                  {image.licence}
                </a>
              ) : (
                image.licence
              )}
              {' · '}
              <a href={image.source_page} target="_blank" rel="noreferrer">
                {messages.picker.example.sourceLink}
              </a>
            </p>
          </section>
        ) : null}

        <button type="button" className="button button--quiet" onClick={close}>
          {t.close}
        </button>
      </div>
    </dialog>
  );
}
