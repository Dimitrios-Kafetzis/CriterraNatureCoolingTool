"""Assessment orchestration: the engine's public entry point.

``run_assessment`` is a pure function of (validated input, methodology
configuration): no I/O, no network access, no clock, no randomness, no global
mutable state. Identical input plus identical methodology version yields
byte-identical output.

Since ``2026.08.04`` an assessment proposes one or more catalogue entries
(D-044.2). Each is scored individually by the same modules that have always
scored one; :mod:`nature_cooling.engine.package` then combines the component
results into the package's headline outputs under rules that never sum a
temperature. A single-intervention assessment is a package of one, so its
top-level blocks are exactly its only component's.
"""

from __future__ import annotations

import nature_cooling
from nature_cooling.engine import availability as availability_module
from nature_cooling.engine import confidence as confidence_module
from nature_cooling.engine import package as package_module
from nature_cooling.engine import recommendation as recommendation_module
from nature_cooling.engine.config import ConfigError, MethodologyConfig, Typology
from nature_cooling.engine.models import (
    AssessmentInput,
    AssessmentResult,
    ComponentBlock,
    TypologySummary,
)
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


def _typologies_for(inp: AssessmentInput, config: MethodologyConfig) -> list[Typology]:
    try:
        return [config.typologies.by_type(name) for name in inp.nbs_type]
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


def _availability_warnings(
    inp: AssessmentInput, typologies: list[Typology], config: MethodologyConfig
) -> list[str]:
    """Warn where a selected entry is not one the matrix offers here.

    Never an error: availability guides selection and never blocks it (D-019),
    and a professional deliberately testing a hypothesis is not overridden. The
    warning states the fact so it reaches the report rather than being silently
    dropped.
    """
    conditions = availability_module.site_conditions(inp)
    withheld = [
        typology.display_name
        for typology in typologies
        if not availability_module.is_available(
            typology, inp.assessment_scale, inp.land_use, conditions, config
        )
    ]
    if not withheld:
        return []
    return [
        f"selected but not offered for this site by the availability matrix: "
        f"{', '.join(withheld)}; scored as specified"
    ]


_CO_BENEFIT_DIMENSIONS = (
    "biodiversity",
    "stormwater",
    "public_health",
    "social_inclusion",
    "urban_quality",
)


def _co_benefit_summary(label: str, inp: AssessmentInput, typology: Typology) -> str:
    """One itemised line covering a component's co-benefit defaults.

    A package applies the same handful of defaults once per component, and
    repeating five near-identical sentences for each of them buries the
    disclosure they exist to make. This states the same facts — which
    dimensions took the library's cited default, and which had no default and
    fell to the neutral 50 — in a form that stays legible at six components.
    The defaults themselves are identical either way; only their itemisation
    differs.
    """
    from_library: list[str] = []
    neutral: list[str] = []
    for name in _CO_BENEFIT_DIMENSIONS:
        if getattr(inp, f"co_benefit_{name}") not in (None, "unknown"):
            continue
        (from_library if typology.co_benefit_defaults.get(name) else neutral).append(name)

    parts: list[str] = []
    if from_library:
        parts.append(f"{', '.join(from_library)} taken from the typology's library defaults")
    if neutral:
        parts.append(f"{', '.join(neutral)} has no typology default; neutral value 50 applied")
    return f"{label}: co-benefits — {'; '.join(parts)}"


def _component(
    inp: AssessmentInput,
    typology: Typology,
    config: MethodologyConfig,
    *,
    in_package: bool,
) -> tuple[ComponentBlock, list[str]]:
    """Score one package component on its own values.

    ``in_package`` changes only how the co-benefit defaults are *itemised*, not
    which are applied: every component applies the same defaults either way.
    """
    assumptions: list[str] = []
    label = typology.display_name

    adjustment_block, notes = adjustment.compute(inp, typology, config)
    assumptions.extend(notes)

    cooling_block = cooling.compute(inp, typology, adjustment_block.factor, config)

    suitability_block, notes = suitability.compute(inp, typology, config)
    assumptions.extend(notes)

    co_benefits_block, notes = co_benefits.compute(inp, typology, config)
    if not in_package:
        assumptions.extend(notes)
    elif notes:
        assumptions.append(_co_benefit_summary(label, inp, typology))

    block = ComponentBlock(
        typology=TypologySummary.of(typology),
        adjustment=adjustment_block,
        suitability=suitability_block,
        cooling=cooling_block,
        co_benefits=co_benefits_block,
        is_representative=False,
    )
    return block, assumptions


def run_assessment(inp: AssessmentInput, config: MethodologyConfig) -> AssessmentResult:
    """Run one complete assessment. Pure and deterministic.

    Raises:
        ValueError: if any entry in ``inp.nbs_type`` names no typology.
    """
    typologies = _typologies_for(inp, config)
    assumptions: list[str] = []

    heat_block, notes = heat_exposure.compute(inp, config)
    assumptions.extend(notes)

    vulnerability_block, notes = vulnerability.compute(inp, config)
    assumptions.extend(notes)

    heat_priority_block = heat_priority.compute(heat_block.score, vulnerability_block.score, config)

    components: list[ComponentBlock] = []
    component_assumptions: list[str] = []
    in_package = len(typologies) > 1
    for typology in typologies:
        block, notes = _component(inp, typology, config, in_package=in_package)
        components.append(block)
        component_assumptions.extend(notes)

    representative = package_module.choose_representative(components)
    energy_index = package_module.choose_energy_component(components)
    components = [
        block.model_copy(update={"is_representative": index == representative})
        for index, block in enumerate(components)
    ]
    carrier = typologies[representative]
    carrier_block = components[representative]

    # Component-level assumptions are itemised only where the package has more
    # than one component; for a single component they are the assessment's own,
    # exactly as before.
    if len(components) == 1:
        assumptions.extend(component_assumptions)
    else:
        assumptions.extend(component_assumptions)
        assumptions.append(
            f"package temperature reported from {carrier.display_name}, "
            f"{package_module.COOLING_RULE}"
        )

    suitability_block = package_module.combine_suitability(components)
    co_benefits_block = package_module.combine_co_benefits(components, config)
    cooling_block = carrier_block.cooling

    confidence_block = confidence_module.compute(inp, carrier, config)

    energy_typology = typologies[energy_index] if energy_index is not None else carrier
    energy_cooling = components[energy_index].cooling if energy_index is not None else cooling_block
    energy_block = energy_ghg.compute_energy(inp, energy_typology, energy_cooling, config)
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
        carrier,
        config=config,
        components=components,
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
        typology=carrier_block.typology,
        components=components,
        package=package_module.describe(components, representative, energy_index),
        heat_exposure=heat_block,
        vulnerability=vulnerability_block,
        heat_priority=heat_priority_block,
        adjustment=carrier_block.adjustment,
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
        warnings=_warnings(inp)
        + _availability_warnings(inp, typologies, config)
        + package_module.size_warnings(components, config),
    )
