"""Contract tests: POST /api/assessments/validate (D-028).

The endpoint's contract is fixed by D-028: errors and warnings only (OQ-08),
a per-block confidence preview from the engine's confidence module, and the
highest-value missing field hint per block.
"""

from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

from nature_cooling.engine import confidence as confidence_module
from nature_cooling.engine.config import MethodologyConfig
from nature_cooling.engine.models import AssessmentInput

# The first six cooling groups in derived_scores.yaml configured order.
_SIX_COOLING_FIELDS: dict[str, Any] = {
    "existing_tree_canopy_percent": 20.0,
    "existing_green_cover_percent": 30.0,
    "impervious_surface_percent": 50.0,
    "soil_availability": "moderate",
    "irrigation_availability": "occasional",
    "current_shade_level": "low",
}

_ALL_EQUITY_FIELDS: dict[str, Any] = {
    "population_density": "high",
    "vulnerable_population_presence": "medium",
    "access_to_cooled_indoor_space": "low",
    "safety_concern": "medium",
    "public_accessibility": "high",
    "community_participation": "low",
}


def _validate(client: TestClient, payload: dict[str, Any]) -> dict[str, Any]:
    response = client.post("/api/assessments/validate", json=payload)
    assert response.status_code == 200
    body: dict[str, Any] = response.json()
    return body


def _error_fields(body: dict[str, Any]) -> set[str]:
    return {item["field"] for item in body["errors"]}


def test_a_complete_minimal_input_is_valid(
    client: TestClient, minimal_input: dict[str, Any]
) -> None:
    body = _validate(client, minimal_input)
    assert body["valid"] is True
    assert body["errors"] == []
    assert body["warnings"] == []


def test_missing_required_fields_are_errors(client: TestClient) -> None:
    body = _validate(client, {})
    assert body["valid"] is False
    assert _error_fields(body) == {
        "assessment_scale",
        "site_area_m2",
        "climate_zone",
        "nbs_type",
    }
    # The preview is still computed, from an empty questionnaire.
    for block in ("cooling", "energy", "economic", "equity"):
        assert body["confidence"][block]["level"] == "low"
        assert body["confidence"][block]["completeness_percent"] == 0.0
    assert body["confidence"]["overall"] == "low"


def test_invalid_values_are_field_errors_and_do_not_poison_the_preview(
    client: TestClient, minimal_input: dict[str, Any]
) -> None:
    payload = {
        **minimal_input,
        "existing_tree_canopy_percent": 150.0,  # invalid: dropped from the preview
        "existing_green_cover_percent": 40.0,  # valid: counted by the preview
    }
    body = _validate(client, payload)
    assert body["valid"] is False
    assert _error_fields(body) == {"existing_tree_canopy_percent"}
    assert body["confidence"]["cooling"]["completeness_percent"] == 10.0


def test_unknown_fields_are_errors(client: TestClient, minimal_input: dict[str, Any]) -> None:
    body = _validate(client, {**minimal_input, "planted_area_m2": 12.0})
    assert body["valid"] is False
    assert _error_fields(body) == {"planted_area_m2"}


def test_unknown_typology_is_an_error(client: TestClient, minimal_input: dict[str, Any]) -> None:
    # The error is addressed to the offending list position (D-044.2), so a
    # package whose third component is a typo says which one it is.
    body = _validate(client, {**minimal_input, "nbs_type": ["not_a_typology"]})
    assert body["valid"] is False
    assert body["errors"] == [
        {"field": "nbs_type.0", "message": "unknown nbs_type: 'not_a_typology'"}
    ]
    assert body["confidence"]["cooling_capped_by_evidence"] is False


def test_each_unknown_package_component_is_reported_at_its_own_position(
    client: TestClient, minimal_input: dict[str, Any]
) -> None:
    """A package reports every unresolvable component, never just the first."""
    body = _validate(
        client, {**minimal_input, "nbs_type": ["tree_avenue", "not_a_typology", "also_not_one"]}
    )
    assert body["valid"] is False
    assert body["errors"] == [
        {"field": "nbs_type.1", "message": "unknown nbs_type: 'not_a_typology'"},
        {"field": "nbs_type.2", "message": "unknown nbs_type: 'also_not_one'"},
    ]


def test_a_package_of_several_known_typologies_is_valid(
    client: TestClient, package_draft: dict[str, Any]
) -> None:
    """D-044.2: several simultaneously available entries are a valid selection."""
    body = _validate(client, package_draft)
    assert body["valid"] is True
    assert body["errors"] == []


