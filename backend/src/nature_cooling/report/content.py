"""Shaping of stored assessments into the rows both report formats render.

Pure functions from the stored data (project name, label, created_at, input,
result) to display rows — for the single-assessment report and, since v2.4,
for the 2–4-scenario comparison. **No number originates here**: every figure,
level, band, flag, recommendation, and assumption is read from the stored
result or the stored input and formatted for display — the engine is never
called, and nothing is recomputed (OQ-15). Status enums and input levels
render through the module-level catalog, mirroring the web application.

The stored ``input`` and ``result`` arrive as the plain JSON objects the
storage layer holds. They are deliberately not re-validated against the
current engine schemas (D-029): results are validated exactly once, when the
engine produces them.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from nature_cooling.report.catalog import (
    BRACKET_LABELS,
    FIELD_LABELS,
    FIELD_UNITS,
    INPUT_FIELD_ORDER,
    OPTION_LABELS,
    PATH_LABELS,
    SOURCE_LABELS,
    STATUS_TEXTS,
    STRINGS,
)


@dataclass(frozen=True)
class Row:
    """One label/value display row."""

    label: str
    value: str


@dataclass(frozen=True)
class Block:
    """One output block: title, its confidence badge, and its rows.

    ``note`` carries a block-level sentence rendered below the rows (a status
    explanation for a block that could not be calculated, or a standing
    methodology note such as the equity-aggregation disclosure).
    """

    title: str
    confidence: str | None
    rows: tuple[Row, ...]
    sub_heading: str | None = None
    sub_rows: tuple[Row, ...] = ()
    note: str | None = None


@dataclass(frozen=True)
class ScoreCard:
    """One page-1 score card, mirroring the results dashboard."""

    title: str
    score: str
    scale_note: str
    category: str
    confidence: str
    extra_rows: tuple[Row, ...]


@dataclass(frozen=True)
class InputRow:
    """One row of the workbook's Inputs sheet."""

    field: str
    label: str
    value: str
    marker: str


@dataclass(frozen=True)
class PackageRow:
    """One package component as both formats render it (D-038).

    Every field is displayed: an earlier shape overloaded one slot to carry
    either the representative marker or the suitability score, which meant the
    representative component's suitability was never shown anywhere.
    """

    name: str
    archetype: str
    evidence: str
    cooling_range: str
    suitability: str
    is_representative: bool


@dataclass(frozen=True)
class ReportContent:
    """Everything the PDF and the workbook render, in results-page order."""

    project_name: str
    label: str
    typology: str
    created_date: str
    version_line: str
    cards: tuple[ScoreCard, ScoreCard]
    flags: tuple[str, ...]
    recommendation: str
    confidence_rows: tuple[Row, ...]
    blocks: tuple[Block, ...]
    components: tuple[tuple[str, str, str, str], ...]
    components_excluded: str | None
    package_rows: tuple[PackageRow, ...]
    package_note: str
    assumptions: tuple[str, ...]
    warnings: tuple[str, ...]
    method_note: str
    inputs: tuple[InputRow, ...]


def fmt(value: float) -> str:
    """Format a stored number the way the web app does: thousands-separated,
    at most two decimals, no trailing zeros."""
    text = f"{value:,.2f}"
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def _option(value: str) -> str:
    return OPTION_LABELS.get(value, value)


def _status(code: str) -> str:
    return STATUS_TEXTS.get(code, code)


def _range(minimum: float, maximum: float, unit: str) -> str:
    return f"{fmt(minimum)}–{fmt(maximum)} {unit}".rstrip()


def _confidence_row(label: str, level: str, percent: float | None) -> Row:
    if percent is None:
        return Row(label, _option(level))
    value = STRINGS["confidence_value"].format(level=_option(level), percent=fmt(percent))
    return Row(label, value)


