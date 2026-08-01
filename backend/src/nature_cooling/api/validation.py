"""Dry-run validation and the confidence preview (D-028).

``validate_payload`` takes the questionnaire state as the user has it — any
subset of the engine's input fields — and returns exactly what the inline form
needs (OQ-04/08, UX specification sections 3-4):

* **errors**, which block progression within their step: invalid values,
  missing required fields, unknown fields, and an unknown typology;
* **warnings**, which never block — produced by the engine's own rules
  (``runner._warnings``), never re-implemented here;
* a **per-block confidence preview** computed by
  ``nature_cooling.engine.confidence``, with the highest-value missing field
  hint per block: the first unsupplied field group in the configured
  ``derived_scores.yaml`` order whose single completion would raise the
  block's confidence level, falling back to the first unsupplied group when no
  single completion raises the level.

Everything is deterministic and config-driven; no threshold, level, or warning
text originates in this module.
"""

from __future__ import annotations

import math
from typing import Any

from pydantic import ValidationError

from nature_cooling.api.schemas import (
    BlockConfidencePreview,
    ConfidenceHint,
    ConfidencePreview,
    FieldIssue,
    ValidateResponse,
)
from nature_cooling.engine import confidence as confidence_module
from nature_cooling.engine import runner as runner_module
from nature_cooling.engine.config import ConfigError, MethodologyConfig, Typology
from nature_cooling.engine.models import AssessmentInput

_BLOCKS = ("cooling", "energy", "economic", "equity")
_RANK = {"low": 0, "medium": 1, "high": 2}

# Placeholders for absent required fields, so the engine's confidence and
# warning code can run against a structurally complete input. None of the
# required fields appears in any confidence block, so the placeholders cannot
# alter completeness. The site area is +inf so that an absent site area never
# fabricates an "intervention exceeds site area" warning.
_REQUIRED_PLACEHOLDERS: dict[str, Any] = {
    "assessment_scale": "site",
    "site_area_m2": math.inf,
    "climate_zone": "other",
    "nbs_type": ["__unset__"],
}

# A stand-in for the presence-only completion probe (see ``_hint``): the
# engine's completeness check asks only whether a value is neither ``None``
# nor ``"unknown"``, so any other sentinel marks a field as supplied.
_SUPPLIED_SENTINEL = 1.0


def _no_cap_typology() -> Typology:
    # When no typology is resolvable yet (step 5 not reached, or an unknown
    # nbs_type), the evidence-confidence cap cannot apply. The confidence
    # module reads only ``evidence_confidence``, so a minimal stand-in rated
    # high (= no cap) lets the engine compute the preview unchanged.
    return Typology.model_construct(evidence_confidence="high")


def issues_from(error: ValidationError) -> list[FieldIssue]:
    """Map a pydantic validation error to per-field issues."""
    return [
        FieldIssue(
            field=".".join(str(part) for part in item["loc"]),
            message=item["msg"],
        )
        for item in error.errors()
    ]


def _placeholder_input(payload: dict[str, Any], invalid_fields: set[str]) -> AssessmentInput:
    clean = {key: value for key, value in payload.items() if key not in invalid_fields}
    fills = {field: value for field, value in _REQUIRED_PLACEHOLDERS.items() if field not in clean}
    return AssessmentInput.model_validate({**clean, **fills})


def _hint(
    inp: AssessmentInput,
    typology: Typology,
    block: str,
    current_level: str,
    config: MethodologyConfig,
) -> ConfidenceHint | None:
    groups: list[list[str]] = config.derived_scores["confidence"]["blocks"][block]
    unsupplied = [
        group
        for group in groups
        if not any(confidence_module._supplied(inp, field) for field in group)
    ]
    if not unsupplied:
        return None
    for group in unsupplied:
        # Probe the engine with the group hypothetically answered. Only
        # presence matters to completeness, so the sentinel stands in for a
        # real value; the probe input never leaves this function.
        probe = inp.model_copy(update={group[0]: _SUPPLIED_SENTINEL})
        level = getattr(confidence_module.compute(probe, typology, config), block)
        if _RANK[level] > _RANK[current_level]:
            return ConfidenceHint(fields=list(group), raises_level_to=level)
    return ConfidenceHint(fields=list(unsupplied[0]), raises_level_to=None)


def _preview(
    inp: AssessmentInput, typology: Typology, config: MethodologyConfig
) -> ConfidencePreview:
    computed = confidence_module.compute(inp, typology, config)
    blocks = {
        block: BlockConfidencePreview(
            level=getattr(computed, block),
            completeness_percent=computed.completeness_percent[block],
            hint=_hint(inp, typology, block, getattr(computed, block), config),
        )
        for block in _BLOCKS
    }
    return ConfidencePreview(
        **blocks,
        overall=computed.overall,
        cooling_capped_by_evidence=computed.cooling_capped_by_evidence,
    )


def validate_payload(payload: dict[str, Any], config: MethodologyConfig) -> ValidateResponse:
    """Validate a partial questionnaire state. Deterministic; never raises."""
    errors: list[FieldIssue] = []
    invalid_fields: set[str] = set()
    try:
        inp: AssessmentInput | None = AssessmentInput.model_validate(payload)
    except ValidationError as exc:
        inp = None
        errors = issues_from(exc)
        invalid_fields = {str(item["loc"][0]) for item in exc.errors()}

    # The evidence-confidence cap follows the component that would carry the
    # package's cooling estimate, which is the same component the engine would
    # choose (best evidence, then widest envelope). Until every selected entry
    # resolves, no cap can be asserted and the preview is computed uncapped
    # (D-029) — a promise about confidence must not rest on a typology the
    # library cannot find.
    typology: Typology | None = None
    supplied_types = payload.get("nbs_type")
    if isinstance(supplied_types, list) and "nbs_type" not in invalid_fields:
        # Every element is a string here: a non-string would have failed
        # pydantic validation above, putting ``nbs_type`` in ``invalid_fields``
        # and skipping this block entirely.
        resolved: list[Typology] = []
        for index, name in enumerate(supplied_types):
            try:
                resolved.append(config.typologies.by_type(name))
            except ConfigError as exc:
                errors.append(FieldIssue(field=f"nbs_type.{index}", message=str(exc)))
        if resolved:
            typology = max(
                resolved,
                key=lambda item: (
                    _RANK[item.evidence_confidence],
                    item.temp_reduction_max_c,
                ),
            )

    if inp is None:
        inp = _placeholder_input(payload, invalid_fields)

    return ValidateResponse(
        valid=not errors,
        errors=errors,
        warnings=runner_module._warnings(inp),
        confidence=_preview(inp, typology or _no_cap_typology(), config),
    )
