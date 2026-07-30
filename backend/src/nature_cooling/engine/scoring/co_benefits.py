"""Co-benefit Score (OQ-18): typology defaults with user override.

The library supplies cited default levels for four of the five sub-indicators;
social inclusion has no defensible typology default and falls to the neutral
50 unless the user supplies it, itemised as an applied assumption.
"""

from __future__ import annotations

from nature_cooling.engine.config import MethodologyConfig, Typology
from nature_cooling.engine.models import AssessmentInput, CoBenefitsBlock
from nature_cooling.engine.normalisation import clamp

_SUB_INDICATORS = (
    "biodiversity",
    "stormwater",
    "public_health",
    "social_inclusion",
    "urban_quality",
)


def compute(
    inp: AssessmentInput, typology: Typology, config: MethodologyConfig
) -> tuple[CoBenefitsBlock, list[str]]:
    """Return the Co-benefit Score and the assumptions it applied."""
    assumptions: list[str] = []
    levels: dict[str, float] = dict(config.input_mapping["standard_levels"])
    scores: dict[str, float] = {}

    for name in _SUB_INDICATORS:
        override: str | None = getattr(inp, f"co_benefit_{name}")
        if override not in (None, "unknown"):
            scores[name] = float(levels[override])
            continue
        default = typology.co_benefit_defaults.get(name)
        if default is None:
            scores[name] = float(levels["unknown"])
            assumptions.append(
                f"co-benefit '{name}' has no typology default and was not provided; "
                "neutral value 50 applied"
            )
        else:
            scores[name] = float(levels[default])
            assumptions.append(f"co-benefit '{name}' taken from the typology default '{default}'")

    weights = config.weights["co_benefits"]
    score = round(
        clamp(sum(float(weights[name]) * scores[name] for name in _SUB_INDICATORS)),
        2,
    )
    block = CoBenefitsBlock(
        score=score,
        biodiversity=scores["biodiversity"],
        stormwater=scores["stormwater"],
        public_health=scores["public_health"],
        social_inclusion=scores["social_inclusion"],
        urban_quality=scores["urban_quality"],
    )
    return block, assumptions
