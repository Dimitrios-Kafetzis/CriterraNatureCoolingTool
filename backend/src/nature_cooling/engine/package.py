"""Multi-intervention package combination (D-038 semantics, D-044.4 bound).

An assessment proposes one or more catalogue entries. Each is scored
individually by the ordinary scoring modules; this module says how the
individual results combine into the package's headline outputs, and nothing
else. It computes no new methodology value: every rule below either selects
among component results or takes an extremum of them.

The one rule that matters most is the one this release must not get wrong:
**temperature is capped at the best-evidenced single component and never
summed.** D-014 established that no retrieved source quantifies super-additive
cooling from combining measures, and this is that finding applied rather than
re-argued.
"""

from __future__ import annotations

from nature_cooling.engine.config import MethodologyConfig
from nature_cooling.engine.models import (
    CoBenefitsBlock,
    ComponentBlock,
    PackageBlock,
    SuitabilityBlock,
    SuitabilityFlag,
)
from nature_cooling.engine.normalisation import clamp

_EVIDENCE_RANK = {"low": 0, "medium": 1, "high": 2}

_CO_BENEFIT_DIMENSIONS = (
    "biodiversity",
    "stormwater",
    "public_health",
    "social_inclusion",
    "urban_quality",
)

COOLING_RULE = (
    "capped at the best-evidenced component's adjusted range; component estimates are never summed"
)
CO_BENEFIT_RULE = "union of the components: the maximum per dimension"
SUITABILITY_RULE = "the minimum across components: a package is limited by its weakest fit"
COST_RULE = "capital cost is entered once for the whole package and is not apportioned"


def _evidence_key(component: ComponentBlock) -> tuple[int, float]:
    """Rank one component as a candidate to carry the package's headline.

    Highest evidence rating first; ties broken by the wider adjusted envelope,
    so among equally well-evidenced components the package reports the stronger
    one rather than an arbitrary one.
    """
    return (
        _EVIDENCE_RANK[component.typology.evidence_confidence],
        component.cooling.delta_t_max_c,
    )


def choose_representative(components: list[ComponentBlock]) -> int:
    """Index of the component whose cooling the package reports.

    Deterministic: ties on both evidence and range fall to the earliest
    component, which is the user's own selection order.
    """
    best = 0
    for index in range(1, len(components)):
        if _evidence_key(components[index]) > _evidence_key(components[best]):
            best = index
    return best


def choose_energy_component(components: list[ComponentBlock]) -> int | None:
    """Index of the component the energy derivation follows, if any.

    The same selection rule restricted to components whose typology is
    building-energy applicable. Restricting rather than summing keeps the
    derivation traceable to exactly one component: energy savings are a
    function of one cooling estimate (D-015), and the package has only one.
    """
    applicable = [
        index
        for index, component in enumerate(components)
        if component.typology.building_energy_applicable
    ]
    if not applicable:
        return None
    return max(applicable, key=lambda index: _evidence_key(components[index]))


def combine_co_benefits(
    components: list[ComponentBlock], config: MethodologyConfig
) -> CoBenefitsBlock:
    """Union the components' co-benefits: the maximum per dimension.

    A package delivers each dimension at least as well as its best component
    does, and adding a component can only broaden the benefit — which is
    exactly the advantage a package has, since it is not permitted to claim
    additional degrees.
    """
    best = {
        dimension: max(getattr(component.co_benefits, dimension) for component in components)
        for dimension in _CO_BENEFIT_DIMENSIONS
    }
    weights = config.weights["co_benefits"]
    score = round(
        clamp(sum(float(weights[dimension]) * best[dimension] for dimension in best)),
        2,
    )
    return CoBenefitsBlock(score=score, **best)


def combine_suitability(components: list[ComponentBlock]) -> SuitabilityBlock:
    """Take the least suitable component, carrying every component's flags.

    The score is the minimum, not the mean: a package cannot be more
    deliverable on this site than its worst-fitting member, and averaging would
    let a well-fitting component hide one that cannot be built here. Flags stay
    per component and all of them are surfaced, each naming its own entry, so
    the user sees which part of the package is the problem.
    """
    weakest = min(components, key=lambda component: component.suitability.score)
    flags: list[SuitabilityFlag] = []
    for component in components:
        for flag in component.suitability.flags:
            flags.append(
                SuitabilityFlag(
                    code=flag.code,
                    message=(
                        flag.message
                        if len(components) == 1
                        else f"{component.typology.display_name}: {flag.message}"
                    ),
                )
            )
    return SuitabilityBlock(
        score=weakest.suitability.score,
        space=weakest.suitability.space,
        soil=weakest.suitability.soil,
        water=weakest.suitability.water,
        maintenance=weakest.suitability.maintenance,
        urban_context=weakest.suitability.urban_context,
        flags=flags,
        suitable=not flags,
    )


def describe(
    components: list[ComponentBlock],
    representative: int,
    energy_component: int | None,
) -> PackageBlock:
    """State how this package's headline outputs were combined."""
    carrier = components[representative].typology
    reason = (
        "the only component"
        if len(components) == 1
        else (
            f"the best-evidenced component ({carrier.evidence_confidence} evidence, "
            f"inherited from the {carrier.archetype_display_name} class)"
        )
    )
    return PackageBlock(
        component_count=len(components),
        representative_nbs_type=carrier.nbs_type,
        representative_reason=reason,
        cooling_rule=COOLING_RULE,
        co_benefit_rule=CO_BENEFIT_RULE,
        suitability_rule=SUITABILITY_RULE,
        cost_rule=COST_RULE,
        energy_component_nbs_type=(
            None if energy_component is None else components[energy_component].typology.nbs_type
        ),
    )


def size_warnings(components: list[ComponentBlock], config: MethodologyConfig) -> list[str]:
    """The D-044.4 warning, which states plainly what a cap would have hidden."""
    threshold = int(config.availability["packages"]["warn_above_components"])
    if len(components) <= threshold:
        return []
    return [
        f"this package has {len(components)} components, above the {threshold} at which the "
        "tool warns: the combined temperature estimate is carried by the best-evidenced "
        "component and is never summed, so adding a further component will not raise it — "
        "it adds co-benefit breadth and capital cost only"
    ]