def _score_cards(result: dict[str, Any]) -> tuple[ScoreCard, ScoreCard]:
    overall = _option(result["confidence"]["overall"])
    heat = result["heat_priority"]
    exposure = result["heat_exposure"]
    heat_card = ScoreCard(
        title=STRINGS["heat_priority"],
        score=fmt(heat["score"]),
        scale_note=STRINGS["heat_priority_scale"],
        category=_option(heat["category"]),
        confidence=overall,
        extra_rows=(
            Row(
                f"{STRINGS['sub_heat_exposure']} ({PATH_LABELS[exposure['path']]})",
                fmt(exposure["score"]),
            ),
            Row(STRINGS["sub_vulnerability"], fmt(result["vulnerability"]["score"])),
        ),
    )
    opportunity = result["opportunity"]
    opportunity_card = ScoreCard(
        title=STRINGS["opportunity"],
        score=fmt(opportunity["score"]),
        scale_note=STRINGS["opportunity_scale"],
        category=_option(opportunity["category"]),
        confidence=overall,
        extra_rows=(),
    )
    return heat_card, opportunity_card


def _flags(result: dict[str, Any]) -> tuple[str, ...]:
    """Suitability flags first (D-009), then the evidence-cap caveat, then a
    low overall confidence caveat — exactly the results dashboard's order."""
    confidence = result["confidence"]
    flags = [str(flag["message"]) for flag in result["suitability"]["flags"]]
    if confidence["cooling_capped_by_evidence"]:
        flags.append(STRINGS["evidence_cap"])
    if confidence["overall"] == "low":
        flags.append(STRINGS["low_overall_confidence"])
    return tuple(flags)


def _confidence_rows(result: dict[str, Any]) -> tuple[Row, ...]:
    confidence = result["confidence"]
    completeness = confidence["completeness_percent"]
    return (
        _confidence_row(
            STRINGS["block_cooling"], confidence["cooling"], completeness.get("cooling")
        ),
        _confidence_row(STRINGS["block_energy"], confidence["energy"], completeness.get("energy")),
        _confidence_row(
            STRINGS["block_costs"], confidence["economic"], completeness.get("economic")
        ),
        _confidence_row(STRINGS["block_equity"], confidence["equity"], completeness.get("equity")),
        _confidence_row(STRINGS["confidence_overall"], confidence["overall"], None),
    )


def _cooling_block(result: dict[str, Any]) -> Block:
    cooling = result["cooling"]
    adjustment = result["adjustment"]
    suitability = result["suitability"]
    if cooling["shade_potential_status"] == "calculated":
        shade = f"{fmt(cooling['shade_potential_percent'])} %"
    else:
        shade = STATUS_TEXTS["not_estimated_input"]
    if cooling["time_to_benefit_status"] == "derived":
        time_to_benefit = _option(cooling["time_to_benefit"])
    else:
        time_to_benefit = STATUS_TEXTS["not_estimated_input"]
    rows = (
        Row(STRINGS["cooling_potential"], f"{fmt(cooling['potential_score'])} / 100"),
        Row(
            STRINGS["cooling_delta_t"],
            _range(cooling["delta_t_min_c"], cooling["delta_t_max_c"], "°C"),
        ),
        Row(
            STRINGS["cooling_heat_index_improvement"],
            _option(cooling["heat_index_improvement"]),
        ),
        Row(STRINGS["cooling_shade_potential"], shade),
        Row(STRINGS["cooling_time_to_benefit"], time_to_benefit),
        Row(STRINGS["cooling_adjustment"], fmt(adjustment["factor"])),
    )
    sub_rows = [
        Row(
            STRINGS[f"adjustment_{condition}"],
            f"{_option(adjustment[condition]['level'])} (× {fmt(adjustment[condition]['factor'])})"
            + (f" — {adjustment[condition]['detail']}" if adjustment[condition]["detail"] else ""),
        )
        for condition in ("canopy", "soil_water", "scale", "climate")
    ]
    sub_rows.append(Row(STRINGS["sub_suitability"], f"{fmt(suitability['score'])} / 100"))
    sub_rows.extend(
        Row(STRINGS[f"sub_{indicator}"], fmt(suitability[indicator]))
        for indicator in ("space", "soil", "water", "maintenance", "urban_context")
    )
    return Block(
        title=STRINGS["block_cooling"],
        confidence=_option(result["confidence"]["cooling"]),
        rows=rows,
        sub_heading=STRINGS["sub_scores_heading"],
        sub_rows=tuple(sub_rows),
        note=STRINGS["cooling_delta_t_note"],
    )


