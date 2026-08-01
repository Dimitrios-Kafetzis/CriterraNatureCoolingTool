"""Multi-intervention package combination (D-038 semantics, D-044.4 bound).

The rules under test are the ones that decide what a package is allowed to
claim. The first of them is the one this release must not get wrong: a
package's temperature is capped at its best-evidenced component and is never
the sum of its parts, because no retrieved source quantifies super-additive
cooling from combining measures (D-014).
"""

from __future__ import annotations

import pytest

from nature_cooling.engine import package, run_assessment
from nature_cooling.engine.models import AssessmentInput

SITE = {
    "assessment_scale": "neighbourhood",
    "site_area_m2": 20000.0,
    "climate_zone": "temperate",
    "land_use": "mixed_use",
    "soil_availability": "high",
    "irrigation_availability": "reliable",
}


def assess(config, *components, **overrides):
    return run_assessment(
        AssessmentInput(**{**SITE, **overrides, "nbs_type": list(components)}), config
    )


def test_a_single_intervention_is_a_package_of_one(config):
    """Nothing about the single case changed shape when packages arrived."""
    result = assess(config, "tree_avenue")
    assert len(result.components) == 1
    assert result.package.component_count == 1
    assert result.package.representative_nbs_type == "tree_avenue"
    assert result.package.representative_reason == "the only component"
    component = result.components[0]
    assert component.is_representative is True
    assert result.cooling == component.cooling
    assert result.adjustment == component.adjustment
    assert result.suitability.score == component.suitability.score
    assert result.co_benefits == component.co_benefits


def test_temperature_is_the_best_evidenced_component_and_never_the_sum(config):
    """The rule, on a case constructed so summing would be visibly wrong."""
    alone = assess(config, "tree_avenue")
    packaged = assess(config, "tree_avenue", "blue_green_corridor", "rain_garden")

    assert packaged.cooling.delta_t_max_c == alone.cooling.delta_t_max_c
    assert packaged.cooling.delta_t_min_c == alone.cooling.delta_t_min_c
    summed = sum(component.cooling.delta_t_max_c for component in packaged.components)
    assert packaged.cooling.delta_t_max_c < summed


def test_the_carrier_is_chosen_by_evidence_before_magnitude(config):
    """A low-evidence component with a higher ceiling does not carry the package.

    A green facade is rated 0.3-2.0 C at LOW confidence; a pocket park is
    0.5-2.0 C at HIGH confidence. Evidence decides, not the headline number —
    otherwise the least certain estimate would speak for the package.
    """
    result = assess(config, "indirect_ground_rooted_green_facade", "pocket_park")
    assert result.package.representative_nbs_type == "pocket_park"
    assert result.typology.evidence_confidence == "high"


def test_a_tie_on_evidence_is_broken_by_the_wider_envelope(config):
    """Among equally well-evidenced components, the package reports the stronger."""
    result = assess(config, "pocket_park", "urban_woodland_site")
    assert result.package.representative_nbs_type == "urban_woodland_site"
    assert result.cooling.delta_t_max_c == 3.0


def test_selection_order_does_not_change_the_result(config):
    """Determinism: the same components in any order score identically."""
    forward = assess(config, "tree_avenue", "rain_garden", "pocket_park")
    reverse = assess(config, "pocket_park", "rain_garden", "tree_avenue")
    assert forward.cooling == reverse.cooling
    assert forward.co_benefits == reverse.co_benefits
    assert forward.suitability.score == reverse.suitability.score
    assert forward.opportunity.score == reverse.opportunity.score


def test_co_benefits_take_the_union_across_components(config):
    """A package delivers each dimension at least as well as its best component."""
    result = assess(config, "tree_avenue", "rain_garden", "extensive_green_roof")
    for dimension in ("biodiversity", "stormwater", "public_health", "urban_quality"):
        expected = max(getattr(component.co_benefits, dimension) for component in result.components)
        assert getattr(result.co_benefits, dimension) == expected
    assert result.co_benefits.score >= max(
        component.co_benefits.score for component in result.components
    )


