"""Contract tests: POST /api/assessments/evaluate."""

from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

from nature_cooling.engine import run_assessment
from nature_cooling.engine.config import MethodologyConfig
from nature_cooling.engine.models import AssessmentInput


def test_evaluate_returns_the_engine_result_verbatim(
    client: TestClient, config: MethodologyConfig, minimal_input: dict[str, Any]
) -> None:
    response = client.post("/api/assessments/evaluate", json=minimal_input)
    assert response.status_code == 200
    expected = run_assessment(AssessmentInput.model_validate(minimal_input), config)
    assert response.json() == expected.model_dump(mode="json")


def test_evaluate_is_byte_deterministic(client: TestClient, minimal_input: dict[str, Any]) -> None:
    first = client.post("/api/assessments/evaluate", json=minimal_input)
    second = client.post("/api/assessments/evaluate", json=minimal_input)
    assert first.status_code == second.status_code == 200
    assert first.content == second.content


def test_evaluate_rejects_an_invalid_body(
    client: TestClient, minimal_input: dict[str, Any]
) -> None:
    minimal_input["site_area_m2"] = -1
    response = client.post("/api/assessments/evaluate", json=minimal_input)
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert any(item["loc"][-1] == "site_area_m2" for item in detail)


def test_evaluate_rejects_a_missing_required_field(
    client: TestClient, minimal_input: dict[str, Any]
) -> None:
    del minimal_input["climate_zone"]
    response = client.post("/api/assessments/evaluate", json=minimal_input)
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert any(item["loc"][-1] == "climate_zone" and item["type"] == "missing" for item in detail)


def test_evaluate_rejects_an_unknown_typology(
    client: TestClient, minimal_input: dict[str, Any]
) -> None:
    minimal_input["nbs_type"] = ["not_a_typology"]
    response = client.post("/api/assessments/evaluate", json=minimal_input)
    assert response.status_code == 422
    assert response.json() == {"detail": "unknown nbs_type: 'not_a_typology'"}


def test_evaluate_rejects_a_bare_string_typology(
    client: TestClient, minimal_input: dict[str, Any]
) -> None:
    """``nbs_type`` is a list since D-044.2; a bare string is a schema error.

    Storage migrates an older *stored* draft explicitly (D-029); the API itself
    never quietly reinterprets a request body.
    """
    minimal_input["nbs_type"] = "tree_avenue"
    response = client.post("/api/assessments/evaluate", json=minimal_input)
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert any(item["loc"][-1] == "nbs_type" and item["type"] == "list_type" for item in detail)


def test_evaluate_scores_a_package_component_by_component(
    client: TestClient, config: MethodologyConfig, package_draft: dict[str, Any]
) -> None:
    """D-038/D-044.4: every component is itemised and the package says how it combined.

    The top-level blocks are the package's; the representative component is the
    one whose adjusted range the package reports, and the temperature is never
    the sum of the parts.
    """
    response = client.post("/api/assessments/evaluate", json=package_draft)
    assert response.status_code == 200
    body = response.json()
    expected = run_assessment(AssessmentInput.model_validate(package_draft), config)
    assert body == expected.model_dump(mode="json")

    assert [item["typology"]["nbs_type"] for item in body["components"]] == package_draft[
        "nbs_type"
    ]
    assert body["package"]["component_count"] == 3
    representative = next(item for item in body["components"] if item["is_representative"])
    assert body["package"]["representative_nbs_type"] == representative["typology"]["nbs_type"]
    assert body["cooling"]["delta_t_max_c"] == representative["cooling"]["delta_t_max_c"]
    # Suitability takes the minimum: a package is no more deliverable here than
    # its least suitable component (D-009).
    assert body["suitability"]["score"] == min(
        item["suitability"]["score"] for item in body["components"]
    )


def test_a_single_intervention_is_a_package_of_one(
    client: TestClient, minimal_input: dict[str, Any]
) -> None:
    """Nothing about the single case changed shape: the top-level blocks equal
    its only component's."""
    body = client.post("/api/assessments/evaluate", json=minimal_input).json()
    assert body["package"]["component_count"] == 1
    (component,) = body["components"]
    assert component["is_representative"] is True
    assert body["typology"] == component["typology"]
    assert body["cooling"] == component["cooling"]
    assert body["suitability"] == component["suitability"]
    assert body["co_benefits"] == component["co_benefits"]
    assert body["adjustment"] == component["adjustment"]