def _energy_block(result: dict[str, Any]) -> Block:
    energy = result["energy"]
    confidence = _option(result["confidence"]["energy"])
    if energy["status"] != "calculated":
        # The engine states why in its own words; render them verbatim.
        return Block(
            title=STRINGS["block_energy"],
            confidence=confidence,
            rows=(),
            note=energy["status_message"],
        )
    savings = _range(
        energy["savings_min_kwh_per_year"],
        energy["savings_max_kwh_per_year"],
        STRINGS["energy_unit"],
    )
    return Block(
        title=STRINGS["block_energy"],
        confidence=confidence,
        rows=(Row(STRINGS["energy_savings"], savings),),
    )


def _ghg_block(result: dict[str, Any]) -> Block:
    ghg = result["ghg"]
    confidence = _option(result["confidence"]["energy"])
    if ghg["status"] != "calculated":
        return Block(
            title=STRINGS["block_ghg"],
            confidence=confidence,
            rows=(),
            note=_status(ghg["status"]),
        )
    origin = ghg["emission_factor_origin"]
    factor = fmt(ghg["emission_factor_kgco2e_per_kwh"])
    if origin:
        factor = f"{factor} ({STRINGS[f'origin_{origin}']})"
    return Block(
        title=STRINGS["block_ghg"],
        confidence=confidence,
        rows=(
            Row(
                STRINGS["ghg_avoided"],
                _range(
                    ghg["avoided_min_kgco2e_per_year"],
                    ghg["avoided_max_kgco2e_per_year"],
                    STRINGS["ghg_unit"],
                ),
            ),
            Row(STRINGS["ghg_factor"], factor),
        ),
    )


def _costs_block(result: dict[str, Any]) -> Block:
    costs = result["costs"]
    if costs["annual_savings_status"] == "calculated":
        currency = costs["currency"] or ""
        savings = _range(
            costs["annual_savings_min"], costs["annual_savings_max"], f"{currency}/year"
        )
    else:
        savings = _status(costs["annual_savings_status"])
    if costs["payback_status"] == "calculated":
        payback = (
            f"{_range(costs['payback_years_min'], costs['payback_years_max'], '')}"
            f" {STRINGS['costs_payback_unit']}"
            f" ({STRINGS['costs_payback_central']}: {fmt(costs['payback_years_central'])})"
        )
    else:
        payback = _status(costs["payback_status"])
    if costs["cost_feasibility_status"] == "derived":
        feasibility = f"{fmt(costs['cost_feasibility_score'])} / 100"
        if costs["payback_bracket"]:
            feasibility += f" — {BRACKET_LABELS[costs['payback_bracket']]}"
    else:
        feasibility = _status("not_estimated")
    if costs["investment_readiness_status"] == "derived":
        readiness = _option(costs["investment_readiness"])
    else:
        readiness = _status("not_estimated")
    return Block(
        title=STRINGS["block_costs"],
        confidence=_option(result["confidence"]["economic"]),
        rows=(
            Row(STRINGS["costs_annual_savings"], savings),
            Row(STRINGS["costs_payback"], payback),
            Row(STRINGS["costs_feasibility"], feasibility),
            Row(STRINGS["costs_readiness"], readiness),
        ),
    )


def _co_benefits_block(result: dict[str, Any]) -> Block:
    co_benefits = result["co_benefits"]
    rows = [Row(STRINGS["score"], f"{fmt(co_benefits['score'])} / 100")]
    rows.extend(
        Row(STRINGS[f"sub_{indicator}"], fmt(co_benefits[indicator]))
        for indicator in (
            "biodiversity",
            "stormwater",
            "public_health",
            "social_inclusion",
            "urban_quality",
        )
    )
    # The result schema deliberately has no co-benefit confidence; none is shown.
    return Block(title=STRINGS["block_co_benefits"], confidence=None, rows=tuple(rows))


