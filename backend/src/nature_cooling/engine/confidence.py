"""Branched per-block confidence (Methodology Report 6.2, D-011/OQ-09, D-024).

Confidence is computed separately for cooling, energy, economic, and equity
blocks from the completeness of the inputs feeding each. The field-to-block
mapping lives in ``derived_scores.yaml``: each block is a list of groups, and
a group counts as supplied when any of its fields is present (the LST anomaly
and the qualitative heat exposure level are alternative signals for the same
slot). A field answered ``unknown`` counts as not supplied.

Evidence confidence propagates: a typology rated low in the library caps the
cooling block at medium regardless of input completeness — complete inputs
cannot compensate for thin underlying evidence.
"""

from __future__ import annotations

from typing import Any

from nature_cooling.engine.config import ConfidenceLevel, MethodologyConfig, Typology
from nature_cooling.engine.models import AssessmentInput, ConfidenceBlock

_RANK: dict[str, int] = {"low": 0, "medium": 1, "high": 2}
_LEVELS: tuple[ConfidenceLevel, ...] = ("low", "medium", "high")


def _supplied(inp: AssessmentInput, field: str) -> bool:
    value = getattr(inp, field)
    return value is not None and value != "unknown"


def _completeness(inp: AssessmentInput, groups: list[list[str]]) -> float:
    supplied = sum(1 for group in groups if any(_supplied(inp, field) for field in group))
    return round(supplied / len(groups) * 100.0, 1)


def _level(percent: float, thresholds: dict[str, Any]) -> ConfidenceLevel:
    if percent < float(thresholds["low_below_percent"]):
        return "low"
    if percent <= float(thresholds["high_above_percent"]):
        return "medium"
    return "high"


def compute(inp: AssessmentInput, typology: Typology, config: MethodologyConfig) -> ConfidenceBlock:
    """Return per-block confidence, the overall rating, and completeness."""
    rules: dict[str, Any] = config.derived_scores["confidence"]
    thresholds: dict[str, Any] = rules["thresholds"]

    completeness: dict[str, float] = {}
    levels: dict[str, ConfidenceLevel] = {}
    for block in ("cooling", "energy", "economic", "equity"):
        percent = _completeness(inp, rules["blocks"][block])
        completeness[block] = percent
        levels[block] = _level(percent, thresholds)

    capped = False
    if typology.evidence_confidence == "low" and _RANK[levels["cooling"]] > _RANK["medium"]:
        levels["cooling"] = "medium"
        capped = True

    ranks = sorted(_RANK[levels[block]] for block in ("cooling", "energy", "economic", "equity"))
    overall = _LEVELS[ranks[1]]  # lower median of four

    return ConfidenceBlock(
        cooling=levels["cooling"],
        energy=levels["energy"],
        economic=levels["economic"],
        equity=levels["equity"],
        overall=overall,
        cooling_capped_by_evidence=capped,
        completeness_percent=completeness,
    )
