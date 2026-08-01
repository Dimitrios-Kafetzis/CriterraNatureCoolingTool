"""Methodology configuration: loading, schema validation, and citation enforcement.

The methodology lives in ``config/*.yaml``, not in code. This module loads those
files, validates them against Pydantic schemas, and refuses to produce a
configuration that violates the project's evidence rules.

Since version ``2026.08.04`` the typology library has two levels (D-044). An
**archetype** is a cited evidence class: it carries every performance value —
the temperature envelope, the base cooling score, the evidence rating, the
suitability conditions, the co-benefit defaults — and the citations behind
them. A **typology** is one of the 110 catalogue entries: it carries identity,
family, availability, and the archetype it inherits from, plus per-entry
suitability overrides where the source text states a constraint (D-044.3).
Loading resolves the two into the flat ``Typology`` the scoring modules have
always consumed, so no formula changed shape when the library grew.

Three rules are enforced here rather than left to review:

1. Every typology's performance values must carry at least one source citation
   (decision D-012). Because values are inherited, this is enforced on the
   *resolved* typology: an entry whose archetype cites nothing is a hard error.
2. Every source key referenced anywhere in the configuration must exist in the
   bibliography (``docs/methodology/BIBLIOGRAPHY.md``), so a citation cannot
   point at a source that was never recorded.
3. Every typology must name an archetype that exists, and every archetype must
   be used by at least one typology — an evidence class nothing inherits from
   is a citation with no consumer, and a dangling archetype reference would
   otherwise fail at scoring time rather than at load time.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

CategoryName = Literal["green", "building", "blue_green", "hybrid"]
ConfidenceLevel = Literal["low", "medium", "high"]
EntryKind = Literal["element", "composite"]
Provenance = Literal["existing", "new", "derived"]
AssessmentScaleName = Literal["city", "district", "neighbourhood", "site", "building"]
WaterfrontType = Literal["lake", "river", "dry_river", "covered_river", "sea"]
GovernanceType = Literal["community", "individual", "institutional", "commercial"]

_VERSION_PATTERN = re.compile(r"^\d{4}\.\d{2}\.\d{2}$")
_BIBLIOGRAPHY_KEY_PATTERN = re.compile(r"^\*\*`([a-z0-9]+)`\*\*", re.MULTILINE)


class ConfigError(RuntimeError):
    """Raised when the methodology configuration is invalid or inconsistent."""


class Source(BaseModel):
    """A citation supporting a configuration value."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    key: str = Field(min_length=1)
    finding: str = Field(min_length=1)


class Suitability(BaseModel):
    """Conditions under which a typology is considered unsuitable for a site."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    minimum_site_area_m2: float = Field(gt=0)
    requires_soil: Literal["none", "limited", "moderate", "high"]
    requires_irrigation: Literal["none", "occasional", "reliable"]
    unsuitable_climate_zones: list[str] = Field(default_factory=list)


class SuitabilityOverride(BaseModel):
    """A per-entry departure from the archetype's suitability conditions.

    Permitted only where the catalogue's own description of the entry makes an
    inherited value plainly wrong (D-044.3); every replacement value is one
    already present in the cited v1.1 library, so no new number enters the
    methodology through an override.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    minimum_site_area_m2: float | None = Field(default=None, gt=0)
    requires_soil: Literal["none", "limited", "moderate", "high"] | None = None
    requires_irrigation: Literal["none", "occasional", "reliable"] | None = None


class Availability(BaseModel):
    """When an entry is offered to the user (D-043, D-044.1).

    Availability gates *selection*; it feeds no score. A condition that is
    ``None``/``False`` is ungated — notably the four constructed water features,
    which need no existing water body, and the woodland *creation* types, which
    need no existing woodland.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    scales: list[AssessmentScaleName] = Field(min_length=1)
    land_uses: list[str] | Literal["all"]
    requires_waterfront: list[WaterfrontType] | None = None
    requires_railway: bool = False
    requires_existing_woodland: bool = False
    requires_governance: GovernanceType | None = None


class Archetype(BaseModel):
    """One cited cooling evidence class (D-044).

    Every performance value in the library lives here, with the citations that
    support it. The 110 catalogue entries carry no performance value of their
    own; each inherits exactly one archetype and the report names the evidence
    class it inherited from.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    archetype: str
    display_name: str
    provenance: Provenance
    category: CategoryName
    base_cooling_score: float = Field(ge=0, le=100)
    temp_reduction_min_c: float = Field(ge=0)
    temp_reduction_max_c: float = Field(ge=0)
    evidence_confidence: ConfidenceLevel
    building_energy_applicable: bool
    suitability: Suitability
    co_benefit_defaults: dict[str, str]
    output_caveats: list[str] = Field(default_factory=list)
    sources: list[Source] = Field(min_length=1)
    notes: str | None = None

    @field_validator("temp_reduction_max_c")
    @classmethod
    def _max_above_min(cls, value: float, info: Any) -> float:
        minimum = info.data.get("temp_reduction_min_c")
        if minimum is not None and value < minimum:
            raise ValueError(
                f"temp_reduction_max_c ({value}) must be >= temp_reduction_min_c ({minimum})"
            )
        return value


