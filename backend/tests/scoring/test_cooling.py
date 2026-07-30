"""Unit tests for the Cooling Potential Score and envelope clipping (D-008)."""

from __future__ import annotations

import pytest

from nature_cooling.engine.scoring import cooling


def _typology(config, nbs_type="street_tree_planting"):
    return config.typologies.by_type(nbs_type)


def test_worked_example_lower_clip_binds(config, build_input):
    """A=0.95: raw lower bound 0.475 is clipped up to the 0.5 floor."""
    block = cooling.compute(
        build_input(new_canopy_area_at_maturity_m2=1200), _typology(config), 0.95, config
    )
    assert block.potential_score == 71.25
    assert block.delta_t_min_c == 0.5
    assert block.delta_t_max_c == 2.85
    assert block.delta_t_midpoint_c == 1.675
    assert block.heat_index_improvement == "high"
    assert block.shade_potential_percent == 20.0
    assert block.shade_potential_status == "calculated"


def test_upper_clip_binds_above_one(config, build_input):
    """A=1.2 on urban forest: 3.0*1.2=3.6 must clip to the 3.0 ceiling."""
    block = cooling.compute(build_input(), _typology(config, "urban_forest"), 1.2, config)
    assert block.delta_t_max_c == 3.0
    assert block.delta_t_min_c == 1.2
    assert block.potential_score == 100.0  # 90*1.2=108 clamps to 100


def test_range_always_within_envelope_for_all_typologies(config, build_input):
    """Property: no adjustment factor may push the range outside the envelope."""
    for typology in config.typologies.typologies:
        for factor in (0.5, 0.605, 0.8, 0.95, 1.0, 1.12, 1.2):
            block = cooling.compute(build_input(), typology, factor, config)
            assert typology.temp_reduction_min_c <= block.delta_t_min_c
            assert block.delta_t_min_c <= block.delta_t_max_c
            assert block.delta_t_max_c <= typology.temp_reduction_max_c
            assert 0.0 <= block.potential_score <= 100.0


@pytest.mark.parametrize(
    ("factor", "expected_bucket"),
    [
        (0.5, "low"),  # green roof midpoint (0.1+0.5)/2 = 0.3
        (1.0, "medium"),  # (0.1+1.0)/2 = 0.55
    ],
)
def test_heat_index_buckets_low_and_medium(config, build_input, factor, expected_bucket):
    block = cooling.compute(build_input(), _typology(config, "green_roof"), factor, config)
    assert block.heat_index_improvement == expected_bucket


def test_heat_index_bucket_boundary_at_one_point_five(config, build_input):
    """Midpoint exactly 1.5 falls in the high bucket ([min, max) convention)."""
    block = cooling.compute(build_input(), _typology(config, "permeable_shaded_plaza"), 1.0, config)
    assert block.delta_t_midpoint_c == 1.5
    assert block.heat_index_improvement == "high"


def test_shade_potential_missing_canopy_is_not_estimated(config, build_input):
    block = cooling.compute(build_input(), _typology(config), 1.0, config)
    assert block.shade_potential_percent is None
    assert block.shade_potential_status == "not_estimated"


def test_shade_potential_clamped_at_hundred(config, build_input):
    inp = build_input(site_area_m2=1000, new_canopy_area_at_maturity_m2=1500)
    block = cooling.compute(inp, _typology(config), 1.0, config)
    assert block.shade_potential_percent == 100.0


@pytest.mark.parametrize(
    ("years", "expected"),
    [
        (0.5, "immediate"),
        (1.0, "short_term"),
        (3.0, "medium_term"),
        (5.0, "medium_term"),
        (10.0, "long_term"),
        (25.0, "long_term"),
    ],
)
def test_time_to_benefit_buckets(config, build_input, years, expected):
    block = cooling.compute(
        build_input(expected_maturity_period_years=years), _typology(config), 1.0, config
    )
    assert block.time_to_benefit == expected
    assert block.time_to_benefit_status == "derived"


def test_time_to_benefit_missing(config, build_input):
    block = cooling.compute(build_input(), _typology(config), 1.0, config)
    assert block.time_to_benefit is None
    assert block.time_to_benefit_status == "not_estimated"
