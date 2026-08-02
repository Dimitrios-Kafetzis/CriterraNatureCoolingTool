/**
 * The map step (v2.1, scope item 1; reworked in v2.2, D-049): first in the
 * questionnaire, skippable in one action, and never required.
 *
 * Three inputs are filled in from a location and no others (D-047). Everything
 * else the questionnaire asks about the site needs satellite or census data,
 * which is the GIS workflow deferred by D-002 — and real imagery on screen
 * makes that temptation stronger, not weaker, so it is worth restating:
 * neither the tile layer nor place search is a back door to it. Place search
 * (D-049.6) moves the map and fills in nothing.
 *
 * The tile layer resolves in this order (D-049.4):
 *   1. a source the user named this visit (with its required attribution),
 *   2. otherwise the deployment's configured source from /api/meta — unless
 *      the user switched it off for this visit,
 *   3. otherwise nothing: the bundled offline outlines, and no third-party
 *      request of any kind (D-049.1).
 * A source that turns out unreachable degrades to the bundled outlines
 * (D-049.8) rather than leaving a blank map.
 *
 * The rule that governs everything below: **autofill never overwrites an
 * answer the user has already given** (D-047.2).
 */

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { api } from '../api/client';
import { messages } from '../i18n/en';
import { useDebouncedValue } from '../lib/useDebouncedValue';
import type { DraftInput, GeoLookupResponse, PlaceResult, TileSource } from '../api/types';
import type { BasemapDocument } from '../api/types';
import { SiteMap, type FlyTarget, type Point, type TileSelection } from './SiteMap';

export interface MapStepProps {
  draft: DraftInput;
  autofilled: Record<string, string>;
  onAutofill: (values: DraftInput, sources: Record<string, string>) => void;
  onSkip: () => void;
}

/** The three fields a lookup can offer, and where each comes from. */
type Offer = { field: 'country' | 'climate_zone' | 'site_area_m2'; value: string | number };

