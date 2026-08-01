"""The 2-page PDF: extracted text and document structure, never pixels."""

from __future__ import annotations

import re
from io import BytesIO
from typing import Any

from pypdf import PdfReader

from nature_cooling.engine import run_assessment
from nature_cooling.engine.models import AssessmentInput
from nature_cooling.report import build_pdf_report
from nature_cooling.report.catalog import STATUS_TEXTS, STRINGS
from nature_cooling.report.content import fmt


def _pages(payload: bytes) -> list[str]:
    return [page.extract_text() for page in PdfReader(BytesIO(payload)).pages]


def test_every_golden_scenario_renders_exactly_two_pages(
    render_args: Any, scenario_names: list[str]
) -> None:
    """The 2-page contract (OQ-13/D-011) holds for every scenario, packages included.

    Every offender is named rather than only the first, so a layout regression
    reports its full extent in one run.
    """
    page_counts = {
        name: len(PdfReader(BytesIO(build_pdf_report(**render_args(name)))).pages)
        for name in scenario_names
    }
    assert {name: count for name, count in page_counts.items() if count != 2} == {}


def test_page_one_carries_identity_scores_categories_and_versions(
    render_args: Any, project_name: str
) -> None:
    args = render_args("s01_temperate_street_trees_worked_example")
    result = args["result"]
    page_one, _ = _pages(build_pdf_report(**args))
    assert project_name in page_one
    assert args["label"] in page_one
    assert result["typology"]["display_name"] in page_one
    assert fmt(result["heat_priority"]["score"]) in page_one
    assert fmt(result["opportunity"]["score"]) in page_one
    assert STRINGS["heat_priority"].upper() in page_one
    assert STRINGS["opportunity"].upper() in page_one
    assert result["recommendation"][:60] in page_one.replace("\n", " ")
    assert result["methodology_version"] in page_one
    assert result["engine_version"] in page_one
    # Per-block and overall confidence are summarised on page 1.
    assert STRINGS["confidence_heading"].upper() in page_one
    assert STRINGS["confidence_overall"] in page_one


def test_suitability_flags_render_prominently_on_page_one(render_args: Any) -> None:
    args = render_args("s04_unsuitable_riparian_small_dry_site")
    page_one, _ = _pages(build_pdf_report(**args))
    flat = page_one.replace("\n", " ")
    assert STRINGS["flags_heading"].upper() in page_one
    for flag in args["result"]["suitability"]["flags"]:
        assert flag["message"][:50] in flat


def test_evidence_cap_flag_appears_when_the_result_reports_it(render_args: Any) -> None:
    page_one, _ = _pages(build_pdf_report(**render_args("s07_green_facade_low_evidence_full_data")))
    assert STRINGS["evidence_cap"][:60] in page_one.replace("\n", " ")


def test_page_two_details_blocks_ranges_and_the_required_caveats(render_args: Any) -> None:
    args = render_args("s16_urban_forest_short_payback_high_readiness")
    result = args["result"]
    _, page_two = _pages(build_pdf_report(**args))
    flat = page_two.replace("\n", " ")

    for title in (
        "block_cooling",
        "block_energy",
        "block_ghg",
        "block_costs",
        "block_co_benefits",
        "block_equity",
    ):
        assert STRINGS[title].upper() in page_two
    cooling = result["cooling"]
    assert f"{fmt(cooling['delta_t_min_c'])}–{fmt(cooling['delta_t_max_c'])} °C" in flat
    assert STRINGS["sub_scores_heading"] in flat
    assert STRINGS["assumptions_heading"].upper() in page_two
    for assumption in result["assumptions_applied"]:
        assert assumption[:50] in flat
    # The method note carries the screening-level and daytime-only caveats
    # verbatim from the stored result (Methodology Report §8).
    assert "screening-level" in flat
    assert "daytime values" in flat
    assert "not microclimate simulation outputs" in flat


def test_page_one_names_every_component_of_a_package(render_args: Any) -> None:
    """The identity line says what was assessed, not just the headline entry."""
    args = render_args("s02_tropical_wet_informal_settlement_package")
    page_one, _ = _pages(build_pdf_report(**args))
    flat = page_one.replace("\n", " ")
    names = [item["typology"]["display_name"] for item in args["result"]["components"]]
    assert len(names) > 1
    for name in names:
        assert name in flat


def test_page_two_itemises_a_package_and_states_the_combination_rule(
    render_args: Any,
) -> None:
    """D-038/D-044.4: each component on its own terms, then how they combined.

    The temperature is the best-evidenced component's and is never the sum, so
    the rule is printed beside the table rather than left to be inferred.
    """
    args = render_args("s02_tropical_wet_informal_settlement_package")
    _, page_two = _pages(build_pdf_report(**args))
    flat = page_two.replace("\n", " ")

    assert STRINGS["package_heading"].upper() in page_two
    for component in args["result"]["components"]:
        typology = component["typology"]
        assert typology["display_name"] in flat
        assert typology["archetype_display_name"] in flat
    assert STRINGS["package_representative"] in flat
    assert STRINGS["package_rule"][:60] in flat