def _equity_block(result: dict[str, Any]) -> Block:
    equity = result["equity"]
    rows = [Row(STRINGS["score"], f"{fmt(equity['score'])} / 100")]
    rows.extend(
        Row(STRINGS[f"sub_{indicator}"], fmt(equity[indicator]))
        for indicator in (
            "vulnerable_user_benefit",
            "public_accessibility",
            "safety_comfort",
            "participation_relevance",
        )
    )
    return Block(
        title=STRINGS["block_equity"],
        confidence=_option(result["confidence"]["equity"]),
        rows=tuple(rows),
        note=STRINGS["equity_note"],
    )


def _components(
    result: dict[str, Any],
) -> tuple[tuple[tuple[str, str, str, str], ...], str | None]:
    opportunity = result["opportunity"]
    components = tuple(
        (
            str(component["name"]),
            fmt(component["score"]),
            fmt(component["nominal_weight"]),
            fmt(component["applied_weight"]),
        )
        for component in opportunity["components"]
    )
    excluded = opportunity["excluded_components"]
    excluded_line = (
        STRINGS["components_excluded"].format(names=", ".join(excluded)) if excluded else None
    )
    return components, excluded_line


def _input_value(field: str, value: Any) -> str:
    if isinstance(value, int | float):
        unit = FIELD_UNITS.get(field)
        return f"{fmt(value)} {unit}" if unit else fmt(value)
    if isinstance(value, list):
        # A package's components, and the governance multi-select. An empty
        # list is a real answer meaning "none selected", distinct from absence,
        # so it renders as such rather than falling through to the blank row.
        return (
            ", ".join(_option(str(item)) for item in value) if value else STRINGS["none_selected"]
        )
    return _option(str(value))


def _input_cell(field: str, inp: dict[str, Any], marks: dict[str, str]) -> tuple[str, str]:
    """One stored answer as (display value, provenance marker).

    The marker distinguishes the three ways a value can have got here (D-047.2,
    scope item 4). A field that was not supplied — absent, ``None``, or an
    explicit ``unknown`` — falls back to the methodology's documented rules; the
    defaults the engine *actually* applied are itemised verbatim on the
    Assumptions & Warnings sheet. A field the map filled in is named as such,
    with the dataset it came from, because a value the tool derived should not
    be indistinguishable from one the reader's colleague typed. Everything else
    is the user's own answer and carries no marker, which is the common case
    and reads as one.
    """
    value = inp.get(field)
    if value is None:
        return STRINGS["not_answered"], STRINGS["not_supplied_marker"]
    if value == "unknown":
        return _option("unknown"), STRINGS["answered_unknown_marker"]
    if field in marks:
        marker = STRINGS["autofilled_marker"].format(
            source=SOURCE_LABELS.get(marks[field], marks[field])
        )
        return _input_value(field, value), marker
    return _input_value(field, value), ""


def _input_rows(
    inp: dict[str, Any], autofilled: dict[str, str] | None = None
) -> tuple[InputRow, ...]:
    """The stored draft input, field by field, in questionnaire order."""
    marks = autofilled or {}
    extras = sorted(set(inp) - set(INPUT_FIELD_ORDER))
    return tuple(
        InputRow(field, FIELD_LABELS.get(field, field), *_input_cell(field, inp, marks))
        for field in [*INPUT_FIELD_ORDER, *extras]
    )


def _package_rows(result: dict[str, Any]) -> tuple[PackageRow, ...]:
    """One row per package component, each scored on its own values (D-038).

    Reads the stored result's itemisation verbatim. Nothing is recomputed and
    nothing is averaged here: the component figures are the engine's own, and
    the representative marker is how the report shows which component the
    headline temperature belongs to.
    """
    return tuple(
        PackageRow(
            name=str(component["typology"]["display_name"]),
            archetype=str(component["typology"]["archetype_display_name"]),
            evidence=_option(str(component["typology"]["evidence_confidence"])),
            cooling_range=(
                f"{fmt(component['cooling']['delta_t_min_c'])}–"
                f"{fmt(component['cooling']['delta_t_max_c'])} °C"
            ),
            suitability=fmt(component["suitability"]["score"]),
            is_representative=bool(component["is_representative"]),
        )
        for component in result.get("components", [])
    )


