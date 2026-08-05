"""Availability gating: the published matrix, asserted as a contract.

The availability review published nine situation counts and four land-use
totals. Those numbers are a property of the catalogue, so they are asserted
here directly: if a configuration edit changes what a school site is offered,
this file fails and names the number that moved. They were recomputed at
methodology 2026.08.06, when the catalogue grew from 110 entries to 121.

Availability feeds no score (D-044.1). The last test in this module is the one
that keeps that true.
"""

from __future__ import annotations

import pytest

from nature_cooling.engine import availability, run_assessment
from nature_cooling.engine.models import AssessmentInput, SiteConditions


def offered(config, scale, land_use=None, **conditions):
    """The entries the matrix offers, as the picker would receive them."""
    return availability.available_typologies(scale, land_use, SiteConditions(**conditions), config)


# The counts published in the approved availability review, recomputed at
# methodology 2026.08.06 when the catalogue grew from 110 entries to 121.
# (docs/assets/v1.2-availability-matrix.json is its machine-readable form).
#
# All nine are computed with the productive-governance question UNANSWERED,
# which is how the published table was produced: an unanswered multi-select
# suppresses nothing (D-043.3), so the productive entries are present in every
# row. The governance filter itself is exercised separately below.
PUBLISHED_SITUATIONS = [
    ("school site", 71, {"scale": "site", "land_use": "school"}),
    ("healthcare site", 72, {"scale": "site", "land_use": "healthcare"}),
    ("industrial site", 62, {"scale": "site", "land_use": "industrial"}),
    ("memorial site", 42, {"scale": "site", "land_use": "memorial"}),
    (
        "residential neighbourhood, no conditions met",
        32,
        {"scale": "neighbourhood", "land_use": "residential"},
    ),
    (
        "mixed-use riverfront neighbourhood with a railway",
        32,
        {
            "scale": "neighbourhood",
            "land_use": "mixed_use",
            "waterfront_type": "river",
            "includes_railway": "yes",
        },
    ),
    ("residential building", 56, {"scale": "building", "land_use": "residential"}),
    ("city scale, no conditions met", 3, {"scale": "city"}),
    ("district scale", 5, {"scale": "district"}),
]


@pytest.mark.parametrize(
    ("label", "expected", "query"),
    PUBLISHED_SITUATIONS,
    ids=[label for label, _, _ in PUBLISHED_SITUATIONS],
)
def test_published_situation_counts(config, label, expected, query) -> None:
    scale = query.pop("scale")
    land_use = query.pop("land_use", None)
    assert len(offered(config, scale, land_use, **query)) == expected, label


@pytest.mark.parametrize(
    ("land_use", "expected"),
    [("campus", 98), ("healthcare", 81), ("school", 77), ("memorial", 44)],
)
def test_published_land_use_totals(config, land_use, expected) -> None:
    """D-043.1: a land use maps to real interventions, and this is how many.

    Memorial is deliberately the sparsest — tree groves, meadows, woodland and
    quiet permeable planting are in; plazas, playgrounds, tram corridors,
    living walls and productive landscapes are out.
    """
    applicable = [
        typology
        for typology in config.typologies.resolved
        if land_use in typology.typical_use_context
    ]
    assert len(applicable) == expected


def test_the_retired_land_use_contexts_are_not_selectable(config) -> None:
    """D-043.1: the tool never offers, as an intervention, the land use it was told."""
    names = {typology.nbs_type for typology in config.typologies.resolved}
    for retired in (
        "schoolyard_greening",
        "hospital_landscape",
        "campus_landscape",
        "memorial_landscape",
    ):
        assert retired not in names


def test_constructed_water_features_need_no_waterfront(config) -> None:
    """The ruling that a constructed feature needs no existing water body."""
    constructed = {"constructed_wetland", "retention_pond", "detention_basin", "water_square"}
    without = {t.nbs_type for t in offered(config, "neighbourhood")}
    assert constructed <= without


def test_waterfront_entries_appear_only_once_the_waterfront_is_confirmed(config) -> None:
    """A physical precondition gates on positive confirmation.

    Offering river restoration before the user says there is a river would be
    offering an intervention that cannot be built here.
    """
    unanswered = {t.nbs_type for t in offered(config, "neighbourhood")}
    assert "river_restoration" not in unanswered

    with_river = {t.nbs_type for t in offered(config, "neighbourhood", waterfront_type="river")}
    assert "river_restoration" in with_river

    with_lake = {t.nbs_type for t in offered(config, "neighbourhood", waterfront_type="lake")}
    assert "river_restoration" not in with_lake
    assert "urban_lake_restoration" in with_lake


