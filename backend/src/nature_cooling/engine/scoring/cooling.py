"""Cooling Potential Score and temperature reduction (Methodology Report 5.5).

The 0-100 score scales freely with the site adjustment factor; the reported
degrees-Celsius range is clipped to the typology's literature envelope
(D-008). Site quality may degrade an estimate below the envelope; it may never
push a physical claim above published evidence.
"""

from __future__ import annotations

from typing import cast

from nature_cooling.engine.config import MethodologyConfig, Typology
from nature_cooling.engine.models import (
    AssessmentInput,
    CalculatedStatus,
    CoolingBlock,
    DerivedStatus,
    HeatIndexImprovement,
    TimeToBenefit,
)
from nature_cooling.engine.normalisation import clamp, clip, pick_bracket


def compute(
    inp: AssessmentInput, typology: Typology, adjustment_factor: float, config: MethodologyConfig
) -> CoolingBlock:
    """Return the cooling block: score, clipped range, and derived outputs."""
    envelope_min = typology.temp_reduction_min_c
    envelope_max = typology.temp_reduction_max_c

    potential = round(clamp(typology.base_cooling_score * adjustment_factor), 2)
    delta_t_min = round(clip(envelope_min * adjustment_factor, envelope_min, envelope_max), 2)
    delta_t_max = round(clip(envelope_max * adjustment_factor, envelope_min, envelope_max), 2)
    midpoint = round((delta_t_min + delta_t_max) / 2.0, 3)

    buckets = config.input_mapping["heat_index_improvement_buckets"]
    improvement: HeatIndexImprovement = "low"
    for label in ("low", "medium", "high"):
        bounds = buckets[label]
        lower_ok = "min_c" not in bounds or midpoint >= float(bounds["min_c"])
        upper_ok = "max_c" not in bounds or midpoint < float(bounds["max_c"])
        if lower_ok and upper_ok:
            improvement = label
            break

    shade_percent: float | None
    shade_status: CalculatedStatus
    if inp.new_canopy_area_at_maturity_m2 is None:
        shade_percent = None
        shade_status = "not_estimated"
    else:
        shade_percent = round(
            clamp(inp.new_canopy_area_at_maturity_m2 / inp.site_area_m2 * 100.0), 2
        )
        shade_status = "calculated"

    time_to_benefit: TimeToBenefit | None
    time_status: DerivedStatus
    if inp.expected_maturity_period_years is None:
        time_to_benefit = None
        time_status = "not_estimated"
    else:
        bucket = pick_bracket(
            config.derived_scores["time_to_benefit"]["buckets"],
            inp.expected_maturity_period_years,
            "min_years",
            "max_years",
        )
        time_to_benefit = cast(TimeToBenefit, bucket["label"])
        time_status = "derived"

    return CoolingBlock(
        potential_score=potential,
        delta_t_min_c=delta_t_min,
        delta_t_max_c=delta_t_max,
        delta_t_midpoint_c=midpoint,
        heat_index_improvement=improvement,
        shade_potential_percent=shade_percent,
        shade_potential_status=shade_status,
        time_to_benefit=time_to_benefit,
        time_to_benefit_status=time_status,
    )
