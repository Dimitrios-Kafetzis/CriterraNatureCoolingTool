/**
 * The offline site map (v2.1, D-047.1).
 *
 * Drawn as inline SVG over the bundled Natural Earth outlines, with no map
 * library. That is a deliberate choice, not an omission. The app's only runtime
 * dependencies are React and react-router; a WebGL map library would be the
 * first exception, would ship inside the wheel, and would not instantiate under
 * the test environment at all — leaving either a mock that tests nothing or a
 * visible loosening of the jsdom setup. SVG gives pan, zoom, point placement
 * and polygon drawing in a few hundred lines, renders under test, and makes the
 * offline guarantee structural rather than configured: in the default build
 * there is no tile URL to forget to turn off.
 *
 * Projection is Web Mercator over the unit square, which is what every slippy
 * map on the web uses. It is chosen for one concrete reason: the opt-in tiles
 * D-047.1 permits are published in Web Mercator, and a plate-carrée basemap
 * underneath them would simply not line up. Areas are never measured from the
 * projection — `site_area_m2` is computed geodesically on the server from the
 * drawn longitude/latitude ring — so Mercator's area distortion costs nothing.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { messages } from '../i18n/en';
import type { BasemapDocument } from '../api/types';

/** A drawn vertex, in the order the user placed it. */
export interface Point {
  longitude: number;
  latitude: number;
}

interface SiteMapProps {
  basemap: BasemapDocument | null;
  boundary: Point[];
  centre: Point | null;
  tileTemplate: string | null;
  drawing: boolean;
  onBoundaryChange: (boundary: Point[]) => void;
  onCentreChange: (centre: Point) => void;
}

/** Web Mercator clamps at the latitude where the projection runs to infinity. */
export const MERCATOR_LIMIT = 85.05112878;
const MIN_ZOOM = 1;
const MAX_ZOOM = 4096;

function clamp(value: number, low: number, high: number): number {
  return Math.min(Math.max(value, low), high);
}

/** Longitude to unit-square x. */
export function toX(longitude: number): number {
  return (longitude + 180) / 360;
}

/** Latitude to unit-square y, north at 0. */
export function toY(latitude: number): number {
  const phi = (clamp(latitude, -MERCATOR_LIMIT, MERCATOR_LIMIT) * Math.PI) / 180;
  return (1 - Math.log(Math.tan(phi) + 1 / Math.cos(phi)) / Math.PI) / 2;
}

/** Unit-square x back to longitude. */
export function toLongitude(x: number): number {
  return clamp(x * 360 - 180, -180, 180);
}

/** Unit-square y back to latitude. */
export function toLatitude(y: number): number {
  const n = Math.PI * (1 - 2 * clamp(y, 0, 1));
  return (Math.atan(Math.sinh(n)) * 180) / Math.PI;
}

/** One country's outlines as an SVG path in unit-square coordinates. */
function outlinePath(polygons: number[][][][]): string {
  const parts: string[] = [];
  for (const polygon of polygons) {
    for (const ring of polygon) {
      const [first, ...rest] = ring;
      if (first === undefined) continue;
      parts.push(`M ${toX(first[0] ?? 0).toFixed(6)} ${toY(first[1] ?? 0).toFixed(6)}`);
      for (const point of rest) {
        parts.push(`L ${toX(point[0] ?? 0).toFixed(6)} ${toY(point[1] ?? 0).toFixed(6)}`);
      }
      parts.push('Z');
    }
  }
  return parts.join(' ');
}

