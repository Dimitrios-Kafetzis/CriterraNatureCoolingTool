"""Contract tests: report export under
/api/projects/{id}/assessments/{aid}/report.{pdf,xlsx} (D-033, OQ-15)."""

from __future__ import annotations

from io import BytesIO
from typing import Any

from fastapi.testclient import TestClient
from pypdf import PdfReader
from tests.api.test_project_assessments import FULL_DRAFT

from nature_cooling.report import build_pdf_report, build_xlsx_report

_MISSING_ID = "00000000-0000-0000-0000-000000000000"

_XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _evaluated_assessment(client: TestClient) -> tuple[str, str, dict[str, Any]]:
    project_id: str = client.post("/api/projects", json={"name": "Riverside pilot"}).json()[
        "project_id"
    ]
    created = client.post(
        f"/api/projects/{project_id}/assessments", json={"label": "Option A", "input": FULL_DRAFT}
    ).json()
    evaluated: dict[str, Any] = client.post(
        f"/api/projects/{project_id}/assessments/{created['assessment_id']}/evaluate"
    ).json()
    return project_id, created["assessment_id"], evaluated


def test_pdf_report_renders_the_stored_result_verbatim(client: TestClient) -> None:
    project_id, assessment_id, stored = _evaluated_assessment(client)
    response = client.get(f"/api/projects/{project_id}/assessments/{assessment_id}/report.pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["content-disposition"] == (
        'attachment; filename="riverside-pilot-option-a.pdf"'
    )
    assert response.content.startswith(b"%PDF")
    # Exactly the builder's bytes for the stored document — nothing recomputed.
    expected = build_pdf_report(
        project_name="Riverside pilot",
        label=stored["label"],
        created_at=stored["created_at"],
        inp=stored["input"],
        result=stored["result"],
    )
    assert response.content == expected
    assert len(PdfReader(BytesIO(response.content)).pages) == 2


def test_xlsx_report_renders_the_stored_result_verbatim(client: TestClient) -> None:
    project_id, assessment_id, stored = _evaluated_assessment(client)
    response = client.get(f"/api/projects/{project_id}/assessments/{assessment_id}/report.xlsx")
    assert response.status_code == 200
    assert response.headers["content-type"] == _XLSX_MEDIA_TYPE
    assert response.headers["content-disposition"] == (
        'attachment; filename="riverside-pilot-option-a.xlsx"'
    )
    assert response.content.startswith(b"PK")
    expected = build_xlsx_report(
        project_name="Riverside pilot",
        label=stored["label"],
        created_at=stored["created_at"],
        inp=stored["input"],
        result=stored["result"],
    )
    assert response.content == expected


def test_repeated_downloads_are_byte_identical(client: TestClient) -> None:
    project_id, assessment_id, _ = _evaluated_assessment(client)
    for extension in ("pdf", "xlsx"):
        url = f"/api/projects/{project_id}/assessments/{assessment_id}/report.{extension}"
        assert client.get(url).content == client.get(url).content


def test_unknown_ids_are_404(client: TestClient) -> None:
    project_id, _, _ = _evaluated_assessment(client)
    for extension in ("pdf", "xlsx"):
        missing_project = client.get(
            f"/api/projects/{_MISSING_ID}/assessments/{_MISSING_ID}/report.{extension}"
        )
        assert missing_project.status_code == 404
        assert missing_project.json() == {"detail": f"project not found: {_MISSING_ID}"}
        missing_assessment = client.get(
            f"/api/projects/{project_id}/assessments/{_MISSING_ID}/report.{extension}"
        )
        assert missing_assessment.status_code == 404
        assert missing_assessment.json() == {"detail": f"assessment not found: {_MISSING_ID}"}


def test_a_draft_without_a_result_is_refused_with_409(client: TestClient) -> None:
    project_id: str = client.post("/api/projects", json={"name": "Riverside pilot"}).json()[
        "project_id"
    ]
    draft = client.post(
        f"/api/projects/{project_id}/assessments", json={"label": "Draft", "input": FULL_DRAFT}
    ).json()
    for extension in ("pdf", "xlsx"):
        response = client.get(
            f"/api/projects/{project_id}/assessments/{draft['assessment_id']}/report.{extension}"
        )
        assert response.status_code == 409
        assert "stored results only" in response.json()["detail"]


def test_awkward_names_still_produce_a_usable_filename(client: TestClient) -> None:
    project_id: str = client.post("/api/projects", json={"name": "***"}).json()["project_id"]
    created = client.post(
        f"/api/projects/{project_id}/assessments", json={"label": "///", "input": FULL_DRAFT}
    ).json()
    client.post(f"/api/projects/{project_id}/assessments/{created['assessment_id']}/evaluate")
    response = client.get(
        f"/api/projects/{project_id}/assessments/{created['assessment_id']}/report.pdf"
    )
    assert response.headers["content-disposition"] == 'attachment; filename="assessment.pdf"'
