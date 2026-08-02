/**
 * The site map (v2.1, D-047.1; reworked on Leaflet in v2.2, D-049.5).
 *
 * v2.1 hand-rolled this as inline SVG (D-048.5) because a WebGL map library
 * would not instantiate under the test environment. Leaflet does — map, SVG
 * vector renderer, tile layer, attribution control and click handling all run
 * under jsdom, which is what dissolved D-048.5's objection — and it brings
 * the interaction that makes a map navigable (drag, inertia, cursor-anchored
 * wheel zoom, touch, date-line wrap) as 42 KB of BSD-2-Clause code with zero
 * dependencies. Its licence ships beside the build; see NOTICE.
 *
 * The offline guarantee is unchanged: with no tile source resolved, the map
 * is the bundled Natural Earth outlines and nothing is requested from
 * anywhere. A tile layer exists only when `tiles` is non-null, which happens
 * only when a deployer configured a source (D-049.2) or the user named one
 * (D-047.1) — and every tile source renders its attribution on the map, which
 * Leaflet's attribution control does per layer (D-049.2).
 *
 * Degradation is detected, not assumed (D-049.8): if the first tiles of a
 * configured source all fail, `onTileFailure` fires and the caller falls back
 * to the bundled outlines, so an optimistically configured restricted-network
 * deployment still has a working map.
 */

