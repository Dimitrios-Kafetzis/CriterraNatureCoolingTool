"""The map-picker endpoints, and the autofill provenance record (D-047, v2.1).

Two contracts are load-bearing here and neither is about geography.

**Only three inputs may be autofilled.** The set is closed at the API boundary,
not merely by what the interface happens to send, so that "the map fills in
three inputs" stays true as the questionnaire grows. Filling in canopy,
imperviousness or LST from imagery is the GIS workflow deferred by D-002.

**An autofilled value is marked, and the mark never outlives the value.** A
field the user overrides or clears loses its mark on the way in, whatever a
stale client keeps sending.
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from nature_cooling.api.schemas import AUTOFILLABLE_FIELDS

ATHENS = {"latitude": 37.9838, "longitude": 23.7275}


def _project(client: TestClient) -> str:
    return str(client.post("/api/projects", json={"name": "Riverside pilot"}).json()["project_id"])


def _assessment(client: TestClient, project_id: str, **body: Any) -> dict[str, Any]:
    payload = {"label": "Option A", **body}
    response = client.post(f"/api/projects/{project_id}/assessments", json=payload)
    assert response.status_code == 201, response.text
    return dict(response.json())


# --- The lookup endpoint -----------------------------------------------------


def test_a_point_returns_the_country_and_climate_zone(client: TestClient) -> None:
    body = client.post("/api/geo/lookup", json=ATHENS).json()
    assert body["country"]["iso_a2"] == "GR"
    assert body["climate"]["zone"] == "temperate"
    assert body["climate"]["koppen_class"] == "Csa"
    assert body["site_area_m2"] is None, "no polygon was drawn, so no area is invented"


def test_a_drawn_polygon_returns_its_area(client: TestClient) -> None:
    payload = {
        **ATHENS,
        "boundary": [
            [23.7275, 37.9838],
            [23.7285, 37.9838],
            [23.7285, 37.9848],
            [23.7275, 37.9848],
        ],
    }
    body = client.post("/api/geo/lookup", json=payload).json()
    assert body["site_area_m2"] is not None
    assert 8_000 < body["site_area_m2"] < 12_000


def test_the_response_carries_the_attribution_the_licences_require(client: TestClient) -> None:
    body = client.post("/api/geo/lookup", json=ATHENS).json()
    assert "CC BY 4.0" in body["climate"]["attribution"]
    assert "Natural Earth" in body["country"]["attribution"]
    assert body["climate"]["note"]
    assert body["climate"]["resolution_caveat"]


def test_an_unclassifiable_point_returns_nulls_rather_than_a_guess(client: TestClient) -> None:
    body = client.post("/api/geo/lookup", json={"latitude": 30.0, "longitude": -40.0}).json()
    assert body["country"]["iso_a2"] is None
    assert body["climate"]["zone"] is None
    assert body["country"]["matched"] == "none"


@pytest.mark.parametrize(
    "payload",
    [
        {"latitude": 91.0, "longitude": 0.0},
        {"latitude": 0.0, "longitude": 181.0},
        {"latitude": 0.0, "longitude": 0.0, "boundary": [[0.0]]},
        {"latitude": 0.0, "longitude": 0.0, "boundary": [[500.0, 0.0]]},
    ],
)
def test_an_out_of_range_location_is_refused(client: TestClient, payload: dict[str, Any]) -> None:
    assert client.post("/api/geo/lookup", json=payload).status_code == 422


def test_the_basemap_is_served_from_the_bundled_data(client: TestClient) -> None:
    """It is served locally precisely so the default build fetches no tiles."""
    body = client.get("/api/geo/basemap").json()
    assert body["scale"] == "1:110m"
    assert body["licence"] == "public domain"
    assert len(body["countries"]) > 150


# --- The provenance record ---------------------------------------------------


def test_only_the_three_derivable_inputs_may_be_marked_as_autofilled() -> None:
    """The closed set is the mechanism by which D-047's boundary holds."""
    assert {"site_area_m2", "country", "climate_zone"} == AUTOFILLABLE_FIELDS