def test_a_single_intervention_spends_no_page_on_a_package_table(render_args: Any) -> None:
    """A package of one would gain a table restating the card above it, and the
    two-page contract has no room to spend on that."""
    args = render_args("s01_temperate_street_trees_worked_example")
    _, page_two = _pages(build_pdf_report(**args))
    assert STRINGS["package_heading"].upper() not in page_two
    assert STRINGS["package_representative"] not in page_two.replace("\n", " ")


def test_page_two_reports_statuses_for_what_was_not_calculated(render_args: Any) -> None:
    args = render_args("s19_explicit_unknowns_everywhere")
    result = args["result"]
    _, page_two = _pages(build_pdf_report(**args))
    flat = page_two.replace("\n", " ")
    assert result["energy"]["status_message"][:50] in flat
    assert STATUS_TEXTS["not_estimated"][:40] in flat  # cost outputs say so (D-016)
    assert STATUS_TEXTS["not_estimated_input"][:40] in flat


def test_warnings_render_when_the_result_recorded_them(render_args: Any) -> None:
    args = render_args("s20_validation_warnings")
    _, page_two = _pages(build_pdf_report(**args))
    flat = page_two.replace("\n", " ")
    assert STRINGS["warnings_heading"].upper() in page_two.replace("\n", " ").upper()
    for warning in args["result"]["warnings"]:
        assert warning[:50] in flat


def test_an_empty_assumptions_list_is_stated_not_omitted(render_args: Any) -> None:
    args = render_args("s16_urban_forest_short_payback_high_readiness")
    args["result"]["assumptions_applied"] = []
    _, page_two = _pages(build_pdf_report(**args))
    assert STRINGS["assumptions_none"][:40] in page_two.replace("\n", " ")


def test_document_metadata_derives_from_created_at_never_the_clock(
    render_args: Any, project_name: str
) -> None:
    args = render_args("s01_temperate_street_trees_worked_example")
    reader = PdfReader(BytesIO(build_pdf_report(**args)))
    metadata = reader.metadata
    assert metadata is not None
    assert metadata.get("/CreationDate") == "D:20260730202254Z"
    assert metadata.get("/Author") == "Criterra"
    assert project_name in str(metadata.get("/Title"))


def test_the_brand_families_are_embedded_in_the_document(render_args: Any) -> None:
    payload = build_pdf_report(**render_args("s01_temperate_street_trees_worked_example"))
    for family in (b"Newsreader", b"HankenGrotesk", b"IBMPlexMono"):
        assert family in payload


def test_same_stored_assessment_produces_byte_identical_pdfs(
    render_args: Any, scenario_names: list[str]
) -> None:
    for name in scenario_names:
        args = render_args(name)
        assert build_pdf_report(**args) == build_pdf_report(**args), name


def test_a_package_larger_than_the_page_is_counted_never_silently_dropped(
    render_args: Any, config
) -> None:
    """The two-page contract meets unbounded package size (D-034 vs D-044.4).

    Package size is deliberately uncapped, so a package can name far more
    components — and apply far more defaults — than two pages can itemise. Both
    growing lists are rendered against a measured space budget and state how
    many lines were left out; dropping them silently would let the report imply
    it had shown the whole package. The workbook, which has no page limit,
    still carries every line.
    """
    args = render_args("s23_package_capped_at_best_evidenced_component")
    inp = dict(args["inp"])
    inp["assessment_scale"] = "site"
    inp["nbs_type"] = [
        typology.nbs_type for typology in config.typologies.resolved if typology.family == "street"
    ] + [
        typology.nbs_type
        for typology in config.typologies.resolved
        if typology.family in ("park", "public_space", "tree_based")
    ]
    assert len(inp["nbs_type"]) > 25, "the package must exceed what two pages can itemise"
    args = {
        **args,
        "inp": inp,
        "result": run_assessment(AssessmentInput(**inp), config).model_dump(),
    }

    reader = PdfReader(BytesIO(build_pdf_report(**args)))
    assert len(reader.pages) == 2, "the two-page contract must hold at any package size"

    text = " ".join(" ".join(page.extract_text() for page in reader.pages).split())
    # How many fit depends on how each line wraps, so the test asserts that the
    # remainder is stated and adds up — never a hard-coded count, which would
    # break the moment a display name got longer.
    components = re.search(r"and (\d+)\s+further\s+component", text)
    assumptions = re.search(r"and (\d+)\s+further\s+assumption", text)
    assert components, "components that did not fit must be counted, not dropped"
    assert assumptions, "assumptions that did not fit must be counted, not dropped"
    assert 0 < int(components.group(1)) < len(inp["nbs_type"])

    # Warnings are never truncated: they are safety information, and the method
    # note carrying the daytime-only caveat always renders.
    assert "never summed" in text
    assert "All cooling estimates are daytime values" in text