import { useEffect, useMemo, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { messages } from '../i18n/en';
import type { BasemapDocument } from '../api/types';

/** A drawn vertex, in the order the user placed it. */
export interface Point {
  longitude: number;
  latitude: number;
}

/** A resolved tile source: the template and the credit it requires. */
export interface TileSelection {
  template: string;
  attribution: string;
}

/** Somewhere to move the map to — a selected place. Never an answer. */
export interface FlyTarget {
  longitude: number;
  latitude: number;
  zoom: number;
}

interface SiteMapProps {
  basemap: BasemapDocument | null;
  boundary: Point[];
  centre: Point | null;
  tiles: TileSelection | null;
  drawing: boolean;
  flyTo: FlyTarget | null;
  onBoundaryChange: (boundary: Point[]) => void;
  onCentreChange: (centre: Point) => void;
  onTileFailure: () => void;
}

/**
 * How many consecutive failures, with nothing loaded yet, mean the source is
 * unreachable rather than missing one tile. The first world view shows a
 * handful of tiles, so four failures with zero successes is decisive.
 */
const TILE_FAILURES_BEFORE_FALLBACK = 4;

/** One country's outlines as GeoJSON coordinates (already [lon, lat]). */
function toFeatures(basemap: BasemapDocument): GeoJSON.Feature[] {
  const features: GeoJSON.Feature[] = [];
  for (const entry of basemap.countries) {
    features.push({
      type: 'Feature',
      properties: { unassigned: false },
      geometry: { type: 'MultiPolygon', coordinates: entry.polygons },
    });
  }
  for (const entry of basemap.unassigned) {
    features.push({
      type: 'Feature',
      properties: { unassigned: true },
      geometry: { type: 'MultiPolygon', coordinates: entry.polygons },
    });
  }
  return features;
}

export function SiteMap(props: SiteMapProps) {
  const { basemap, boundary, centre, tiles, drawing, flyTo } = props;
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<L.Map | null>(null);
  const outlinesRef = useRef<L.GeoJSON | null>(null);
  const tileLayerRef = useRef<L.TileLayer | null>(null);
  const drawnRef = useRef<L.LayerGroup | null>(null);

  // The click handler reads these through refs so the map subscribes once.
  const stateRef = useRef({ drawing, boundary });
  stateRef.current = { drawing, boundary };
  const callbacksRef = useRef({
    onBoundaryChange: props.onBoundaryChange,
    onCentreChange: props.onCentreChange,
    onTileFailure: props.onTileFailure,
  });
  callbacksRef.current = {
    onBoundaryChange: props.onBoundaryChange,
    onCentreChange: props.onCentreChange,
    onTileFailure: props.onTileFailure,
  };

  const map = messages.map;

  // The map itself, created once.
  useEffect(() => {
    const container = containerRef.current;
    if (container === null) return;
    const leafletMap = L.map(container, {
      center: [25, 10],
      zoom: 2,
      minZoom: 1,
      maxZoom: 19,
      // Fractional zoom: the wheel and pinch land between integer levels
      // rather than jumping octaves of scale.
      zoomSnap: 0.25,
      zoomDelta: 0.5,
      // Panning across the date line re-centres the world copy under the view.
      worldCopyJump: true,
      maxBounds: [
        [-85.06, -540],
        [85.06, 540],
      ],
      maxBoundsViscosity: 0.75,
      zoomControl: false,
      attributionControl: false,
    });
    // Controls built explicitly so their strings come from the catalog and
    // the attribution control carries no prefix link.
    L.control
      .zoom({ zoomInTitle: map.zoomIn, zoomOutTitle: map.zoomOut, position: 'topleft' })
      .addTo(leafletMap);
    L.control.attribution({ prefix: false, position: 'bottomright' }).addTo(leafletMap);

    leafletMap.on('click', (event: L.LeafletMouseEvent) => {
      const point = {
        longitude: event.latlng.wrap().lng,
        latitude: event.latlng.lat,
      };
      const current = stateRef.current;
      if (current.drawing) {
        callbacksRef.current.onBoundaryChange([...current.boundary, point]);
      } else {
        callbacksRef.current.onCentreChange(point);
      }
    });

    mapRef.current = leafletMap;
    return () => {
      leafletMap.remove();
      mapRef.current = null;
      outlinesRef.current = null;
      tileLayerRef.current = null;
      drawnRef.current = null;
    };
    // The catalog is a module constant; the map is created exactly once.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // The bundled outlines — the layer that makes the map work offline.
  const features = useMemo(() => (basemap === null ? null : toFeatures(basemap)), [basemap]);
  useEffect(() => {
    const leafletMap = mapRef.current;
    if (leafletMap === null || features === null || basemap === null) return;
    const layer = L.geoJSON({ type: 'FeatureCollection', features } as GeoJSON.FeatureCollection, {
      style: (feature) => ({
        className:
          (feature?.properties as { unassigned?: boolean } | undefined)?.unassigned === true
            ? 'sitemap__land sitemap__land--unassigned'
            : 'sitemap__land',
      }),
      attribution: basemap.attribution,
      // Clicks belong to the map, not the polygons under the cursor.
      interactive: false,
    }).addTo(leafletMap);
    outlinesRef.current = layer;
    return () => {
      layer.remove();
      outlinesRef.current = null;
    };
  }, [features, basemap]);

  // The tile layer — exists only while a source is resolved (D-049.1), and
  // detects total failure rather than assuming reachability (D-049.8).
  useEffect(() => {
    const leafletMap = mapRef.current;
    if (leafletMap === null || tiles === null) return;
    let loaded = 0;
    let failed = 0;
    const layer = L.tileLayer(tiles.template, {
      attribution: tiles.attribution,
      maxZoom: 19,
    });
    layer.on('tileload', () => {
      loaded += 1;
    });
    layer.on('tileerror', () => {
      failed += 1;
      // Some tiles failing at the edge of a provider's coverage is normal;
      // nothing at all loading is an unreachable source.
      if (loaded === 0 && failed >= TILE_FAILURES_BEFORE_FALLBACK) {
        callbacksRef.current.onTileFailure();
      }
    });
    layer.addTo(leafletMap);
    tileLayerRef.current = layer;
    return () => {
      layer.remove();
      tileLayerRef.current = null;
    };
  }, [tiles]);

  // The user's drawing: the boundary ring, its vertices, and the site point.
  useEffect(() => {
    const leafletMap = mapRef.current;
    if (leafletMap === null) return;
    const group = L.layerGroup();
    if (boundary.length > 0) {
      const ring = boundary.map((point) => [point.latitude, point.longitude] as L.LatLngTuple);
      if (boundary.length > 2) {
        group.addLayer(L.polygon(ring, { className: 'sitemap__boundary', interactive: false }));
      } else {
        group.addLayer(L.polyline(ring, { className: 'sitemap__boundary', interactive: false }));
      }
      for (const point of boundary) {
        group.addLayer(
          L.circleMarker([point.latitude, point.longitude], {
            radius: 4,
            className: 'sitemap__vertex',
            interactive: false,
          }),
        );
      }
    }
    if (centre !== null) {
      group.addLayer(
        L.circleMarker([centre.latitude, centre.longitude], {
          radius: 6,
          className: 'sitemap__centre',
          interactive: false,
        }),
      );
    }
    group.addTo(leafletMap);
    drawnRef.current = group;
    return () => {
      group.remove();
      drawnRef.current = null;
    };
  }, [boundary, centre]);

  // Follow a site set from outside — a resumed draft, or a typed coordinate —
  // without yanking the view when the user placed the point themselves.
  useEffect(() => {
    const leafletMap = mapRef.current;
    if (leafletMap === null || centre === null) return;
    const latlng = L.latLng(centre.latitude, centre.longitude);
    if (!leafletMap.getBounds().contains(latlng)) {
      leafletMap.setView(latlng, Math.max(leafletMap.getZoom(), 9));
    }
  }, [centre]);

  // A selected place: navigation, never an answer (D-049.6).
  useEffect(() => {
    const leafletMap = mapRef.current;
    if (leafletMap === null || flyTo === null) return;
    leafletMap.flyTo([flyTo.latitude, flyTo.longitude], flyTo.zoom, { duration: 0.8 });
  }, [flyTo]);

  return (
    <div className={tiles !== null ? 'sitemap sitemap--imagery' : 'sitemap'}>
      <div
        ref={containerRef}
        className="sitemap__frame"
        role="application"
        aria-label={drawing ? map.canvasLabelDrawing : map.canvasLabelPlacing}
      />
    </div>
  );
}