# The page-one identity line is a title, not an itemisation: the itemisation
# is the package table on page two and the Results sheet in the workbook. A
# package can name dozens of components, so the line names a few and counts the
# rest rather than growing without bound and pushing page one over.
_HEADING_COMPONENTS = 3


def _package_heading(result: dict[str, Any]) -> str:
    """The identity line: one intervention, or a package naming its components."""
    components = result.get("components", [])
    if len(components) <= 1:
        return str(result["typology"]["display_name"])
    names = [str(item["typology"]["display_name"]) for item in components]
    if len(names) <= _HEADING_COMPONENTS:
        return f"{', '.join(names[:-1])} and {names[-1]}"
    shown = names[:_HEADING_COMPONENTS]
    return STRINGS["package_heading_more"].format(
        components=", ".join(shown), count=len(names) - len(shown)
    )


def build_content(
    *,
    project_name: str,
    label: str,
    created_at: str,
    inp: dict[str, Any],
    result: dict[str, Any],
    autofilled: dict[str, str] | None = None,
) -> ReportContent:
    """Shape one stored, evaluated assessment for rendering."""
    components, excluded_line = _components(result)
    package_components = result.get("components", [])
    return ReportContent(
        project_name=project_name,
        label=label,
        typology=_package_heading(result),
        created_date=created_at[:10],
        version_line=STRINGS["versions"].format(
            methodology=result["methodology_version"], engine=result["engine_version"]
        ),
        cards=_score_cards(result),
        flags=_flags(result),
        recommendation=str(result["recommendation"]),
        confidence_rows=_confidence_rows(result),
        blocks=(
            _cooling_block(result),
            _energy_block(result),
            _ghg_block(result),
            _costs_block(result),
            _co_benefits_block(result),
            _equity_block(result),
        ),
        components=components,
        components_excluded=excluded_line,
        package_rows=_package_rows(result),
        package_note=(
            STRINGS["package_rule"] if len(package_components) > 1 else STRINGS["package_single"]
        ),
        assumptions=tuple(str(item) for item in result["assumptions_applied"]),
        warnings=tuple(str(item) for item in result["warnings"]),
        method_note=str(result["method_note"]),
        inputs=_input_rows(inp, autofilled),
    )


# --- Scenario comparison (v2.4) ----------------------------------------------


@dataclass(frozen=True)
class ScenarioSource:
    """One stored, evaluated assessment, exactly as the comparison receives it."""

    label: str
    created_at: str
    inp: dict[str, Any]
    result: dict[str, Any]
    autofilled: dict[str, str] | None = None


@dataclass(frozen=True)
class ComparisonScenario:
    """One scenario's overview entry, plus its per-scenario itemisations."""

    label: str
    typology: str
    scale: str
    created_date: str
    version_line: str
    flags: tuple[str, ...]
    assumptions: tuple[str, ...]
    warnings: tuple[str, ...]
    # Set only when the stored method notes differ between scenarios;
    # otherwise the shared note renders once (``shared_method_note``).
    method_note: str | None


@dataclass(frozen=True)
class ComparisonRow:
    """One criterion across the compared scenarios.

    ``best`` marks the scenario(s) holding the best value on this criterion —
    the decided verdict style: per-criterion, never an overall winner. It is
    all ``False`` when the criterion has no better direction, when any
    scenario reports a status instead of a figure, when every value ties, or
    when the scenarios are not like for like. ``differs`` carries the web
    comparison's difference emphasis: identical rows render muted.
    """

    label: str
    values: tuple[str, ...]
    best: tuple[bool, ...]
    differs: bool


@dataclass(frozen=True)
class ComparisonContent:
    """Everything both comparison formats render, in report order.

    ``created_at`` is the newest compared scenario's stored timestamp: the
    comparison exists once its last scenario does, and deriving the document
    clocks from stored data is what keeps both formats byte-deterministic
    (D-033).
    """

    project_name: str
    created_at: str
    created_date: str
    scenarios: tuple[ComparisonScenario, ...]
    like_for_like: bool
    cross_scale_note: str | None
    methodology_note: str | None
    narrative: str
    rows: tuple[ComparisonRow, ...]
    site_rows: tuple[InputRow, ...]
    site_differences: tuple[ComparisonRow, ...]
    shared_method_note: str | None


