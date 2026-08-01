"""The three derivations a map may perform (D-047, v2.1).

The contract under test is as much about what does NOT happen as what does.
Only three inputs are derivable; a location that cannot be classified is left
unfilled rather than guessed at; a territory the boundary set carries no ISO
code for is answered "no country" rather than assigned to a claimant; and
Köppen classes with no urban-heat counterpart resolve to ``other``, not to
``temperate`` (D-047.3).

Expected values are derived from the published sources — the Köppen legend and
the ISO codes of well-known cities — never recorded from this code's own
output.
"""

from __future__ import annotations

import json
import zlib
from pathlib import Path

import pytest

from nature_cooling.engine.config import default_geo_data_dir
from nature_cooling.geo import (
    GeoDataError,
    load_basemap,
    load_countries,
    load_koppen,
    look_up_site,
    polygon_area_m2,
)
from nature_cooling.geo.datasets import _countries_from
from nature_cooling.geo.lookup import (
    COASTAL_TOLERANCE_M,
    EARTH_AUTHALIC_RADIUS_M,
    MAX_REASONABLE_SITE_AREA_M2,
    _point_in_country,
    koppen_class_at,
    look_up_climate,
    look_up_country,
)

# --- The bundled datasets ----------------------------------------------------


def test_the_country_layer_loads_and_covers_the_world() -> None:
    boundaries = load_countries()
    assert boundaries.scale == "1:50m"
    assert boundaries.source_key == "naturalearth"
    assert boundaries.licence == "public domain"
    # Every UN member state and then some; the exact count is the source's.
    assert len(boundaries.countries) > 190
    for country in boundaries.countries:
        assert len(country.iso_a2) == 2, country.name
        assert len(country.iso_a3) == 3, country.name
    # A country may appear as several features — Australia carries its Indian
    # Ocean territories separately — which is the source's structure and costs
    # the lookup nothing, since each feature keeps its own bounding box.
    assert {country.iso_a2 for country in boundaries.countries} >= {"GR", "US", "SG", "MT"}


def test_the_climate_grid_loads_at_the_published_shape_and_legend() -> None:
    grid = load_koppen()
    assert (grid.rows, grid.cols) == (1800, 3600), "0.1 degrees over the whole globe"
    assert len(grid.values) == grid.rows * grid.cols
    assert grid.period == "1991-2020"
    assert grid.licence == "CC BY 4.0"
    assert grid.source_key == "beck2023"
    # The published legend is 30 classes; 0 is ocean, not a class.
    assert len(grid.classes) == 30
    assert grid.classes[1] == "Af"
    assert grid.classes[30] == "EF"
    assert grid.ocean_value == 0


def test_the_basemap_layer_is_the_coarser_scale_and_carries_no_attributes() -> None:
    """The browser draws outlines at world zoom and interprets nothing."""
    basemap = load_basemap()
    assert basemap["scale"] == "1:110m"
    for entry in basemap["countries"]:
        assert set(entry) == {"iso_a2", "polygons"}


def test_a_missing_dataset_is_reported_not_guessed_at(tmp_path: Path) -> None:
    load_countries.cache_clear()
    try:
        with pytest.raises(GeoDataError, match="missing bundled geographic dataset"):
            load_countries(tmp_path)
    finally:
        load_countries.cache_clear()


def test_a_corrupt_compressed_dataset_is_reported(tmp_path: Path) -> None:
    (tmp_path / "countries.json.z").write_bytes(b"not zlib")
    load_countries.cache_clear()
    try:
        with pytest.raises(GeoDataError, match="corrupt compressed dataset"):
            load_countries(tmp_path)
    finally:
        load_countries.cache_clear()


def test_invalid_json_is_reported(tmp_path: Path) -> None:
    (tmp_path / "basemap.json").write_text("{not json", encoding="utf-8")
    load_basemap.cache_clear()
    try:
        with pytest.raises(GeoDataError, match="invalid JSON"):
            load_basemap(tmp_path)
    finally:
        load_basemap.cache_clear()