def test_woodland_restoration_is_gated_but_woodland_creation_is_not(config) -> None:
    """Only restoration types require woodland to already be there."""
    without = {t.nbs_type for t in offered(config, "neighbourhood")}
    assert {
        "microforest",
        "afforestation",
        "urban_woodland_site",
        "urban_woodland_buffer",
    } <= without
    assert "degraded_woodland_restoration" not in without
    assert "reforestation" not in without

    with_woodland = {t.nbs_type for t in offered(config, "neighbourhood", existing_woodland="yes")}
    assert {"degraded_woodland_restoration", "reforestation"} <= with_woodland


def test_railway_gates_exactly_one_entry(config) -> None:
    gated = [
        typology.nbs_type
        for typology in config.typologies.resolved
        if typology.availability.requires_railway
    ]
    assert gated == ["railway_green_corridor"]

    assert "railway_green_corridor" not in {t.nbs_type for t in offered(config, "city")}
    assert "railway_green_corridor" in {
        t.nbs_type for t in offered(config, "city", includes_railway="yes")
    }


def test_an_unanswered_governance_question_suppresses_nothing(config) -> None:
    """D-043.3, and the reason the question changed shape.

    The approved yes/no would have suppressed the urban farm and the
    agroforestry system on a "no" — the highest-cooling entries in the group and
    the ones a municipality is most likely to deliver. A multi-select left empty
    is not evidence that no delivery model exists, so it filters nothing.
    """
    unanswered = {t.nbs_type for t in offered(config, "site", "school")}
    assert {"community_garden", "urban_farm", "school_garden"} <= unanswered


def test_an_answered_governance_question_filters_to_what_it_names(config) -> None:
    commercial = {
        t.nbs_type for t in offered(config, "site", "school", productive_governance=["commercial"])
    }
    assert "urban_farm" in commercial
    assert "community_garden" not in commercial
    assert "school_garden" not in commercial

    both = {
        t.nbs_type
        for t in offered(
            config, "site", "school", productive_governance=["commercial", "community"]
        )
    }
    assert {"urban_farm", "community_garden"} <= both
    assert "school_garden" not in both


def test_city_and_district_scales_compose_packages(config) -> None:
    """D-043.2: at these scales the user composes rather than chooses."""
    assert availability.composes_packages("city", config) is True
    assert availability.composes_packages("district", config) is True
    for scale in ("neighbourhood", "site", "building"):
        assert availability.composes_packages(scale, config) is False


def test_selecting_an_unoffered_entry_warns_but_never_blocks(config) -> None:
    """Availability guides selection; it never overrides the professional (D-019)."""
    result = run_assessment(
        AssessmentInput(
            assessment_scale="neighbourhood",
            site_area_m2=5000,
            climate_zone="temperate",
            land_use="residential",
            nbs_type=["river_restoration"],
        ),
        config,
    )
    assert result.cooling.delta_t_max_c > 0
    assert any("not offered for this site" in warning for warning in result.warnings)


def test_the_four_gating_answers_move_no_score(config) -> None:
    """D-044.1 stated as a property: gating is not scoring.

    The same site scored with every availability question answered and with
    none of them answered must produce byte-identical output apart from the
    availability warning itself, which is the only place these answers may
    appear.
    """
    base = {
        "assessment_scale": "neighbourhood",
        "site_area_m2": 8000,
        "climate_zone": "temperate",
        "land_use": "residential",
        "nbs_type": ["tree_avenue"],
        "existing_tree_canopy_percent": 12,
        "soil_availability": "moderate",
        "irrigation_availability": "reliable",
        "population_density": "high",
        "new_canopy_area_at_maturity_m2": 900,
    }
    silent = run_assessment(AssessmentInput(**base), config)
    answered = run_assessment(
        AssessmentInput(
            **base,
            includes_railway="yes",
            existing_woodland="yes",
            waterfront_type="river",
            productive_governance=["community", "commercial"],
        ),
        config,
    )
    assert silent.model_dump() == answered.model_dump()
