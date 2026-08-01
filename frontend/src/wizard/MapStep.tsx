/**
 * The map step (v2.1, scope item 1): first in the questionnaire, skippable in
 * one action, and never required.
 *
 * Three inputs are filled in from a location and no others (D-047). Everything
 * else the questionnaire asks about the site needs satellite or census data,
 * which is the GIS workflow deferred by D-002 — filling in canopy cover from
 * an NDVI lookup would demo extremely well and would produce this tool's most
 * decision-relevant inputs from an unvalidated pipeline with no evidence table
 * behind it, which is the defect D-016 refused for cost defaults.
 *
 * The rule that governs everything below: **autofill never overwrites an
 * answer the user has already given** (D-047.2). A value is offered only where
 * the field is empty; where it is not, the lookup's answer is shown as a
 * suggestion the user may take, and taking it is a click they perform.
 */

import { useCallback, useEffect, useState } from 'react';
import { api } from '../api/client';
import { messages } from '../i18n/en';
import type { DraftInput, GeoLookupResponse } from '../api/types';
import type { BasemapDocument } from '../api/types';
import { SiteMap, type Point } from './SiteMap';

export interface MapStepProps {
  draft: DraftInput;
  autofilled: Record<string, string>;
  onAutofill: (values: DraftInput, sources: Record<string, string>) => void;
  onSkip: () => void;
}

/** The three fields a lookup can offer, and where each comes from. */
type Offer = { field: 'country' | 'climate_zone' | 'site_area_m2'; value: string | number };

function offersFrom(lookup: GeoLookupResponse): { offer: Offer; source: string }[] {
  const out: { offer: Offer; source: string }[] = [];
  if (lookup.country.iso_a2 !== null && lookup.country.iso_a2 !== undefined) {
    out.push({
      offer: { field: 'country', value: lookup.country.iso_a2 },
      source: lookup.country.source_key,
    });
  }
  if (lookup.climate.zone !== null && lookup.climate.zone !== undefined) {
    out.push({
      offer: { field: 'climate_zone', value: lookup.climate.zone },
      source: lookup.climate.source_key,
    });
  }
  if (lookup.site_area_m2 !== null && lookup.site_area_m2 !== undefined) {
    out.push({
      offer: { field: 'site_area_m2', value: lookup.site_area_m2 },
      source: 'drawn_polygon',
    });
  }
  return out;
}