def test_a_json_document_that_is_not_an_object_is_reported(tmp_path: Path) -> None:
    (tmp_path / "basemap.json").write_text("[1, 2]", encoding="utf-8")
    load_basemap.cache_clear()
    try:
        with pytest.raises(GeoDataError, match="must contain a JSON object"):
            load_basemap(tmp_path)
    finally:
        load_basemap.cache_clear()


def test_an_empty_basemap_is_refused(tmp_path: Path) -> None:
    (tmp_path / "basemap.json").write_text('{"countries": []}', encoding="utf-8")
    load_basemap.cache_clear()
    try:
        with pytest.raises(GeoDataError, match="declares no outlines"):
            load_basemap(tmp_path)
    finally:
        load_basemap.cache_clear()


def test_a_country_layer_declaring_no_countries_is_refused(tmp_path: Path) -> None:
    with pytest.raises(GeoDataError, match="declares no countries"):
        _countries_from({"countries": []}, tmp_path / "countries.json.z")


def test_a_grid_whose_bytes_contradict_its_metadata_is_refused(tmp_path: Path) -> None:
    """A truncated grid must fail loudly, not index into whatever is there."""
    meta = json.loads((default_geo_data_dir() / "koppen_geiger.json").read_text(encoding="utf-8"))
    (tmp_path / "koppen_geiger.json").write_text(json.dumps(meta), encoding="utf-8")
    (tmp_path / meta["grid_file"]).write_bytes(zlib.compress(b"\x00" * 10))
    load_koppen.cache_clear()
    try:
        with pytest.raises(GeoDataError, match="decompressed to 10 bytes"):
            load_koppen(tmp_path)
    finally:
        load_koppen.cache_clear()


def test_a_missing_grid_file_is_reported(tmp_path: Path) -> None:
    meta = json.loads((default_geo_data_dir() / "koppen_geiger.json").read_text(encoding="utf-8"))
    (tmp_path / "koppen_geiger.json").write_text(json.dumps(meta), encoding="utf-8")
    load_koppen.cache_clear()
    try:
        with pytest.raises(GeoDataError, match="missing bundled climate grid"):
            load_koppen(tmp_path)
    finally:
        load_koppen.cache_clear()


def test_a_corrupt_grid_is_reported(tmp_path: Path) -> None:
    meta = json.loads((default_geo_data_dir() / "koppen_geiger.json").read_text(encoding="utf-8"))
    (tmp_path / "koppen_geiger.json").write_text(json.dumps(meta), encoding="utf-8")
    (tmp_path / meta["grid_file"]).write_bytes(b"not zlib either")
    load_koppen.cache_clear()
    try:
        with pytest.raises(GeoDataError, match="corrupt climate grid"):
            load_koppen(tmp_path)
    finally:
        load_koppen.cache_clear()


# --- Country identification --------------------------------------------------

# Cities whose country is not in dispute. The expected code is the ISO 3166-1
# alpha-2 of the state the city is in, not anything this code produced.
CONTAINED_CITIES = [
    ("Athens", 37.9838, 23.7275, "GR"),
    ("Chicago", 41.8781, -87.6298, "US"),
    ("Cairo", 30.0444, 31.2357, "EG"),
    ("Tokyo", 35.6762, 139.6503, "JP"),
    ("Lima", -12.0464, -77.0428, "PE"),
    ("Nairobi", -1.2921, 36.8219, "KE"),
    ("Reykjavik", 64.1466, -21.9426, "IS"),
    ("Melbourne", -37.8136, 144.9631, "AU"),
    ("Singapore", 1.3521, 103.8198, "SG"),
    ("Valletta", 35.8989, 14.5146, "MT"),
]