const SEARCH_DEBOUNCE_MS = 250;
/** Close enough to read a neighbourhood; far enough to see the whole town. */
const PLACE_ZOOM = 12;

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

  // The deployment's configured source (D-049.2), and the user's two per-visit
  // controls over it (D-049.4): off, or replaced by a source of their own.
  const [deployerTiles, setDeployerTiles] = useState<TileSource | null>(null);
  const [deployerTilesOff, setDeployerTilesOff] = useState(false);
  const [userTiles, setUserTiles] = useState<TileSelection | null>(null);
  const [tileDraftUrl, setTileDraftUrl] = useState('');
  const [tileDraftAttribution, setTileDraftAttribution] = useState('');
  // The template that failed outright, if any — cleared when the source
  // changes so a retry is possible (D-049.8).
  const [failedTemplate, setFailedTemplate] = useState<string | null>(null);

  // Offline navigation by name (D-049.6).
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<PlaceResult[] | null>(null);
  const [flyTo, setFlyTo] = useState<FlyTarget | null>(null);
  const debouncedQuery = useDebouncedValue(searchQuery, SEARCH_DEBOUNCE_MS);

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
    void api
      .meta()
      .then((meta) => {
        if (live) setDeployerTiles(meta.tiles ?? null);
      })
      .catch(() => {
        // No metadata means no configured source; the offline map stands.
      });
    return () => {
      live = false;
    };
  }, []);

  useEffect(() => {
    const query = debouncedQuery.trim();
    if (query.length < 2) {
      setSearchResults(null);
      return;
    }
    let live = true;
    void api
      .places(query)
      .then((response) => {
        if (live) setSearchResults(response.results);
      })
      .catch(() => {
        if (live) setSearchResults(null);
      });
    return () => {
      live = false;
    };
  }, [debouncedQuery]);

  /**
   * Which source the map uses right now (D-049.4): the user's own source
   * wins, then the deployer's unless switched off or failed, then nothing.
   */
  const tiles = useMemo<TileSelection | null>(() => {
    const resolved =
      userTiles ??
      (deployerTiles !== null && !deployerTilesOff
        ? { template: deployerTiles.url_template, attribution: deployerTiles.attribution }
        : null);
    if (resolved === null) return null;
    return resolved.template === failedTemplate ? null : resolved;
  }, [userTiles, deployerTiles, deployerTilesOff, failedTemplate]);

  const tilesRef = useRef(tiles);
  tilesRef.current = tiles;
  const handleTileFailure = useCallback(() => {
    if (tilesRef.current !== null) setFailedTemplate(tilesRef.current.template);
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

  const selectPlace = useCallback((place: PlaceResult) => {
    // Navigation, never an answer (D-049.6): the map moves, and no
    // questionnaire field changes.
    setFlyTo({
      longitude: place.longitude,
      latitude: place.latitude,
      zoom: PLACE_ZOOM,
      name: place.name,
    });
    setSearchQuery('');
    setSearchResults(null);
  }, []);

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
  const userActive = userTiles !== null;

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
            <div className="sitemap__search">
              <label className="field__label" htmlFor="place-search">
                {map.searchLabel}
              </label>
              <input
                id="place-search"
                type="search"
                value={searchQuery}
                placeholder={map.searchPlaceholder}
                autoComplete="off"
                onChange={(event) => {
                  setSearchQuery(event.target.value);
                }}
              />
              {searchResults !== null ? (
                searchResults.length > 0 ? (
                  <ul className="sitemap__search-results">
                    {searchResults.map((place) => (
                      <li key={`${place.name}/${place.admin}/${String(place.latitude)}`}>
                        <button
                          type="button"
                          onClick={() => {
                            selectPlace(place);
                          }}
                        >
                          {map.searchResult(place.name, place.admin)}
                        </button>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="small muted">{map.searchNoResults}</p>
                )
              ) : null}
            </div>
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
            tiles={tiles}
            flyTo={flyTo}
            onBoundaryChange={handleBoundary}
            onCentreChange={handleCentre}
            onTileFailure={handleTileFailure}
          />
        </>
      )}

      {failedTemplate !== null ? (
        <p className="notice notice--warn" role="status">
          {map.tilesUnreachable}{' '}
          <button
            type="button"
            className="button button--quiet"
            onClick={() => {
              setFailedTemplate(null);
            }}
          >
            {map.tilesRetry}
          </button>
        </p>
      ) : null}

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
        <summary>
          {deployerTiles !== null ? map.tilesSummaryDeployer : map.tilesSummaryUser}
        </summary>
        <p className="field__help">
          {deployerTiles !== null ? map.tilesExplanationDeployer : map.tilesExplanationUser}
        </p>

        {deployerTiles !== null && userTiles === null ? (
          <div className="mapstep__tiles-form">
            <p className="small">
              {deployerTilesOff
                ? map.tilesDeployerOff
                : map.tilesDeployerOn(deployerTiles.attribution)}
            </p>
            <button
              type="button"
              className="button button--quiet"
              onClick={() => {
                setDeployerTilesOff((current) => !current);
                setFailedTemplate(null);
              }}
            >
              {deployerTilesOff ? map.tilesDeployerEnable : map.tilesDeployerDisable}
            </button>
          </div>
        ) : null}

        {userActive ? (
          <div className="mapstep__tiles-form">
            <p className="small">{map.tilesEnabled(userTiles.template)}</p>
            <button
              type="button"
              className="button button--quiet"
              onClick={() => {
                setUserTiles(null);
                setFailedTemplate(null);
              }}
            >
              {map.tilesDisable}
            </button>
          </div>
        ) : (
          <div className="mapstep__tiles-form">
            <label className="field__label" htmlFor="tile-template">
              {map.tilesLabel}
            </label>
            <input
              id="tile-template"
              type="url"
              value={tileDraftUrl}
              placeholder="https://…/{z}/{x}/{y}.png"
              onChange={(event) => {
                setTileDraftUrl(event.target.value);
              }}
            />
            <label className="field__label" htmlFor="tile-attribution">
              {map.tilesAttributionLabel}
            </label>
            <input
              id="tile-attribution"
              type="text"
              value={tileDraftAttribution}
              placeholder={map.tilesAttributionPlaceholder}
              onChange={(event) => {
                setTileDraftAttribution(event.target.value);
              }}
            />
            <p className="field__help">{map.tilesAttributionHelp}</p>
            <button
              type="button"
              className="button button--secondary"
              disabled={
                !tileDraftUrl.includes('{z}') ||
                !tileDraftUrl.includes('{x}') ||
                !tileDraftUrl.includes('{y}') ||
                tileDraftAttribution.trim() === ''
              }
              onClick={() => {
                setUserTiles({
                  template: tileDraftUrl,
                  attribution: tileDraftAttribution.trim(),
                });
                setFailedTemplate(null);
              }}
            >
              {map.tilesEnable}
            </button>
          </div>
        )}
      </details>
    </div>
  );
}