class TypologyEntry(BaseModel):
    """One catalogue entry, as written in ``nbs_typologies.yaml``."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    nbs_id: str
    nbs_type: str
    display_name: str
    archetype: str
    family: str
    kind: EntryKind
    primary_cooling_mechanism: str
    availability: Availability
    suitability_overrides: SuitabilityOverride | None = None
    notes: str | None = None


class Typology(BaseModel):
    """One catalogue entry resolved against its archetype.

    This is the flat view every scoring module consumes, and the shape the API
    serves. ``archetype`` and ``evidence_provenance`` are reported so a result
    can always name the evidence class its numbers came from.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    nbs_id: str
    nbs_type: str
    display_name: str
    family: str
    kind: EntryKind
    archetype: str
    archetype_display_name: str
    evidence_provenance: Provenance
    category: CategoryName
    base_cooling_score: float = Field(ge=0, le=100)
    temp_reduction_min_c: float = Field(ge=0)
    temp_reduction_max_c: float = Field(ge=0)
    evidence_confidence: ConfidenceLevel
    primary_cooling_mechanism: str
    building_energy_applicable: bool
    typical_use_context: list[str]
    availability: Availability
    suitability: Suitability
    suitability_inherited: bool
    co_benefit_defaults: dict[str, str]
    output_caveats: list[str] = Field(default_factory=list)
    sources: list[Source] = Field(min_length=1)
    notes: str | None = None


# The land-use enumeration the availability matrix and the urban-context
# sub-indicator share. Declared here so that ``land_uses: all`` resolves to a
# concrete list rather than a special case every consumer must remember.
LAND_USES: tuple[str, ...] = (
    "street_corridor",
    "residential",
    "mixed_use",
    "commercial",
    "public_space",
    "park",
    "school",
    "campus",
    "healthcare",
    "memorial",
    "industrial",
    "other",
)


def _resolve(entry: TypologyEntry, archetype: Archetype) -> Typology:
    """Merge one entry with its archetype into the flat scoring view."""
    override = entry.suitability_overrides
    conditions = archetype.suitability
    if override is not None:
        conditions = Suitability(
            minimum_site_area_m2=(
                override.minimum_site_area_m2
                if override.minimum_site_area_m2 is not None
                else conditions.minimum_site_area_m2
            ),
            requires_soil=override.requires_soil or conditions.requires_soil,
            requires_irrigation=override.requires_irrigation or conditions.requires_irrigation,
            unsuitable_climate_zones=list(conditions.unsuitable_climate_zones),
        )
    land_uses = entry.availability.land_uses
    return Typology(
        nbs_id=entry.nbs_id,
        nbs_type=entry.nbs_type,
        display_name=entry.display_name,
        family=entry.family,
        kind=entry.kind,
        archetype=archetype.archetype,
        archetype_display_name=archetype.display_name,
        evidence_provenance=archetype.provenance,
        category=archetype.category,
        base_cooling_score=archetype.base_cooling_score,
        temp_reduction_min_c=archetype.temp_reduction_min_c,
        temp_reduction_max_c=archetype.temp_reduction_max_c,
        evidence_confidence=archetype.evidence_confidence,
        primary_cooling_mechanism=entry.primary_cooling_mechanism,
        building_energy_applicable=archetype.building_energy_applicable,
        # The urban-context sub-indicator (D-022) compares the site's land use
        # against the entry's own land-use list, which is the availability
        # matrix's list: an entry is "in context" exactly where it is offered.
        typical_use_context=list(LAND_USES) if land_uses == "all" else list(land_uses),
        availability=entry.availability,
        suitability=conditions,
        suitability_inherited=override is None,
        co_benefit_defaults=dict(archetype.co_benefit_defaults),
        output_caveats=list(archetype.output_caveats),
        sources=list(archetype.sources),
        notes=entry.notes if entry.notes is not None else archetype.notes,
    )