@pytest.mark.parametrize(("name", "latitude", "longitude", "expected"), CONTAINED_CITIES)
def test_a_city_resolves_to_its_own_country(
    name: str, latitude: float, longitude: float, expected: str
) -> None:
    found = look_up_country(latitude, longitude)
    assert found.iso_a2 == expected, name
    assert found.matched == "contains"
    assert found.iso_a3 is not None


def test_a_microstate_is_not_swallowed_by_its_neighbour() -> None:
    """The lookup layer is 1:50m for exactly this reason.

    At 1:110m Natural Earth omits every country below roughly a thousand square
    kilometres, so Singapore resolved to Malaysia — a wrong country stated
    confidently, which is worse than no country, and wrong for precisely the
    dense hot cities this tool serves.
    """
    assert look_up_country(1.3521, 103.8198).iso_a2 == "SG"


# A generalised coastline is drawn inland of the real one, so these waterfront
# capitals fall in the sea. The expected code is the country they are in.
COASTAL_CITIES = [
    ("Beirut", 33.8938, 35.5018, "LB"),
    ("Manama", 26.2285, 50.5860, "BH"),
    ("Kingston", 17.9714, -76.7931, "JM"),
    ("Monaco", 43.7384, 7.4246, "MC"),
    ("Hong Kong", 22.3193, 114.1694, "HK"),
]


@pytest.mark.parametrize(("name", "latitude", "longitude", "expected"), COASTAL_CITIES)
def test_a_waterfront_site_is_attributed_to_the_coast_it_sits_on(
    name: str, latitude: float, longitude: float, expected: str
) -> None:
    found = look_up_country(latitude, longitude)
    assert found.iso_a2 == expected, name
    assert found.matched == "nearest", "and the lookup says so rather than implying containment"


def test_open_ocean_yields_no_country_at_all() -> None:
    """The coastal tolerance is narrower than any open-water distance."""
    for latitude, longitude in ((30.0, -40.0), (0.0, -150.0), (-40.0, 80.0)):
        found = look_up_country(latitude, longitude)
        assert found.iso_a2 is None
        assert found.matched == "none"


@pytest.mark.parametrize(
    ("name", "latitude", "longitude"),
    [
        ("Northern Cyprus", 35.33, 33.48),
        ("Somaliland", 9.56, 44.07),
        ("Kosovo", 42.66, 21.16),
    ],
)
def test_a_territory_with_no_iso_code_is_answered_no_country(
    name: str, latitude: float, longitude: float
) -> None:
    """Not assigned to the state that claims it, and not left to the coastal
    tolerance to hand over by proximity either.

    The outlines are kept as explicit exclusion zones for this reason: deleting
    them would leave holes that the nearest-country fallback then filled,
    reintroducing through an accident exactly the claim the dataset build
    declined to make on purpose.
    """
    found = look_up_country(latitude, longitude)
    assert found.iso_a2 is None, name
    assert found.matched == "none"


def test_the_coastal_tolerance_is_stated_in_kilometres_not_degrees() -> None:
    """A tolerance in degrees would be six times looser at 80° than at 0°."""
    assert COASTAL_TOLERANCE_M == 25_000.0


# --- Climate classification --------------------------------------------------

# City, coordinates, the Köppen class published for it, and the zone this
# methodology's table resolves that class to.
CLIMATE_CITIES = [
    ("Singapore", 1.3521, 103.8198, "Af", "tropical_wet"),
    ("Miami", 25.7617, -80.1918, "Am", "tropical_wet"),
    ("Cairo", 30.0444, 31.2357, "BWh", "arid"),
    ("Denver", 39.7392, -104.9903, "Dfa", "temperate"),
    ("Beijing", 39.9042, 116.4074, "BSk", "semi_arid"),
    ("Khartoum", 15.5007, 32.5599, "BWh", "arid"),
    ("Lagos", 6.5244, 3.3792, "Aw", "tropical_dry"),
    ("Ulaanbaatar", 47.8864, 106.9057, "Dwc", "other"),
    ("Athens", 37.9838, 23.7275, "Csa", "temperate"),
    ("London", 51.5074, -0.1278, "Cfb", "temperate"),
    ("Chicago", 41.8781, -87.6298, "Dfa", "temperate"),
    ("Moscow", 55.7558, 37.6173, "Dfb", "temperate"),
    ("Reykjavik", 64.1466, -21.9426, "Cfc", "other"),
    ("Nuuk", 64.1835, -51.7216, "ET", "other"),
]