@pytest.mark.parametrize(
    "field",
    ["existing_tree_canopy_percent", "impervious_surface_percent", "lst_anomaly_c", "land_use"],
)
def test_marking_a_gis_derived_input_as_autofilled_is_refused(
    client: TestClient, field: str
) -> None:
    """Deriving these from imagery is the GIS workflow D-002 deferred.

    They would demo extremely well, and they are the tool's most
    decision-relevant site inputs — which is exactly why the refusal is
    enforced here rather than left to the interface's good manners.
    """
    project_id = _project(client)
    response = client.post(
        f"/api/projects/{project_id}/assessments",
        json={"label": "Option A", "input": {field: 30.0}, "autofilled": {field: "beck2023"}},
    )
    assert response.status_code == 422
    assert "may be autofilled" in response.text


def test_an_autofilled_value_is_stored_with_the_dataset_it_came_from(
    client: TestClient,
) -> None:
    project_id = _project(client)
    stored = _assessment(
        client,
        project_id,
        input={"climate_zone": "temperate", "country": "GR"},
        autofilled={"climate_zone": "beck2023", "country": "naturalearth"},
    )
    assert stored["autofilled"] == {"climate_zone": "beck2023", "country": "naturalearth"}


def test_a_mark_for_a_field_that_was_never_supplied_is_dropped(client: TestClient) -> None:
    """The mark would otherwise outlive the value it describes, and the report
    would itemise provenance for an answer that is not there."""
    project_id = _project(client)
    stored = _assessment(client, project_id, input={}, autofilled={"climate_zone": "beck2023"})
    assert stored["autofilled"] == {}


def test_overriding_an_autofilled_answer_removes_its_mark(client: TestClient) -> None:
    """A user who disagrees with the classification overrides it, and the
    marking disappears with it (D-047.2)."""
    project_id = _project(client)
    stored = _assessment(
        client,
        project_id,
        input={"climate_zone": "temperate"},
        autofilled={"climate_zone": "beck2023"},
    )
    assessment_id = stored["assessment_id"]

    patched = client.patch(
        f"/api/projects/{project_id}/assessments/{assessment_id}",
        json={"input": {"climate_zone": "arid"}, "autofilled": {}},
    ).json()
    assert patched["input"]["climate_zone"] == "arid"
    assert patched["autofilled"] == {}


def test_a_stale_mark_is_dropped_even_if_the_client_keeps_sending_it(
    client: TestClient,
) -> None:
    """The marking follows the data, not the client's memory of it."""
    project_id = _project(client)
    stored = _assessment(
        client,
        project_id,
        input={"climate_zone": "temperate"},
        autofilled={"climate_zone": "beck2023"},
    )
    assessment_id = stored["assessment_id"]

    # The user cleared the answer; the client still claims it was autofilled.
    patched = client.patch(
        f"/api/projects/{project_id}/assessments/{assessment_id}",
        json={"input": {}, "autofilled": {"climate_zone": "beck2023"}},
    ).json()
    assert patched["autofilled"] == {}


def test_patching_the_input_alone_re_settles_the_marks(client: TestClient) -> None:
    """A client that patches an override without mentioning provenance must not
    leave a value marked as autofilled when it is no longer."""
    project_id = _project(client)
    stored = _assessment(
        client,
        project_id,
        input={"climate_zone": "temperate", "country": "GR"},
        autofilled={"climate_zone": "beck2023", "country": "naturalearth"},
    )
    assessment_id = stored["assessment_id"]

    patched = client.patch(
        f"/api/projects/{project_id}/assessments/{assessment_id}",
        json={"input": {"climate_zone": "temperate"}},
    ).json()
    assert patched["autofilled"] == {"climate_zone": "beck2023"}, "country is gone, so its mark is"