class TypologyLibrary(BaseModel):
    """The complete typology library, as loaded from ``nbs_typologies.yaml``.

    ``archetypes`` and ``typologies`` are the file as written; ``resolved`` is
    the flat scoring view, computed once at load.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    version: str
    archetypes: list[Archetype] = Field(min_length=1)
    typologies: list[TypologyEntry] = Field(min_length=1)
    resolved: list[Typology] = Field(default_factory=list)

    @field_validator("version")
    @classmethod
    def _dated_version(cls, value: str) -> str:
        if not _VERSION_PATTERN.match(value):
            raise ValueError(f"version must be date-stamped as YYYY.MM.DD, got {value!r}")
        return value

    @field_validator("archetypes")
    @classmethod
    def _unique_archetypes(cls, value: list[Archetype]) -> list[Archetype]:
        names = [item.archetype for item in value]
        duplicates = {name for name in names if names.count(name) > 1}
        if duplicates:
            raise ValueError(f"duplicate archetype: {sorted(duplicates)}")
        return value

    @field_validator("typologies")
    @classmethod
    def _unique_identifiers(cls, value: list[TypologyEntry]) -> list[TypologyEntry]:
        for field in ("nbs_id", "nbs_type"):
            seen = [getattr(item, field) for item in value]
            duplicates = {item for item in seen if seen.count(item) > 1}
            if duplicates:
                raise ValueError(f"duplicate {field}: {sorted(duplicates)}")
        return value

    @model_validator(mode="after")
    def _resolve_inheritance(self) -> TypologyLibrary:
        by_name = {item.archetype: item for item in self.archetypes}
        missing = sorted({e.archetype for e in self.typologies} - set(by_name))
        if missing:
            raise ValueError(f"typologies reference unknown archetypes: {missing}")
        unused = sorted(set(by_name) - {e.archetype for e in self.typologies})
        if unused:
            raise ValueError(f"archetypes no typology inherits from: {unused}")
        unknown_uses = sorted(
            {
                use
                for entry in self.typologies
                if entry.availability.land_uses != "all"
                for use in entry.availability.land_uses
                if use not in LAND_USES
            }
        )
        if unknown_uses:
            raise ValueError(f"availability names unknown land uses: {unknown_uses}")
        object.__setattr__(
            self,
            "resolved",
            [_resolve(entry, by_name[entry.archetype]) for entry in self.typologies],
        )
        return self

    def by_type(self, nbs_type: str) -> Typology:
        """Return the resolved typology with this ``nbs_type``, or raise."""
        for typology in self.resolved:
            if typology.nbs_type == nbs_type:
                return typology
        raise ConfigError(f"unknown nbs_type: {nbs_type!r}")

    def archetype_by_name(self, name: str) -> Archetype:
        """Return one archetype by name, or raise ``ConfigError``."""
        for archetype in self.archetypes:
            if archetype.archetype == name:
                return archetype
        raise ConfigError(f"unknown archetype: {name!r}")


class MethodologyConfig(BaseModel):
    """The full methodology configuration backing one assessment run."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    version: str
    typologies: TypologyLibrary
    weights: dict[str, Any]
    adjustment_factors: dict[str, Any]
    input_mapping: dict[str, Any]
    energy_model: dict[str, Any]
    country_defaults: dict[str, Any]
    recommendation_templates: dict[str, Any]
    derived_scores: dict[str, Any]
    availability: dict[str, Any]


_CONFIG_FILES = {
    "weights": "weights.yaml",
    "adjustment_factors": "adjustment_factors.yaml",
    "input_mapping": "input_mapping.yaml",
    "energy_model": "energy_model.yaml",
    "country_defaults": "country_defaults.yaml",
    "recommendation_templates": "recommendation_templates.yaml",
    "derived_scores": "derived_scores.yaml",
    "availability": "availability.yaml",
}


def repo_root() -> Path:
    """Return the repository root, located from this file's position."""
    return Path(__file__).resolve().parents[4]


def bundled_data_dir() -> Path:
    """Return the wheel's embedded data directory (D-035).

    The distributable wheel embeds the methodology configuration, the
    bibliography, and the production frontend build under
    ``nature_cooling/_bundled`` (staged by ``tools/build_wheel.sh``; never
    committed). In a repository checkout the directory does not exist.
    """
    return Path(__file__).resolve().parents[1] / "_bundled"


