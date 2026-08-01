"""The three derivations a map may perform, and nothing else (D-047).

``polygon_area_m2``  — pure geometry. No dataset, no inference, no uncertainty
                       beyond the user's own drawing.
``look_up_country``  — point-in-polygon against a public-domain boundary set.
                       Deterministic given the data.
``look_up_climate``  — an indexed read of a cited classification, resolved to
                       one of the tool's six zones by the methodology's own
                       documented mapping table.

Each returns the provenance of its own answer — the dataset it consulted and,
for climate, the Köppen class actually found — because a value the tool filled
in must be able to say where it came from when the report itemises it (D-047.2).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from nature_cooling.engine.config import MethodologyConfig
from nature_cooling.geo.datasets import (
    CountryBoundaries,
    KoppenGrid,
    Ring,
    load_countries,
    load_koppen,
)

# WGS 84 authalic (equal-area) mean radius, in metres. The authalic radius is
# the one to use when the quantity wanted is an area: it is defined as the
# radius of the sphere with the same surface area as the ellipsoid, so a
# spherical area formula evaluated on it carries no systematic bias.
EARTH_AUTHALIC_RADIUS_M = 6371007.181

# A drawn site boundary is a site, not a region. Beyond this the polygon is
# almost certainly a mis-click or a stray vertex, and passing it to the engine
# as `site_area_m2` would silently drive the scale-condition adjustment.
MAX_REASONABLE_SITE_AREA_M2 = 1.0e10  # 10 000 km²


# How far outside every boundary a point may sit and still be attributed to the
# nearest country. A generalised 1:50m coastline is drawn inland of the real
# one, so a great many coastal cities — Beirut, Nicosia, Manama, Kingston,
# Monaco, Hong Kong among them — fall in the sea by a few kilometres. Refusing
# to name a country for a waterfront site in Beirut would be precision the data
# does not have, in the direction of uselessness. Twenty-five kilometres is
# comfortably wider than that generalisation error and far narrower than any
# open-water distance, so a genuinely offshore point still returns nothing.
#
# This only ever runs when the point is inside NO country, so it cannot
# override a containment match or pick between two neighbours at a land border.
COASTAL_TOLERANCE_M = 25_000.0

EARTH_MEAN_RADIUS_M = 6371008.8


@dataclass(frozen=True)
class CountryLookup:
    """The country a point falls in, or the fact that none was found.

    ``matched`` records how the answer was reached: ``contains`` when the point
    is inside the boundary, ``nearest`` when it sat just outside one and was
    attributed to it, ``none`` when no country was identified.
    """

    iso_a2: str | None
    iso_a3: str | None
    name: str | None
    source_key: str
    attribution: str
    matched: str


@dataclass(frozen=True)
class ClimateLookup:
    """The climate zone a point classifies to, and the class it came from."""

    zone: str | None
    koppen_class: str | None
    koppen_index: int
    source_key: str
    attribution: str
    note: str
    resolution_caveat: str


@dataclass(frozen=True)
class SiteLookup:
    """Everything a map click can honestly say about a location."""

    latitude: float
    longitude: float
    country: CountryLookup
    climate: ClimateLookup
    site_area_m2: float | None


def _point_in_ring(longitude: float, latitude: float, ring: Ring) -> bool:
    """Ray-casting test: is the point inside this ring?

    Counts the ring edges crossed by a ray cast east from the point. An odd
    count means inside. Edges are compared half-open in latitude
    (``lat0 > lat`` differing from ``lat1 > lat``) so that a vertex lying
    exactly on the ray is counted once rather than twice or not at all.
    """
    inside = False
    count = len(ring)
    previous = ring[count - 1]
    for current in ring:
        lon0, lat0 = previous[0], previous[1]
        lon1, lat1 = current[0], current[1]
        if (lat0 > latitude) != (lat1 > latitude):
            crossing_lon = lon0 + (latitude - lat0) / (lat1 - lat0) * (lon1 - lon0)
            if longitude < crossing_lon:
                inside = not inside
        previous = current
    return inside


def _point_in_country(longitude: float, latitude: float, country: Any) -> bool:
    """Is the point inside any of a country's polygons, and outside its holes?"""
    min_lon, min_lat, max_lon, max_lat = country.bbox
    if not (min_lon <= longitude <= max_lon and min_lat <= latitude <= max_lat):
        return False
    for polygon in country.polygons:
        outer = polygon[0]
        if not _point_in_ring(longitude, latitude, outer):
            continue
        if any(_point_in_ring(longitude, latitude, hole) for hole in polygon[1:]):
            continue
        return True
    return False


