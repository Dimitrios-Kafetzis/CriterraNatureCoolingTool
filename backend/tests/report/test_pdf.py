"""The 2-page PDF: extracted text and document structure, never pixels."""

from __future__ import annotations

from io import BytesIO
from typing import Any

from pypdf import PdfReader

from nature_cooling.report import build_pdf_report
from nature_cooling.report.catalog import STATUS_TEXTS, STRINGS
from nature_cooling.report.content import fmt


def _pages(payload: bytes) -> list[str]:
    return [page.extract_text() for page in PdfReader(BytesIO(payload)).pages]


def test_every_golden_scenario_renders_exactly_two_pages(
    render_args: Any, scenario_names: list[str]
) -> None:
    for name in scenario_names:
        reader = PdfReader(BytesIO(build_pdf_report(**render_args(name))))
        assert len(reader.pages) == 2, name


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
