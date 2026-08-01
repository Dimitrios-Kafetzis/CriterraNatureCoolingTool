"""Shaping of one stored assessment into the rows both report formats render.

Pure functions from the stored data (project name, label, created_at, input,
result) to display rows. **No number originates here**: every figure, level,
band, flag, recommendation, and assumption is read from the stored result or
the stored input and formatted for display — the engine is never called, and
nothing is recomputed (OQ-15). Status enums and input levels render through
the module-level catalog, mirroring the web application.

The stored ``input`` and ``result`` arrive as the plain JSON objects the
storage layer holds. They are deliberately not re-validated against the
current engine schemas (D-029): results are validated exactly once, when the
engine produces them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from nature_cooling.report.catalog import (
    BRACKET_LABELS,
    FIELD_LABELS,
    FIELD_UNITS,
    INPUT_FIELD_ORDER,
    OPTION_LABELS,
    PATH_LABELS,
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


def _input_rows(inp: dict[str, Any]) -> tuple[InputRow, ...]:
    """The stored draft input, field by field, in questionnaire order.

    The marker states only what the stored input shows: a field that was not
    supplied (absent, ``None``, or an explicit ``unknown``) falls back to the
    methodology's documented rules; the defaults the engine *actually* applied
    are itemised verbatim on the Assumptions & Warnings sheet.
    """
    rows = []
    extras = sorted(set(inp) - set(INPUT_FIELD_ORDER))
    for field in [*INPUT_FIELD_ORDER, *extras]:
        value = inp.get(field)
        display_label = FIELD_LABELS.get(field, field)
        if value is None:
            rows.append(
                InputRow(
                    field, display_label, STRINGS["not_answered"], STRINGS["not_supplied_marker"]
                )
            )
        elif value == "unknown":
            rows.append(
                InputRow(
                    field, display_label, _option("unknown"), STRINGS["answered_unknown_marker"]
                )
            )
        else:
            rows.append(InputRow(field, display_label, _input_value(field, value), ""))
    return tuple(rows)


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
        inputs=_input_rows(inp),
    )
