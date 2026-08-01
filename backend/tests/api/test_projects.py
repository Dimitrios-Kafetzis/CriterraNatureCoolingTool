"""Contract tests: project CRUD under /api/projects."""

from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

from nature_cooling.api.schemas import STORAGE_SCHEMA_VERSION
from nature_cooling.engine.config import MethodologyConfig

_MISSING_ID = "00000000-0000-0000-0000-000000000000"


def _create(client: TestClient, name: str = "Riverside pilot", **extra: Any) -> dict[str, Any]:
    response = client.post("/api/projects", json={"name": name, **extra})
    assert response.status_code == 201
    body: dict[str, Any] = response.json()
    return body


def test_create_project_returns_the_full_document(
    client: TestClient, config: MethodologyConfig
) -> None:
    body = _create(client, site={"site_area_m2": 6000.0, "climate_zone": "temperate"})
    assert body["schema_version"] == STORAGE_SCHEMA_VERSION
    assert body["name"] == "Riverside pilot"
    assert body["site"] == {"site_area_m2": 6000.0, "climate_zone": "temperate"}
    assert body["assessments"] == []
    assert body["created_at"] == body["updated_at"]
    assert body["created_at"].endswith("+00:00")
    assert body["current_methodology_version"] == config.version
    # A project this build wrote was never migrated, so it has nothing to
    # itemise (D-029): the notes describe an event, not the project.
    assert body["migrated_notes"] == []


def test_the_availability_answers_are_site_description_and_travel_with_the_project(
    client: TestClient,
) -> None:
    """D-044.1: the four gating answers describe the site, so a project holds them."""
    body = _create(
        client,
        site={
            "includes_railway": "yes",
            "existing_woodland": "no",
            "waterfront_type": "river",
            "productive_governance": ["community", "institutional"],
        },
    )
    assert body["site"]["waterfront_type"] == "river"
    assert body["site"]["productive_governance"] == ["community", "institutional"]


def test_create_project_rejects_unknown_site_fields(client: TestClient) -> None:
    response = client.post("/api/projects", json={"name": "x", "site": {"capital_cost": 100.0}})
    assert response.status_code == 422
    assert "unknown site description field(s): ['capital_cost']" in str(response.json())


def test_create_project_rejects_an_empty_name(client: TestClient) -> None:
    response = client.post("/api/projects", json={"name": ""})
    assert response.status_code == 422


def test_list_projects_returns_summaries_most_recently_updated_first(
    client: TestClient,
) -> None:
    assert client.get("/api/projects").json() == []
    first = _create(client, name="First")
    second = _create(client, name="Second")
    client.patch(f"/api/projects/{first['project_id']}", json={"name": "First renamed"})
    listed = client.get("/api/projects").json()
    assert [item["name"] for item in listed] == ["First renamed", "Second"]
    assert listed[0]["assessment_count"] == 0
    assert set(listed[0]) == {
        "project_id",
        "name",
        "created_at",
        "updated_at",
        "assessment_count",
    }
    assert listed[1]["project_id"] == second["project_id"]


def test_get_project_roundtrips(client: TestClient) -> None:
    created = _create(client)
    fetched = client.get(f"/api/projects/{created['project_id']}")
    assert fetched.status_code == 200
    assert fetched.json() == created


def test_patch_project_updates_name_and_site_and_bumps_updated_at(
    client: TestClient,
) -> None:
    created = _create(client)
    response = client.patch(
        f"/api/projects/{created['project_id']}",
        json={"name": "Renamed", "site": {"land_use": "park"}},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Renamed"
    assert body["site"] == {"land_use": "park"}
    assert body["created_at"] == created["created_at"]
    assert body["updated_at"] >= created["updated_at"]


def test_patch_project_with_explicit_nulls_changes_nothing(client: TestClient) -> None:
    created = _create(client, site={"land_use": "park"})
    response = client.patch(
        f"/api/projects/{created['project_id']}", json={"name": None, "site": None}
    )
    assert response.status_code == 200
    assert response.json()["name"] == created["name"]
    assert response.json()["site"] == {"land_use": "park"}


def test_delete_project_removes_it(client: TestClient) -> None:
    created = _create(client)
    assert client.delete(f"/api/projects/{created['project_id']}").status_code == 204
    assert client.get(f"/api/projects/{created['project_id']}").status_code == 404
    assert client.get("/api/projects").json() == []


def test_unknown_project_is_404_everywhere(client: TestClient) -> None:
    detail = {"detail": f"project not found: {_MISSING_ID}"}
    assert client.get(f"/api/projects/{_MISSING_ID}").json() == detail
    assert client.patch(f"/api/projects/{_MISSING_ID}", json={"name": "x"}).json() == detail
    assert client.delete(f"/api/projects/{_MISSING_ID}").status_code == 404
    assert (
        client.post(f"/api/projects/{_MISSING_ID}/assessments", json={"label": "A"}).status_code
        == 404
    )


def test_a_malformed_project_id_is_rejected(client: TestClient) -> None:
    assert client.get("/api/projects/not-a-uuid").status_code == 422
