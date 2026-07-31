"""Normalisation helpers: qualitative levels, bounds, brackets, and bands.

All lookups read the injected configuration; nothing here carries a
methodology value. Two bounding operators from the Methodology Report are
implemented: ``clamp`` bounds a score to the 0-100 reporting scale, ``clip``
bounds a physical estimate to a stated envelope (D-008).
"""

from __future__ import annotations

from typing import Any

from nature_cooling.engine.config import MethodologyConfig


def clamp(value: float) -> float:
    """Bound a score to the 0-100 reporting scale."""
    return min(100.0, max(0.0, value))


def clip(value: float, lower: float, upper: float) -> float:
    """Bound a physical estimate to a stated envelope."""
    return min(upper, max(lower, value))


def qualitative_score(config: MethodologyConfig, field: str, value: str | None) -> float:
    """Normalise a qualitative level to 0-100 via ``input_mapping.yaml``.

    ``None`` is treated as the explicit level ``unknown``. The field's entry
    may name a shared scale (``standard_levels`` / ``inverted_levels``), wrap
    one in a mapping with a ``scale`` key, or carry an inline level table.
    """
    spec: Any = config.input_mapping["fields"][field]
    if isinstance(spec, dict) and "scale" in spec:
        spec = spec["scale"]
    table: dict[str, Any] = config.input_mapping[spec] if isinstance(spec, str) else dict(spec)
    return float(table[value if value is not None else "unknown"])


def lst_score(config: MethodologyConfig, anomaly_c: float) -> float:
    """Convert a land-surface-temperature anomaly to a 0-100 score (OQ-05)."""
    rule: Any = config.input_mapping["lst_normalisation"]
    zero = float(rule["anomaly_c_at_zero"])
    hundred = float(rule["anomaly_c_at_hundred"])
    return clamp((anomaly_c - zero) / (hundred - zero) * 100.0)


def pick_bracket(
    brackets: list[dict[str, Any]],
    value: float,
    min_key: str,
    max_key: str,
) -> dict[str, Any]:
    """Return the first bracket containing ``value`` (>= min, < max)."""
    for bracket in brackets:
        lower_ok = min_key not in bracket or value >= float(bracket[min_key])
        upper_ok = max_key not in bracket or value < float(bracket[max_key])
        if lower_ok and upper_ok:
            return bracket
    raise ValueError(f"no bracket contains {value}")


def score_band(config: MethodologyConfig, band_set: str, score: float) -> str:
    """Return the interpretation band label for a score ((min, max] bands)."""
    bands: list[dict[str, Any]] = config.derived_scores["score_bands"][band_set]
    for band in bands:
        if "max" not in band or score <= float(band["max"]):
            return str(band["label"])
    raise ValueError(f"no band contains {score}")  # pragma: no cover - defensive


def default_note(field: str, value: str | None) -> str:
    """The ``assumptions_applied`` entry for a neutrally defaulted field."""
    if value == "unknown":
        return f"{field} answered 'unknown'; neutral value 50 applied"
    return f"{field} not provided; neutral value 50 applied"


def dimension_default_note(dimension: str) -> str:
    """The ``assumptions_applied`` entry for a neutrally defaulted dimension.

    Used where a dimension is measured by several alternative indicators and
    none was supplied (D-039): one default was applied, so one entry is
    itemised, naming the dimension rather than each unanswered indicator.
    """
    return f"{dimension}: no indicator supplied; neutral value 50 applied"
