"""Project and assessment CRUD over the local-first store (D-020, D-028).

Domain rules enforced here, not in storage:

* A stored result is never recomputed (OQ-15). Evaluating an assessment that
  already has a result is refused (409); a newer methodology version is only
  ever *surfaced* via ``methodology_update_available``, and re-running is an
  explicit user action that creates a new assessment.
* Once evaluated, an assessment's input is frozen — editing it would detach
  the stored result from the answers that produced it. Its label stays
  editable.
* Duplication (D-021) carries the site and vulnerability description forward
  and blanks the intervention and cost/energy groups, so a comparison isolates
  the option, not re-typed site data.
"""

from __future__ import annotations

from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import ValidationError

from nature_cooling.api.schemas import (
    SITE_DESCRIPTION_FIELDS,
    STORAGE_SCHEMA_VERSION,
    AssessmentCreate,
    AssessmentDuplicate,
    AssessmentPatch,
    AssessmentView,
    Project,
    ProjectCreate,
    ProjectPatch,
    ProjectSummary,
    ProjectView,
    StoredAssessment,
)
from nature_cooling.api.storage import ProjectNotFoundError, ProjectStore, utc_now_iso
from nature_cooling.api.validation import issues_from
from nature_cooling.engine import run_assessment
from nature_cooling.engine.config import MethodologyConfig
from nature_cooling.engine.models import AssessmentInput

router = APIRouter(prefix="/projects", tags=["projects"])


def _store(request: Request) -> ProjectStore:
    store: ProjectStore = request.app.state.store
    return store


def _config(request: Request) -> MethodologyConfig:
    config: MethodologyConfig = request.app.state.config
    return config


def _load(request: Request, project_id: UUID) -> Project:
    try:
        return _store(request).load(str(project_id))
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"project not found: {project_id}") from exc


def _assessment(project: Project, assessment_id: UUID) -> StoredAssessment:
    for stored in project.assessments:
        if stored.assessment_id == str(assessment_id):
            return stored
    raise HTTPException(status_code=404, detail=f"assessment not found: {assessment_id}")


def _view(request: Request, stored: StoredAssessment) -> AssessmentView:
    return AssessmentView.of(stored, _config(request).version)


@router.get("")
def list_projects(request: Request) -> list[ProjectSummary]:
    """All projects, most recently updated first."""
    return [ProjectSummary.of(project) for project in _store(request).list_all()]


@router.post("", status_code=201)
def create_project(body: ProjectCreate, request: Request) -> ProjectView:
    now = utc_now_iso()
    project = Project(
        schema_version=STORAGE_SCHEMA_VERSION,
        project_id=str(uuid4()),
        name=body.name,
        created_at=now,
        updated_at=now,
        site=body.site,
        assessments=[],
    )
    _store(request).save(project)
    return ProjectView.of(project, _config(request).version)


@router.get("/{project_id}")
def get_project(project_id: UUID, request: Request) -> ProjectView:
    return ProjectView.of(_load(request, project_id), _config(request).version)


@router.patch("/{project_id}")
def update_project(project_id: UUID, body: ProjectPatch, request: Request) -> ProjectView:
    project = _load(request, project_id)
    if body.name is not None:
        project.name = body.name
    if body.site is not None:
        project.site = body.site
    project.updated_at = utc_now_iso()
    _store(request).save(project)
    return ProjectView.of(project, _config(request).version)


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: UUID, request: Request) -> Response:
    try:
        _store(request).delete(str(project_id))
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"project not found: {project_id}") from exc
    return Response(status_code=204)


@router.post("/{project_id}/assessments", status_code=201)
def create_assessment(project_id: UUID, body: AssessmentCreate, request: Request) -> AssessmentView:
    project = _load(request, project_id)
    stored = StoredAssessment(
        assessment_id=str(uuid4()),
        label=body.label,
        created_at=utc_now_iso(),
        input=body.input,
        result=None,
    )
    project.assessments.append(stored)
    project.updated_at = utc_now_iso()
    _store(request).save(project)
    return _view(request, stored)


@router.get("/{project_id}/assessments/{assessment_id}")
def get_assessment(project_id: UUID, assessment_id: UUID, request: Request) -> AssessmentView:
    return _view(request, _assessment(_load(request, project_id), assessment_id))


@router.patch("/{project_id}/assessments/{assessment_id}")
def update_assessment(
    project_id: UUID, assessment_id: UUID, body: AssessmentPatch, request: Request
) -> AssessmentView:
    project = _load(request, project_id)
    stored = _assessment(project, assessment_id)
    if body.input is not None and stored.result is not None:
        raise HTTPException(
            status_code=409,
            detail="assessment already evaluated; its input is frozen. "
            "Duplicate it or create a new assessment to change the input.",
        )
    if body.label is not None:
        stored.label = body.label
    if body.input is not None:
        stored.input = body.input
    project.updated_at = utc_now_iso()
    _store(request).save(project)
    return _view(request, stored)


@router.delete("/{project_id}/assessments/{assessment_id}", status_code=204)
def delete_assessment(project_id: UUID, assessment_id: UUID, request: Request) -> Response:
    project = _load(request, project_id)
    stored = _assessment(project, assessment_id)
    project.assessments.remove(stored)
    project.updated_at = utc_now_iso()
    _store(request).save(project)
    return Response(status_code=204)


@router.post("/{project_id}/assessments/{assessment_id}/evaluate")
def evaluate_assessment(project_id: UUID, assessment_id: UUID, request: Request) -> AssessmentView:
    """Run the engine on the stored draft input and persist the result.

    An explicit user action (OQ-15): refused once a result exists, because a
    stored result is never recomputed — re-running means creating a new
    assessment.
    """
    project = _load(request, project_id)
    stored = _assessment(project, assessment_id)
    if stored.result is not None:
        raise HTTPException(
            status_code=409,
            detail="assessment already evaluated; stored results are never recomputed. "
            "Duplicate it or create a new assessment to re-run.",
        )
    try:
        inp = AssessmentInput.model_validate(stored.input)
    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=[issue.model_dump() for issue in issues_from(exc)],
        ) from exc
    try:
        result = run_assessment(inp, _config(request))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    stored.result = result.model_dump(mode="json")
    project.updated_at = utc_now_iso()
    _store(request).save(project)
    return _view(request, stored)


@router.post("/{project_id}/assessments/{assessment_id}/duplicate", status_code=201)
def duplicate_assessment(
    project_id: UUID,
    assessment_id: UUID,
    request: Request,
    body: AssessmentDuplicate | None = None,
) -> AssessmentView:
    """Create a comparison draft from an existing assessment (D-021)."""
    project = _load(request, project_id)
    source = _assessment(project, assessment_id)
    label = f"{source.label} (copy)" if body is None or body.label is None else body.label
    duplicate = StoredAssessment(
        assessment_id=str(uuid4()),
        label=label,
        created_at=utc_now_iso(),
        input={
            field: value
            for field, value in source.input.items()
            if field in SITE_DESCRIPTION_FIELDS
        },
        result=None,
    )
    project.assessments.append(duplicate)
    project.updated_at = utc_now_iso()
    _store(request).save(project)
    return _view(request, duplicate)
