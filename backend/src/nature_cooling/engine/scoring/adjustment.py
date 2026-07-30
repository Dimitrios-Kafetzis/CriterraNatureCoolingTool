"""Derived site adjustment factor (Methodology Report 5.4, OQ-16/17).

All four conditions — canopy, soil-water, scale, climate — are derived from
inputs the user has already supplied, through the rules in
``adjustment_factors.yaml``. A condition whose inputs are absent resolves to
``unknown`` (neutral factor 1.0) with an itemised assumption; a level is never
guessed from partial information.
"""

from __future__ import annotations

from typing import Any, cast

from nature_cooling.engine.config import MethodologyConfig, Typology
from nature_cooling.engine.models import (
    AdjustmentBlock,
    AdjustmentCondition,
    AssessmentInput,
    ConditionLevel,
)

_CONDITION_ORDER: dict[str, int] = {"poor": 0, "moderate": 1, "good": 2, "excellent": 3}


def _factor(config: MethodologyConfig, level: str) -> float:
    return float(config.adjustment_factors["condition_factors"][level])


def _condition(
    config: MethodologyConfig, level: ConditionLevel, detail: str | None = None
) -> AdjustmentCondition:
    return AdjustmentCondition(level=level, factor=_factor(config, level), detail=detail)


def _canopy(
    inp: AssessmentInput, config: MethodologyConfig
) -> tuple[AdjustmentCondition, list[str]]:
    missing = [
        field
        for field, value in (
            ("existing_tree_canopy_percent", inp.existing_tree_canopy_percent),
            ("new_canopy_area_at_maturity_m2", inp.new_canopy_area_at_maturity_m2),
        )
        if value is None
    ]
    if missing:
        note = (
            f"canopy condition set to 'unknown' (factor 1.0): {' and '.join(missing)} not provided"
        )
        return _condition(config, "unknown"), [note]

    assert inp.existing_tree_canopy_percent is not None
    assert inp.new_canopy_area_at_maturity_m2 is not None
    percent = (
        inp.existing_tree_canopy_percent
        + inp.new_canopy_area_at_maturity_m2 / inp.site_area_m2 * 100.0
    )
    thresholds: dict[str, Any] = config.adjustment_factors["derivation"]["canopy_condition"][
        "thresholds"
    ]
    level: ConditionLevel = "poor"
    for candidate, bounds in thresholds.items():
        lower_ok = "min_percent" not in bounds or percent >= float(bounds["min_percent"])
        upper_ok = "max_percent" not in bounds or percent < float(bounds["max_percent"])
        if lower_ok and upper_ok:
            level = cast(ConditionLevel, candidate)
            break
    detail = f"combined canopy at maturity: {round(percent, 1)}% of site"
    return _condition(config, level, detail), []


def _soil_water(
    inp: AssessmentInput, config: MethodologyConfig
) -> tuple[AdjustmentCondition, list[str]]:
    rules = config.adjustment_factors["derivation"]["soil_water_condition"]
    mapping: dict[str, str] = rules["mapping"]
    levels: list[ConditionLevel] = []
    missing: list[str] = []
    for field, value in (
        ("soil_availability", inp.soil_availability),
        ("irrigation_availability", inp.irrigation_availability),
    ):
        if value in (None, "unknown"):
            missing.append(field)
        else:
            levels.append(cast(ConditionLevel, mapping[cast(str, value)]))
    if not levels:
        note = (
            "soil-water condition set to 'unknown' (factor 1.0): neither soil_availability "
            "nor irrigation_availability provided"
        )
        return _condition(config, "unknown"), [note]
    limiting = min(levels, key=lambda level: _CONDITION_ORDER[level])
    if missing:
        # A condition pair containing an unknown may never exceed the neutral
        # factor (D-026): the known half alone cannot certify 'excellent'.
        cap = cast(ConditionLevel, rules["unknown_partner_cap"])
        if _CONDITION_ORDER[limiting] > _CONDITION_ORDER[cap]:
            note = (
                f"soil-water condition capped at '{cap}': {missing[0]} not provided, and a "
                "condition pair containing an unknown cannot exceed the neutral factor"
            )
            return _condition(config, cap), [note]
    return _condition(config, limiting), []


def _scale(inp: AssessmentInput, config: MethodologyConfig) -> AdjustmentCondition:
    mapping: dict[str, str] = config.adjustment_factors["derivation"]["scale_condition"]["mapping"]
    return _condition(config, cast(ConditionLevel, mapping[inp.assessment_scale]))


def _climate(
    inp: AssessmentInput, typology: Typology, config: MethodologyConfig
) -> AdjustmentCondition:
    matrix: dict[str, dict[str, str]] = config.adjustment_factors["derivation"][
        "climate_condition"
    ]["matrix"]
    level = cast(ConditionLevel, matrix[inp.climate_zone][typology.category])
    detail = f"{typology.category} typology in {inp.climate_zone} climate zone"
    return _condition(config, level, detail)


def compute(
    inp: AssessmentInput, typology: Typology, config: MethodologyConfig
) -> tuple[AdjustmentBlock, list[str]]:
    """Derive the four site conditions and the composite adjustment factor."""
    canopy, canopy_notes = _canopy(inp, config)
    soil_water, soil_notes = _soil_water(inp, config)
    scale = _scale(inp, config)
    climate = _climate(inp, typology, config)

    weights = config.weights["site_adjustment"]
    factor = round(
        float(weights["canopy"]) * canopy.factor
        + float(weights["soil_water"]) * soil_water.factor
        + float(weights["scale"]) * scale.factor
        + float(weights["climate"]) * climate.factor,
        4,
    )
    block = AdjustmentBlock(
        factor=factor, canopy=canopy, soil_water=soil_water, scale=scale, climate=climate
    )
    return block, canopy_notes + soil_notes
