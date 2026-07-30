"""Cost outputs: savings, payback, derived feasibility, readiness (5.8, D-010, D-016).

No default cost values exist. Without a user-supplied capital cost there is no
payback and no cost feasibility — all reported as ``not_estimated``, and the
feasibility weight is redistributed in the final aggregation rather than
substituted with a neutral 50.

The payback bracket is applied to the payback computed from the central energy
estimate (the midpoint of the savings range); the reported payback interval
still carries both ends. Investment readiness resolves OQ-11.
"""

from __future__ import annotations

from typing import Any, cast

from nature_cooling.engine.config import ConfidenceLevel, MethodologyConfig
from nature_cooling.engine.models import (
    AnnualSavingsStatus,
    AssessmentInput,
    CostsBlock,
    DerivedStatus,
    EnergyBlock,
    PaybackBracket,
    PaybackStatus,
    ReadinessLevel,
)
from nature_cooling.engine.normalisation import default_note, pick_bracket, qualitative_score


def _downgrade(level: ReadinessLevel, order: list[str]) -> ReadinessLevel:
    index = order.index(level)
    return cast(ReadinessLevel, order[max(0, index - 1)])


def compute(
    inp: AssessmentInput,
    energy: EnergyBlock,
    energy_confidence: ConfidenceLevel,
    config: MethodologyConfig,
) -> tuple[CostsBlock, list[str]]:
    """Return the costs block and the assumptions it applied."""
    assumptions: list[str] = []

    annual_status: AnnualSavingsStatus
    annual_min: float | None = None
    annual_max: float | None = None
    if energy.status != "calculated":
        annual_status = "energy_not_calculated"
    elif inp.energy_price_per_kwh is None:
        annual_status = "missing_energy_price"
    else:
        assert energy.savings_min_kwh_per_year is not None
        assert energy.savings_max_kwh_per_year is not None
        annual_min = round(energy.savings_min_kwh_per_year * inp.energy_price_per_kwh, 2)
        annual_max = round(energy.savings_max_kwh_per_year * inp.energy_price_per_kwh, 2)
        annual_status = "calculated"

    payback_status: PaybackStatus
    payback_min: float | None = None
    payback_max: float | None = None
    payback_central: float | None = None
    if inp.capital_cost is None:
        payback_status = "missing_capital_cost"
    elif annual_status != "calculated" or annual_min is None or annual_min <= 0:
        payback_status = "annual_savings_unavailable"
    else:
        assert annual_max is not None
        payback_min = round(inp.capital_cost / annual_max, 2)
        payback_max = round(inp.capital_cost / annual_min, 2)
        payback_central = round(inp.capital_cost / ((annual_min + annual_max) / 2.0), 2)
        payback_status = "calculated"

    feasibility_status: DerivedStatus
    feasibility_score: float | None = None
    bracket_label: PaybackBracket | None = None
    if payback_status != "calculated":
        feasibility_status = "not_estimated"
    else:
        assert payback_central is not None
        rules: dict[str, Any] = config.derived_scores["cost_feasibility"]
        bracket = pick_bracket(rules["payback_brackets"], payback_central, "min_years", "max_years")
        bracket_label = cast(PaybackBracket, bracket["label"])

        if inp.implementation_complexity in (None, "unknown"):
            assumptions.append(
                default_note("implementation_complexity", inp.implementation_complexity)
            )
        complexity_score = qualitative_score(
            config, "implementation_complexity", inp.implementation_complexity
        )
        if inp.maintenance_intensity in (None, "unknown"):
            assumptions.append(default_note("maintenance_intensity", inp.maintenance_intensity))
        maintenance_score = qualitative_score(
            config, "maintenance_intensity", inp.maintenance_intensity
        )

        weights = config.weights["cost_feasibility"]
        feasibility_score = round(
            float(weights["payback"]) * float(bracket["score"])
            + float(weights["implementation_complexity"]) * complexity_score
            + float(weights["maintenance_intensity"]) * maintenance_score,
            2,
        )
        feasibility_status = "derived"

    readiness_status: DerivedStatus
    readiness: ReadinessLevel | None = None
    if feasibility_status != "derived":
        readiness_status = "not_estimated"
    else:
        assert bracket_label is not None
        rules = config.derived_scores["investment_readiness"]
        order: list[str] = rules["levels_order"]
        readiness = cast(ReadinessLevel, rules["base_by_payback_bracket"][bracket_label])
        if bool(rules["downgrade_if_complexity_high"]) and inp.implementation_complexity == "high":
            readiness = _downgrade(readiness, order)
        if bool(rules["downgrade_if_energy_confidence_low"]) and energy_confidence == "low":
            readiness = _downgrade(readiness, order)
        readiness_status = "derived"

    block = CostsBlock(
        annual_savings_status=annual_status,
        annual_savings_min=annual_min,
        annual_savings_max=annual_max,
        currency=inp.currency,
        payback_status=payback_status,
        payback_years_min=payback_min,
        payback_years_max=payback_max,
        payback_years_central=payback_central,
        cost_feasibility_status=feasibility_status,
        cost_feasibility_score=feasibility_score,
        payback_bracket=bracket_label,
        investment_readiness_status=readiness_status,
        investment_readiness=readiness,
    )
    return block, assumptions