# Overall confidence is an ordered level, not a number; the order is the
# engine's ``ConfidenceLevel`` order.
_CONFIDENCE_RANK: dict[str, float] = {"low": 0.0, "medium": 1.0, "high": 2.0}


def _best_indices(keys: Sequence[tuple[float, ...] | None], *, lowest: bool) -> tuple[int, ...]:
    """The scenario indices holding the best key, or none when marking would lie.

    A ``None`` key means that scenario reports a status instead of a figure —
    "not estimated" cannot lose to a number, so the whole criterion goes
    unmarked. A criterion where every scenario ties is unmarked too: there is
    no best among equals.
    """
    known = [key for key in keys if key is not None]
    if len(known) < len(keys) or len(set(known)) == 1:
        return ()
    best = min(known) if lowest else max(known)
    return tuple(index for index, key in enumerate(keys) if key == best)


def _sentence(
    labels: Sequence[str],
    best: tuple[int, ...],
    criterion: str,
    value: str,
    *,
    lowest: bool,
) -> str:
    """One narrative sentence stating a fact the table marks — never a verdict."""
    key = "comparison_superlative_lowest" if lowest else "comparison_superlative_highest"
    superlative = STRINGS[key]
    winners = [labels[index] for index in best]
    if len(winners) == 1:
        return STRINGS["comparison_best_single"].format(
            scenario=winners[0], superlative=superlative, criterion=criterion, value=value
        )
    joined = f"{', '.join(winners[:-1])} and {winners[-1]}"
    return STRINGS["comparison_best_tied"].format(
        scenarios=joined, superlative=superlative, criterion=criterion, value=value
    )


def _delta_t_cell(result: dict[str, Any]) -> tuple[str, tuple[float, ...]]:
    cooling = result["cooling"]
    return (
        _range(cooling["delta_t_min_c"], cooling["delta_t_max_c"], "°C"),
        (float(cooling["delta_t_max_c"]), float(cooling["delta_t_min_c"])),
    )


def _energy_cell(result: dict[str, Any]) -> tuple[str, tuple[float, ...] | None]:
    energy = result["energy"]
    if energy["status"] != "calculated":
        # The engine states why in its own words; render them verbatim.
        return str(energy["status_message"]), None
    return (
        _range(
            energy["savings_min_kwh_per_year"],
            energy["savings_max_kwh_per_year"],
            STRINGS["energy_unit"],
        ),
        (float(energy["savings_max_kwh_per_year"]), float(energy["savings_min_kwh_per_year"])),
    )


def _savings_cell(result: dict[str, Any]) -> tuple[str, tuple[float, ...] | None]:
    costs = result["costs"]
    if costs["annual_savings_status"] != "calculated":
        return _status(costs["annual_savings_status"]), None
    currency = costs["currency"] or ""
    return (
        _range(costs["annual_savings_min"], costs["annual_savings_max"], f"{currency}/year"),
        (float(costs["annual_savings_max"]), float(costs["annual_savings_min"])),
    )


def _payback_cell(result: dict[str, Any]) -> tuple[str, tuple[float, ...] | None, str]:
    """(cell, key, narrative value): the narrative names the central figure only."""
    costs = result["costs"]
    if costs["payback_status"] != "calculated":
        status = _status(costs["payback_status"])
        return status, None, status
    cell = (
        f"{_range(costs['payback_years_min'], costs['payback_years_max'], '')}"
        f" {STRINGS['costs_payback_unit']}"
        f" ({STRINGS['costs_payback_central']}: {fmt(costs['payback_years_central'])})"
    )
    central = f"{fmt(costs['payback_years_central'])} {STRINGS['costs_payback_unit']}"
    return cell, (float(costs["payback_years_central"]),), central