def test_patching_provenance_alone_is_settled_against_the_stored_input(
    client: TestClient,
) -> None:
    project_id = _project(client)
    stored = _assessment(client, project_id, input={"country": "GR"})
    assessment_id = stored["assessment_id"]

    patched = client.patch(
        f"/api/projects/{project_id}/assessments/{assessment_id}",
        json={"autofilled": {"country": "naturalearth", "climate_zone": "beck2023"}},
    ).json()
    assert patched["autofilled"] == {"country": "naturalearth"}


def test_a_duplicate_carries_the_site_provenance_forward(client: TestClient) -> None:
    """All three autofillable fields describe the site, so they survive
    duplication — and their provenance must survive with them (D-021)."""
    project_id = _project(client)
    stored = _assessment(
        client,
        project_id,
        input={"climate_zone": "temperate", "site_area_m2": 6000.0},
        autofilled={"climate_zone": "beck2023", "site_area_m2": "drawn_polygon"},
    )
    duplicate = client.post(
        f"/api/projects/{project_id}/assessments/{stored['assessment_id']}/duplicate"
    ).json()
    assert duplicate["autofilled"] == {
        "climate_zone": "beck2023",
        "site_area_m2": "drawn_polygon",
    }


def test_an_assessment_created_without_a_map_carries_an_empty_record(
    client: TestClient,
) -> None:
    """The common case: the questionnaire is fully usable without a map."""
    project_id = _project(client)
    assert _assessment(client, project_id, input={"country": "GR"})["autofilled"] == {}


# --- Confidence is unaffected, by construction -------------------------------


def test_an_autofilled_value_counts_as_supplied_exactly_as_a_typed_one_does(
    client: TestClient,
) -> None:
    """D-047.2, and the perversity it was ruled to avoid.

    Clicking the map and typing the same climate zone must not produce
    different confidence readings for identical inputs — that would teach users
    the confidence meter measures effort rather than information. The engine
    reads the validated input and has no idea where a value came from, so this
    holds by construction; the test is here to keep it that way.
    """
    draft = {
        "assessment_scale": "neighbourhood",
        "site_area_m2": 6000.0,
        "climate_zone": "temperate",
        "country": "GR",
        "nbs_type": ["tree_avenue"],
    }
    project_id = _project(client)
    typed = _assessment(client, project_id, input=draft)
    mapped = _assessment(
        client,
        project_id,
        input=dict(draft),
        autofilled={
            "climate_zone": "beck2023",
            "country": "naturalearth",
            "site_area_m2": "drawn_polygon",
        },
    )
    assert mapped["autofilled"], "the marks were in fact recorded"

    def evaluate(assessment: dict[str, Any]) -> dict[str, Any]:
        response = client.post(
            f"/api/projects/{project_id}/assessments/{assessment['assessment_id']}/evaluate"
        )
        assert response.status_code == 200, response.text
        return dict(response.json()["result"])

    typed_result = evaluate(typed)
    mapped_result = evaluate(mapped)
    assert typed_result["confidence"] == mapped_result["confidence"]
    # And not only the confidence: identical answers must score identically,
    # whatever route they arrived by.
    assert typed_result["opportunity"] == mapped_result["opportunity"]


def test_an_explicit_null_boundary_is_a_placed_point(client: TestClient) -> None:
    """A client that sends the field as null means the same as omitting it."""
    body = client.post("/api/geo/lookup", json={**ATHENS, "boundary": None}).json()
    assert body["country"]["iso_a2"] == "GR"
    assert body["site_area_m2"] is None


def test_patching_with_an_explicit_null_leaves_the_marks_alone(client: TestClient) -> None:
    """``null`` is "I am not saying anything about provenance", which is not the
    same as ``{}`` — "there is no provenance"."""
    project_id = _project(client)
    stored = _assessment(
        client,
        project_id,
        input={"climate_zone": "temperate"},
        autofilled={"climate_zone": "beck2023"},
    )
    patched = client.patch(
        f"/api/projects/{project_id}/assessments/{stored['assessment_id']}",
        json={"label": "Renamed", "autofilled": None},
    ).json()
    assert patched["autofilled"] == {"climate_zone": "beck2023"}
