"""Unit tests for the derived site adjustment factor (Methodology Report 5.4)."""

from __future__ import annotations

import pytest

from nature_cooling.engine.scoring import adjustment


def _typology(config, nbs_type="street_tree_planting"):
    return config.typologies.by_type(nbs_type)


def test_worked_example_factor(config, build_input):
    """Hand-derived: 0.40*1.0 + 0.25*0.8 + 0.20*1.0 + 0.15*1.0 = 0.95."""
    inp = build_input(
        existing_tree_canopy_percent=8,
        new_canopy_area_at_maturity_m2=1200,
        soil_availability="limited",
        irrigation_availability="occasional",
    )
    block, assumptions = adjustment.compute(inp, _typology(config), config)
    assert block.factor == 0.95
    assert block.canopy.level == "good"
    assert block.canopy.detail == "combined canopy at maturity: 28.0% of site"
    assert block.soil_water.level == "moderate"
    assert block.scale.level == "good"
    assert block.climate.level == "good"
    assert assumptions == []


@pytest.mark.parametrize(
    ("existing", "new_area", "expected_level"),
    [
        (0, 0, "poor"),  # 0% < 10%
        (5, 300, "moderate"),  # 5 + 5 = 10%, lower edge of moderate
        (10, 900, "good"),  # 10 + 15 = 25%, lower edge of good
        (20, 1200, "excellent"),  # 20 + 20 = 40%, the ziter2019 inflection
        (50, 3000, "excellent"),  # 100%
    ],
)
def test_canopy_thresholds(config, build_input, existing, new_area, expected_level):
    inp = build_input(
        existing_tree_canopy_percent=existing, new_canopy_area_at_maturity_m2=new_area
    )
    block, _ = adjustment.compute(inp, _typology(config), config)
    assert block.canopy.level == expected_level


def test_canopy_unknown_when_any_input_missing(config, build_input):
    block, assumptions = adjustment.compute(
        build_input(existing_tree_canopy_percent=8), _typology(config), config
    )
    assert block.canopy.level == "unknown"
    assert block.canopy.factor == 1.0
    assert assumptions[0] == (
        "canopy condition set to 'unknown' (factor 1.0): "
        "new_canopy_area_at_maturity_m2 not provided"
    )


def test_soil_water_takes_the_more_limiting(config, build_input):
    inp = build_input(soil_availability="high", irrigation_availability="none")
    block, _ = adjustment.compute(inp, _typology(config), config)
    assert block.soil_water.level == "poor"


def test_soil_water_reliable_irrigation_reaches_excellent(config, build_input):
    """D-026: the best honest answers yield excellent; reliable no longer caps."""
    inp = build_input(soil_availability="high", irrigation_availability="reliable")
    block, assumptions = adjustment.compute(inp, _typology(config), config)
    assert block.soil_water.level == "excellent"
    assert not any("soil-water" in note for note in assumptions)


def test_soil_water_unknown_partner_caps_at_neutral(config, build_input):
    """D-026: a pair containing an unknown never exceeds the neutral factor,
    so silence can never beat the best honest answer."""
    soil_only, assumptions = adjustment.compute(
        build_input(soil_availability="high"), _typology(config), config
    )
    assert soil_only.soil_water.level == "good"
    assert soil_only.soil_water.factor == 1.0
    assert any(
        "soil-water condition capped at 'good': irrigation_availability not provided" in note
        for note in assumptions
    )

    irrigation_only, _ = adjustment.compute(
        build_input(irrigation_availability="reliable"), _typology(config), config
    )
    assert irrigation_only.soil_water.level == "good"


def test_soil_water_cap_not_noted_when_not_binding(config, build_input):
    """A known level at or below the cap passes through without a cap note."""
    block, assumptions = adjustment.compute(
        build_input(soil_availability="limited"), _typology(config), config
    )
    assert block.soil_water.level == "moderate"
    assert not any("capped" in note for note in assumptions)


def test_soil_water_unknown_when_both_missing(config, build_input):
    block, assumptions = adjustment.compute(
        build_input(soil_availability="unknown"), _typology(config), config
    )
    assert block.soil_water.level == "unknown"
    assert len(assumptions) == 2  # canopy note + soil-water note
    assert "soil-water condition set to 'unknown'" in assumptions[1]


@pytest.mark.parametrize(
    ("scale", "expected"),
    [
        ("city", "excellent"),
        ("district", "excellent"),
        ("neighbourhood", "good"),
        ("site", "moderate"),
        ("building", "moderate"),
    ],
)
def test_scale_condition(config, build_input, scale, expected):
    block, _ = adjustment.compute(build_input(assessment_scale=scale), _typology(config), config)
    assert block.scale.level == expected


@pytest.mark.parametrize(
    ("zone", "nbs_type", "expected"),
    [
        ("tropical_wet", "blue_green_corridor", "moderate"),  # humidity caveat
        ("tropical_dry", "blue_green_corridor", "excellent"),
        ("arid", "street_tree_planting", "moderate"),  # water limitation
        ("arid", "permeable_shaded_plaza", "good"),
        ("semi_arid", "green_roof", "good"),
        ("temperate", "street_tree_planting", "good"),
        ("other", "street_tree_planting", "unknown"),
    ],
)
def test_climate_matrix(config, build_input, zone, nbs_type, expected):
    inp = build_input(climate_zone=zone, nbs_type=nbs_type)
    block, _ = adjustment.compute(inp, _typology(config, nbs_type), config)
    assert block.climate.level == expected


def test_factor_bounds_all_poor_and_all_excellent(config, build_input):
    """The factor attains 0.5 and 1.2 only at the extremes."""
    worst = build_input(
        existing_tree_canopy_percent=0,
        new_canopy_area_at_maturity_m2=0,
        soil_availability="none",
        irrigation_availability="none",
        assessment_scale="site",
        climate_zone="arid",
    )
    block, _ = adjustment.compute(worst, _typology(config), config)
    # 0.40*0.5 + 0.25*0.5 + 0.20*0.8 + 0.15*0.8 = 0.605
    assert block.factor == 0.605

    best = build_input(
        existing_tree_canopy_percent=45,
        new_canopy_area_at_maturity_m2=0,
        soil_availability="high",
        irrigation_availability="reliable",
        assessment_scale="city",
        climate_zone="tropical_dry",
        nbs_type="riparian_restoration",
    )
    block, _ = adjustment.compute(best, _typology(config, "riparian_restoration"), config)
    assert block.factor == 1.2