export function SiteMap(props: SiteMapProps) {
  const { basemap, boundary, centre, drawing, onBoundaryChange, onCentreChange } = props;
  const svgRef = useRef<SVGSVGElement | null>(null);
  const [zoom, setZoom] = useState(1);
  const [focus, setFocus] = useState<Point>({ longitude: 0, latitude: 25 });

  // The visible window, derived rather than stored so zoom and focus can never
  // disagree about where the map is looking.
  const view = useMemo(() => {
    const size = 1 / zoom;
    return {
      size,
      minX: clamp(toX(focus.longitude) - size / 2, 0, 1 - size),
      minY: clamp(toY(focus.latitude) - size / 2, 0, 1 - size),
    };
  }, [zoom, focus]);

  const paths = useMemo(() => {
    if (basemap === null) return [];
    return [
      ...basemap.countries.map((entry) => ({
        key: entry.iso_a2,
        d: outlinePath(entry.polygons),
        unassigned: false,
      })),
      ...basemap.unassigned.map((entry, index) => ({
        key: `unassigned-${index}`,
        d: outlinePath(entry.polygons),
        unassigned: true,
      })),
    ];
  }, [basemap]);

  const handleClick = useCallback(
    (event: React.MouseEvent<SVGSVGElement>) => {
      const svg = svgRef.current;
      if (svg === null) return;
      const rect = svg.getBoundingClientRect();
      if (rect.width === 0 || rect.height === 0) return;
      const point = {
        longitude: toLongitude(view.minX + ((event.clientX - rect.left) / rect.width) * view.size),
        latitude: toLatitude(view.minY + ((event.clientY - rect.top) / rect.height) * view.size),
      };
      if (drawing) {
        onBoundaryChange([...boundary, point]);
      } else {
        onCentreChange(point);
      }
    },
    [view, drawing, boundary, onBoundaryChange, onCentreChange],
  );

  const changeZoom = useCallback((factor: number) => {
    setZoom((current) => clamp(current * factor, MIN_ZOOM, MAX_ZOOM));
  }, []);

  const pan = useCallback(
    (dx: number, dy: number) => {
      setFocus((current) => ({
        longitude: toLongitude(clamp(toX(current.longitude) + (dx * 0.25) / zoom, 0, 1)),
        latitude: toLatitude(clamp(toY(current.latitude) + (dy * 0.25) / zoom, 0, 1)),
      }));
    },
    [zoom],
  );

  // Follow a site set from outside — a resumed draft, or a typed coordinate.
  useEffect(() => {
    if (centre !== null) {
      setFocus(centre);
    }
  }, [centre]);

  const project = (point: Point) => `${toX(point.longitude)} ${toY(point.latitude)}`;
  const boundaryPath =
    boundary.length > 0
      ? `M ${boundary.map(project).join(' L ')}${boundary.length > 2 ? ' Z' : ''}`
      : '';
  const markerRadius = view.size / 90;

  const map = messages.map;
  return (
    <div className="sitemap">
      <div className="sitemap__frame">
        {/*
          The tile layer exists in the DOM only once a user has named a source
          and switched it on. Rendering it hidden would still fetch it.
        */}
        {props.tileTemplate !== null ? (
          <TileLayer template={props.tileTemplate} view={view} zoom={zoom} />
        ) : null}
        <svg
          ref={svgRef}
          className="sitemap__canvas"
          viewBox={`${view.minX} ${view.minY} ${view.size} ${view.size}`}
          preserveAspectRatio="xMidYMid slice"
          onClick={handleClick}
          role="application"
          aria-label={drawing ? map.canvasLabelDrawing : map.canvasLabelPlacing}
        >
          {props.tileTemplate === null ? (
            <rect x={0} y={0} width={1} height={1} className="sitemap__sea" />
          ) : null}
          {paths.map((entry) => (
            <path
              key={entry.key}
              d={entry.d}
              className={
                entry.unassigned ? 'sitemap__land sitemap__land--unassigned' : 'sitemap__land'
              }
              vectorEffect="non-scaling-stroke"
            />
          ))}
          {boundaryPath !== '' ? (
            <path
              d={boundaryPath}
              className="sitemap__boundary"
              vectorEffect="non-scaling-stroke"
            />
          ) : null}
          {boundary.map((point, index) => (
            <circle
              key={`${String(point.longitude)},${String(point.latitude)},${String(index)}`}
              cx={toX(point.longitude)}
              cy={toY(point.latitude)}
              r={markerRadius}
              className="sitemap__vertex"
            />
          ))}
          {centre !== null ? (
            <circle
              cx={toX(centre.longitude)}
              cy={toY(centre.latitude)}
              r={markerRadius * 1.4}
              className="sitemap__centre"
            />
          ) : null}
        </svg>
      </div>

      <div className="sitemap__controls">
        <div className="sitemap__pad">
          <button type="button" className="button button--quiet" onClick={() => pan(0, -1)}>
            {map.panNorth}
          </button>
          <div className="sitemap__pad-row">
            <button type="button" className="button button--quiet" onClick={() => pan(-1, 0)}>
              {map.panWest}
            </button>
            <button type="button" className="button button--quiet" onClick={() => pan(1, 0)}>
              {map.panEast}
            </button>
          </div>
          <button type="button" className="button button--quiet" onClick={() => pan(0, 1)}>
            {map.panSouth}
          </button>
        </div>
        <div className="sitemap__zoom">
          <button
            type="button"
            className="button button--quiet"
            onClick={() => changeZoom(2)}
            disabled={zoom >= MAX_ZOOM}
          >
            {map.zoomIn}
          </button>
          <button
            type="button"
            className="button button--quiet"
            onClick={() => changeZoom(0.5)}
            disabled={zoom <= MIN_ZOOM}
          >
            {map.zoomOut}
          </button>
        </div>
      </div>

      {basemap !== null ? <p className="small muted">{basemap.attribution}</p> : null}
    </div>
  );
}

