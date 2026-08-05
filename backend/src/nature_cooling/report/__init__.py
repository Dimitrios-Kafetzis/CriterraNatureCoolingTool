"""Report export: pure functions from stored assessments to document bytes.

The builders render stored, evaluated assessments **verbatim** (OQ-15,
D-033): every figure, level, band, flag, recommendation, and assumption comes
from the stored result or the stored input; the engine is never called, and
no number originates here. Both formats are byte-deterministic — document
timestamps derive from stored ``created_at`` values, never from the clock.

Two report shapes exist: the single-assessment report, and the v2.4
comparison report over 2–4 scenarios of one project, which shares the same
format-neutral content layer (:mod:`nature_cooling.report.content`).
"""

from nature_cooling.report.content import ScenarioSource
from nature_cooling.report.pdf import build_comparison_pdf_report, build_pdf_report
from nature_cooling.report.xlsx import build_comparison_xlsx_report, build_xlsx_report

__all__ = [
    "ScenarioSource",
    "build_comparison_pdf_report",
    "build_comparison_xlsx_report",
    "build_pdf_report",
    "build_xlsx_report",
]
