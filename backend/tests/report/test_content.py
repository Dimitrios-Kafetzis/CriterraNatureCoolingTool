"""The shared content shaping: stored data in, display rows out, verbatim."""

from __future__ import annotations

from typing import Any

from nature_cooling.report.catalog import (
    BRACKET_LABELS,
    FIELD_LABELS,
    INPUT_FIELD_ORDER,
    OPTION_LABELS,
    STATUS_TEXTS,
    STRINGS,
)
from nature_cooling.report.content import build_content, fmt


def test_fmt_matches_the_web_apps_number_formatting() -> None:
    assert fmt(72.33) == "72.33"
    assert fmt(90.0) == "90"
    assert fmt(0.95) == "0.95"
    assert fmt(13680.0) == "13,680"
    assert fmt(1675.5) == "1,675.5"


def test_every_figure_renders_verbatim_from_the_stored_result(render_args: Any) -> None:
    args = render_args("s01_temperate_street_trees_worked_example")
    result = args["result"]
    content = build_content(**args)

    heat_card, opportunity_card = content.cards
    assert heat_card.score == fmt(result["heat_priority"]["score"])
    assert heat_card.category == OPTION_LABELS[result["heat_priority"]["category"]]
    assert opportunity_card.score == fmt(result["opportunity"]["score"])
    assert content.recommendation == result["recommendation"]
    assert content.method_note == result["method_note"]
    assert content.assumptions == tuple(result["assumptions_applied"])
    assert content.typology == result["typology"]["display_name"]
    assert result["methodology_version"] in content.version_line
    assert result["engine_version"] in content.version_line
    assert content.created_date == "2026-07-30"


def test_flags_keep_the_dashboard_order_suitability_then_caveats(render_args: Any) -> None:
    args = render_args("s04_unsuitable_riparian_small_dry_site")
    stored_flags = [flag["message"] for flag in args["result"]["suitability"]["flags"]]
    content = build_content(**args)
    # Suitability flags first (D-009), then the low-overall-confidence caveat.
    assert list(content.flags[: len(stored_flags)]) == stored_flags
    assert content.flags[-1] == STRINGS["low_overall_confidence"]


def test_evidence_cap_renders_as_a_flag(render_args: Any) -> None:
    content = build_content(**render_args("s07_green_facade_low_evidence_full_data"))
    assert STRINGS["evidence_cap"] in content.flags


def test_no_flags_for_a_suitable_high_confidence_result(render_args: Any) -> None:
    content = build_content(**render_args("s16_urban_forest_short_payback_high_readiness"))
    assert content.flags == ()


def test_blocks_carry_statuses_through_the_catalog(render_args: Any) -> None:
    args = render_args("s19_explicit_unknowns_everywhere")
    result = args["result"]
    content = build_content(**args)
    cooling, energy, ghg, costs, co_benefits, equity = content.blocks

    # The energy block explains itself in the engine's own words.
    assert energy.rows == ()
    assert energy.note == result["energy"]["status_message"]
    assert ghg.note == STATUS_TEXTS[result["ghg"]["status"]]
    # Cooling outputs that were not derived use the neutral input wording,
    # never the economic "requires cost data" sentence.
    shade_row = next(row for row in cooling.rows if row.label == STRINGS["cooling_shade_potential"])
    assert shade_row.value == STATUS_TEXTS["not_estimated_input"]
    # Economic outputs that were not estimated say so (D-016).
    for row in costs.rows[1:]:
        assert "not estimated" in row.value.lower()
    assert co_benefits.confidence is None
    assert equity.note == STRINGS["equity_note"]


def test_calculated_blocks_render_ranges_never_point_estimates(render_args: Any) -> None:
    args = render_args("s16_urban_forest_short_payback_high_readiness")
    result = args["result"]
    content = build_content(**args)
    _, energy, _, costs, _, _ = content.blocks
    savings = energy.rows[0].value
    assert fmt(result["energy"]["savings_min_kwh_per_year"]) in savings
    assert fmt(result["energy"]["savings_max_kwh_per_year"]) in savings
    assert "–" in savings
    payback = costs.rows[1].value
    assert fmt(result["costs"]["payback_years_central"]) in payback
    feasibility = costs.rows[2].value
    assert BRACKET_LABELS[result["costs"]["payback_bracket"]] in feasibility


