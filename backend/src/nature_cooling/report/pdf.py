"""The 2-page PDF report (OQ-13/D-011), mirroring the results page (UX §6).

Page 1 — summary: identity, both score cards with categories, suitability
flags rendered prominently (D-009), the recommendation, per-block and overall
confidence, and the methodology/engine version stamp. Page 2 — detail: the
six output blocks with ranges and statuses, adjustment and suitability
sub-scores, itemised assumptions, warnings, and the method note carrying the
daytime-only and screening-level caveats verbatim from the stored result.

The PDF embeds static TTF builds of the three self-hosted brand families
(Newsreader / Hanken Grotesk / IBM Plex Mono; OFL notice alongside the font
files) and the Criterra lockup as vector paths (D-042), so the document is
self-contained on any machine. The document ``CreationDate`` derives from the
assessment's ``created_at``, never from the clock, which keeps the output
byte-deterministic (D-033).
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from fpdf import FPDF

from nature_cooling.report.catalog import STRINGS
from nature_cooling.report.content import Block, ReportContent, Row, ScoreCard, build_content

_FONT_DIR = Path(__file__).parent / "fonts"
_BRAND_DIR = Path(__file__).parent / "brand"
_LOCKUP = _BRAND_DIR / "criterra-lockup.svg"
_LOCKUP_WIDTH_MM = 30.0

_MARGIN = 14.0
_PAGE_WIDTH = 210.0
_CONTENT_WIDTH = _PAGE_WIDTH - 2 * _MARGIN
_COLUMN_GAP = 6.0
_COLUMN_WIDTH = (_CONTENT_WIDTH - _COLUMN_GAP) / 2

_INK = (22, 35, 28)
_MUTED = (95, 106, 99)
_GREEN = (46, 106, 78)
_PAPER = (234, 235, 226)
_FLAG_FILL = (246, 233, 227)
_FLAG_BAR = (154, 52, 30)
_RULE = (203, 207, 196)


class _ReportPDF(FPDF):
    """A4 portrait with the brand families registered."""

    def __init__(self) -> None:
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_margins(_MARGIN, _MARGIN)
        self.set_auto_page_break(True, margin=_MARGIN)
        self.add_font("Newsreader", "", _FONT_DIR / "Newsreader-Regular.ttf")
        self.add_font("Newsreader", "B", _FONT_DIR / "Newsreader-SemiBold.ttf")
        self.add_font("Hanken", "", _FONT_DIR / "HankenGrotesk-Regular.ttf")
        self.add_font("Hanken", "B", _FONT_DIR / "HankenGrotesk-Bold.ttf")
        self.add_font("Mono", "", _FONT_DIR / "IBMPlexMono-Regular.ttf")


def _line_height(size: float) -> float:
    return size * 0.47


def _text(
    pdf: FPDF,
    text: str,
    *,
    family: str = "Hanken",
    style: str = "",
    size: float = 9.0,
    color: tuple[int, int, int] = _INK,
    width: float = _CONTENT_WIDTH,
    x: float | None = None,
) -> None:
    if x is not None:
        pdf.set_x(x)
    pdf.set_font(family, style, size)
    pdf.set_text_color(*color)
    pdf.multi_cell(width, _line_height(size), text, align="L", new_x="LMARGIN", new_y="NEXT")


def _heading(pdf: FPDF, text: str) -> None:
    pdf.ln(1.4)
    _text(pdf, text.upper(), style="B", size=8.5, color=_GREEN)
    pdf.ln(0.6)


def _label_value_rows(
    pdf: FPDF,
    rows: tuple[Row, ...],
    *,
    x: float,
    width: float,
    label_width: float,
    size: float = 8.2,
) -> None:
    height = _line_height(size)
    for row in rows:
        start = pdf.get_y()
        pdf.set_xy(x, start)
        pdf.set_font("Hanken", "", size)
        pdf.set_text_color(*_MUTED)
        pdf.multi_cell(label_width, height, row.label, align="L")
        label_end = pdf.get_y()
        pdf.set_xy(x + label_width, start)
        pdf.set_font("Hanken", "B", size)
        pdf.set_text_color(*_INK)
        pdf.multi_cell(width - label_width, height, row.value, align="L")
        pdf.set_y(max(label_end, pdf.get_y()) + 0.5)


def _score_card(pdf: FPDF, card: ScoreCard, x: float, y: float, height: float) -> None:
    pdf.set_fill_color(*_PAPER)
    pdf.set_draw_color(*_RULE)
    pdf.rect(x, y, _COLUMN_WIDTH, height, style="DF")
    inner_x = x + 4.0
    inner_width = _COLUMN_WIDTH - 8.0
    pdf.set_xy(inner_x, y + 3.5)
    _text(pdf, card.title.upper(), style="B", size=8.0, color=_GREEN, width=inner_width, x=inner_x)
    pdf.set_xy(inner_x, pdf.get_y() + 0.5)
    _text(pdf, card.score, family="Newsreader", style="B", size=25, width=inner_width, x=inner_x)
    _text(pdf, card.scale_note, size=7.0, color=_MUTED, width=inner_width, x=inner_x)
    pdf.set_xy(inner_x, pdf.get_y() + 1.2)
    _text(
        pdf,
        f"{card.category} · {STRINGS['confidence_badge'].format(level=card.confidence)}",
        style="B",
        size=8.6,
        width=inner_width,
        x=inner_x,
    )
    if card.extra_rows:
        pdf.set_xy(inner_x, pdf.get_y() + 1.2)
        _label_value_rows(
            pdf, card.extra_rows, x=inner_x, width=inner_width, label_width=inner_width - 16.0
        )


def _flag_box(pdf: FPDF, text: str) -> None:
    size = 8.6
    start = pdf.get_y()
    pdf.set_fill_color(*_FLAG_FILL)
    text_x = _MARGIN + 4.0
    pdf.set_xy(text_x, start + 1.6)
    pdf.set_font("Hanken", "B", size)
    pdf.set_text_color(*_FLAG_BAR)
    pdf.multi_cell(_CONTENT_WIDTH - 8.0, _line_height(size), text, align="L")
    end = pdf.get_y() + 1.6
    pdf.set_draw_color(*_FLAG_BAR)
    pdf.set_fill_color(*_FLAG_BAR)
    pdf.rect(_MARGIN, start, 1.4, end - start, style="F")
    pdf.set_y(end + 1.4)


def _page_one(pdf: FPDF, content: ReportContent) -> None:
    pdf.add_page()
    # The Criterra lockup, as vector paths, above the product name (D-042).
    pdf.image(_LOCKUP, x=_MARGIN, y=_MARGIN - 1.0, w=_LOCKUP_WIDTH_MM)
    pdf.set_y(_MARGIN + 8.0)
    pdf.set_font("Hanken", "B", 8.5)
    pdf.set_text_color(*_GREEN)
    pdf.cell(
        _CONTENT_WIDTH / 2,
        _line_height(8.5),
        f"{STRINGS['app_title']} — {STRINGS['app_subtitle']}".upper(),
    )
    pdf.set_font("Mono", "", 7.5)
    pdf.set_text_color(*_MUTED)
    pdf.cell(
        _CONTENT_WIDTH / 2, _line_height(8.5), STRINGS["report_title"], align="R", new_x="LMARGIN"
    )
    pdf.ln(7)

    _text(pdf, content.project_name, family="Newsreader", style="B", size=19)
    pdf.ln(0.6)
    _text(
        pdf,
        f"{content.label} · {content.typology}",
        size=10.0,
    )
    pdf.ln(0.6)
    _text(
        pdf,
        f"{STRINGS['created']} {content.created_date} · {content.version_line}",
        family="Mono",
        size=7.3,
        color=_MUTED,
    )
    pdf.ln(1.6)
    pdf.set_draw_color(*_GREEN)
    pdf.line(_MARGIN, pdf.get_y(), _PAGE_WIDTH - _MARGIN, pdf.get_y())
    pdf.ln(3.4)

    card_height = 41.0
    card_y = pdf.get_y()
    heat_card, opportunity_card = content.cards
    _score_card(pdf, heat_card, _MARGIN, card_y, card_height)
    _score_card(pdf, opportunity_card, _MARGIN + _COLUMN_WIDTH + _COLUMN_GAP, card_y, card_height)
    pdf.set_y(card_y + card_height + 1.5)

    if content.flags:
        _heading(pdf, STRINGS["flags_heading"])
        for flag in content.flags:
            _flag_box(pdf, flag)

    _heading(pdf, STRINGS["recommendation_heading"])
    _text(pdf, content.recommendation, family="Newsreader", size=10.2)

    _heading(pdf, STRINGS["confidence_heading"])
    _label_value_rows(
        pdf, content.confidence_rows, x=_MARGIN, width=_CONTENT_WIDTH, label_width=40.0, size=8.6
    )

    pdf.set_y(-_MARGIN - 4.5)
    pdf.set_font("Mono", "", 7.0)
    pdf.set_text_color(*_MUTED)
    pdf.cell(_CONTENT_WIDTH / 2, _line_height(7.0), STRINGS["copyright_line"])
    pdf.cell(_CONTENT_WIDTH / 2, _line_height(7.0), STRINGS["license_line"], align="R")


def _block(pdf: FPDF, block: Block, x: float, y: float) -> float:
    pdf.set_xy(x, y)
    title = block.title.upper()
    if block.confidence is not None:
        badge = STRINGS["confidence_badge"].format(level=block.confidence)
        title = f"{title} · {badge}"
    _text(pdf, title, style="B", size=8.0, color=_GREEN, width=_COLUMN_WIDTH, x=x)
    pdf.set_y(pdf.get_y() + 1.0)
    _label_value_rows(pdf, block.rows, x=x, width=_COLUMN_WIDTH, label_width=37.0)
    if block.sub_rows:
        pdf.set_x(x)
        pdf.set_y(pdf.get_y() + 0.6)
        _text(pdf, block.sub_heading or "", style="B", size=7.2, color=_MUTED, x=x)
        pdf.set_y(pdf.get_y() + 0.6)
        _label_value_rows(pdf, block.sub_rows, x=x, width=_COLUMN_WIDTH, label_width=37.0)
    if block.note is not None:
        pdf.set_xy(x, pdf.get_y() + 0.4)
        _text(pdf, block.note, size=7.2, color=_MUTED, width=_COLUMN_WIDTH, x=x)
    return pdf.get_y() + 2.8


def _page_two(pdf: FPDF, content: ReportContent) -> None:
    pdf.add_page()
    _text(pdf, STRINGS["page2_heading"].upper(), style="B", size=8.5, color=_GREEN)
    pdf.ln(2.0)
    top = pdf.get_y()

    cooling, energy, ghg, costs, co_benefits, equity = content.blocks
    left_y = top
    for block in (cooling, co_benefits):
        left_y = _block(pdf, block, _MARGIN, left_y)
    right_x = _MARGIN + _COLUMN_WIDTH + _COLUMN_GAP
    right_y = top
    for block in (energy, ghg, costs, equity):
        right_y = _block(pdf, block, right_x, right_y)
    pdf.set_y(max(left_y, right_y))

    _heading(pdf, STRINGS["assumptions_heading"])
    if content.assumptions:
        _text(pdf, STRINGS["assumptions_intro"], size=7.4, color=_MUTED)
        pdf.ln(0.6)
        for assumption in content.assumptions:
            _text(pdf, f"–  {assumption}", size=7.2)
    else:
        _text(pdf, STRINGS["assumptions_none"], size=7.2)

    if content.warnings:
        _heading(pdf, STRINGS["warnings_heading"])
        for warning in content.warnings:
            _text(pdf, f"–  {warning}", size=7.2)

    _heading(pdf, STRINGS["method_note_heading"])
    _text(pdf, content.method_note, family="Newsreader", size=8.8)
    pdf.ln(1.0)
    _text(pdf, content.version_line, family="Mono", size=7.3, color=_MUTED)


def build_pdf_report(
    *,
    project_name: str,
    label: str,
    created_at: str,
    inp: dict[str, Any],
    result: dict[str, Any],
) -> bytes:
    """Render one stored, evaluated assessment as 2-page PDF bytes."""
    content = build_content(
        project_name=project_name, label=label, created_at=created_at, inp=inp, result=result
    )
    pdf = _ReportPDF()
    pdf.set_title(f"{STRINGS['app_title']} {STRINGS['report_title']} — {project_name} · {label}")
    pdf.set_author("Criterra")
    pdf.set_creator(f"{STRINGS['app_title']} — {STRINGS['app_subtitle']}")
    pdf.set_lang("en")
    pdf.set_creation_date(datetime.fromisoformat(created_at))
    _page_one(pdf, content)
    _page_two(pdf, content)
    return bytes(pdf.output())
