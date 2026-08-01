"""Which catalogue entries are offered for a site (D-043, D-044.1).

Availability decides what the picker shows. It feeds no score, enters no
formula, and can never move a result: the four site questions it reads change
the menu and nothing else. A user who deliberately selects an entry the matrix
did not offer is not blocked (D-019) — the engine scores it exactly as it
scores any other, and the D-009 suitability flags carry the honest verdict.

Every rule applied here is read from configuration: the per-entry conditions
from ``nbs_typologies.yaml`` and the per-condition policy from
``availability.yaml``. This module holds the mechanism, not the methodology.
"""

from __future__ import annotations

from typing import Any, Literal

from nature_cooling.engine.config import MethodologyConfig, Typology
from nature_cooling.engine.models import AssessmentInput, SiteConditions


def site_conditions(inp: AssessmentInput) -> SiteConditions:
    """Read the four gating answers off an assessment input.

    ``unknown`` and absence are the same thing here, as everywhere else in the
    tool: an explicit unknown carries no more information than a skipped
    question (D-024).
    """
    return SiteConditions(
        waterfront_type=inp.waterfront_type,
        includes_railway=_yes_no(inp.includes_railway),
        existing_woodland=_yes_no(inp.existing_woodland),
        productive_governance=list(inp.productive_governance or []),
    )


def _yes_no(value: str | None) -> Literal["yes", "no"] | None:
    """Narrow a yes/no/unknown answer, treating ``unknown`` as unanswered."""
    if value == "yes":
        return "yes"
    if value == "no":
        return "no"
    return None


def _condition_policy(config: MethodologyConfig, name: str) -> str:
    policy: dict[str, Any] = config.availability["conditions"][name]
    return str(policy["unanswered_behaviour"])


def _passes_waterfront(
    typology: Typology, conditions: SiteConditions, config: MethodologyConfig
) -> bool:
    required = typology.availability.requires_waterfront
    if not required:
        return True
    if conditions.waterfront_type is None:
        return _condition_policy(config, "waterfront") == "offers"
    return conditions.waterfront_type in required


def _passes_railway(
    typology: Typology, conditions: SiteConditions, config: MethodologyConfig
) -> bool:
    if not typology.availability.requires_railway:
        return True
    if conditions.includes_railway is None:
        return _condition_policy(config, "railway") == "offers"
    return conditions.includes_railway == "yes"


def _passes_woodland(
    typology: Typology, conditions: SiteConditions, config: MethodologyConfig
) -> bool:
    if not typology.availability.requires_existing_woodland:
        return True
    if conditions.existing_woodland is None:
        return _condition_policy(config, "existing_woodland") == "offers"
    return conditions.existing_woodland == "yes"


def _passes_governance(
    typology: Typology, conditions: SiteConditions, config: MethodologyConfig
) -> bool:
    required = typology.availability.requires_governance
    if required is None:
        return True
    if not conditions.productive_governance:
        # An unanswered multi-select suppresses nothing (D-043.3): the question
        # asks who could deliver, and silence is not a "no one can".
        return _condition_policy(config, "productive_governance") == "offers"
    return required in conditions.productive_governance


def is_available(
    typology: Typology,
    scale: str,
    land_use: str | None,
    conditions: SiteConditions,
    config: MethodologyConfig,
) -> bool:
    """Whether one entry is offered for this scale, land use, and conditions."""
    if scale not in typology.availability.scales:
        return False
    if land_use is not None and land_use not in typology.typical_use_context:
        return False
    return (
        _passes_waterfront(typology, conditions, config)
        and _passes_railway(typology, conditions, config)
        and _passes_woodland(typology, conditions, config)
        and _passes_governance(typology, conditions, config)
    )


def available_typologies(
    scale: str,
    land_use: str | None,
    conditions: SiteConditions,
    config: MethodologyConfig,
) -> list[Typology]:
    """Every entry offered for this site, in library order.

    An unanswered land use filters nothing — the site has not said what it is,
    and the tool never asserts a negative from absent information.
    """
    return [
        typology
        for typology in config.typologies.resolved
        if is_available(typology, scale, land_use, conditions, config)
    ]


def composes_packages(scale: str, config: MethodologyConfig) -> bool:
    """Whether this scale offers package components rather than alternatives."""
    rules: dict[str, Any] = config.availability["scales"][scale]
    return bool(rules["composes_packages"])


def warn_above_components(config: MethodologyConfig) -> int:
    """The package size above which the tool warns (D-044.4)."""
    return int(config.availability["packages"]["warn_above_components"])
