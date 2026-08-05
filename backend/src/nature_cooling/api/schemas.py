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

from nature_cooling.engine.config import Archetype, ConfidenceLevel, Typology, TypologyEntry
from nature_cooling.engine.models import AssessmentInput

STORAGE_SCHEMA_VERSION = 3

INPUT_FIELDS = frozenset(AssessmentInput.model_fields)

# The only three inputs a map may fill in (D-047, v2.1 brief). The set is
# closed on purpose and enforced on the way in: everything else the
# questionnaire asks about the site — canopy, imperviousness, LST anomaly, land
# use — needs satellite or census data, which is the GIS workflow deferred by
# D-002. Filling those in from imagery would demo well and would generate the
# tool's most decision-relevant inputs from an unvalidated pipeline with no
# evidence table behind it, which is the defect D-016 refused for cost defaults.
AUTOFILLABLE_FIELDS = frozenset({"site_area_m2", "country", "climate_zone"})

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


class TileSource(_RequestModel):
    """The deployment's configured tile source (v2.2, D-049).

    Both halves travel together by construction: the application refuses to
    start with a URL and no attribution, so imagery can never reach a browser
    without the credit its licence requires (D-049.2).
    """

    url_template: str
    attribution: str


class MetaResponse(_RequestModel):
    """``GET /api/meta``."""

    engine_version: str
    methodology_version: str
    license: str
    # None in the unconfigured deployment — the default, in which the
    # application makes no third-party request (D-049.1).
    tiles: TileSource | None


class PlaceResult(_RequestModel):
    """One place-search match (v2.2, D-049.6): a name and somewhere to move
    the map to. Never an answer to any questionnaire field."""

    name: str
    admin: str
    latitude: float
    longitude: float
    population: int


class PlaceSearchResponse(_RequestModel):
    """``GET /api/geo/places`` — offline navigation by name."""

    query: str
    results: list[PlaceResult]
    attribution: str


class NbsImage(_RequestModel):
    """One bundled example photograph (v2.3, D-051), with its attribution.

    ``nbs_type`` is ``None`` for an archetype-level image; a non-null value is
    a per-typology override that outranks the archetype image for that entry.
    The image is an illustrative example, not evidence: captions built from
    ``caption_subject``, ``place`` and ``zone`` state what and where, never a
    performance claim (D-051.6).
    """

    file: str
    archetype: str
    nbs_type: str | None
    zone: str
    place: str
    caption_subject: str
    author: str
    licence: str
    licence_url: str | None
    source_page: str
    width: int
    height: int


class NbsImageManifest(_RequestModel):
    """``GET /api/images/manifest`` — every example image this package serves.

    One request tells the picker which (archetype-or-override, zone) pairs
    have a verified image; every pair absent from this list renders no
    affordance at all (D-051.5). Empty is an expected answer, not an error.
    """

    purpose: str
    images: list[NbsImage]


class SourceReference(_RequestModel):
    """One bibliography entry, served so a citation key can name its work.

    ``reference`` is the full citation in plain text; ``doi`` and ``url`` are
    the identifier and link the bibliography itself carries. A link the user
    clicks is not a request the app makes (the D-051.3 reading), so serving
    these leaves the request gates untouched.
    """

    reference: str
    doi: str | None
    url: str | None


class TypologyLibraryResponse(_RequestModel):
    """``GET /api/typologies`` — the library, verbatim, plus curation provenance.

    ``archetypes``, ``typologies`` and ``resolved`` are the engine's own loaded
    models, serialised unchanged — the single source of truth the picker
    renders and the engine scores. Two maps ride beside them (v2.6) so the
    detail dialog costs no request the picker was not already making:
    ``curation_reasons``, the one-line reason each shipped entry was kept,
    keyed by ``nbs_id`` and read from the published curation records in
    ``docs/assets/``; and ``bibliography``, the full reference behind every
    citation key, parsed from the bibliography the wheel already carries — a
    key like ``jacobs2020`` says nothing on its own, so the interface renders
    the work it names, with its DOI or URL as a link.
    """

    version: str
    archetypes: list[Archetype]
    typologies: list[TypologyEntry]
    resolved: list[Typology]
    curation_reasons: dict[str, str]
    bibliography: dict[str, SourceReference]


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


class AvailableTypologies(_RequestModel):
    """``GET /api/typologies/available`` (D-043, D-044.1).

    A declared response model rather than a bare mapping, so the shape is part
    of the OpenAPI schema and the frontend's generated types can check it —
    the same contract every other endpoint offers (D-030).

    ``nbs_types`` lists what the matrix offers, in library order. It is not a
    permission list: an entry absent from it stays fully selectable (D-019),
    and the engine scores it with the honest suitability flags of D-009.
    """

    version: str
    assessment_scale: str
    land_use: str | None
    composes_packages: bool
    warn_above_components: int
    count: int
    nbs_types: list[str]


class GeoLookupRequest(_RequestModel):
    """``POST /api/geo/lookup`` — what a map click can honestly answer (D-047).

    ``boundary`` is the polygon the user drew, as ``[longitude, latitude]``
    pairs. When it is absent the user placed a point rather than drawing a
    site, and no area is returned.
    """

    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)
    boundary: list[list[float]] | None = None

    @field_validator("boundary")
    @classmethod
    def _boundary_points(cls, value: list[list[float]] | None) -> list[list[float]] | None:
        if value is None:
            return None
        for point in value:
            if len(point) != 2:
                raise ValueError("each boundary point must be a [longitude, latitude] pair")
            longitude, latitude = point
            if not (-180.0 <= longitude <= 180.0 and -90.0 <= latitude <= 90.0):
                raise ValueError("boundary point out of range")
        return value