export function MapStep(props: MapStepProps) {
  const { draft, autofilled, onAutofill, onSkip } = props;
  const [basemap, setBasemap] = useState<BasemapDocument | null>(null);
  const [basemapError, setBasemapError] = useState(false);
  const [boundary, setBoundary] = useState<Point[]>([]);
  const [centre, setCentre] = useState<Point | null>(null);
  const [drawing, setDrawing] = useState(false);
  const [lookup, setLookup] = useState<GeoLookupResponse | null>(null);
  const [looking, setLooking] = useState(false);
  const [tileTemplate, setTileTemplate] = useState<string | null>(null);
  const [tileDraft, setTileDraft] = useState('');

  useEffect(() => {
    let live = true;
    void api
      .basemap()
      .then((document) => {
        if (live) setBasemap(document);
      })
      .catch(() => {
        if (live) setBasemapError(true);
      });
    return () => {
      live = false;
    };
  }, []);

  const runLookup = useCallback((point: Point, ring: Point[]) => {
    setLooking(true);
    void api
      .geoLookup({
        latitude: point.latitude,
        longitude: point.longitude,
        boundary:
          ring.length >= 3 ? ring.map((vertex) => [vertex.longitude, vertex.latitude]) : null,
      })
      .then((response) => {
        setLookup(response);
      })
      .catch(() => {
        setLookup(null);
      })
      .finally(() => {
        setLooking(false);
      });
  }, []);

  const handleCentre = useCallback(
    (point: Point) => {
      setCentre(point);
      runLookup(point, boundary);
    },
    [boundary, runLookup],
  );

  const handleBoundary = useCallback(
    (ring: Point[]) => {
      setBoundary(ring);
      if (ring.length >= 3) {
        // The centroid of the drawn ring is what the classification applies to.
        const point = {
          longitude: ring.reduce((sum, v) => sum + v.longitude, 0) / ring.length,
          latitude: ring.reduce((sum, v) => sum + v.latitude, 0) / ring.length,
        };
        setCentre(point);
        runLookup(point, ring);
      }
    },
    [runLookup],
  );

  const offers = lookup === null ? [] : offersFrom(lookup);
  const available = offers.filter(({ offer }) => draft[offer.field] === undefined);
  const conflicting = offers.filter(({ offer }) => draft[offer.field] !== undefined);

  const apply = useCallback(
    (chosen: { offer: Offer; source: string }[]) => {
      const values: DraftInput = {};
      const sources: Record<string, string> = {};
      for (const { offer, source } of chosen) {
        if (offer.field === 'site_area_m2') {
          values.site_area_m2 = Math.round(offer.value as number);
        } else if (offer.field === 'country') {
          values.country = offer.value as string;
        } else {
          values.climate_zone = offer.value as DraftInput['climate_zone'];
        }
        sources[offer.field] = source;
      }
      onAutofill(values, sources);
    },
    [onAutofill],
  );

  const map = messages.map;
  return (
    <div className="mapstep">
      <p className="notice">
        {map.intro}{' '}
        <button type="button" className="button button--quiet" onClick={onSkip}>
          {map.skip}
        </button>
      </p>

      {basemapError ? (
        <p className="notice notice--warn">{map.basemapUnavailable}</p>
      ) : (
        <>
          <div className="sitemap__toolbar">
            <button
              type="button"
              className={drawing ? 'button' : 'button button--secondary'}
              aria-pressed={drawing}
              onClick={() => {
                setDrawing((current) => !current);
              }}
            >
              {drawing ? map.drawingOn : map.drawingOff}
            </button>
            <button
              type="button"
              className="button button--quiet"
              disabled={boundary.length === 0}
              onClick={() => {
                setBoundary([]);
              }}
            >
              {map.clearBoundary}
            </button>
          </div>
          <p className="field__help">{drawing ? map.drawingHint : map.placingHint}</p>

          <SiteMap
            basemap={basemap}
            boundary={boundary}
            centre={centre}
            drawing={drawing}
            tileTemplate={tileTemplate}
            onBoundaryChange={handleBoundary}
            onCentreChange={handleCentre}
          />
        </>
      )}

      {looking ? <p className="small muted">{map.looking}</p> : null}

      {lookup !== null && !looking ? (
        <div className="card mapstep__result">
          <h2>{map.foundHeading}</h2>
          {offers.length === 0 ? (
            <p className="muted">{map.foundNothing}</p>
          ) : (
            <>
              <ul className="mapstep__offers">
                {offers.map(({ offer }) => (
                  <li key={offer.field}>
                    <strong>{messages.fields[offer.field]?.label ?? offer.field}:</strong>{' '}
                    {offer.field === 'site_area_m2'
                      ? `${Math.round(offer.value as number).toLocaleString()} m²`
                      : offer.field === 'climate_zone'
                        ? (messages.options.climate_zone[
                            offer.value as keyof typeof messages.options.climate_zone
                          ] ?? String(offer.value))
                        : String(offer.value)}
                    {draft[offer.field] !== undefined ? (
                      <span className="badge badge--warn"> {map.alreadyAnswered}</span>
                    ) : null}
                  </li>
                ))}
              </ul>

              {lookup.climate.zone !== null ? (
                <p className="small muted">
                  {lookup.climate.note} {lookup.climate.resolution_caveat}
                </p>
              ) : null}

              <div className="actions-row">
                <button
                  type="button"
                  className="button"
                  disabled={available.length === 0}
                  onClick={() => {
                    apply(available);
                  }}
                >
                  {map.applyEmpty}
                </button>
                {/*
                  Overwriting is possible but never automatic: it is a second,
                  differently-worded button that says what it will replace
                  (D-047.2 — autofill never overwrites an answer already given).
                */}
                {conflicting.length > 0 ? (
                  <button
                    type="button"
                    className="button button--secondary"
                    onClick={() => {
                      apply(offers);
                    }}
                  >
                    {map.applyReplacing(conflicting.length)}
                  </button>
                ) : null}
              </div>
            </>
          )}
        </div>
      ) : null}

      {Object.keys(autofilled).length > 0 ? (
        <p className="notice notice--accent">{map.appliedNote(Object.keys(autofilled).length)}</p>
      ) : null}

      <details className="mapstep__tiles-optin">
        <summary>{map.tilesSummary}</summary>
        <p className="field__help">{map.tilesExplanation}</p>
        {tileTemplate === null ? (
          <div className="mapstep__tiles-form">
            <label className="field__label" htmlFor="tile-template">
              {map.tilesLabel}
            </label>
            <input
              id="tile-template"
              type="url"
              value={tileDraft}
              placeholder="https://…/{z}/{x}/{y}.png"
              onChange={(event) => {
                setTileDraft(event.target.value);
              }}
            />
            <button
              type="button"
              className="button button--secondary"
              disabled={!tileDraft.includes('{z}')}
              onClick={() => {
                setTileTemplate(tileDraft);
              }}
            >
              {map.tilesEnable}
            </button>
          </div>
        ) : (
          <div className="mapstep__tiles-form">
            <p className="small">{map.tilesEnabled(tileTemplate)}</p>
            <button
              type="button"
              className="button button--quiet"
              onClick={() => {
                setTileTemplate(null);
              }}
            >
              {map.tilesDisable}
            </button>
          </div>
        )}
      </details>
    </div>
  );
}
