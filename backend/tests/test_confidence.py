"""Unit tests for branched confidence (6.2, D-011/OQ-09, D-024)."""

from __future__ import annotations

from nature_cooling.engine import confidence


def _typology(config, nbs_type="street_tree_planting"):
    return config.typologies.by_type(nbs_type)


def test_worked_example_blocks(config, build_input):
    """Cooling 8/10 -> high; energy 2/3 -> medium; economic 0/4 -> low;
    equity 3/6 -> medium; overall lower median -> medium."""
    inp = build_input(
        existing_tree_canopy_percent=8,
        existing_green_cover_percent=12,
        impervious_surface_percent=85,
        soil_availability="limited",
        irrigation_availability="occasional",
        lst_anomaly_c=4.2,
        solar_exposure="high",
        new_canopy_area_at_maturity_m2=1200,
        population_density="high",
        vulnerable_population_presence="high",
        access_to_cooled_indoor_space="low",
        nearby_building_cooling_demand_relevant="yes",
        annual_cooling_energy_demand_kwh=450000,
    )
    block = confidence.compute(inp, _typology(config), config)
    assert block.completeness_percent == {
        "cooling": 80.0,
        "energy": 66.7,
        "economic": 0.0,
        "equity": 50.0,
    }
    assert (block.cooling, block.energy, block.economic, block.equity) == (
        "high",
        "medium",
        "low",
        "medium",
    )
    assert block.overall == "medium"
    assert block.cooling_capped_by_evidence is False


def test_alternative_fields_fill_one_slot(config, build_input):
    """Supplying both LST and the qualitative level fills the same single slot."""
    only_level = confidence.compute(
        build_input(heat_exposure_level="high"), _typology(config), config
    )
    both = confidence.compute(
        build_input(heat_exposure_level="high", lst_anomaly_c=4.0), _typology(config), config
    )
    assert only_level.completeness_percent["cooling"] == 10.0
    assert both.completeness_percent["cooling"] == 10.0


def test_unknown_counts_as_not_supplied(config, build_input):
    block = confidence.compute(
        build_input(soil_availability="unknown", solar_exposure="unknown"),
        _typology(config),
        config,
    )
    assert block.completeness_percent["cooling"] == 0.0


def test_threshold_boundaries(config, build_input):
    """Exactly 40% is medium; exactly 70% is medium; above 70% is high."""
    # 4/10 cooling fields = 40% -> medium
    at_forty = confidence.compute(
        build_input(
            existing_tree_canopy_percent=5,
            existing_green_cover_percent=10,
            impervious_surface_percent=80,
            soil_availability="limited",
        ),
        _typology(config),
        config,
    )
    assert at_forty.completeness_percent["cooling"] == 40.0
    assert at_forty.cooling == "medium"

    # 7/10 = 70% -> still medium
    at_seventy = confidence.compute(
        build_input(
            existing_tree_canopy_percent=5,
            existing_green_cover_percent=10,
            impervious_surface_percent=80,
            soil_availability="limited",
            irrigation_availability="occasional",
            current_shade_level="low",
            solar_exposure="high",
        ),
        _typology(config),
        config,
    )
    assert at_seventy.completeness_percent["cooling"] == 70.0
    assert at_seventy.cooling == "medium"


def test_low_evidence_typology_caps_cooling_at_medium(config, build_input):
    """Complete cooling inputs cannot compensate for thin evidence (green facade)."""
    inp = build_input(
        nbs_type="green_facade",
        existing_tree_canopy_percent=0,
        existing_green_cover_percent=2,
        impervious_surface_percent=95,
        soil_availability="high",
        irrigation_availability="reliable",
        current_shade_level="very_low",
        lst_anomaly_c=8.0,
        solar_exposure="very_high",
        new_canopy_area_at_maturity_m2=0,
        expected_maturity_period_years=1,
    )
    block = confidence.compute(inp, _typology(config, "green_facade"), config)
    assert block.completeness_percent["cooling"] == 100.0
    assert block.cooling == "medium"
    assert block.cooling_capped_by_evidence is True


def test_cap_not_reported_when_not_binding(config, build_input):
    """A low-evidence typology with sparse inputs is low anyway: no cap claim."""
    block = confidence.compute(
        build_input(nbs_type="green_facade"), _typology(config, "green_facade"), config
    )
    assert block.cooling == "low"
    assert block.cooling_capped_by_evidence is False


def test_overall_is_lower_median(config, build_input):
    """[low, low, low, high] must give low, not medium."""
    inp = build_input(
        population_density="high",
        vulnerable_population_presence="high",
        access_to_cooled_indoor_space="low",
        safety_concern="high",
        public_accessibility="high",
        community_participation="high",
    )
    block = confidence.compute(inp, _typology(config), config)
    assert (block.cooling, block.energy, block.economic, block.equity) == (
        "low",
        "low",
        "low",
        "high",
    )
    assert block.overall == "low"


def test_the_two_cooling_refuge_indicators_share_one_slot(config, build_input):
    """D-039: either indicator answers the completeness question, and answering
    both does not inflate completeness — the equity denominator stays at six."""
    indoor_only = confidence.compute(
        build_input(access_to_cooled_indoor_space="low"), _typology(config), config
    )
    outdoor_only = confidence.compute(
        build_input(access_to_cool_outdoor_refuge="low"), _typology(config), config
    )
    both = confidence.compute(
        build_input(access_to_cooled_indoor_space="low", access_to_cool_outdoor_refuge="low"),
        _typology(config),
        config,
    )
    one_slot_of_six = round(100 / 6, 1)
    assert indoor_only.completeness_percent["equity"] == one_slot_of_six
    assert outdoor_only.completeness_percent["equity"] == one_slot_of_six
    assert both.completeness_percent["equity"] == one_slot_of_six