def default_config_dir() -> Path:
    """Return the ``config/`` directory: the repository's, else the wheel's.

    The repository copy wins whenever it exists, so a checkout always runs
    against the live methodology files; the embedded copy serves installed
    wheels, where no repository layout surrounds the package.
    """
    repo_config = repo_root() / "config"
    return repo_config if repo_config.is_dir() else bundled_data_dir() / "config"


def default_bibliography_path() -> Path:
    """Return the methodology bibliography: the repository's, else the wheel's."""
    repo_bibliography = repo_root() / "docs" / "methodology" / "BIBLIOGRAPHY.md"
    if repo_bibliography.is_file():
        return repo_bibliography
    return bundled_data_dir() / "BIBLIOGRAPHY.md"


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ConfigError(f"missing configuration file: {path}")
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:  # pragma: no cover - defensive
        raise ConfigError(f"invalid YAML in {path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise ConfigError(f"{path} must contain a YAML mapping at the top level")
    return loaded


def bibliography_keys(path: Path | None = None) -> set[str]:
    """Return the set of source keys declared in the bibliography."""
    bibliography = path or default_bibliography_path()
    if not bibliography.is_file():
        raise ConfigError(f"missing bibliography: {bibliography}")
    return set(_BIBLIOGRAPHY_KEY_PATTERN.findall(bibliography.read_text(encoding="utf-8")))


def collect_source_keys(node: Any) -> set[str]:
    """Recursively collect every ``sources[].key`` value in a configuration tree."""
    found: set[str] = set()
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "sources" and isinstance(value, list):
                found.update(
                    entry["key"]
                    for entry in value
                    if isinstance(entry, dict) and isinstance(entry.get("key"), str)
                )
            else:
                found |= collect_source_keys(value)
    elif isinstance(node, list):
        for item in node:
            found |= collect_source_keys(item)
    return found


def load_config(
    config_dir: Path | None = None,
    bibliography_path: Path | None = None,
) -> MethodologyConfig:
    """Load, validate, and cross-check the methodology configuration.

    Raises:
        ConfigError: if a file is missing, a schema is violated, versions
            disagree across files, or a citation references an unknown source.
    """
    directory = config_dir or default_config_dir()

    library = TypologyLibrary.model_validate(_load_yaml(directory / "nbs_typologies.yaml"))
    documents = {name: _load_yaml(directory / filename) for name, filename in _CONFIG_FILES.items()}

    mismatched = {
        name: document.get("version")
        for name, document in documents.items()
        if document.get("version") != library.version
    }
    if mismatched:
        raise ConfigError(
            f"configuration version mismatch: nbs_typologies.yaml is {library.version!r} "
            f"but {mismatched} differ. All methodology files must share one version."
        )

    # D-012/D-017 — every typology's performance values carry a citation — is
    # enforced structurally rather than here: ``Archetype.sources`` has a
    # minimum length of one, every typology inherits exactly one archetype, and
    # an archetype nothing inherits from is rejected above. A resolved typology
    # therefore cannot exist without a citation, and a second runtime check
    # would be unreachable code asserting what the schema already guarantees.

    known = bibliography_keys(bibliography_path)
    cited = collect_source_keys(
        {"typologies": library.model_dump(), **documents},
    )
    unknown = sorted(cited - known)
    if unknown:
        raise ConfigError(
            f"citations reference sources absent from the bibliography: {unknown}. "
            "Add them to docs/methodology/BIBLIOGRAPHY.md or correct the keys."
        )

    # Every output caveat an archetype declares must have text to render, or a
    # result would silently drop a caveat the evidence requires it to state.
    caveat_texts = documents["recommendation_templates"].get("flags", {})
    missing_caveats = sorted(
        {
            caveat
            for archetype in library.archetypes
            for caveat in archetype.output_caveats
            if caveat not in caveat_texts
        }
    )
    if missing_caveats:
        raise ConfigError(
            f"output caveats have no text in recommendation_templates.yaml: {missing_caveats}."
        )

    return MethodologyConfig(
        version=library.version,
        typologies=library,
        **documents,
    )


@lru_cache(maxsize=1)
def get_config() -> MethodologyConfig:
    """Return the process-wide methodology configuration, loading it once."""
    return load_config()