def test_a_duplicated_package_component_is_an_error(
    client: TestClient, minimal_input: dict[str, Any]
) -> None:
    """The same entry twice is not a package of two; it is a mistake."""
    body = _validate(client, {**minimal_input, "nbs_type": ["tree_avenue", "tree_avenue"]})
    assert body["valid"] is False
    assert _error_fields(body) == {"nbs_type"}
    assert "duplicate package components" in body["errors"][0]["message"]


def test_an_empty_package_is_an_error(client: TestClient, minimal_input: dict[str, Any]) -> None:
    """An assessment always proposes at least one intervention (min_length=1)."""
    body = _validate(client, {**minimal_input, "nbs_type": []})
    assert body["valid"] is False
    assert _error_fields(body) == {"nbs_type"}


def test_the_availability_answers_feed_no_confidence_block(
    client: TestClient, minimal_input: dict[str, Any]
) -> None:
    """D-044.1: the four gating answers change the menu and nothing else.

    They appear in no formula, in no confidence block, and in no aggregation,
    so supplying all four must leave every completeness figure untouched.
    """
    bare = _validate(client, minimal_input)["confidence"]
    gated = _validate(
        client,
        {
            **minimal_input,
            "includes_railway": "yes",
            "existing_woodland": "no",
            "waterfront_type": "river",
            "productive_governance": ["community", "commercial"],
        },
    )["confidence"]
    assert gated == bare


def test_engine_warning_rules_cover_sum_and_intervention_area(
    client: TestClient, minimal_input: dict[str, Any]
) -> None:
    payload = {
        **minimal_input,
        "existing_green_cover_percent": 60.0,
        "impervious_surface_percent": 55.0,
        "intervention_area_m2": 7000.0,
    }
    body = _validate(client, payload)
    assert body["valid"] is True
    assert body["warnings"] == [
        "existing green cover plus impervious surface totals 115.0%, "
        "which exceeds 105% of the site",
        "intervention area (7000 m2) exceeds site area (6000 m2)",
    ]


def test_no_site_area_means_no_intervention_area_warning(client: TestClient) -> None:
    # Without a site area the exceedance cannot be asserted; the only issues
    # are the missing required fields.
    body = _validate(client, {"intervention_area_m2": 7000.0})
    assert body["warnings"] == []
    assert "site_area_m2" in _error_fields(body)


def test_preview_matches_the_engine_confidence_module(
    client: TestClient, config: MethodologyConfig, minimal_input: dict[str, Any]
) -> None:
    payload = {**minimal_input, **_SIX_COOLING_FIELDS, **_ALL_EQUITY_FIELDS}
    body = _validate(client, payload)
    expected = confidence_module.compute(
        AssessmentInput.model_validate(payload),
        config.typologies.by_type("tree_avenue"),
        config,
    )
    for block in ("cooling", "energy", "economic", "equity"):
        assert body["confidence"][block]["level"] == getattr(expected, block)
        assert (
            body["confidence"][block]["completeness_percent"]
            == expected.completeness_percent[block]
        )
    assert body["confidence"]["overall"] == expected.overall


def test_hint_names_the_group_whose_completion_raises_the_level(
    client: TestClient, minimal_input: dict[str, Any]
) -> None:
    # Three of ten cooling groups supplied: 30% (low). One more reaches 40%,
    # the medium boundary — so the first unsupplied group in configured order
    # is the highest-value missing field.
    payload = {
        **minimal_input,
        "existing_tree_canopy_percent": 20.0,
        "existing_green_cover_percent": 30.0,
        "impervious_surface_percent": 50.0,
    }
    body = _validate(client, payload)
    assert body["confidence"]["cooling"]["level"] == "low"
    assert body["confidence"]["cooling"]["hint"] == {
        "fields": ["soil_availability"],
        "raises_level_to": "medium",
    }


def test_hint_falls_back_to_first_unsupplied_group_when_nothing_raises(
    client: TestClient, minimal_input: dict[str, Any]
) -> None:
    # Empty cooling block: one answer reaches only 10%, still low. The hint
    # falls back to the first unsupplied group in configured order.
    body = _validate(client, minimal_input)
    assert body["confidence"]["cooling"]["hint"] == {
        "fields": ["existing_tree_canopy_percent"],
        "raises_level_to": None,
    }