def test_suitability_takes_the_minimum_and_keeps_every_flag(config):
    """A package is no more deliverable than its least suitable component (D-009).

    Averaging would let a well-fitting component conceal one that cannot be
    built here, so the score is the minimum and every component's flag is
    surfaced, each naming the entry it belongs to.
    """
    result = assess(
        config,
        "tree_avenue",
        "urban_woodland_site",
        site_area_m2=800.0,
    )
    assert result.suitability.score == min(c.suitability.score for c in result.components)
    assert not result.suitability.suitable
    messages = [flag.message for flag in result.suitability.flags]
    assert any(message.startswith("Urban woodland (site):") for message in messages)
    assert any("below the minimum viable area" in message for message in messages)


def test_a_single_component_flag_is_not_prefixed(config):
    """The one-component message is unchanged from every previous version."""
    result = assess(config, "urban_woodland_site", site_area_m2=800.0)
    assert result.suitability.flags
    assert not result.suitability.flags[0].message.startswith("Urban woodland (site):")


def test_energy_follows_one_applicable_component_and_is_never_summed(config):
    """Energy is a function of ONE cooling estimate (D-015), even for a package."""
    result = assess(
        config,
        "pocket_park",
        "tree_avenue",
        nearby_building_cooling_demand_relevant="yes",
        annual_cooling_energy_demand_kwh=400000.0,
    )
    assert result.energy.status == "calculated"
    assert result.package.energy_component_nbs_type == "tree_avenue"
    carrier = next(c for c in result.components if c.typology.nbs_type == "tree_avenue")
    assert result.energy.savings_min_kwh_per_year == pytest.approx(
        400000.0 * carrier.cooling.delta_t_min_c * 0.02, abs=0.05
    )


def test_a_package_of_only_amenity_components_reports_no_energy(config):
    """No applicable component means the limitation is reported, not a number."""
    result = assess(
        config,
        "pocket_park",
        "rain_garden",
        nearby_building_cooling_demand_relevant="yes",
        annual_cooling_energy_demand_kwh=400000.0,
    )
    assert result.energy.status == "typology_not_applicable"
    assert result.package.energy_component_nbs_type is None
    assert result.energy.savings_min_kwh_per_year is None


def test_caveats_are_unioned_across_the_package(config):
    """A caveat earned by any component is a caveat on the assessment.

    The small-water caveat must appear even though the tree avenue carries the
    headline temperature: the user is being sold a constructed wetland too, and
    the evidence about it does not stop applying because a stronger component
    was selected alongside it.
    """
    result = assess(config, "tree_avenue", "constructed_wetland")
    assert "negligible in design practice" in result.recommendation
    assert result.package.representative_nbs_type == "tree_avenue"


def test_a_large_package_is_allowed_but_warned(config):
    """D-044.4: unbounded, warned above five, and the warning says why.

    A hard cap would forbid something harmless, because a sixth component adds
    co-benefit breadth rather than degrees. The warning states exactly that,
    which is the information a refusal would have conveyed only by refusing.
    """
    six = [
        "tree_avenue",
        "green_median",
        "blue_green_corridor",
        "pocket_park",
        "courtyard_greening",
        "permeable_plaza",
    ]
    result = run_assessment(AssessmentInput(**SITE, nbs_type=six), config)
    assert result.package.component_count == 6
    warning = next(w for w in result.warnings if "above the 5" in w)
    assert "will not raise it" in warning

    five = run_assessment(AssessmentInput(**SITE, nbs_type=six[:5]), config)
    assert not any("above the 5" in w for w in five.warnings)
    # The sixth component genuinely adds nothing to the temperature, which is
    # what the warning promises.
    assert result.cooling == five.cooling


def test_the_package_block_states_every_combination_rule(config):
    """The result explains itself: no rule is applied without being named."""
    result = assess(config, "tree_avenue", "rain_garden")
    assert "never summed" in result.package.cooling_rule
    assert "maximum per dimension" in result.package.co_benefit_rule
    assert "minimum across components" in result.package.suitability_rule
    assert "entered once for the whole package" in result.package.cost_rule
    assert "best-evidenced component" in result.package.representative_reason


def test_choose_representative_prefers_the_earliest_on_a_complete_tie(config):
    """Ties on both evidence and range fall to the user's own selection order."""
    result = assess(config, "tree_avenue", "green_street")
    assert result.package.representative_nbs_type == "tree_avenue"
    assert package.choose_representative(list(result.components)) == 0
