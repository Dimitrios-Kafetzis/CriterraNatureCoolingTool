"""Runner tests: orchestration, determinism, warnings, and cross-cutting properties."""

from __future__ import annotations

import itertools

import pytest

from nature_cooling.engine import run_assessment
from nature_cooling.engine.config import load_config


def test_determinism_byte_identical(config, build_input):
    """Identical input + identical methodology version -> byte-identical output."""
    inp = build_input(
        lst_anomaly_c=4.2,
        impervious_surface_percent=85,
        existing_green_cover_percent=12,
        existing_tree_canopy_percent=8,
        new_canopy_area_at_maturity_m2=1200,
        soil_availability="limited",
        irrigation_availability="occasional",
        solar_exposure="high",
        population_density="high",
        vulnerable_population_presence="high",
        access_to_cooled_indoor_space="low",
        nearby_building_cooling_demand_relevant="yes",
        annual_cooling_energy_demand_kwh=450000,
        grid_emission_factor_kgco2e_per_kwh=0.3,
    )
    first = run_assessment(inp, config).model_dump_json()
    for _ in range(5):
        assert run_assessment(inp, config).model_dump_json() == first
    # A freshly loaded configuration of the same version changes nothing.
    assert run_assessment(inp, load_config()).model_dump_json().encode() == first.encode()


def test_versions_are_stamped(config, build_input):
    result = run_assessment(build_input(), config)
    assert result.methodology_version == config.version
    assert result.engine_version
    assert result.method_note


def test_unknown_typology_raises_value_error(config, build_input):
    with pytest.raises(ValueError, match="unknown nbs_type"):
        run_assessment(build_input(nbs_type="teleportation_grove"), config)


def test_cover_sum_warning(config, build_input):
    result = run_assessment(
        build_input(existing_green_cover_percent=60, impervious_surface_percent=50),
        config,
    )
    assert result.warnings == [
        "existing green cover plus impervious surface totals 110.0%, which exceeds 105% of the site"
    ]


def test_intervention_area_warning(config, build_input):
    result = run_assessment(build_input(site_area_m2=6000, intervention_area_m2=7000), config)
    assert result.warnings == ["intervention area (7000 m2) exceeds site area (6000 m2)"]


def test_no_silent_zero_anywhere(config, build_input):
    """A minimal input yields explicit statuses, never zero quantities."""
    result = run_assessment(build_input(), config)
    assert result.energy.status == "relevance_not_confirmed"
    assert result.energy.savings_min_kwh_per_year is None
    assert result.ghg.status == "energy_not_calculated"
    assert result.costs.payback_status == "missing_capital_cost"
    assert result.costs.cost_feasibility_status == "not_estimated"
    assert result.cooling.shade_potential_status == "not_estimated"
    assert result.cooling.time_to_benefit_status == "not_estimated"
    assert "cost feasibility not estimated" in " ".join(result.assumptions_applied)


def test_property_scores_bounded_and_envelope_respected(config, build_input):
    """Sweep every typology x climate x scale: all scores in [0, 100], every
    reported temperature range inside the literature envelope, and applied
    aggregation weights always summing to one."""
    zones = ["tropical_wet", "tropical_dry", "arid", "semi_arid", "temperate", "other"]
    scales = ["city", "neighbourhood", "building"]
    for typology, zone, scale in itertools.product(config.typologies.typologies, zones, scales):
        result = run_assessment(
            build_input(
                nbs_type=typology.nbs_type,
                climate_zone=zone,
                assessment_scale=scale,
                site_area_m2=2500.0,
                existing_tree_canopy_percent=30,
                new_canopy_area_at_maturity_m2=500,
                soil_availability="high",
                irrigation_availability="reliable",
            ),
            config,
        )
        for score in (
            result.heat_exposure.score,
            result.vulnerability.score,
            result.heat_priority.score,
            result.cooling.potential_score,
            result.suitability.score,
            result.co_benefits.score,
            result.equity.score,
            result.opportunity.score,
        ):
            assert 0.0 <= score <= 100.0
        assert typology.temp_reduction_min_c <= result.cooling.delta_t_min_c
        assert result.cooling.delta_t_min_c <= result.cooling.delta_t_max_c
        assert result.cooling.delta_t_max_c <= typology.temp_reduction_max_c
        applied = sum(component.applied_weight for component in result.opportunity.components)
        assert applied == pytest.approx(1.0, abs=5e-4)
