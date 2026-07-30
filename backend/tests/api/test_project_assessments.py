"""Contract tests: assessment CRUD, explicit evaluation (OQ-15), and
duplication (D-021) under /api/projects/{id}/assessments."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from nature_cooling.api.schemas import BLANKED_ON_DUPLICATE, SITE_DESCRIPTION_FIELDS
from nature_cooling.engine import run_assessment
from nature_cooling.engine.config import MethodologyConfig
from nature_cooling.engine.models import AssessmentInput

_MISSING_ID = "00000000-0000-0000-0000-000000000000"

# A draft touching every duplication group: carried site/climate/vulnerability
# fields plus blanked intervention, co-benefit override, and cost/energy ones.
FULL_DRAFT: dict[str, Any] = {
    "project_name": "Riverside pilot",
    "assessment_scale": "neighbourhood",
    "country": "GR",
    "site_area_m2": 6000.0,
    "existing_tree_canopy_percent": 15.0,
    "land_use": "residential",
    "climate_zone": "temperate",
    "heat_exposure_level": "high",
    "population_density": "high",
    "vulnerable_population_presence": "medium",
    "nbs_type": "street_tree_planting",
    "intervention_area_m2": 900.0,
    "expected_maturity_period_years": 6.0,
    "implementation_complexity": "medium",
    "maintenance_intensity": "medium",
    "co_benefit_biodiversity": "high",
    "nearby_building_cooling_demand_relevant": "yes",
    "annual_cooling_energy_demand_kwh": 120000.0,
    "energy_price_per_kwh": 0.2,
    "capital_cost": 90000.0,
    "currency": "EUR",
}


def _project(client: TestClient) -> str:
    response = client.post("/api/projects", json={"name": "Riverside pilot"})
    assert response.status_code == 201
    project_id: str = response.json()["project_id"]
    return project_id


def _assessment(
    client: TestClient, project_id: str, label: str = "Option A", **extra: Any
) -> dict[str, Any]:
    response = client.post(
        f"/api/projects/{project_id}/assessments", json={"label": label, **extra}
    )
    assert response.status_code == 201
    body: dict[str, Any] = response.json()
    return body


def test_create_assessment_starts_as_a_draft(client: TestClient) -> None:
    project_id = _project(client)
    body = _assessment(client, project_id, input={"site_area_m2": 6000.0})
    assert body["label"] == "Option A"
    assert body["input"] == {"site_area_m2": 6000.0}
    assert body["result"] is None
    assert body["methodology_update_available"] is False


def test_create_assessment_rejects_unknown_input_fields(client: TestClient) -> None:
    project_id = _project(client)
    response = client.post(
        f"/api/projects/{project_id}/assessments",
        json={"label": "A", "input": {"planted_area_m2": 5.0}},
    )
    assert response.status_code == 422
    assert "unknown assessment input field(s): ['planted_area_m2']" in str(response.json())


def test_get_patch_and_delete_an_assessment(client: TestClient) -> None:
    project_id = _project(client)
    created = _assessment(client, project_id)
    base = f"/api/projects/{project_id}/assessments/{created['assessment_id']}"

    assert client.get(base).json() == created

    patched = client.patch(base, json={"label": "Option A2", "input": FULL_DRAFT})
    assert patched.status_code == 200
    assert patched.json()["label"] == "Option A2"
    assert patched.json()["input"] == FULL_DRAFT

    assert client.delete(base).status_code == 204
    assert client.get(base).status_code == 404
    assert client.get(f"/api/projects/{project_id}").json()["assessments"] == []


def test_patch_assessment_with_explicit_nulls_changes_nothing(client: TestClient) -> None:
    project_id = _project(client)
    created = _assessment(client, project_id, input={"site_area_m2": 6000.0})
    response = client.patch(
        f"/api/projects/{project_id}/assessments/{created['assessment_id']}",
        json={"label": None, "input": None},
    )
    assert response.status_code == 200
    assert response.json()["label"] == created["label"]
    assert response.json()["input"] == {"site_area_m2": 6000.0}


def test_unknown_assessment_is_404(client: TestClient) -> None:
    project_id = _project(client)
    base = f"/api/projects/{project_id}/assessments/{_MISSING_ID}"
    detail = {"detail": f"assessment not found: {_MISSING_ID}"}
    assert client.get(base).json() == detail
    assert client.patch(base, json={"label": "x"}).json() == detail
    assert client.delete(base).status_code == 404
    assert client.post(f"{base}/evaluate").json() == detail
    assert client.post(f"{base}/duplicate").json() == detail


def test_evaluate_stores_the_engine_result_and_bumps_updated_at(
    client: TestClient, config: MethodologyConfig
) -> None:
    project_id = _project(client)
    created = _assessment(client, project_id, input=FULL_DRAFT)
    before = client.get(f"/api/projects/{project_id}").json()["updated_at"]

    response = client.post(
        f"/api/projects/{project_id}/assessments/{created['assessment_id']}/evaluate"
    )
    assert response.status_code == 200
    body = response.json()
    expected = run_assessment(AssessmentInput.model_validate(FULL_DRAFT), config)
    assert body["result"] == expected.model_dump(mode="json")
    assert body["input"] == FULL_DRAFT
    assert body["methodology_update_available"] is False

    after = client.get(f"/api/projects/{project_id}").json()
    assert after["updated_at"] >= before
    assert after["assessments"][0]["result"] == expected.model_dump(mode="json")


def test_evaluate_refuses_to_recompute_a_stored_result(client: TestClient) -> None:
    project_id = _project(client)
    created = _assessment(client, project_id, input=FULL_DRAFT)
    base = f"/api/projects/{project_id}/assessments/{created['assessment_id']}"
    assert client.post(f"{base}/evaluate").status_code == 200

    second = client.post(f"{base}/evaluate")
    assert second.status_code == 409
    assert "never recomputed" in second.json()["detail"]


def test_an_evaluated_assessments_input_is_frozen_but_its_label_is_not(
    client: TestClient,
) -> None:
    project_id = _project(client)
    created = _assessment(client, project_id, input=FULL_DRAFT)
    base = f"/api/projects/{project_id}/assessments/{created['assessment_id']}"
    assert client.post(f"{base}/evaluate").status_code == 200

    frozen = client.patch(base, json={"input": {"site_area_m2": 1.0}})
    assert frozen.status_code == 409
    assert "frozen" in frozen.json()["detail"]

    relabelled = client.patch(base, json={"label": "Option A (final)"})
    assert relabelled.status_code == 200
    assert relabelled.json()["label"] == "Option A (final)"


def test_evaluate_rejects_an_incomplete_draft(client: TestClient) -> None:
    project_id = _project(client)
    created = _assessment(client, project_id, input={"site_area_m2": 6000.0})
    response = client.post(
        f"/api/projects/{project_id}/assessments/{created['assessment_id']}/evaluate"
    )
    assert response.status_code == 422
    fields = {item["field"] for item in response.json()["detail"]}
    assert fields == {"assessment_scale", "climate_zone", "nbs_type"}


def test_evaluate_rejects_an_unknown_typology(client: TestClient) -> None:
    project_id = _project(client)
    created = _assessment(client, project_id, input={**FULL_DRAFT, "nbs_type": "not_a_typology"})
    response = client.post(
        f"/api/projects/{project_id}/assessments/{created['assessment_id']}/evaluate"
    )
    assert response.status_code == 422
    assert response.json() == {"detail": "unknown nbs_type: 'not_a_typology'"}


def test_duplicate_carries_the_site_and_blanks_the_intervention_and_cost_groups(
    client: TestClient,
) -> None:
    project_id = _project(client)
    created = _assessment(client, project_id, input=FULL_DRAFT)
    base = f"/api/projects/{project_id}/assessments/{created['assessment_id']}"
    assert client.post(f"{base}/evaluate").status_code == 200

    response = client.post(f"{base}/duplicate", json={"label": "Option B"})
    assert response.status_code == 201
    body = response.json()
    assert body["assessment_id"] != created["assessment_id"]
    assert body["label"] == "Option B"
    assert body["result"] is None
    assert body["input"] == {
        field: value for field, value in FULL_DRAFT.items() if field in SITE_DESCRIPTION_FIELDS
    }
    assert not set(body["input"]) & BLANKED_ON_DUPLICATE
    # The duplicate is a fresh draft: it can be edited and evaluated.
    assert set(body["input"]) & {"population_density", "heat_exposure_level"}


def test_duplicate_without_a_body_derives_a_label(client: TestClient) -> None:
    project_id = _project(client)
    created = _assessment(client, project_id, label="Option A")
    response = client.post(
        f"/api/projects/{project_id}/assessments/{created['assessment_id']}/duplicate"
    )
    assert response.status_code == 201
    assert response.json()["label"] == "Option A (copy)"


def test_methodology_update_is_surfaced_but_the_result_is_untouched(
    client: TestClient, storage_root: Path
) -> None:
    project_id = _project(client)
    created = _assessment(client, project_id, input=FULL_DRAFT)
    base = f"/api/projects/{project_id}/assessments/{created['assessment_id']}"
    stored_result = client.post(f"{base}/evaluate").json()["result"]

    # Simulate a result written under an older methodology version by editing
    # the stored file directly (the API offers no way to alter a result).
    path = storage_root / f"{project_id}.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    document["assessments"][0]["result"]["methodology_version"] = "2000.01.01"
    path.write_text(json.dumps(document), encoding="utf-8")

    body = client.get(base).json()
    assert body["methodology_update_available"] is True
    assert body["result"] == {**stored_result, "methodology_version": "2000.01.01"}
    # Surfacing is not recomputation: evaluate still refuses (OQ-15).
    assert client.post(f"{base}/evaluate").status_code == 409