def _confidence_key(result: dict[str, Any]) -> tuple[float, ...] | None:
    rank = _CONFIDENCE_RANK.get(str(result["confidence"]["overall"]))
    return None if rank is None else (rank,)


def _site_context(
    scenarios: Sequence[ScenarioSource],
) -> tuple[tuple[InputRow, ...], tuple[ComparisonRow, ...]]:
    """The site description: printed once where shared, disclosed where not.

    The field set is exactly what the duplicate operation carries forward
    (D-021): the comparison prints once precisely what a comparison draft
    inherits. ``assessment_scale`` is excluded here because it is disclosed
    per scenario in the overview — it is the like-for-like axis, not context.
    Evaluated inputs cannot hold unknown fields (they were validated when the
    engine ran), so questionnaire order covers everything.
    """
    from nature_cooling.api.schemas import SITE_DESCRIPTION_FIELDS

    shared: list[InputRow] = []
    differing: list[ComparisonRow] = []
    for field in INPUT_FIELD_ORDER:
        if field not in SITE_DESCRIPTION_FIELDS or field == "assessment_scale":
            continue
        cells = [_input_cell(field, s.inp, s.autofilled or {}) for s in scenarios]
        values = [value for value, _ in cells]
        markers = [marker for _, marker in cells]
        if len(set(values)) == 1:
            # The value is shared; its provenance usually is too (duplication
            # carries the autofill marks with the site, D-047.2). Where it is
            # not, saying so beats printing one scenario's marker as if it
            # described them all.
            marker = markers[0] if len(set(markers)) == 1 else STRINGS["provenance_differs"]
            shared.append(InputRow(field, FIELD_LABELS[field], values[0], marker))
        else:
            shown = tuple(
                value if marker == "" else f"{value} — {marker}" for value, marker in cells
            )
            differing.append(ComparisonRow(FIELD_LABELS[field], shown, (False,) * len(cells), True))
    return tuple(shared), tuple(differing)


