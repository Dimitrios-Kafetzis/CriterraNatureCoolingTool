"""Shared fixtures: the loaded methodology configuration and an input factory."""

from __future__ import annotations

from typing import Any

import pytest

from nature_cooling.engine.config import MethodologyConfig, load_config
from nature_cooling.engine.models import AssessmentInput

REQUIRED_DEFAULTS: dict[str, Any] = {
    "assessment_scale": "neighbourhood",
    "site_area_m2": 6000.0,
    "climate_zone": "temperate",
    # A package of one. `tree_avenue` inherits the street_tree_canopy
    # archetype — the same cited values the retired `street_tree_planting`
    # typology carried — and is offered at neighbourhood scale, so the default
    # fixture raises no availability warning of its own.
    "nbs_type": ["tree_avenue"],
}


def _build_input(**overrides: Any) -> AssessmentInput:
    return AssessmentInput(**{**REQUIRED_DEFAULTS, **overrides})


@pytest.fixture(scope="session")
def build_input():
    """Factory: an AssessmentInput with only the required fields, plus overrides."""
    return _build_input


@pytest.fixture(scope="session")
def config() -> MethodologyConfig:
    return load_config()