def _segment_distance_m(
    longitude: float, latitude: float, start: list[float], end: list[float]
) -> float:
    """Distance from a point to a lon/lat segment, in metres.

    Works in a local equirectangular projection about the point — accurate well
    inside a tolerance measured in tens of kilometres, and free of the
    trigonometry a great-circle formula would spend on every edge of every
    country.
    """
    scale = math.cos(math.radians(latitude))
    metres_per_degree = math.pi * EARTH_MEAN_RADIUS_M / 180.0
    px = 0.0
    py = 0.0
    ax = (start[0] - longitude) * scale
    ay = start[1] - latitude
    bx = (end[0] - longitude) * scale
    by = end[1] - latitude

    dx = bx - ax
    dy = by - ay
    length_squared = dx * dx + dy * dy
    if length_squared == 0.0:
        nearest_x, nearest_y = ax, ay
    else:
        t = ((px - ax) * dx + (py - ay) * dy) / length_squared
        t = min(max(t, 0.0), 1.0)
        nearest_x, nearest_y = ax + t * dx, ay + t * dy
    return math.hypot(nearest_x, nearest_y) * metres_per_degree


def _distance_to_country_m(longitude: float, latitude: float, country: Any) -> float:
    """Shortest distance from a point to any of a country's outer rings."""
    best = math.inf
    for polygon in country.polygons:
        ring = polygon[0]
        previous = ring[-1]
        for current in ring:
            best = min(best, _segment_distance_m(longitude, latitude, previous, current))
            previous = current
    return best


def look_up_country(
    latitude: float,
    longitude: float,
    boundaries: CountryBoundaries | None = None,
) -> CountryLookup:
    """Identify the country containing a point, or the one it sits just outside."""
    data = boundaries or load_countries()

    def found(country: Any, matched: str) -> CountryLookup:
        return CountryLookup(
            iso_a2=country.iso_a2,
            iso_a3=country.iso_a3,
            name=country.name,
            source_key=data.source_key,
            attribution=data.attribution,
            matched=matched,
        )

    for country in data.countries:
        if _point_in_country(longitude, latitude, country):
            return found(country, "contains")

    # A point inside a territory the source carries no ISO code for is answered
    # "no country", definitively, and does not reach the coastal tolerance
    # below — which would otherwise hand a site in Northern Cyprus to Cyprus on
    # proximity alone, asserting by accident what the dataset build declined to
    # assert on purpose.
    for territory in data.unassigned:
        if _point_in_country(longitude, latitude, territory):
            return CountryLookup(
                iso_a2=None,
                iso_a3=None,
                name=None,
                source_key=data.source_key,
                attribution=data.attribution,
                matched="none",
            )

    # Inside nothing. Either the point is genuinely at sea or in a territory the
    # dataset carries no ISO code for, or it is a coastal site a few kilometres
    # outside a generalised coastline. Only the second is recoverable, and only
    # within a stated tolerance.
    tolerance_degrees = COASTAL_TOLERANCE_M / (math.pi * EARTH_MEAN_RADIUS_M / 180.0)
    nearest: tuple[float, Any] | None = None
    for country in data.countries:
        min_lon, min_lat, max_lon, max_lat = country.bbox
        if not (
            min_lon - tolerance_degrees <= longitude <= max_lon + tolerance_degrees
            and min_lat - tolerance_degrees <= latitude <= max_lat + tolerance_degrees
        ):
            continue
        distance = _distance_to_country_m(longitude, latitude, country)
        if distance <= COASTAL_TOLERANCE_M and (nearest is None or distance < nearest[0]):
            nearest = (distance, country)
    if nearest is not None:
        return found(nearest[1], "nearest")

    # No country identified. This is reported plainly and the user may type one;
    # it is never guessed at, and a site inside Northern Cyprus, Somaliland or
    # Kosovo reaches here by design rather than being assigned to the state that
    # claims it.
    return CountryLookup(
        iso_a2=None,
        iso_a3=None,
        name=None,
        source_key=data.source_key,
        attribution=data.attribution,
        matched="none",
    )


