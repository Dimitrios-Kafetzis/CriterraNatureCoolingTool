"""Heat Priority Index (Methodology Report 5.3)."""

from __future__ import annotations

from typing import cast

from nature_cooling.engine.config import MethodologyConfig
from nature_cooling.engine.models import HeatPriorityBlock, HeatPriorityCategory
from nature_cooling.engine.normalisation import clamp, score_band


def compute(
    heat_exposure_score: float, vulnerability_score: float, config: MethodologyConfig
) -> HeatPriorityBlock:
    """Combine heat exposure and vulnerability into the Heat Priority Index."""
    weights = config.weights["heat_priority_index"]
    score = round(
        clamp(
            float(weights["heat_exposure"]) * heat_exposure_score
            + float(weights["vulnerability"]) * vulnerability_score
        ),
        2,
    )
    category = cast(HeatPriorityCategory, score_band(config, "heat_priority_index", score))
    return HeatPriorityBlock(score=score, category=category)
