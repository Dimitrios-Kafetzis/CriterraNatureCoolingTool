"""Heat Exposure Score (Methodology Report 5.1).

Two paths, selected by data availability: the data-rich path applies when a
land-surface-temperature anomaly is supplied; otherwise the qualitative heat
exposure level is used directly. On the data-rich path, a missing component
enters as the neutral 50 with an itemised assumption — the alternative,
propagating *not calculated* into a composite score, would block the score a
missing sub-input was only meant to weaken.
"""

from __future__ import annotations

from nature_cooling.engine.config import MethodologyConfig
from nature_cooling.engine.models import AssessmentInput, HeatExposureBlock
from nature_cooling.engine.normalisation import clamp, default_note, lst_score, qualitative_score


def compute(inp: AssessmentInput, config: MethodologyConfig) -> tuple[HeatExposureBlock, list[str]]:
    """Return the Heat Exposure Score and the assumptions it applied."""
    assumptions: list[str] = []

    if inp.lst_anomaly_c is None:
        if inp.heat_exposure_level in (None, "unknown"):
            assumptions.append(default_note("heat_exposure_level", inp.heat_exposure_level))
        score = qualitative_score(config, "heat_exposure_level", inp.heat_exposure_level)
        return HeatExposureBlock(score=round(score, 2), path="data_poor"), assumptions

    weights = config.weights["heat_exposure"]

    s_lst = lst_score(config, inp.lst_anomaly_c)

    if inp.impervious_surface_percent is None:
        s_imperviousness = 50.0
        assumptions.append(default_note("impervious_surface_percent", None))
    else:
        s_imperviousness = float(inp.impervious_surface_percent)

    if inp.solar_exposure in (None, "unknown"):
        assumptions.append(default_note("solar_exposure", inp.solar_exposure))
    s_solar = qualitative_score(config, "solar_exposure", inp.solar_exposure)

    if inp.existing_green_cover_percent is None:
        s_vegetation_deficit = 50.0
        assumptions.append(default_note("existing_green_cover_percent", None))
    else:
        s_vegetation_deficit = clamp(100.0 - inp.existing_green_cover_percent)

    score = clamp(
        float(weights["lst"]) * s_lst
        + float(weights["imperviousness"]) * s_imperviousness
        + float(weights["solar_exposure"]) * s_solar
        + float(weights["vegetation_deficit"]) * s_vegetation_deficit
    )
    return HeatExposureBlock(score=round(score, 2), path="data_rich"), assumptions