def koppen_class_at(latitude: float, longitude: float, grid: KoppenGrid) -> int:
    """Return the raw Köppen class index at a point, or the ocean value."""
    row = int((90.0 - latitude) / 180.0 * grid.rows)
    col = int((longitude + 180.0) / 360.0 * grid.cols)
    row = min(max(row, 0), grid.rows - 1)
    col = min(max(col, 0), grid.cols - 1)
    return grid.values[row * grid.cols + col]


def look_up_climate(
    latitude: float,
    longitude: float,
    config: MethodologyConfig,
    grid: KoppenGrid | None = None,
) -> ClimateLookup:
    """Classify a point, then resolve the class through the methodology table.

    The classification is the cited dataset's; the resolution onto the tool's
    six zones is the methodology's own value, declared in
    ``config/climate_classification.yaml`` with a rationale per branch.
    """
    data = grid or load_koppen()
    table = config.climate_classification["koppen_to_zone"]
    disclosure = table["disclosure"]

    index = koppen_class_at(latitude, longitude, data)
    if index == data.ocean_value:
        # A point at sea has no classification. It is left unfilled rather than
        # nudged to the nearest land cell: guessing which coast the user meant
        # would be inventing the answer, and climate_zone is required, so a
        # wrong guess here silently selects a row of the adjustment matrix.
        return ClimateLookup(
            zone=None,
            koppen_class=None,
            koppen_index=index,
            source_key=data.source_key,
            attribution=data.attribution,
            note=disclosure["autofill_note"],
            resolution_caveat=disclosure["resolution_caveat"],
        )

    koppen_class = data.classes[index]
    zone = str(table["classes"][koppen_class]["zone"])
    return ClimateLookup(
        zone=zone,
        koppen_class=koppen_class,
        koppen_index=index,
        source_key=data.source_key,
        attribution=data.attribution,
        note=disclosure["autofill_note"],
        resolution_caveat=disclosure["resolution_caveat"],
    )


def polygon_area_m2(ring: list[list[float]]) -> float:
    """Return the geodesic area of a closed lon/lat ring, in square metres.

    Uses the spherical excess of the polygon, evaluated on the authalic sphere.
    A planar formula would understate area away from the equator by roughly
    ``1 / cos(latitude)`` — 35% at 45° and more than half at 60° — which for an
    input that feeds the scale-condition adjustment is not a rounding error.

    The ring may be given closed or open; a repeated final point is ignored.
    """
    points = list(ring)
    if len(points) >= 2 and points[0] == points[-1]:
        points = points[:-1]
    if len(points) < 3:
        return 0.0

    total = 0.0
    count = len(points)
    for index, current in enumerate(points):
        following = points[(index + 1) % count]
        lon1, lat1 = math.radians(current[0]), math.radians(current[1])
        lon2, lat2 = math.radians(following[0]), math.radians(following[1])
        total += (lon2 - lon1) * (2.0 + math.sin(lat1) + math.sin(lat2))

    return abs(total * EARTH_AUTHALIC_RADIUS_M * EARTH_AUTHALIC_RADIUS_M / 2.0)


def look_up_site(
    latitude: float,
    longitude: float,
    config: MethodologyConfig,
    boundary: list[list[float]] | None = None,
    boundaries: CountryBoundaries | None = None,
    grid: KoppenGrid | None = None,
) -> SiteLookup:
    """Answer all three map-derivable questions for one location.

    ``boundary``, when given, is the polygon the user drew; its area is
    returned. When it is absent the user placed a point rather than drawing a
    site, and only country and climate zone are available.
    """
    area: float | None = None
    if boundary is not None:
        computed = polygon_area_m2(boundary)
        # Zero area means the drawing collapsed to a line or a point, and an
        # implausibly large one means it is not a site boundary. Neither is
        # offered as an answer; `site_area_m2` must be positive (models.py).
        if 0.0 < computed <= MAX_REASONABLE_SITE_AREA_M2:
            area = computed

    return SiteLookup(
        latitude=latitude,
        longitude=longitude,
        country=look_up_country(latitude, longitude, boundaries),
        climate=look_up_climate(latitude, longitude, config, grid),
        site_area_m2=area,
    )
