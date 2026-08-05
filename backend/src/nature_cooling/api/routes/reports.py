"""Report export endpoints (D-033, OQ-15).

Reports render **stored** results only: the builders receive the stored
input and result verbatim and never call the engine. A draft without a
result is refused with 409, consistent with the D-029 evaluation-state
rules; unknown identifiers are 404. Same stored assessment → byte-identical
response body, in both formats.

The v2.4 comparison endpoints follow the same rules over 2–4 assessments of
one project: the count is enforced at the parameter layer, every compared
assessment must hold a stored result, and the ids' order is the caller's —
it is the column order the user chose.
"""

from __future__ import annotations

import re
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Request, Response

from nature_cooling.api.routes.projects import _assessment, _load
from nature_cooling.api.schemas import Project, StoredAssessment
from nature_cooling.report import (
    ScenarioSource,
    build_comparison_pdf_report,
    build_comparison_xlsx_report,
    build_pdf_report,
    build_xlsx_report,
)

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


# 2–4 scenarios: fewer than two is not a comparison, and beyond four the
# side-by-side table stops being readable on one page width (v2.4 brief).
_ComparisonIds = Annotated[list[UUID], Query(min_length=2, max_length=4)]


def _comparison_scenarios(project: Project, assessment_ids: list[UUID]) -> list[ScenarioSource]:
    """Resolve the requested ids, in the caller's order, to stored scenarios.

    A repeated id is refused: comparing a scenario against itself states
    nothing, and silently deduplicating would change the column count the
    caller asked for.
    """
    if len(set(assessment_ids)) != len(assessment_ids):
        raise HTTPException(status_code=422, detail="assessment ids must be distinct to compare")
    scenarios = []
    for assessment_id in assessment_ids:
        stored = _evaluated(project, assessment_id)
        scenarios.append(
            ScenarioSource(
                label=stored.label,
                created_at=stored.created_at,
                inp=stored.input,
                result=stored.result or {},
                autofilled=stored.autofilled,
            )
        )
    return scenarios


def _comparison_filename(project: Project, extension: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", f"{project.name}-comparison").strip("-").lower()
    return f"{slug}.{extension}"


@router.get(
    "/{project_id}/report/comparison.pdf",
    responses=_BINARY_RESPONSE,
    response_class=Response,
)
def comparison_pdf(project_id: UUID, request: Request, assessments: _ComparisonIds) -> Response:
    """The comparison PDF over 2–4 stored, evaluated assessments (v2.4)."""
    project = _load(request, project_id)
    payload = build_comparison_pdf_report(
        project_name=project.name,
        scenarios=_comparison_scenarios(project, assessments),
    )
    return _download(payload, "application/pdf", _comparison_filename(project, "pdf"))


@router.get(
    "/{project_id}/report/comparison.xlsx",
    responses=_BINARY_RESPONSE,
    response_class=Response,
)
def comparison_xlsx(project_id: UUID, request: Request, assessments: _ComparisonIds) -> Response:
    """The comparison workbook over 2–4 stored, evaluated assessments (v2.4)."""
    project = _load(request, project_id)
    payload = build_comparison_xlsx_report(
        project_name=project.name,
        scenarios=_comparison_scenarios(project, assessments),
    )
    return _download(
        payload,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        _comparison_filename(project, "xlsx"),
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
        autofilled=stored.autofilled,
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
        autofilled=stored.autofilled,
    )
    return _download(
        payload,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        _filename(project, stored, "xlsx"),
    )
