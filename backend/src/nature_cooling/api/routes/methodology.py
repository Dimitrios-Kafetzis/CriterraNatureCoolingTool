"""The methodology, served as data: typology library and configuration.

Both endpoints return the loaded configuration verbatim — the same objects
the engine scores with — so the methodology browser and the questionnaire
render from the single source of truth, citations included.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Request

from nature_cooling.engine.config import MethodologyConfig, TypologyLibrary

router = APIRouter(tags=["methodology"])


def _config(request: Request) -> MethodologyConfig:
    config: MethodologyConfig = request.app.state.config
    return config


@router.get("/typologies")
def typologies(request: Request) -> TypologyLibrary:
    """The NbS typology library, including suitability conditions and citations."""
    return _config(request).typologies


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
    }
