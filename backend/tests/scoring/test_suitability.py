"""Unit tests for the NbS Suitability Score and hard flags (D-009, D-022)."""

from __future__ import annotations

import pytest

from nature_cooling.engine.config import Availability, Suitability, Typology
from nature_cooling.engine.scoring import suitability


def _typology(config, nbs_type="tree_avenue"):
    return config.typologies.by_type(nbs_type)


def test_worked_example(config, build_input):
    """Hand-derived: 0.30*100 + 0.25*75 + 0.20*75 + 0.15*50 + 0.10*50 = 76.25."""
    inp = build_input(soil_availability="limited", irrigation_availability="occasional")
    block, assumptions = suitability.compute(inp, _typology(config), config)
    assert block.score == 76.25
    assert (block.space, block.soil, block.water) == (100.0, 75.0, 75.0)
    assert (block.maintenance, block.urban_context) == (50.0, 50.0)
    assert block.flags == []
    assert block.suitable is True
    assert len(assumptions) == 2  # maintenance and land use defaulted


@pytest.mark.parametrize(
    ("site_area", "expected_score", "flagged"),
    [
        (99, 25.0, True),  # below the 100 m2 minimum
        (100, 50.0, False),  # exactly the minimum
        (150, 50.0, False),
        (200, 75.0, False),  # twofold margin
        (450, 75.0, False),
        (500, 100.0, False),  # fivefold margin
    ],
)
def test_space_brackets(config, build_input, site_area, expected_score, flagged):
    block, _ = suitability.compute(build_input(site_area_m2=site_area), _typology(config), config)
    assert block.space == expected_score
    assert any(flag.code == "below_minimum_area" for flag in block.flags) == flagged


def test_below_minimum_area_flag_message(config, build_input):
    block, _ = suitability.compute(
        build_input(site_area_m2=400, nbs_type=["river_restoration"]),
        _typology(config, "river_restoration"),
        config,
    )
    assert block.suitable is False
    assert block.flags[0].message == (
        "site area 400 m2 is below the minimum viable area of 1000 m2 for River Restoration"
    )


def test_soil_below_requirement_flags(config, build_input):
    """Urban woodland requires moderate soil; limited soil disqualifies."""
    block, _ = suitability.compute(
        build_input(
            site_area_m2=5000, nbs_type=["urban_woodland_site"], soil_availability="limited"
        ),
        _typology(config, "urban_woodland_site"),
        config,
    )
    assert block.soil == 25.0
    assert any(flag.code == "insufficient_soil" for flag in block.flags)


def test_soil_no_requirement_scores_full(config, build_input):
    """Green roof requires no soil: full score whatever the site offers."""
    block, _ = suitability.compute(
        build_input(nbs_type=["extensive_green_roof"], soil_availability="none"),
        _typology(config, "extensive_green_roof"),
        config,
    )
    assert block.soil == 100.0


def test_soil_exceeds_requirement(config, build_input):
    block, _ = suitability.compute(build_input(soil_availability="high"), _typology(config), config)
    assert block.soil == 100.0


def test_irrigation_below_requirement_flags(config, build_input):
    """Green facade requires reliable irrigation; occasional disqualifies."""
    block, _ = suitability.compute(
        build_input(
            nbs_type=["indirect_ground_rooted_green_facade"], irrigation_availability="occasional"
        ),
        _typology(config, "indirect_ground_rooted_green_facade"),
        config,
    )
    assert block.water == 25.0
    assert any(flag.code == "insufficient_irrigation" for flag in block.flags)


def test_unknown_availability_never_flags(config, build_input):
    """Absent information must not assert a disqualification."""
    block, assumptions = suitability.compute(
        build_input(nbs_type=["indirect_ground_rooted_green_facade"]),
        _typology(config, "indirect_ground_rooted_green_facade"),
        config,
    )
    assert block.water == 50.0
    assert block.flags == []
    assert any("irrigation_availability" in note for note in assumptions)


def test_maintenance_low_scores_high(config, build_input):
    block, _ = suitability.compute(
        build_input(maintenance_intensity="low"), _typology(config), config
    )
    assert block.maintenance == 100.0


def test_urban_context_match_and_mismatch(config, build_input):
    """D-022: the entry's own availability land-use list IS its use context.

    A tree avenue is offered in a street corridor and not in a school ground,
    so the same entry scores full marks on the one and out-of-context on the
    other.
    """
    matched, _ = suitability.compute(
        build_input(land_use="street_corridor"), _typology(config), config
    )
    assert matched.urban_context == 100.0
    mismatched, _ = suitability.compute(build_input(land_use="school"), _typology(config), config)
    assert mismatched.urban_context == 25.0


def test_unsuitable_climate_zone_flag(config, build_input):
    """No shipped typology declares one; verify the rule with a synthetic typology."""
    typology = Typology(
        nbs_id="99",
        nbs_type="synthetic",
        display_name="Synthetic",
        family="synthetic",
        kind="element",
        archetype="synthetic_archetype",
        archetype_display_name="Synthetic archetype",
        evidence_provenance="new",
        category="green",
        base_cooling_score=50,
        temp_reduction_min_c=0.1,
        temp_reduction_max_c=1.0,
        evidence_confidence="low",
        primary_cooling_mechanism="none",
        building_energy_applicable=False,
        typical_use_context=["park"],
        availability=Availability(scales=["site"], land_uses=["park"]),
        suitability_inherited=True,
        suitability=Suitability(
            minimum_site_area_m2=10,
            requires_soil="none",
            requires_irrigation="none",
            unsuitable_climate_zones=["arid"],
        ),
        co_benefit_defaults={},
        sources=[{"key": "bowler2010", "finding": "test"}],
    )
    block, _ = suitability.compute(build_input(climate_zone="arid"), typology, config)
    assert any(flag.code == "unsuitable_climate" for flag in block.flags)
    assert block.suitable is False
