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
    minimal_input["nbs_type"] = "not_a_typology"
    response = client.post("/api/assessments/evaluate", json=minimal_input)
    assert response.status_code == 422
    assert response.json() == {"detail": "unknown nbs_type: 'not_a_typology'"}
