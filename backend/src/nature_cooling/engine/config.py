"""Methodology configuration: loading, schema validation, and citation enforcement.

The methodology lives in ``config/*.yaml``, not in code. This module loads those
files, validates them against Pydantic schemas, and refuses to produce a
configuration that violates the project's evidence rules.

Two rules are enforced here rather than left to review:

1. Every typology's performance values must carry at least one source citation
   (decision D-012). An uncited typology is a hard error, not a warning.
2. Every source key referenced anywhere in the configuration must exist in the
   bibliography (``docs/methodology/BIBLIOGRAPHY.md``), so a citation cannot
   point at a source that was never recorded.
"""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

CategoryName = Literal["green", "building", "blue_green", "hybrid"]
ConfidenceLevel = Literal["low", "medium", "high"]

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


class Typology(BaseModel):
    """One NbS typology and its literature-grounded performance assumptions."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    nbs_id: str
    nbs_type: str
    display_name: str
    category: CategoryName
    base_cooling_score: float = Field(ge=0, le=100)
    temp_reduction_min_c: float = Field(ge=0)
    temp_reduction_max_c: float = Field(ge=0)
    evidence_confidence: ConfidenceLevel
    primary_cooling_mechanism: str
    building_energy_applicable: bool
    typical_use_context: list[str]
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


class TypologyLibrary(BaseModel):
    """The complete typology library, as loaded from ``nbs_typologies.yaml``."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    version: str
    typologies: list[Typology] = Field(min_length=1)

    @field_validator("version")
    @classmethod
    def _dated_version(cls, value: str) -> str:
        if not _VERSION_PATTERN.match(value):
            raise ValueError(f"version must be date-stamped as YYYY.MM.DD, got {value!r}")
        return value

    @field_validator("typologies")
    @classmethod
    def _unique_identifiers(cls, value: list[Typology]) -> list[Typology]:
        for field in ("nbs_id", "nbs_type"):
            seen = [getattr(item, field) for item in value]
            duplicates = {item for item in seen if seen.count(item) > 1}
            if duplicates:
                raise ValueError(f"duplicate {field}: {sorted(duplicates)}")
        return value

    def by_type(self, nbs_type: str) -> Typology:
        """Return the typology with this ``nbs_type``, or raise ``ConfigError``."""
        for typology in self.typologies:
            if typology.nbs_type == nbs_type:
                return typology
        raise ConfigError(f"unknown nbs_type: {nbs_type!r}")


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


_CONFIG_FILES = {
    "weights": "weights.yaml",
    "adjustment_factors": "adjustment_factors.yaml",
    "input_mapping": "input_mapping.yaml",
    "energy_model": "energy_model.yaml",
    "country_defaults": "country_defaults.yaml",
    "recommendation_templates": "recommendation_templates.yaml",
    "derived_scores": "derived_scores.yaml",
}


def repo_root() -> Path:
    """Return the repository root, located from this file's position."""
    return Path(__file__).resolve().parents[4]


def default_config_dir() -> Path:
    """Return the repository's ``config/`` directory."""
    return repo_root() / "config"


def default_bibliography_path() -> Path:
    """Return the path to the methodology bibliography."""
    return repo_root() / "docs" / "methodology" / "BIBLIOGRAPHY.md"


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

    return MethodologyConfig(
        version=library.version,
        typologies=library,
        **documents,
    )


@lru_cache(maxsize=1)
def get_config() -> MethodologyConfig:
    """Return the process-wide methodology configuration, loading it once."""
    return load_config()
