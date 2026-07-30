"""NbS Suitability Score and hard suitability flags (D-009, D-022).

Sub-indicator rules live in ``derived_scores.yaml``. A disqualifying condition
scores 25 on its axis and raises a named flag; the assessment still computes
and returns transparently (D-009). No flag is ever raised from absent
information — a disqualification requires positive evidence.
"""

from __future__ import annotations

from typing import Any

from nature_cooling.engine.config import MethodologyConfig, Typology
from nature_cooling.engine.models import (
    AssessmentInput,
    SuitabilityBlock,
    SuitabilityFlag,
    SuitabilityFlagCode,
)
from nature_cooling.engine.normalisation import (
    clamp,
    default_note,
    pick_bracket,
    qualitative_score,
)


def _space(
    inp: AssessmentInput, typology: Typology, rules: dict[str, Any]
) -> tuple[float, SuitabilityFlag | None]:
    ratio = inp.site_area_m2 / typology.suitability.minimum_site_area_m2
    bracket = pick_bracket(rules["space"]["brackets"], ratio, "min_ratio", "max_ratio")
    flag = None
    if "flag" in bracket:
        message = (
            f"site area {inp.site_area_m2:g} m2 is below the minimum viable area of "
            f"{typology.suitability.minimum_site_area_m2:g} m2 for {typology.display_name}"
        )
        flag = SuitabilityFlag(code="below_minimum_area", message=message)
    return float(bracket["score"]), flag


def _requirement_match(
    required: str,
    available: str | None,
    ranks: dict[str, int],
    rules: dict[str, Any],
    flag_code: SuitabilityFlagCode,
    flag_message: str,
    field: str,
) -> tuple[float, SuitabilityFlag | None, list[str]]:
    match = rules["requirement_match"]
    if ranks[required] == 0:
        return float(match["no_requirement"]), None, []
    if available in (None, "unknown"):
        return (
            float(match["unknown_availability"]),
            None,
            [default_note(field, available)],
        )
    gap = ranks[available] - ranks[required]
    if gap < 0:
        flag = SuitabilityFlag(code=flag_code, message=flag_message)
        return float(match["below_requirement"]), flag, []
    if gap == 0:
        return float(match["meets_requirement"]), None, []
    return float(match["exceeds_requirement"]), None, []


def compute(
    inp: AssessmentInput, typology: Typology, config: MethodologyConfig
) -> tuple[SuitabilityBlock, list[str]]:
    """Return the NbS Suitability Score, sub-indicators, flags, assumptions."""
    rules: dict[str, Any] = config.derived_scores["suitability_sub_indicators"]
    assumptions: list[str] = []
    flags: list[SuitabilityFlag] = []

    space_score, space_flag = _space(inp, typology, rules)
    if space_flag is not None:
        flags.append(space_flag)

    soil_ranks: dict[str, int] = rules["requirement_match"]["soil_ranks"]
    soil_score, soil_flag, soil_notes = _requirement_match(
        typology.suitability.requires_soil,
        inp.soil_availability,
        soil_ranks,
        rules,
        "insufficient_soil",
        f"soil availability '{inp.soil_availability}' is below the typology requirement "
        f"'{typology.suitability.requires_soil}'",
        "soil_availability",
    )
    if soil_flag is not None:
        flags.append(soil_flag)
    assumptions.extend(soil_notes)

    irrigation_ranks: dict[str, int] = rules["requirement_match"]["irrigation_ranks"]
    water_score, water_flag, water_notes = _requirement_match(
        typology.suitability.requires_irrigation,
        inp.irrigation_availability,
        irrigation_ranks,
        rules,
        "insufficient_irrigation",
        f"irrigation availability '{inp.irrigation_availability}' is below the typology "
        f"requirement '{typology.suitability.requires_irrigation}'",
        "irrigation_availability",
    )
    if water_flag is not None:
        flags.append(water_flag)
    assumptions.extend(water_notes)

    if inp.maintenance_intensity in (None, "unknown"):
        assumptions.append(default_note("maintenance_intensity", inp.maintenance_intensity))
    maintenance_score = qualitative_score(
        config, "maintenance_intensity", inp.maintenance_intensity
    )

    context_rules = rules["urban_context"]
    if inp.land_use is None:
        context_score = float(context_rules["unknown"])
        assumptions.append(default_note("land_use", None))
    elif inp.land_use in typology.typical_use_context:
        context_score = float(context_rules["in_context"])
    else:
        context_score = float(context_rules["out_of_context"])

    if inp.climate_zone in typology.suitability.unsuitable_climate_zones:
        flags.append(
            SuitabilityFlag(
                code="unsuitable_climate",
                message=(
                    f"climate zone '{inp.climate_zone}' is declared unsuitable for "
                    f"{typology.display_name}"
                ),
            )
        )

    weights = config.weights["nbs_suitability"]
    score = round(
        clamp(
            float(weights["space"]) * space_score
            + float(weights["soil"]) * soil_score
            + float(weights["water"]) * water_score
            + float(weights["maintenance"]) * maintenance_score
            + float(weights["urban_context"]) * context_score
        ),
        2,
    )
    block = SuitabilityBlock(
        score=score,
        space=space_score,
        soil=soil_score,
        water=water_score,
        maintenance=maintenance_score,
        urban_context=context_score,
        flags=flags,
        suitable=not flags,
    )
    return block, assumptions