@pytest.mark.parametrize(("name", "latitude", "longitude", "koppen", "zone"), CLIMATE_CITIES)
def test_a_city_classifies_to_its_published_koppen_class_and_mapped_zone(
    name: str, latitude: float, longitude: float, koppen: str, zone: str, config
) -> None:
    found = look_up_climate(latitude, longitude, config)
    assert found.koppen_class == koppen, name
    assert found.zone == zone, name
    assert found.source_key == "beck2023"


def test_a_continental_city_with_a_hot_summer_stays_temperate(config) -> None:
    """D-047.3 sends the classes with no urban-heat counterpart to ``other``.

    It does not send group D there wholesale, and this is the test that stops a
    later simplification from doing so: Chicago, Beijing and Moscow have real
    urban heat problems and sit squarely inside the evidence base behind the
    temperate row.
    """
    for name, latitude, longitude, koppen in (
        ("Chicago", 41.8781, -87.6298, "Dfa"),
        ("Seoul", 37.5665, 126.9780, "Dwa"),
        ("Moscow", 55.7558, 37.6173, "Dfb"),
    ):
        found = look_up_climate(latitude, longitude, config)
        assert found.koppen_class == koppen, name
        assert found.zone == "temperate", name


def test_a_polar_site_maps_to_other_and_never_to_temperate(config) -> None:
    """Forcing ET into temperate would assert that a tundra site cools like a
    temperate one, which no source in the bibliography supports (D-047.3)."""
    found = look_up_climate(64.1835, -51.7216, config)
    assert found.koppen_class == "ET"
    assert found.zone == "other"


def test_other_resolves_to_the_neutral_adjustment_factor(config) -> None:
    """The reason ``other`` is the honest destination: it neither boosts nor
    penalises a site the classification cannot speak to."""
    factors = config.adjustment_factors["condition_factors"]
    matrix = config.adjustment_factors["derivation"]["climate_condition"]["matrix"]
    for family, condition in matrix["other"].items():
        assert factors[condition] == 1.0, family


def test_a_point_at_sea_is_left_unclassified_rather_than_nudged_ashore(config) -> None:
    """``climate_zone`` is required, so a wrong guess here silently selects a
    row of the adjustment matrix. Better to fill nothing in."""
    found = look_up_climate(30.0, -40.0, config)
    assert found.zone is None
    assert found.koppen_class is None


def test_every_published_class_has_exactly_one_mapped_zone(config) -> None:
    """The table must cover the legend, or a real location classifies to nothing."""
    grid = load_koppen()
    table = config.climate_classification["koppen_to_zone"]["classes"]
    assert set(table) == set(grid.classes.values())
    zones = {"tropical_wet", "tropical_dry", "arid", "semi_arid", "temperate", "other"}
    for name, entry in table.items():
        assert entry["zone"] in zones, name
        assert grid.classes[entry["index"]] == name, "index must match the published legend"


def test_the_mapping_follows_its_stated_rule_rather_than_thirty_opinions(config) -> None:
    """Each assignment must follow from the branch it names.

    A thirty-row table of separate judgements could not be reviewed. This test
    is what makes the rule in ``climate_classification.yaml`` load-bearing: it
    re-derives every row from the stated principle and fails if one drifts.
    """
    table = config.climate_classification["koppen_to_zone"]["classes"]
    for name, entry in table.items():
        group = name[0]
        if group == "A":
            expected = "tropical_wet" if name in {"Af", "Am"} else "tropical_dry"
            branch = "tropical"
        elif group == "B":
            expected = "arid" if name[1] == "W" else "semi_arid"
            branch = "arid"
        elif group == "E":
            expected, branch = "other", "no_warm_season"
        elif name[2] in {"a", "b"}:
            expected, branch = "temperate", "warm_season"
        else:
            expected, branch = "other", "no_warm_season"
        assert entry["zone"] == expected, f"{name} does not follow the {branch} branch"
        assert entry["branch"] == branch, name