class GeoCountry(_RequestModel):
    """The country a point resolved to, and how the lookup reached it."""

    iso_a2: str | None
    iso_a3: str | None
    name: str | None
    matched: str
    source_key: str
    attribution: str


class GeoClimate(_RequestModel):
    """The climate zone a point resolved to, and the class it came from."""

    zone: str | None
    koppen_class: str | None
    source_key: str
    attribution: str
    note: str
    resolution_caveat: str


class GeoLookupResponse(_RequestModel):
    """``POST /api/geo/lookup``.

    Every value is a suggestion. The interface applies each one only where the
    user has not already answered, marks what it applied as autofilled, and
    lets any of them be overridden (D-047.2).
    """

    latitude: float
    longitude: float
    site_area_m2: float | None
    country: GeoCountry
    climate: GeoClimate


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


def _autofilled_keys_only(value: dict[str, str], label: str) -> dict[str, str]:
    """Reject a provenance record naming a field a map may not fill in.

    The closed set is enforced here, at the boundary, rather than trusted from
    the client: it is the mechanism by which "only these three inputs autofill"
    stays true as the questionnaire grows (D-047, D-048).
    """
    unknown = sorted(set(value) - AUTOFILLABLE_FIELDS)
    if unknown:
        raise ValueError(
            f"unknown {label} field(s): {unknown}; only "
            f"{sorted(AUTOFILLABLE_FIELDS)} may be autofilled"
        )
    return value


class AssessmentCreate(_RequestModel):
    label: str = Field(min_length=1)
    input: dict[str, Any] = Field(default_factory=dict)
    autofilled: dict[str, str] = Field(default_factory=dict)

    @field_validator("input")
    @classmethod
    def _input_keys(cls, value: dict[str, Any]) -> dict[str, Any]:
        return _known_keys_only(value, INPUT_FIELDS, "assessment input")

    @field_validator("autofilled")
    @classmethod
    def _autofilled_keys(cls, value: dict[str, str]) -> dict[str, str]:
        return _autofilled_keys_only(value, "autofill provenance")


class AssessmentPatch(_RequestModel):
    label: str | None = Field(default=None, min_length=1)
    input: dict[str, Any] | None = None
    autofilled: dict[str, str] | None = None

    @field_validator("input")
    @classmethod
    def _input_keys(cls, value: dict[str, Any] | None) -> dict[str, Any] | None:
        if value is None:
            return None
        return _known_keys_only(value, INPUT_FIELDS, "assessment input")

    @field_validator("autofilled")
    @classmethod
    def _autofilled_keys(cls, value: dict[str, str] | None) -> dict[str, str] | None:
        if value is None:
            return None
        return _autofilled_keys_only(value, "autofill provenance")


class AssessmentDuplicate(_RequestModel):
    label: str | None = Field(default=None, min_length=1)


class StoredAssessment(BaseModel):
    """One assessment inside a project file.

    ``input`` is the draft questionnaire state (auto-save, D-020): any subset
    of the engine's input fields, validated as a complete ``AssessmentInput``
    only when the user explicitly evaluates. ``result`` is the engine's full
    ``AssessmentResult`` (including ``methodology_version`` and
    ``engine_version``) or ``None`` while the assessment is a draft.

    ``autofilled`` records which of the three map-derivable inputs the map
    filled in, and from which dataset (D-047.2). It is a sibling of ``input``
    rather than a key inside it because ``input`` holds engine fields and
    nothing else — the engine has no concept of where a value came from, and
    correctly does not want one: an autofilled value counts as supplied for
    confidence exactly as a typed one does. The provenance is for the reader of
    the report, not for the scoring. It is dropped for any field the user
    subsequently answers themselves, so the mark disappears with the override.
    """

    model_config = ConfigDict(extra="forbid")

    assessment_id: str
    label: str
    created_at: str
    input: dict[str, Any]
    autofilled: dict[str, str] = Field(default_factory=dict)
    result: dict[str, Any] | None = None


class Project(BaseModel):
    """The on-disk project document: one JSON file per project (D-028).

    A document is validated only after any migration has run, so this model
    always sees the current schema version. An older document is migrated
    explicitly and itemised (D-029, D-044.2); a *newer* one is refused.
    """

    model_config = ConfigDict(extra="forbid")

    schema_version: int
    project_id: str
    name: str
    created_at: str
    updated_at: str
    site: dict[str, Any]
    assessments: list[StoredAssessment]
    # Set for the lifetime of one response when this document was migrated on
    # load, so the interface can tell the user exactly what changed in their
    # saved work. Never persisted: it describes an event, not the project.
    migration_notes: list[str] = Field(default_factory=list, exclude=True)

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
    """A project document plus the current methodology version, for OQ-15.

    ``migrated_notes`` itemises any storage migration applied when this
    document was read, so a user whose saved drafts were reshaped is told what
    changed rather than discovering it (D-029, D-044.2).
    """

    current_methodology_version: str
    assessments: list[AssessmentView]  # type: ignore[assignment]
    migrated_notes: list[str] = Field(default_factory=list)

    @classmethod
    def of(cls, project: Project, current_methodology_version: str) -> ProjectView:
        return cls(
            **project.model_dump(exclude={"assessments"}),
            current_methodology_version=current_methodology_version,
            migrated_notes=list(project.migration_notes),
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