def build_comparison_content(
    *, project_name: str, scenarios: Sequence[ScenarioSource]
) -> ComparisonContent:
    """Shape 2–4 stored, evaluated assessments for side-by-side rendering.

    Every figure is read from each stored result verbatim; nothing is
    recomputed or normalised for comparability (out of scope by design).
    Where the scenarios are not comparable — different assessment scales —
    the fact is stated prominently and best-marking plus the comparative
    narrative are withheld, rather than the rows being silently tabulated.
    """
    if not 2 <= len(scenarios) <= 4:
        raise ValueError("a comparison renders 2 to 4 scenarios")
    labels = [scenario.label for scenario in scenarios]
    results = [scenario.result for scenario in scenarios]

    scales = [str(scenario.inp.get("assessment_scale", "")) for scenario in scenarios]
    like_for_like = len(set(scales)) == 1
    cross_scale_note = None
    if not like_for_like:
        pairs = " · ".join(
            f"{label}: {_option(scale)}" for label, scale in zip(labels, scales, strict=True)
        )
        cross_scale_note = STRINGS["comparison_cross_scale"].format(scales=pairs)

    methodology_versions = [str(result["methodology_version"]) for result in results]
    methodology_note = None
    if len(set(methodology_versions)) > 1:
        pairs = " · ".join(
            f"{label}: {version}"
            for label, version in zip(labels, methodology_versions, strict=True)
        )
        methodology_note = STRINGS["comparison_methodology_differs"].format(versions=pairs)

    method_notes = [str(result["method_note"]) for result in results]
    shared_method_note = method_notes[0] if len(set(method_notes)) == 1 else None

    overview = tuple(
        ComparisonScenario(
            label=scenario.label,
            typology=_package_heading(scenario.result),
            scale=_option(scale),
            created_date=scenario.created_at[:10],
            version_line=STRINGS["versions"].format(
                methodology=scenario.result["methodology_version"],
                engine=scenario.result["engine_version"],
            ),
            flags=_flags(scenario.result),
            assumptions=tuple(str(item) for item in scenario.result["assumptions_applied"]),
            warnings=tuple(str(item) for item in scenario.result["warnings"]),
            method_note=None if shared_method_note else str(scenario.result["method_note"]),
        )
        for scenario, scale in zip(scenarios, scales, strict=True)
    )

    rows: list[ComparisonRow] = []
    sentences: list[str] = []

    def add(
        label: str,
        values: Sequence[str],
        *,
        keys: Sequence[tuple[float, ...] | None] | None = None,
        lowest: bool = False,
        narrative: Sequence[str] | None = None,
    ) -> None:
        best = _best_indices(keys, lowest=lowest) if keys is not None and like_for_like else ()
        marks = tuple(index in best for index in range(len(values)))
        rows.append(ComparisonRow(label, tuple(values), marks, len(set(values)) > 1))
        if best:
            value = (narrative if narrative is not None else values)[best[0]]
            sentences.append(_sentence(labels, best, label, value, lowest=lowest))

    add(
        STRINGS["opportunity"],
        [
            f"{fmt(r['opportunity']['score'])} ({_option(r['opportunity']['category'])})"
            for r in results
        ],
        keys=[(float(r["opportunity"]["score"]),) for r in results],
        narrative=[fmt(r["opportunity"]["score"]) for r in results],
    )
    # The Heat Priority Index describes the site's need, not the option's
    # merit, so it carries no better direction: a hotter site is not a better
    # scenario.
    add(
        STRINGS["heat_priority"],
        [
            f"{fmt(r['heat_priority']['score'])} ({_option(r['heat_priority']['category'])})"
            for r in results
        ],
    )
    add(
        STRINGS["comparison_cooling_potential"],
        [f"{fmt(r['cooling']['potential_score'])} / 100" for r in results],
        keys=[(float(r["cooling"]["potential_score"]),) for r in results],
        narrative=[fmt(r["cooling"]["potential_score"]) for r in results],
    )
    delta_t = [_delta_t_cell(r) for r in results]
    add(
        STRINGS["cooling_delta_t"],
        [cell for cell, _ in delta_t],
        keys=[key for _, key in delta_t],
    )
    energy = [_energy_cell(r) for r in results]
    add(
        STRINGS["energy_savings"],
        [cell for cell, _ in energy],
        keys=[key for _, key in energy],
    )
    savings = [_savings_cell(r) for r in results]
    add(
        STRINGS["costs_annual_savings"],
        [cell for cell, _ in savings],
        keys=[key for _, key in savings],
    )
    payback = [_payback_cell(r) for r in results]
    add(
        STRINGS["costs_payback"],
        [cell for cell, _, _ in payback],
        keys=[key for _, key, _ in payback],
        lowest=True,
        narrative=[central for _, _, central in payback],
    )
    add(
        STRINGS["comparison_co_benefits"],
        [f"{fmt(r['co_benefits']['score'])} / 100" for r in results],
        keys=[(float(r["co_benefits"]["score"]),) for r in results],
        narrative=[fmt(r["co_benefits"]["score"]) for r in results],
    )
    add(
        STRINGS["comparison_suitability"],
        [f"{fmt(r['suitability']['score'])} / 100" for r in results],
        keys=[(float(r["suitability"]["score"]),) for r in results],
        narrative=[fmt(r["suitability"]["score"]) for r in results],
    )
    add(
        STRINGS["comparison_confidence"],
        [_option(str(r["confidence"]["overall"])) for r in results],
        keys=[_confidence_key(r) for r in results],
    )

    if not like_for_like:
        narrative = ""
    elif sentences:
        narrative = " ".join(sentences)
    else:
        narrative = STRINGS["comparison_narrative_empty"]

    site_rows, site_differences = _site_context(scenarios)
    return ComparisonContent(
        project_name=project_name,
        created_at=max(scenario.created_at for scenario in scenarios),
        created_date=max(scenario.created_at for scenario in scenarios)[:10],
        scenarios=overview,
        like_for_like=like_for_like,
        cross_scale_note=cross_scale_note,
        methodology_note=methodology_note,
        narrative=narrative,
        rows=tuple(rows),
        site_rows=site_rows,
        site_differences=site_differences,
        shared_method_note=shared_method_note,
    )
