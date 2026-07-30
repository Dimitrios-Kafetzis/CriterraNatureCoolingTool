"""Report export endpoints (D-033, OQ-15).

Reports render **stored** results only: the builders receive the stored
input and result verbatim and never call the engine. A draft without a
result is refused with 409, consistent with the D-029 evaluation-state
rules; unknown identifiers are 404. Same stored assessment → byte-identical
response body, in both formats.
"""

from __future__ import annotations

import re
from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, Response

from nature_cooling.api.routes.projects import _assessment, _load
from nature_cooling.api.schemas import Project, StoredAssessment
from nature_cooling.report import build_pdf_report, build_xlsx_report

router = APIRouter(prefix="/projects", tags=["reports"])

_BINARY_RESPONSE: dict[int | str, dict[str, Any]] = {
    200: {"content": {"application/octet-stream": {}}}
}


def _evaluated(project: Project, assessment_id: UUID) -> StoredAssessment:
    stored = _assessment(project, assessment_id)
    if stored.result is None:
        raise HTTPException(
            status_code=409,
            detail="assessment has not been evaluated; reports render stored results only. "
            "Evaluate the assessment first.",
        )
    return stored


def _filename(project: Project, stored: StoredAssessment, extension: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", f"{project.name}-{stored.label}").strip("-").lower()
    return f"{slug or 'assessment'}.{extension}"


def _download(payload: bytes, media_type: str, filename: str) -> Response:
    return Response(
        content=payload,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/{project_id}/assessments/{assessment_id}/report.pdf",
    responses=_BINARY_RESPONSE,
    response_class=Response,
)
def report_pdf(project_id: UUID, assessment_id: UUID, request: Request) -> Response:
    """The 2-page PDF report of a stored, evaluated assessment."""
    project = _load(request, project_id)
    stored = _evaluated(project, assessment_id)
    payload = build_pdf_report(
        project_name=project.name,
        label=stored.label,
        created_at=stored.created_at,
        inp=stored.input,
        result=stored.result or {},
    )
    return _download(payload, "application/pdf", _filename(project, stored, "pdf"))


@router.get(
    "/{project_id}/assessments/{assessment_id}/report.xlsx",
    responses=_BINARY_RESPONSE,
    response_class=Response,
)
def report_xlsx(project_id: UUID, assessment_id: UUID, request: Request) -> Response:
    """The XLSX workbook (Inputs, Results, Assumptions & Warnings)."""
    project = _load(request, project_id)
    stored = _evaluated(project, assessment_id)
    payload = build_xlsx_report(
        project_name=project.name,
        label=stored.label,
        created_at=stored.created_at,
        inp=stored.input,
        result=stored.result or {},
    )
    return _download(
        payload,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        _filename(project, stored, "xlsx"),
    )