def test_the_grid_is_indexed_north_west_first(config) -> None:
    """An inverted row or column would classify the whole world plausibly and
    wrongly, which is the failure a spot check of one city would miss."""
    grid = load_koppen()
    # The north-west corner of the grid is Arctic ocean; the Sahara is land.
    assert koppen_class_at(89.9, -179.9, grid) == grid.ocean_value
    assert grid.classes[koppen_class_at(23.0, 13.0, grid)] == "BWh"
    # Antarctica is frost, and it is at the bottom of the grid, not the top.
    assert grid.classes[koppen_class_at(-82.0, 0.0, grid)] == "EF"


def test_grid_indices_are_clamped_at_the_poles_and_the_date_line(config) -> None:
    grid = load_koppen()
    for latitude, longitude in ((90.0, 180.0), (-90.0, -180.0)):
        assert 0 <= koppen_class_at(latitude, longitude, grid) <= 30


# --- Polygon area ------------------------------------------------------------


def test_area_is_geodesic_and_shrinks_with_latitude() -> None:
    """A planar formula would overstate a high-latitude site by 1/cos(lat) —
    35% at 45° and more than half at 60° — for an input that drives the
    scale-condition adjustment."""
    import math

    def square(latitude: float, side: float) -> list[list[float]]:
        return [
            [0.0, latitude],
            [side, latitude],
            [side, latitude + side],
            [0.0, latitude + side],
            [0.0, latitude],
        ]

    # Closed form for a lon/lat rectangle: R^2 * dlon * (sin lat2 - sin lat1).
    def band(latitude: float, side: float) -> float:
        radius = EARTH_AUTHALIC_RADIUS_M
        return (
            radius
            * radius
            * math.radians(side)
            * (math.sin(math.radians(latitude + side)) - math.sin(math.radians(latitude)))
        )

    for latitude in (0.0, 45.0, 60.0):
        assert polygon_area_m2(square(latitude, 0.01)) == pytest.approx(
            band(latitude, 0.01), rel=1e-6
        )

    # And the point of it: the same drawing is materially smaller at 60 degrees.
    assert polygon_area_m2(square(60.0, 0.01)) < 0.51 * polygon_area_m2(square(0.0, 0.01))


def test_a_one_degree_square_at_the_equator_matches_the_closed_form() -> None:
    """Checked against the spherical-cap formula, not against this code."""
    import math

    ring = [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0]]
    radius = EARTH_AUTHALIC_RADIUS_M
    expected = math.radians(1.0) * radius * radius * math.sin(math.radians(1.0))
    assert polygon_area_m2(ring) == pytest.approx(expected, rel=1e-6)


def test_area_is_independent_of_winding_direction() -> None:
    clockwise = [[0.0, 0.0], [0.0, 0.01], [0.01, 0.01], [0.01, 0.0]]
    anticlockwise = list(reversed(clockwise))
    assert polygon_area_m2(clockwise) == pytest.approx(polygon_area_m2(anticlockwise))


def test_an_unclosed_ring_measures_the_same_as_a_closed_one() -> None:
    open_ring = [[0.0, 0.0], [0.01, 0.0], [0.01, 0.01], [0.0, 0.01]]
    closed_ring = [*open_ring, [0.0, 0.0]]
    assert polygon_area_m2(open_ring) == pytest.approx(polygon_area_m2(closed_ring))


