"""Contract tests: /api/meta, /api/typologies, /api/typologies/available,
/api/methodology."""

from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

import nature_cooling
from nature_cooling.engine.config import MethodologyConfig


def _available(client: TestClient, **params: Any) -> dict[str, Any]:
    response = client.get("/api/typologies/available", params=params)
    assert response.status_code == 200
    body: dict[str, Any] = response.json()
    return body


def test_meta_reports_versions_and_licence(client: TestClient, config: MethodologyConfig) -> None:
    response = client.get("/api/meta")
    assert response.status_code == 200
    assert response.json() == {
        "engine_version": nature_cooling.__version__,
        "methodology_version": config.version,
        "license": "Apache-2.0",
        # The unconfigured deployment: no tile source, no third-party request
        # (D-049.1).
        "tiles": None,
    }


def test_typologies_returns_the_full_library(client: TestClient, config: MethodologyConfig) -> None:
    """The archetype library, the catalogue, and the flat merged view (D-044).

    ``archetypes`` carries the citations, ``typologies`` the entries that
    inherit them, and ``resolved`` the merge the picker renders and the engine
    scores — so the interface never has to infer which evidence class a card's
    numbers came from.
    """
    response = client.get("/api/typologies")
    assert response.status_code == 200
    body = response.json()
    assert body["version"] == config.version
    assert len(body["archetypes"]) == len(config.typologies.archetypes) == 18
    assert len(body["typologies"]) == len(config.typologies.typologies) == 121
    assert len(body["resolved"]) == len(config.typologies.resolved) == 121

    # The citations live on the archetype, which carries the cited envelope.
    first_archetype = body["archetypes"][0]
    assert first_archetype["suitability"]["minimum_site_area_m2"] > 0
    assert first_archetype["sources"], "archetype citations must be served"

    # A catalogue entry names the archetype it inherits from and the conditions
    # that gate it, and nothing else duplicates the evidence.
    first_entry = body["typologies"][0]
    assert first_entry["archetype"] in {item["archetype"] for item in body["archetypes"]}
    assert first_entry["availability"]["scales"]

    # The resolved view carries both: the entry's identity and the inherited
    # evidence, so a result can report which evidence class it was scored on.
    first_resolved = body["resolved"][0]
    assert first_resolved["nbs_type"] == first_entry["nbs_type"]
    assert first_resolved["suitability"]["minimum_site_area_m2"] > 0
    assert first_resolved["sources"], "resolved entries must carry their citations"


def test_available_reports_which_scales_compose_packages(client: TestClient) -> None:
    """D-044.1: city and district compose a package; smaller scales offer alternatives."""
    assert _available(client, assessment_scale="city")["composes_packages"] is True
    assert _available(client, assessment_scale="district")["composes_packages"] is True
    for scale in ("neighbourhood", "site", "building"):
        assert _available(client, assessment_scale=scale)["composes_packages"] is False


def test_available_echoes_the_query_and_counts_what_it_offers(
    client: TestClient, config: MethodologyConfig
) -> None:
    body = _available(client, assessment_scale="neighbourhood", land_use="residential")
    assert body["version"] == config.version
    assert body["assessment_scale"] == "neighbourhood"
    assert body["land_use"] == "residential"
    assert body["count"] == len(body["nbs_types"])
    assert body["warn_above_components"] > 0
    # Availability guides selection and never blocks it (D-019): the offered
    # set is a subset of the library, never the whole of it.
    assert 0 < body["count"] < len(config.typologies.resolved)


def test_a_waterfront_entry_is_offered_only_when_the_site_has_that_water_body(
    client: TestClient,
) -> None:
    """An unanswered waterfront question gates (availability.yaml), because a
    river restoration needs a river that is already there."""
    unanswered = _available(client, assessment_scale="neighbourhood")
    assert "river_restoration" not in unanswered["nbs_types"]

    on_a_river = _available(client, assessment_scale="neighbourhood", waterfront_type="river")
    assert "river_restoration" in on_a_river["nbs_types"]

    # The gate reads the water body's category, not merely its presence.
    on_a_lake = _available(client, assessment_scale="neighbourhood", waterfront_type="lake")
    assert "river_restoration" not in on_a_lake["nbs_types"]
    assert "urban_lake_restoration" in on_a_lake["nbs_types"]


