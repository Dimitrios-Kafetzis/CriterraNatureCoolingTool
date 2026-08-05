"""Contract tests: the v2.4 comparison export under
/api/projects/{id}/report/comparison.{pdf,xlsx}.

Same rules as the single-assessment export (D-033, OQ-15) over 2–4
assessments: stored results only, 409 for any unevaluated draft, 404 for
unknown ids — and the ids' order is the caller's column order.
"""

from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

from nature_cooling.report import (
    ScenarioSource,
    build_comparison_pdf_report,
    build_comparison_xlsx_report,
)

_MISSING_ID = "00000000-0000-0000-0000-000000000000"

_XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _project_with_options(
    client: TestClient,
    full_draft: dict[str, Any],
    labels: tuple[str, ...] = ("Option A", "Option B"),
) -> tuple[str, list[dict[str, Any]]]:
    project_id: str = client.post("/api/projects", json={"name": "Riverside pilot"}).json()[
        "project_id"
    ]
    evaluated = []
    for label in labels:
        created = client.post(
            f"/api/projects/{project_id}/assessments",
            json={"label": label, "input": full_draft},
        ).json()
        evaluated.append(
            client.post(
                f"/api/projects/{project_id}/assessments/{created['assessment_id']}/evaluate"
            ).json()
        )
    return project_id, evaluated


def _url(project_id: str, extension: str, ids: list[str]) -> str:
    query = "&".join(f"assessments={assessment_id}" for assessment_id in ids)
    return f"/api/projects/{project_id}/report/comparison.{extension}?{query}"


def _sources(stored: list[dict[str, Any]]) -> list[ScenarioSource]:
    return [
        ScenarioSource(
            label=item["label"],
            created_at=item["created_at"],
            inp=item["input"],
            result=item["result"],
            autofilled=item["autofilled"],
        )
        for item in stored
    ]


def test_comparison_pdf_renders_the_stored_results_verbatim(
    client: TestClient, full_draft: dict[str, Any]
) -> None:
    project_id, stored = _project_with_options(client, full_draft)
    ids = [item["assessment_id"] for item in stored]
    response = client.get(_url(project_id, "pdf", ids))
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["content-disposition"] == (
        'attachment; filename="riverside-pilot-comparison.pdf"'
    )
    assert response.content.startswith(b"%PDF")
    # Exactly the builder's bytes for the stored documents — nothing recomputed.
    expected = build_comparison_pdf_report(
        project_name="Riverside pilot", scenarios=_sources(stored)
    )
    assert response.content == expected


def test_comparison_xlsx_renders_the_stored_results_verbatim(
    client: TestClient, full_draft: dict[str, Any]
) -> None:
    project_id, stored = _project_with_options(client, full_draft)
    ids = [item["assessment_id"] for item in stored]
    response = client.get(_url(project_id, "xlsx", ids))
    assert response.status_code == 200
    assert response.headers["content-type"] == _XLSX_MEDIA_TYPE
    assert response.headers["content-disposition"] == (
        'attachment; filename="riverside-pilot-comparison.xlsx"'
    )
    assert response.content.startswith(b"PK")
    expected = build_comparison_xlsx_report(
        project_name="Riverside pilot", scenarios=_sources(stored)
    )
    assert response.content == expected


def test_the_ids_order_is_the_column_order(client: TestClient, full_draft: dict[str, Any]) -> None:
    project_id, stored = _project_with_options(client, full_draft)
    ids = [item["assessment_id"] for item in stored]
    forward = client.get(_url(project_id, "xlsx", ids))
    reversed_order = client.get(_url(project_id, "xlsx", list(reversed(ids))))
    assert forward.status_code == reversed_order.status_code == 200
    assert forward.content != reversed_order.content


def test_repeated_downloads_are_byte_identical(
    client: TestClient, full_draft: dict[str, Any]
) -> None:
    project_id, stored = _project_with_options(client, full_draft)
    ids = [item["assessment_id"] for item in stored]
    for extension in ("pdf", "xlsx"):
        url = _url(project_id, extension, ids)
        assert client.get(url).content == client.get(url).content


def test_any_unevaluated_draft_is_refused_with_409(
    client: TestClient, full_draft: dict[str, Any]
) -> None:
    project_id, stored = _project_with_options(client, full_draft, labels=("Option A",))
    draft = client.post(
        f"/api/projects/{project_id}/assessments",
        json={"label": "Draft", "input": full_draft},
    ).json()
    ids = [stored[0]["assessment_id"], draft["assessment_id"]]
    for extension in ("pdf", "xlsx"):
        response = client.get(_url(project_id, extension, ids))
        assert response.status_code == 409
        assert "stored results only" in response.json()["detail"]


def test_unknown_ids_are_404(client: TestClient, full_draft: dict[str, Any]) -> None:
    project_id, stored = _project_with_options(client, full_draft)
    ids = [item["assessment_id"] for item in stored]
    for extension in ("pdf", "xlsx"):
        missing_project = client.get(_url(_MISSING_ID, extension, ids))
        assert missing_project.status_code == 404
        assert missing_project.json() == {"detail": f"project not found: {_MISSING_ID}"}
        missing_assessment = client.get(_url(project_id, extension, [ids[0], _MISSING_ID]))
        assert missing_assessment.status_code == 404
        assert missing_assessment.json() == {"detail": f"assessment not found: {_MISSING_ID}"}


def test_fewer_than_two_or_more_than_four_ids_are_422(
    client: TestClient, full_draft: dict[str, Any]
) -> None:
    project_id, stored = _project_with_options(client, full_draft, labels=("A", "B", "C", "D", "E"))
    ids = [item["assessment_id"] for item in stored]
    for extension in ("pdf", "xlsx"):
        assert client.get(_url(project_id, extension, ids[:1])).status_code == 422
        assert client.get(_url(project_id, extension, ids)).status_code == 422


def test_repeated_ids_are_422(client: TestClient, full_draft: dict[str, Any]) -> None:
    """Comparing a scenario against itself states nothing, and silently
    deduplicating would change the column count the caller asked for."""
    project_id, stored = _project_with_options(client, full_draft)
    ids = [stored[0]["assessment_id"], stored[0]["assessment_id"]]
    for extension in ("pdf", "xlsx"):
        response = client.get(_url(project_id, extension, ids))
        assert response.status_code == 422
        assert response.json() == {"detail": "assessment ids must be distinct to compare"}
