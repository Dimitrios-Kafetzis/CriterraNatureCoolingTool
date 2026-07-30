"""The duplication field groups must stay aligned with the engine's schema."""

from __future__ import annotations

from nature_cooling.api import main as main_module
from nature_cooling.api.schemas import (
    BLANKED_ON_DUPLICATE,
    COST_ENERGY_FIELDS,
    INPUT_FIELDS,
    INTERVENTION_FIELDS,
    SITE_DESCRIPTION_FIELDS,
)
from nature_cooling.engine.models import AssessmentInput


def test_field_groups_partition_the_engine_input_schema() -> None:
    assert set(AssessmentInput.model_fields) == INPUT_FIELDS
    assert BLANKED_ON_DUPLICATE <= INPUT_FIELDS
    assert not INTERVENTION_FIELDS & COST_ENERGY_FIELDS
    assert SITE_DESCRIPTION_FIELDS | BLANKED_ON_DUPLICATE == INPUT_FIELDS
    assert not SITE_DESCRIPTION_FIELDS & BLANKED_ON_DUPLICATE


def test_site_description_carries_the_d021_groups() -> None:
    # D-021: the site, climate, and vulnerability description travels with a
    # duplicate; the intervention (including its co-benefit overrides) and the
    # cost/energy answers do not.
    assert {"site_area_m2", "climate_zone", "vulnerable_population_presence"} <= (
        SITE_DESCRIPTION_FIELDS
    )
    assert {"nbs_type", "co_benefit_biodiversity", "capital_cost"} <= BLANKED_ON_DUPLICATE


def test_the_module_level_app_serves_uvicorn() -> None:
    assert main_module.app.title == "Nature for Cooling Rapid Assessment Tool"