def test_ghg_emission_factor_names_its_origin(render_args: Any) -> None:
    args = render_args("s01_temperate_street_trees_worked_example")
    content = build_content(**args)
    ghg = content.blocks[2]
    origin = args["result"]["ghg"]["emission_factor_origin"]
    assert STRINGS[f"origin_{origin}"] in ghg.rows[1].value


def test_opportunity_components_and_exclusions_flatten_verbatim(render_args: Any) -> None:
    args = render_args("s19_explicit_unknowns_everywhere")
    result = args["result"]
    content = build_content(**args)
    assert [name for name, _, _, _ in content.components] == [
        component["name"] for component in result["opportunity"]["components"]
    ]
    assert content.components_excluded is not None
    for name in result["opportunity"]["excluded_components"]:
        assert name in content.components_excluded

    full = build_content(**render_args("s16_urban_forest_short_payback_high_readiness"))
    assert full.components_excluded is None


def test_input_rows_cover_every_field_in_questionnaire_order(render_args: Any) -> None:
    args = render_args("s05_minimal_input_pocket_park")
    content = build_content(**args)
    assert [row.field for row in content.inputs] == list(INPUT_FIELD_ORDER)
    by_field = {row.field: row for row in content.inputs}

    # A supplied number renders with its unit; a supplied enum through its label.
    assert by_field["site_area_m2"].value.endswith("m²")
    assert by_field["site_area_m2"].marker == ""
    assert by_field["climate_zone"].value == OPTION_LABELS[args["inp"]["climate_zone"]]

    # An unanswered field is marked as not supplied — the methodology fallback
    # is documented, and what the engine actually applied is itemised.
    missing = by_field["existing_tree_canopy_percent"]
    assert missing.value == STRINGS["not_answered"]
    assert missing.marker == STRINGS["not_supplied_marker"]
    assert missing.label == FIELD_LABELS["existing_tree_canopy_percent"]


def test_input_rows_mark_explicit_unknowns_and_nulls(render_args: Any) -> None:
    args = render_args("s19_explicit_unknowns_everywhere")
    args["inp"]["land_use"] = None  # a stored draft may hold explicit nulls
    content = build_content(**args)
    by_field = {row.field: row for row in content.inputs}
    assert by_field["soil_availability"].marker == STRINGS["answered_unknown_marker"]
    assert by_field["land_use"].value == STRINGS["not_answered"]
    assert by_field["land_use"].marker == STRINGS["not_supplied_marker"]


def test_input_rows_render_fields_this_catalog_does_not_know(render_args: Any) -> None:
    # A stored input written by a later engine version may carry fields this
    # build's catalog has no label for; they render under their raw name.
    args = render_args("s01_temperate_street_trees_worked_example")
    args["inp"]["field_added_in_a_later_version"] = "some value"
    content = build_content(**args)
    extra = content.inputs[-1]
    assert extra.field == "field_added_in_a_later_version"
    assert extra.label == "field_added_in_a_later_version"
    assert extra.value == "some value"


def test_confidence_rows_state_level_and_completeness(render_args: Any) -> None:
    args = render_args("s01_temperate_street_trees_worked_example")
    result = args["result"]
    content = build_content(**args)
    assert len(content.confidence_rows) == 5
    cooling_row = content.confidence_rows[0]
    assert OPTION_LABELS[result["confidence"]["cooling"]] in cooling_row.value
    assert fmt(result["confidence"]["completeness_percent"]["cooling"]) in cooling_row.value
    overall = content.confidence_rows[-1]
    assert overall.label == STRINGS["confidence_overall"]
    assert overall.value == OPTION_LABELS[result["confidence"]["overall"]]