def test_a_constructed_water_feature_needs_no_existing_water_body(client: TestClient) -> None:
    """The four constructed features carry no waterfront condition (D-038)."""
    offered = _available(client, assessment_scale="neighbourhood")["nbs_types"]
    for constructed in ("constructed_wetland", "retention_pond", "detention_basin", "water_square"):
        assert constructed in offered


def test_the_railway_corridor_is_offered_only_on_a_railway_site(client: TestClient) -> None:
    """Exactly one entry is gated by the railway question."""
    assert "railway_green_corridor" not in _available(client, assessment_scale="city")["nbs_types"]
    assert (
        "railway_green_corridor"
        not in (_available(client, assessment_scale="city", includes_railway=False)["nbs_types"])
    )
    assert (
        "railway_green_corridor"
        in (_available(client, assessment_scale="city", includes_railway=True)["nbs_types"])
    )


def test_woodland_restoration_needs_woodland_but_woodland_creation_does_not(
    client: TestClient,
) -> None:
    """Only the restoration types act on woodland that is already there."""
    unanswered = _available(client, assessment_scale="neighbourhood")["nbs_types"]
    assert "degraded_woodland_restoration" not in unanswered
    assert "reforestation" not in unanswered
    # The creation types are offered regardless.
    for creation in ("urban_woodland_site", "microforest", "afforestation"):
        assert creation in unanswered

    with_woodland = _available(client, assessment_scale="neighbourhood", existing_woodland=True)[
        "nbs_types"
    ]
    assert "degraded_woodland_restoration" in with_woodland
    assert "reforestation" in with_woodland


def test_an_unanswered_governance_question_suppresses_nothing(client: TestClient) -> None:
    """D-043.3: silence is not a "no one can deliver this".

    The multi-select filters when answered and suppresses nothing when empty —
    the tool never asserts a negative from absent information.
    """
    unanswered = _available(client, assessment_scale="neighbourhood")["nbs_types"]
    for productive in ("community_garden", "allotment_garden", "urban_farm", "school_garden"):
        assert productive in unanswered


def test_answering_governance_filters_to_the_named_delivery_models(client: TestClient) -> None:
    commercial_only = _available(
        client, assessment_scale="neighbourhood", productive_governance=["commercial"]
    )["nbs_types"]
    assert "community_garden" not in commercial_only
    assert "allotment_garden" not in commercial_only
    assert "school_garden" not in commercial_only
    assert "urban_farm" in commercial_only

    both = _available(
        client,
        assessment_scale="neighbourhood",
        productive_governance=["commercial", "community"],
    )["nbs_types"]
    assert "community_garden" in both
    assert "urban_farm" in both


def test_land_use_filters_but_leaving_it_unanswered_does_not(client: TestClient) -> None:
    """A site that has not said what it is is never filtered on that basis."""
    unanswered = _available(client, assessment_scale="neighbourhood")
    industrial = _available(client, assessment_scale="neighbourhood", land_use="industrial")
    assert industrial["count"] < unanswered["count"]
    assert set(industrial["nbs_types"]) <= set(unanswered["nbs_types"])


def test_available_refuses_an_unknown_scale_or_condition_value(client: TestClient) -> None:
    """The gating vocabularies are configuration, not free text."""
    assert client.get("/api/typologies/available").status_code == 422
    assert (
        client.get("/api/typologies/available", params={"assessment_scale": "planet"}).status_code
        == 422
    )
    assert (
        client.get(
            "/api/typologies/available",
            params={"assessment_scale": "neighbourhood", "waterfront_type": "canal"},
        ).status_code
        == 422
    )
    assert (
        client.get(
            "/api/typologies/available",
            params={"assessment_scale": "neighbourhood", "productive_governance": ["municipal"]},
        ).status_code
        == 422
    )


def test_methodology_serves_the_loaded_configuration(
    client: TestClient, config: MethodologyConfig
) -> None:
    response = client.get("/api/methodology")
    assert response.status_code == 200
    body = response.json()
    assert body["version"] == config.version
    assert body["weights"] == config.weights
    assert body["adjustment_factors"] == config.adjustment_factors
    assert body["input_mapping"] == config.input_mapping
    assert body["energy_model"] == config.energy_model
    assert body["country_defaults"] == config.country_defaults
    assert body["derived_scores"] == config.derived_scores
    assert body["recommendation_templates"] == config.recommendation_templates
    # Gating is configuration, not code (D-044.1): the availability policy is
    # served with the rest of the methodology, so the rule can be read.
    assert body["availability"] == config.availability
