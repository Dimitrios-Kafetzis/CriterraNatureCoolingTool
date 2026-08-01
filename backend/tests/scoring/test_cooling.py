"""Unit tests for the Cooling Potential Score and envelope clipping (D-008)."""

from __future__ import annotations

import pytest

from nature_cooling.engine.runner import run_assessment
from nature_cooling.engine.scoring import cooling


def _typology(config, nbs_type="tree_avenue"):
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
    """A=1.2 on urban woodland: 3.0*1.2=3.6 must clip to the 3.0 ceiling."""
    block = cooling.compute(build_input(), _typology(config, "urban_woodland_site"), 1.2, config)
    assert block.delta_t_max_c == 3.0
    assert block.delta_t_min_c == 1.2
    assert block.potential_score == 100.0  # 90*1.2=108 clamps to 100


def test_range_always_within_envelope_for_all_typologies(config, build_input):
    """Property: no adjustment factor may push the range outside the envelope."""
    for typology in config.typologies.resolved:
        for factor in (0.5, 0.605, 0.8, 0.95, 1.0, 1.12, 1.2):
            block = cooling.compute(build_input(), typology, factor, config)
            assert typology.temp_reduction_min_c <= block.delta_t_min_c
            assert block.delta_t_min_c <= block.delta_t_max_c
            assert block.delta_t_max_c <= typology.temp_reduction_max_c
            assert 0.0 <= block.potential_score <= 100.0


def test_package_cooling_is_the_best_evidenced_component_and_never_the_sum(config, build_input):
    """D-014/D-038: combining measures may not buy additional degrees.

    No retrieved source quantifies super-additive cooling, so a package is
    reported at its best-evidenced component's adjusted range. Components are
    listed weakest-evidence-first to prove the selection is by evidence rating
    and not by position: the tree avenue (high) carries the estimate over the
    green roof (medium) and the rain garden (low).

    Summing would give 0.1 + 0.1 + 0.5 = 0.7 to 0.8 + 1.0 + 3.0 = 4.8 C, which
    is above every envelope in the package and is exactly the claim D-014
    forbids.
    """
    result = run_assessment(
        build_input(nbs_type=["rain_garden", "extensive_green_roof", "tree_avenue"]), config
    )
    carrier = config.typologies.by_type("tree_avenue")
    assert result.package.representative_nbs_type == "tree_avenue"
    assert (result.cooling.delta_t_min_c, result.cooling.delta_t_max_c) == (0.5, 3.0)
    assert result.cooling.delta_t_max_c == carrier.temp_reduction_max_c
    assert result.cooling.potential_score == carrier.base_cooling_score

    # Never the sum, and never above any single component's own maximum.
    assert result.cooling.delta_t_max_c < sum(
        component.cooling.delta_t_max_c for component in result.components
    )
    assert result.cooling.delta_t_max_c == max(
        component.cooling.delta_t_max_c for component in result.components
    )


@pytest.mark.parametrize(
    ("factor", "expected_bucket"),
    [
        (0.5, "low"),  # green roof midpoint (0.1+0.5)/2 = 0.3
        (1.0, "medium"),  # (0.1+1.0)/2 = 0.55
    ],
)
def test_heat_index_buckets_low_and_medium(config, build_input, factor, expected_bucket):
    block = cooling.compute(
        build_input(), _typology(config, "extensive_green_roof"), factor, config
    )
    assert block.heat_index_improvement == expected_bucket


def test_heat_index_bucket_boundary_at_one_point_five(config, build_input):
    """Midpoint exactly 1.5 falls in the high bucket ([min, max) convention)."""
    block = cooling.compute(build_input(), _typology(config, "permeable_plaza"), 1.0, config)
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