def test_hint_presents_the_either_of_heat_signal_slot_as_alternatives(
    client: TestClient, minimal_input: dict[str, Any]
) -> None:
    # Six of ten cooling groups supplied: 60% (medium). A seventh reaches
    # 70%, which is still medium (the boundary is exclusive), so no single
    # completion raises the level and the hint falls back to the first
    # unsupplied group — the two-field heat signal slot.
    payload = {**minimal_input, **_SIX_COOLING_FIELDS}
    body = _validate(client, payload)
    assert body["confidence"]["cooling"]["level"] == "medium"
    assert body["confidence"]["cooling"]["hint"] == {
        "fields": ["lst_anomaly_c", "heat_exposure_level"],
        "raises_level_to": None,
    }


def test_hint_that_crosses_the_high_boundary(
    client: TestClient, minimal_input: dict[str, Any]
) -> None:
    # Seven of ten supplied (the LST anomaly fills the either-of slot): 70%
    # (medium). One more reaches 80% — high.
    payload = {**minimal_input, **_SIX_COOLING_FIELDS, "lst_anomaly_c": 4.0}
    body = _validate(client, payload)
    assert body["confidence"]["cooling"]["level"] == "medium"
    assert body["confidence"]["cooling"]["hint"] == {
        "fields": ["solar_exposure"],
        "raises_level_to": "high",
    }


def test_hint_is_none_when_every_group_is_supplied(
    client: TestClient, minimal_input: dict[str, Any]
) -> None:
    payload = {**minimal_input, **_ALL_EQUITY_FIELDS}
    body = _validate(client, payload)
    assert body["confidence"]["equity"]["level"] == "high"
    assert body["confidence"]["equity"]["hint"] is None


def test_unknown_answers_count_as_not_supplied(
    client: TestClient, minimal_input: dict[str, Any]
) -> None:
    payload = {**minimal_input, "soil_availability": "unknown"}
    body = _validate(client, payload)
    assert body["confidence"]["cooling"]["completeness_percent"] == 0.0


def test_evidence_cap_binds_the_preview_and_the_hint(
    client: TestClient, minimal_input: dict[str, Any]
) -> None:
    # Eight of ten cooling groups supplied (80%, raw high) on a low-evidence
    # typology: the level is capped at medium (Methodology Report 6.2), and no
    # completion can raise it, so the hint falls back with no promised raise.
    # `indirect_ground_rooted_green_facade` inherits the green_facade_living_wall
    # archetype, the evidence class the retired `green_facade` typology carried.
    payload = {
        **minimal_input,
        "nbs_type": ["indirect_ground_rooted_green_facade"],
        **_SIX_COOLING_FIELDS,
        "lst_anomaly_c": 4.0,
        "solar_exposure": "high",
    }
    body = _validate(client, payload)
    assert body["confidence"]["cooling"]["level"] == "medium"
    assert body["confidence"]["cooling_capped_by_evidence"] is True
    assert body["confidence"]["cooling"]["hint"] == {
        "fields": ["new_canopy_area_at_maturity_m2"],
        "raises_level_to": None,
    }


def test_the_evidence_cap_follows_the_component_that_carries_the_estimate(
    client: TestClient, minimal_input: dict[str, Any]
) -> None:
    """A package is capped by the component the engine would report from.

    The preview follows the same choice the engine makes — best evidence, then
    widest envelope — so adding a well-evidenced component to a thinly
    evidenced one lifts the cap, exactly as the package's own cooling estimate
    would come from that component (D-044.4).
    """
    thin = {
        **minimal_input,
        "nbs_type": ["indirect_ground_rooted_green_facade"],
        **_SIX_COOLING_FIELDS,
        "lst_anomaly_c": 4.0,
        "solar_exposure": "high",
    }
    assert _validate(client, thin)["confidence"]["cooling_capped_by_evidence"] is True

    package = {**thin, "nbs_type": ["indirect_ground_rooted_green_facade", "tree_avenue"]}
    body = _validate(client, package)
    assert body["valid"] is True
    assert body["confidence"]["cooling_capped_by_evidence"] is False
    assert body["confidence"]["cooling"]["level"] == "high"


def test_an_unresolvable_component_never_asserts_a_cap(
    client: TestClient, minimal_input: dict[str, Any]
) -> None:
    """D-029: a promise about confidence never rests on a typology we cannot find."""
    body = _validate(
        client,
        {
            **minimal_input,
            "nbs_type": ["not_a_typology"],
            **_SIX_COOLING_FIELDS,
            "lst_anomaly_c": 4.0,
            "solar_exposure": "high",
        },
    )
    assert body["valid"] is False
    assert body["confidence"]["cooling_capped_by_evidence"] is False


def test_non_object_bodies_are_rejected(client: TestClient) -> None:
    response = client.post("/api/assessments/validate", json=["not", "an", "object"])
    assert response.status_code == 422
