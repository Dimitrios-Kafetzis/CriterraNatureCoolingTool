"""Equity Score (D-022).

Reported as its own output block with its own confidence rating. It does NOT
enter the final aggregation — equity influences the headline score through the
Vulnerability Score instead, as disclosed in the Methodology Report.

Each sub-indicator reads how much equity benefit the intervention can deliver
here, so a deficit raises the score: greater vulnerable presence, and greater
safety and comfort concern, mean more equity value to gain.
"""

from __future__ import annotations

from typing import Any

from nature_cooling.engine.config import MethodologyConfig
from nature_cooling.engine.models import AssessmentInput, EquityBlock
from nature_cooling.engine.normalisation import clamp, default_note, qualitative_score

_SUB_INDICATORS = (
    "vulnerable_user_benefit",
    "public_accessibility",
    "safety_comfort",
    "participation_relevance",
)


def compute(inp: AssessmentInput, config: MethodologyConfig) -> tuple[EquityBlock, list[str]]:
    """Return the Equity Score and the assumptions it applied."""
    rules: dict[str, Any] = config.derived_scores["equity_sub_indicators"]
    assumptions: list[str] = []
    scores: dict[str, float] = {}

    for name in _SUB_INDICATORS:
        field = str(rules[name]["field"])
        value: str | None = getattr(inp, field)
        if value in (None, "unknown"):
            assumptions.append(default_note(field, value))
        scores[name] = qualitative_score(config, field, value)

    weights = config.weights["equity"]
    score = round(
        clamp(sum(float(weights[name]) * scores[name] for name in _SUB_INDICATORS)),
        2,
    )
    block = EquityBlock(
        score=score,
        vulnerable_user_benefit=scores["vulnerable_user_benefit"],
        public_accessibility=scores["public_accessibility"],
        safety_comfort=scores["safety_comfort"],
        participation_relevance=scores["participation_relevance"],
    )
    return block, assumptions
