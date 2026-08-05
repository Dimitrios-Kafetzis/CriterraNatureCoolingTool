"""The methodology, served as data: typology library, availability, configuration.

Every endpoint returns the loaded configuration verbatim — the same objects the
engine scores with — so the methodology browser and the questionnaire render
from the single source of truth, citations included.

The availability endpoint exists because gating is configuration, not code
(ARCHITECTURE boundary 1): the frontend computes no availability rule of its
own, it renders what the service serves. That is also why the rule lives in the
engine and is exercised by the same tests that assert the published matrix.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query, Request

from nature_cooling.api.schemas import AvailableTypologies
from nature_cooling.engine import availability as availability_module
from nature_cooling.engine.config import (
    AssessmentScaleName,
    GovernanceType,
    MethodologyConfig,
    TypologyLibrary,
    WaterfrontType,
)
from nature_cooling.engine.models import SiteConditions

router = APIRouter(tags=["methodology"])

# The governance multi-select arrives as repeated query parameters, so FastAPI
# needs an explicit Query marker; held as a module-level singleton because a
# call in a default argument is evaluated once at import anyway.
_GOVERNANCE_QUERY = Query(default=None)


def _config(request: Request) -> MethodologyConfig:
    config: MethodologyConfig = request.app.state.config
    return config


@router.get("/typologies")
def typologies(request: Request) -> TypologyLibrary:
    """The full library: 18 cited archetypes and the 121 entries inheriting them.

    ``resolved`` carries each entry merged with its archetype — the flat view
    the picker renders and the engine scores — while ``archetypes`` carries the
    citations, so the interface can show which evidence class a card's numbers
    came from without inferring anything.
    """
    return _config(request).typologies


@router.get("/typologies/available")
def available(
    request: Request,
    assessment_scale: AssessmentScaleName,
    land_use: str | None = None,
    waterfront_type: WaterfrontType | None = None,
    includes_railway: bool | None = None,
    existing_woodland: bool | None = None,
    productive_governance: list[GovernanceType] | None = _GOVERNANCE_QUERY,
) -> AvailableTypologies:
    """The entries offered for this site (D-043, D-044.1).

    Availability guides selection and never blocks it (D-019): an entry absent
    from this list stays fully selectable, and the engine scores it with the
    honest suitability flags of D-009. This endpoint answers "what should the
    picker show first", not "what is permitted".
    """
    config = _config(request)
    conditions = SiteConditions(
        waterfront_type=waterfront_type,
        includes_railway=(
            None if includes_railway is None else ("yes" if includes_railway else "no")
        ),
        existing_woodland=(
            None if existing_woodland is None else ("yes" if existing_woodland else "no")
        ),
        productive_governance=sorted(set(productive_governance or [])),
    )
    offered = availability_module.available_typologies(
        assessment_scale, land_use, conditions, config
    )
    return AvailableTypologies(
        version=config.version,
        assessment_scale=assessment_scale,
        land_use=land_use,
        composes_packages=availability_module.composes_packages(assessment_scale, config),
        warn_above_components=availability_module.warn_above_components(config),
        count=len(offered),
        nbs_types=[typology.nbs_type for typology in offered],
    )


@router.get("/methodology")
def methodology(request: Request) -> dict[str, Any]:
    """Formulas, weights, factors, and defaults, with the methodology version."""
    config = _config(request)
    return {
        "version": config.version,
        "weights": config.weights,
        "adjustment_factors": config.adjustment_factors,
        "input_mapping": config.input_mapping,
        "energy_model": config.energy_model,
        "country_defaults": config.country_defaults,
        "derived_scores": config.derived_scores,
        "recommendation_templates": config.recommendation_templates,
        "availability": config.availability,
    }