def test_a_degenerate_ring_has_no_area() -> None:
    assert polygon_area_m2([]) == 0.0
    assert polygon_area_m2([[0.0, 0.0]]) == 0.0
    assert polygon_area_m2([[0.0, 0.0], [1.0, 1.0]]) == 0.0
    assert polygon_area_m2([[0.0, 0.0], [1.0, 1.0], [0.0, 0.0]]) == 0.0


# --- The whole lookup --------------------------------------------------------


def test_a_drawn_polygon_yields_all_three_derivable_inputs(config) -> None:
    """Athens, with a boundary drawn round a city block."""
    boundary = [
        [23.7275, 37.9838],
        [23.7285, 37.9838],
        [23.7285, 37.9848],
        [23.7275, 37.9848],
    ]
    site = look_up_site(37.9838, 23.7275, config, boundary=boundary)
    assert site.country.iso_a2 == "GR"
    assert site.climate.zone == "temperate"
    assert site.site_area_m2 is not None
    # Roughly 88 m x 111 m at this latitude.
    assert 8_000 < site.site_area_m2 < 12_000


def test_a_placed_point_yields_country_and_climate_but_no_area(config) -> None:
    """The user placed a point rather than drawing a site; area is not invented."""
    site = look_up_site(37.9838, 23.7275, config)
    assert site.country.iso_a2 == "GR"
    assert site.climate.zone == "temperate"
    assert site.site_area_m2 is None


def test_a_collapsed_drawing_offers_no_area(config) -> None:
    """``site_area_m2`` must be positive, so zero is never offered as an answer."""
    line = [[23.7275, 37.9838], [23.7285, 37.9848], [23.7275, 37.9838]]
    assert look_up_site(37.9838, 23.7275, config, boundary=line).site_area_m2 is None


def test_an_implausibly_large_drawing_offers_no_area(config) -> None:
    """A polygon spanning a subcontinent is a mis-click, not a site boundary,
    and would silently drive the scale-condition adjustment."""
    huge = [[0.0, 0.0], [30.0, 0.0], [30.0, 30.0], [0.0, 30.0]]
    assert polygon_area_m2(huge) > MAX_REASONABLE_SITE_AREA_M2
    assert look_up_site(15.0, 15.0, config, boundary=huge).site_area_m2 is None


def test_the_lookup_carries_the_attribution_its_licences_require(config) -> None:
    """CC BY 4.0 requires attribution, and it must travel with the value."""
    site = look_up_site(37.9838, 23.7275, config)
    assert "Beck" in site.climate.attribution
    assert "CC BY 4.0" in site.climate.attribution
    assert "Natural Earth" in site.country.attribution
    assert site.climate.note
    assert "11 km" in site.climate.resolution_caveat


def test_an_enclave_is_its_own_country_and_not_the_state_around_it() -> None:
    """Lesotho is a hole in South Africa's outer ring, and holes are subtracted.

    Without the hole test a point in Maseru would resolve to South Africa —
    inside the outer boundary, and wrong. The same shape arises for San Marino
    and the Vatican inside Italy.
    """
    boundaries = load_countries()
    south_africa = next(c for c in boundaries.countries if c.iso_a2 == "ZA")
    assert any(len(polygon) > 1 for polygon in south_africa.polygons), "ZA must carry a hole"

    # Asserted against South Africa directly, not through the whole lookup:
    # "LS" sorts before "ZA", so a scan of every country would answer Lesotho
    # before it ever reached the hole, and the test would pass while the hole
    # subtraction was broken.
    maseru_longitude, maseru_latitude = 27.4869, -29.3151
    assert not _point_in_country(maseru_longitude, maseru_latitude, south_africa)

    pretoria_longitude, pretoria_latitude = 28.2293, -25.7479
    assert _point_in_country(pretoria_longitude, pretoria_latitude, south_africa)

    found = look_up_country(maseru_latitude, maseru_longitude)
    assert found.iso_a2 == "LS"
    assert found.matched == "contains"