interface TileLayerProps {
  template: string;
  view: { minX: number; minY: number; size: number };
  zoom: number;
}

/**
 * Opt-in raster tiles (D-047.1) — the only place this application requests
 * anything from a host the user did not install it from.
 *
 * The template is the user's own. Nothing here supplies a default and no
 * source is named anywhere in the code, because naming one would make it the
 * obvious choice and quietly turn an informed decision back into a default.
 */
function TileLayer(props: TileLayerProps) {
  const level = clamp(Math.round(Math.log2(props.zoom)), 0, 19);
  const count = 2 ** level;

  const tiles = useMemo(() => {
    const out: { key: string; url: string; left: string; top: string; size: string }[] = [];
    const minX = Math.max(0, Math.floor(props.view.minX * count));
    const maxX = Math.min(count - 1, Math.floor((props.view.minX + props.view.size) * count));
    const minY = Math.max(0, Math.floor(props.view.minY * count));
    const maxY = Math.min(count - 1, Math.floor((props.view.minY + props.view.size) * count));

    // A viewport needs a few dozen tiles at most. The cap stops a pathological
    // zoom from issuing thousands of requests to someone else's server on the
    // user's behalf.
    if ((maxX - minX + 1) * (maxY - minY + 1) > 64) return out;

    const percent = (value: number) => `${String((value / props.view.size) * 100)}%`;
    for (let x = minX; x <= maxX; x += 1) {
      for (let y = minY; y <= maxY; y += 1) {
        out.push({
          key: `${String(level)}/${String(x)}/${String(y)}`,
          url: props.template
            .replace('{z}', String(level))
            .replace('{x}', String(x))
            .replace('{y}', String(y)),
          left: percent(x / count - props.view.minX),
          top: percent(y / count - props.view.minY),
          size: percent(1 / count),
        });
      }
    }
    return out;
  }, [props.template, props.view, count, level]);

  return (
    <div className="sitemap__tiles" aria-hidden="true">
      {tiles.map((tile) => (
        <img
          key={tile.key}
          src={tile.url}
          alt=""
          loading="lazy"
          style={{ left: tile.left, top: tile.top, width: tile.size, height: tile.size }}
        />
      ))}
    </div>
  );
}
