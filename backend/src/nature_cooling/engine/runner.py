"""Assessment orchestration: the engine's public entry point.

``run_assessment`` is a pure function of (validated input, methodology
configuration): no I/O, no network access, no clock, no randomness, no global
mutable state. Identical input plus identical methodology version yields
byte-identical output.
"""

from __future__ import annotations

import nature_cooling
from nature_cooling.engine import confidence as confidence_module
from nature_cooling.engine import recommendation as recommendation_module
from nature_cooling.engine.config import ConfigError, MethodologyConfig, Typology
from nature_cooling.engine.models import AssessmentInput, AssessmentResult, TypologySummary
from nature_cooling.engine.scoring import (
    adjustment,
    co_benefits,
    cooling,
    costs,
    energy_ghg,
    equity,
    final_score,
    heat_exposure,
    heat_priority,
    suitability,
    vulnerability,
)


def _typology_for(inp: AssessmentInput, config: MethodologyConfig) -> Typology:
    try:
        return config.typologies.by_type(inp.nbs_type)
    except ConfigError as exc:
        raise ValueError(str(exc)) from exc


def _warnings(inp: AssessmentInput) -> list[str]:
    warnings: list[str] = []
    if (
        inp.existing_green_cover_percent is not None
        and inp.impervious_surface_percent is not None
        and inp.existing_green_cover_percent + inp.impervious_surface_percent > 105.0
    ):
        total = round(inp.existing_green_cover_percent + inp.impervious_surface_percent, 1)
        warnings.append(
            f"existing green cover plus impervious surface totals {total}%, "
            "which exceeds 105% of the site"
        )
    if inp.intervention_area_m2 is not None and inp.intervention_area_m2 > inp.site_area_m2:
        warnings.append(
            f"intervention area ({inp.intervention_area_m2:g} m2) exceeds site area "
            f"({inp.site_area_m2:g} m2)"
        )
    return warnings


def run_assessment(inp: AssessmentInput, config: MethodologyConfig) -> AssessmentResult:
    """Run one complete assessment. Pure and deterministic.

    Raises:
        ValueError: if ``inp.nbs_type`` names no typology in the library.
    """
    typology = _typology_for(inp, config)
    assumptions: list[str] = []

    heat_block, notes = heat_exposure.compute(inp, config)
    assumptions.extend(notes)

    vulnerability_block, notes = vulnerability.compute(inp, config)
    assumptions.extend(notes)

    heat_priority_block = heat_priority.compute(heat_block.score, vulnerability_block.score, config)

    adjustment_block, notes = adjustment.compute(inp, typology, config)
    assumptions.extend(notes)

    cooling_block = cooling.compute(inp, typology, adjustment_block.factor, config)

    suitability_block, notes = suitability.compute(inp, typology, config)
    assumptions.extend(notes)

    confidence_block = confidence_module.compute(inp, typology, config)

    energy_block = energy_ghg.compute_energy(inp, typology, cooling_block, config)
    ghg_block = energy_ghg.compute_ghg(inp, energy_block, config)
    if ghg_block.emission_factor_origin == "user_supplied":
        assumptions.append(
            "grid emission factor supplied by the user "
            f"({ghg_block.emission_factor_kgco2e_per_kwh} kgCO2e/kWh), "
            "not from shipped configuration"
        )

    costs_block, notes = costs.compute(inp, energy_block, confidence_block.energy, config)
    assumptions.extend(notes)
    if costs_block.annual_savings_status == "missing_energy_price":
        assumptions.append("energy price not provided; annual cost savings not computed")

    co_benefits_block, notes = co_benefits.compute(inp, typology, config)
    assumptions.extend(notes)

    equity_block, notes = equity.compute(inp, config)
    assumptions.extend(notes)

    cost_feasibility_score = (
        costs_block.cost_feasibility_score
        if costs_block.cost_feasibility_status == "derived"
        else None
    )
    if cost_feasibility_score is None:
        assumptions.append(
            "cost feasibility not estimated; excluded from the final aggregation "
            "and its weight redistributed proportionally"
        )
    opportunity_block = final_score.compute(
        {
            "heat_priority_index": heat_priority_block.score,
            "cooling_potential": cooling_block.potential_score,
            "nbs_suitability": suitability_block.score,
            "vulnerability": vulnerability_block.score,
            "co_benefits": co_benefits_block.score,
            "cost_feasibility": cost_feasibility_score,
        },
        config,
    )

    recommendation_text = recommendation_module.compose(
        inp,
        typology,
        config=config,
        heat_priority_category=heat_priority_block.category,
        opportunity_category=opportunity_block.category,
        delta_t_min_c=cooling_block.delta_t_min_c,
        delta_t_max_c=cooling_block.delta_t_max_c,
        suitability_flags=[flag.message for flag in suitability_block.flags],
        energy_status=energy_block.status,
        energy_status_message=energy_block.status_message,
        annual_savings_status=costs_block.annual_savings_status,
        payback_status=costs_block.payback_status,
        overall_confidence=confidence_block.overall,
    )

    return AssessmentResult(
        engine_version=nature_cooling.__version__,
        methodology_version=config.version,
        typology=TypologySummary(
            nbs_id=typology.nbs_id,
            nbs_type=typology.nbs_type,
            display_name=typology.display_name,
            category=typology.category,
            evidence_confidence=typology.evidence_confidence,
            base_cooling_score=typology.base_cooling_score,
            temp_reduction_min_c=typology.temp_reduction_min_c,
            temp_reduction_max_c=typology.temp_reduction_max_c,
        ),
        heat_exposure=heat_block,
        vulnerability=vulnerability_block,
        heat_priority=heat_priority_block,
        adjustment=adjustment_block,
        suitability=suitability_block,
        cooling=cooling_block,
        energy=energy_block,
        ghg=ghg_block,
        costs=costs_block,
        co_benefits=co_benefits_block,
        equity=equity_block,
        opportunity=opportunity_block,
        confidence=confidence_block,
        recommendation=recommendation_text,
        method_note=recommendation_module.method_note(config),
        assumptions_applied=assumptions,
        warnings=_warnings(inp),
    )
