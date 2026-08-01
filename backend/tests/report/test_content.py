"""The shared content shaping: stored data in, display rows out, verbatim."""

from __future__ import annotations

from typing import Any

from nature_cooling.report.catalog import (
    BRACKET_LABELS,
    FIELD_LABELS,
    INPUT_FIELD_ORDER,
    OPTION_LABELS,
    SOURCE_LABELS,
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


def test_the_inputs_sheet_distinguishes_supplied_autofilled_and_defaulted(
    render_args: Any,
) -> None:
    """Scope item 4 of the v2.1 brief, and the whole of D-047.2's disclosure.

    A value the tool derived must not be indistinguishable from one the
    reader's colleague typed. Three states, three markers.
    """
    args = render_args("s05_minimal_input_pocket_park")
    content = build_content(
        **args,
        autofilled={"climate_zone": "beck2023", "site_area_m2": "drawn_polygon"},
    )
    by_field = {row.field: row for row in content.inputs}

    # Autofilled: named as such, and the dataset behind it is named too.
    climate = by_field["climate_zone"]
    assert "filled from the map" in climate.marker
    assert SOURCE_LABELS["beck2023"] in climate.marker
    assert "Beck" in climate.marker
    assert climate.value == OPTION_LABELS[args["inp"]["climate_zone"]], "the value is unchanged"
    assert SOURCE_LABELS["drawn_polygon"] in by_field["site_area_m2"].marker

    # User-supplied: no marker at all, which is the common case and reads as one.
    assert by_field["assessment_scale"].marker == ""

    # Not supplied: the methodology fallback, exactly as before.
    assert by_field["existing_tree_canopy_percent"].marker == STRINGS["not_supplied_marker"]


def test_an_unrecognised_provenance_key_is_shown_rather_than_hidden(
    render_args: Any,
) -> None:
    """A provenance record the report cannot name is a fact the reader still
    needs; falling through to the raw key beats dropping the marker."""
    content = build_content(
        **render_args("s05_minimal_input_pocket_park"),
        autofilled={"climate_zone": "some_later_dataset"},
    )
    marker = {row.field: row for row in content.inputs}["climate_zone"].marker
    assert "some_later_dataset" in marker


def test_a_report_with_no_autofill_is_unchanged(render_args: Any) -> None:
    """The overwhelmingly common case: no map was ever opened."""
    args = render_args("s05_minimal_input_pocket_park")
    without = build_content(**args)
    explicit_empty = build_content(**args, autofilled={})
    assert without.inputs == explicit_empty.inputs
    assert all("filled from the map" not in row.marker for row in without.inputs)


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


def test_a_single_intervention_names_itself_and_states_that_it_is_one(
    render_args: Any,
) -> None:
    args = render_args("s01_temperate_street_trees_worked_example")
    content = build_content(**args)
    assert content.typology == args["result"]["typology"]["display_name"]
    assert content.package_note == STRINGS["package_single"]


def test_a_package_names_every_component_in_its_identity_line(render_args: Any) -> None:
    """D-044.2: the report says what was assessed, not just the headline entry."""
    args = render_args("s02_tropical_wet_informal_settlement_package")
    names = [item["typology"]["display_name"] for item in args["result"]["components"]]
    assert len(names) > 1
    content = build_content(**args)
    for name in names:
        assert name in content.typology


def test_package_rows_itemise_each_component_verbatim(render_args: Any) -> None:
    """D-038: every component is reported on its own terms, nothing averaged.

    The figures are the engine's own — the component's inherited evidence
    class, its evidence rating, and its own adjusted cooling range.
    """
    args = render_args("s02_tropical_wet_informal_settlement_package")
    components = args["result"]["components"]
    content = build_content(**args)
    assert len(content.package_rows) == len(components)

    for row, component in zip(content.package_rows, components, strict=True):
        typology = component["typology"]
        assert row.name == typology["display_name"]
        assert row.archetype == typology["archetype_display_name"]
        assert row.evidence == OPTION_LABELS[typology["evidence_confidence"]]
        assert fmt(component["cooling"]["delta_t_min_c"]) in row.cooling_range
        assert fmt(component["cooling"]["delta_t_max_c"]) in row.cooling_range
        # Every component's suitability is displayed, including the
        # representative's: the marker is a separate field, so marking a row
        # can never cost it its score.
        assert row.suitability == fmt(component["suitability"]["score"])
        assert row.is_representative == component["is_representative"]


def test_the_package_note_states_the_capped_never_summed_rule(render_args: Any) -> None:
    """D-014/D-044.4: no retrieved source quantifies super-additive cooling, so
    the report says the estimate is never the sum of its parts."""
    args = render_args("s02_tropical_wet_informal_settlement_package")
    content = build_content(**args)
    assert content.package_note == STRINGS["package_rule"]
    assert "never the sum of its parts" in content.package_note


def test_exactly_one_component_carries_the_package_estimate(render_args: Any) -> None:
    args = render_args("s02_tropical_wet_informal_settlement_package")
    result = args["result"]
    content = build_content(**args)
    marked = [row for row in content.package_rows if row.is_representative]
    assert len(marked) == 1
    representative = next(item for item in result["components"] if item["is_representative"])
    assert marked[0].name == representative["typology"]["display_name"]
    assert marked[0].suitability == fmt(representative["suitability"]["score"])
    assert result["package"]["representative_nbs_type"] == representative["typology"]["nbs_type"]


def test_the_typology_row_names_every_selected_entry(render_args: Any) -> None:
    """``nbs_type`` is a list since D-044.2, and its label says so."""
    args = render_args("s02_tropical_wet_informal_settlement_package")
    content = build_content(**args)
    row = next(item for item in content.inputs if item.field == "nbs_type")
    assert row.label == FIELD_LABELS["nbs_type"] == "Intervention typologies"
    for selected in args["inp"]["nbs_type"]:
        assert selected in row.value
    assert row.marker == ""


def test_the_availability_answers_render_as_availability_only(render_args: Any) -> None:
    """D-044.1: a reader must never look for these four fields' contribution to
    a number, so the Inputs sheet labels them as gating answers."""
    args = render_args("s24_productive_landscape_evidence_gap")
    content = build_content(**args)
    by_field = {row.field: row for row in content.inputs}
    for field in (
        "includes_railway",
        "existing_woodland",
        "waterfront_type",
        "productive_governance",
    ):
        assert by_field[field].label == FIELD_LABELS[field]
        assert "availability only" in by_field[field].label

    governance = by_field["productive_governance"]
    assert governance.value == ", ".join(args["inp"]["productive_governance"])
    assert governance.marker == ""


def test_an_empty_multi_select_is_a_real_answer_not_an_absence(render_args: Any) -> None:
    """ "None selected" is distinct from "not answered": one is an answer."""
    args = render_args("s24_productive_landscape_evidence_gap")
    args["inp"]["productive_governance"] = []
    content = build_content(**args)
    row = next(item for item in content.inputs if item.field == "productive_governance")
    assert row.value == STRINGS["none_selected"]
    assert row.marker == ""


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
