"""API-layer schemas: request bodies, response envelopes, and the storage
document format (D-028).

The engine's own ``AssessmentInput`` / ``AssessmentResult`` schemas are used
directly for scoring payloads; the models here exist only for what the engine
deliberately has no concept of — validation feedback, confidence previews,
projects, and stored assessments.

Stored assessment inputs and results are held as plain JSON objects, not
re-validated engine models: a stored result is never recomputed or
reinterpreted (OQ-15), so a later engine schema change must not make older
stored results unreadable. Results are validated exactly once, at the moment
the engine produces them.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from nature_cooling.engine.config import ConfidenceLevel
from nature_cooling.engine.models import AssessmentInput

STORAGE_SCHEMA_VERSION = 1

INPUT_FIELDS = frozenset(AssessmentInput.model_fields)

# The questionnaire groups blanked by the duplicate-assessment operation
# (D-021, D-028): the intervention itself, its co-benefit overrides (overrides
# describe the chosen typology, so carrying them to a different one would
# silently misdescribe it), and the cost/energy group. Everything else is the
# site description and is carried forward.
INTERVENTION_FIELDS = frozenset(
    {
        "nbs_type",
        "intervention_area_m2",
        "new_canopy_area_at_maturity_m2",
        "expected_maturity_period_years",
        "implementation_complexity",
        "maintenance_intensity",
        "co_benefit_biodiversity",
        "co_benefit_stormwater",
        "co_benefit_public_health",
        "co_benefit_social_inclusion",
        "co_benefit_urban_quality",
    }
)
COST_ENERGY_FIELDS = frozenset(
    {
        "nearby_building_cooling_demand_relevant",
        "annual_cooling_energy_demand_kwh",
        "energy_price_per_kwh",
        "capital_cost",
        "currency",
        "grid_emission_factor_kgco2e_per_kwh",
    }
)
BLANKED_ON_DUPLICATE = INTERVENTION_FIELDS | COST_ENERGY_FIELDS
SITE_DESCRIPTION_FIELDS = INPUT_FIELDS - BLANKED_ON_DUPLICATE


def _known_keys_only(value: dict[str, Any], allowed: frozenset[str], label: str) -> dict[str, Any]:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise ValueError(f"unknown {label} field(s): {unknown}")
    return value


class _RequestModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class MetaResponse(_RequestModel):
    """``GET /api/meta``."""

    engine_version: str
    methodology_version: str
    license: str


class FieldIssue(_RequestModel):
    """One validation error, addressed to the form field it belongs to."""

    field: str
    message: str


class ConfidenceHint(_RequestModel):
    """The highest-value missing field group for one block (D-028).

    ``fields`` lists the group's alternative fields (usually one; the heat
    signal slot offers two). ``raises_level_to`` is the level the block reaches
    if any of them is answered, or ``None`` when no single completion raises
    the level and the group is simply the first unsupplied one in configured
    order.
    """

    fields: list[str]
    raises_level_to: ConfidenceLevel | None


class BlockConfidencePreview(_RequestModel):
    """Live confidence for one output block (UX specification section 4)."""

    level: ConfidenceLevel
    completeness_percent: float
    hint: ConfidenceHint | None


class ConfidencePreview(_RequestModel):
    """Per-block confidence preview, computed by ``nature_cooling.engine.confidence``."""

    cooling: BlockConfidencePreview
    energy: BlockConfidencePreview
    economic: BlockConfidencePreview
    equity: BlockConfidencePreview
    overall: ConfidenceLevel
    cooling_capped_by_evidence: bool


class ValidateResponse(_RequestModel):
    """``POST /api/assessments/validate`` (D-028).

    Exactly two severities exist (OQ-08): ``errors`` block progression within
    their step, ``warnings`` never block. Warning texts are the engine's own.
    """

    valid: bool
    errors: list[FieldIssue]
    warnings: list[str]
    confidence: ConfidencePreview


class ProjectCreate(_RequestModel):
    name: str = Field(min_length=1)
    site: dict[str, Any] = Field(default_factory=dict)

    @field_validator("site")
    @classmethod
    def _site_keys(cls, value: dict[str, Any]) -> dict[str, Any]:
        return _known_keys_only(value, SITE_DESCRIPTION_FIELDS, "site description")


class ProjectPatch(_RequestModel):
    name: str | None = Field(default=None, min_length=1)
    site: dict[str, Any] | None = None

    @field_validator("site")
    @classmethod
    def _site_keys(cls, value: dict[str, Any] | None) -> dict[str, Any] | None:
        if value is None:
            return None
        return _known_keys_only(value, SITE_DESCRIPTION_FIELDS, "site description")


class AssessmentCreate(_RequestModel):
    label: str = Field(min_length=1)
    input: dict[str, Any] = Field(default_factory=dict)

    @field_validator("input")
    @classmethod
    def _input_keys(cls, value: dict[str, Any]) -> dict[str, Any]:
        return _known_keys_only(value, INPUT_FIELDS, "assessment input")


class AssessmentPatch(_RequestModel):
    label: str | None = Field(default=None, min_length=1)
    input: dict[str, Any] | None = None

    @field_validator("input")
    @classmethod
    def _input_keys(cls, value: dict[str, Any] | None) -> dict[str, Any] | None:
        if value is None:
            return None
        return _known_keys_only(value, INPUT_FIELDS, "assessment input")


class AssessmentDuplicate(_RequestModel):
    label: str | None = Field(default=None, min_length=1)


class StoredAssessment(BaseModel):
    """One assessment inside a project file.

    ``input`` is the draft questionnaire state (auto-save, D-020): any subset
    of the engine's input fields, validated as a complete ``AssessmentInput``
    only when the user explicitly evaluates. ``result`` is the engine's full
    ``AssessmentResult`` (including ``methodology_version`` and
    ``engine_version``) or ``None`` while the assessment is a draft.
    """

    model_config = ConfigDict(extra="forbid")

    assessment_id: str
    label: str
    created_at: str
    input: dict[str, Any]
    result: dict[str, Any] | None = None


class Project(BaseModel):
    """The on-disk project document: one JSON file per project (D-028)."""

    model_config = ConfigDict(extra="forbid")

    schema_version: int
    project_id: str
    name: str
    created_at: str
    updated_at: str
    site: dict[str, Any]
    assessments: list[StoredAssessment]

    @field_validator("schema_version")
    @classmethod
    def _supported_schema(cls, value: int) -> int:
        if value != STORAGE_SCHEMA_VERSION:
            raise ValueError(
                f"unsupported storage schema_version {value}; "
                f"this build reads version {STORAGE_SCHEMA_VERSION}"
            )
        return value


class AssessmentView(StoredAssessment):
    """A stored assessment plus the OQ-15 surfacing flag.

    ``methodology_update_available`` is true when the stored result was
    produced under an older methodology version than the one currently loaded.
    The stored result itself is never recomputed; re-running is an explicit
    user action that creates a new assessment.
    """

    methodology_update_available: bool

    @classmethod
    def of(cls, stored: StoredAssessment, current_methodology_version: str) -> AssessmentView:
        result = stored.result
        return cls(
            **stored.model_dump(),
            methodology_update_available=(
                result is not None and result["methodology_version"] != current_methodology_version
            ),
        )


class ProjectView(Project):
    """A project document plus the current methodology version, for OQ-15."""

    current_methodology_version: str
    assessments: list[AssessmentView]  # type: ignore[assignment]

    @classmethod
    def of(cls, project: Project, current_methodology_version: str) -> ProjectView:
        return cls(
            **project.model_dump(exclude={"assessments"}),
            current_methodology_version=current_methodology_version,
            assessments=[
                AssessmentView.of(item, current_methodology_version) for item in project.assessments
            ],
        )


class ProjectSummary(_RequestModel):
    """``GET /api/projects`` list entry."""

    project_id: str
    name: str
    created_at: str
    updated_at: str
    assessment_count: int

    @classmethod
    def of(cls, project: Project) -> ProjectSummary:
        return cls(
            project_id=project.project_id,
            name=project.name,
            created_at=project.created_at,
            updated_at=project.updated_at,
            assessment_count=len(project.assessments),
        )
