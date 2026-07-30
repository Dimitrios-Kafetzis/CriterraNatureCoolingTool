"""NbS Cooling Opportunity Score (Methodology Report 5.9).

When a component is unavailable — in practice, cost feasibility — it is
excluded and the remaining weights are renormalised to a unit sum. The
alternative, substituting a neutral 50, would silently reward projects that
supplied no economic evidence.
"""

from __future__ import annotations

from typing import cast

from nature_cooling.engine.config import MethodologyConfig
from nature_cooling.engine.models import (
    OpportunityBlock,
    OpportunityCategory,
    OpportunityComponent,
)
from nature_cooling.engine.normalisation import clamp, score_band

_COMPONENT_ORDER = (
    "heat_priority_index",
    "cooling_potential",
    "nbs_suitability",
    "vulnerability",
    "co_benefits",
    "cost_feasibility",
)


def compute(
    component_scores: dict[str, float | None], config: MethodologyConfig
) -> OpportunityBlock:
    """Aggregate the available components with proportional redistribution."""
    weights = config.weights["final_opportunity_score"]

    available = [name for name in _COMPONENT_ORDER if component_scores[name] is not None]
    excluded = [name for name in _COMPONENT_ORDER if component_scores[name] is None]
    total_weight = sum(float(weights[name]) for name in available)

    components: list[OpportunityComponent] = []
    weighted_sum = 0.0
    for name in available:
        score = component_scores[name]
        assert score is not None
        nominal = float(weights[name])
        applied = nominal / total_weight
        weighted_sum += applied * score
        components.append(
            OpportunityComponent(
                name=name,
                score=score,
                nominal_weight=nominal,
                applied_weight=round(applied, 4),
            )
        )

    score_value = round(clamp(weighted_sum), 2)
    category = cast(OpportunityCategory, score_band(config, "opportunity", score_value))
    return OpportunityBlock(
        score=score_value,
        category=category,
        components=components,
        excluded_components=excluded,
    )
