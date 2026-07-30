"""Deterministic recommendation composer (D-011/OQ-12).

Text is composed from ``recommendation_templates.yaml`` by score category and
result flags. No language model is involved anywhere in the scoring or
reporting path: identical inputs always produce identical text.

Fragment order is fixed: opening (heat priority band), opportunity band,
cooling clause, then flags — suitability first, evidence caveats next, missing
quantities after, low overall confidence last.
"""

from __future__ import annotations

from typing import Any

from nature_cooling.engine.config import MethodologyConfig, Typology
from nature_cooling.engine.models import AssessmentInput


def _fragment(text: Any) -> str:
    return str(text).strip()


def _format_temp(value: float) -> str:
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return text if "." in text else f"{text}.0"


def _reason(message: str) -> str:
    stripped = message.strip().rstrip(".")
    return stripped[0].lower() + stripped[1:]


def compose(
    inp: AssessmentInput,
    typology: Typology,
    *,
    config: MethodologyConfig,
    heat_priority_category: str,
    opportunity_category: str,
    delta_t_min_c: float,
    delta_t_max_c: float,
    suitability_flags: list[str],
    energy_status: str,
    energy_status_message: str,
    annual_savings_status: str,
    payback_status: str,
    overall_confidence: str,
) -> str:
    """Compose the recommendation text for one assessment."""
    templates = config.recommendation_templates
    parts: list[str] = []

    parts.append(_fragment(templates["opening"]["by_heat_priority"][heat_priority_category]))
    parts.append(_fragment(templates["opportunity"][opportunity_category]))
    parts.append(
        _fragment(templates["cooling_clause"]["template"]).format(
            display_name=typology.display_name,
            temp_min=_format_temp(delta_t_min_c),
            temp_max=_format_temp(delta_t_max_c),
            primary_cooling_mechanism=typology.primary_cooling_mechanism,
        )
    )

    flags = templates["flags"]

    if suitability_flags:
        parts.append(_fragment(flags["not_suitable"]).format(reasons="; ".join(suitability_flags)))
    if typology.evidence_confidence == "low":
        parts.append(_fragment(flags["low_evidence_confidence"]))
    for caveat in typology.output_caveats:
        parts.append(_fragment(flags[caveat]))
    rules: dict[str, Any] = templates["caveat_rules"]
    for caveat, condition in rules.items():
        if (
            typology.category in condition["categories"]
            and inp.climate_zone in condition["climate_zones"]
        ):
            parts.append(_fragment(flags[caveat]))

    if energy_status != "calculated":
        parts.append(
            _fragment(flags["energy_not_calculated"]).format(reason=_reason(energy_status_message))
        )
    if inp.capital_cost is None:
        parts.append(_fragment(flags["cost_not_estimated"]))
    elif payback_status != "calculated":
        reasons = {
            "energy_not_calculated": "energy savings were not calculated",
            "missing_energy_price": "no energy price was supplied",
        }
        parts.append(
            _fragment(flags["payback_not_estimated"]).format(
                reason=reasons.get(annual_savings_status, "annual cost savings are unavailable")
            )
        )
    if overall_confidence == "low":
        parts.append(_fragment(flags["low_confidence"]))

    return " ".join(parts)


def method_note(config: MethodologyConfig) -> str:
    """The standard limitations note attached to every result."""
    closing = config.recommendation_templates["closing"]
    return f"{_fragment(closing['standard'])} {_fragment(closing['daytime_only'])}"
