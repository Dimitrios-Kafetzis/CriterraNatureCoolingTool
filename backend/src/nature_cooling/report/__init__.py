"""Report export: pure functions from one stored assessment to document bytes.

The builders render a stored, evaluated assessment **verbatim** (OQ-15,
D-033): every figure, level, band, flag, recommendation, and assumption comes
from the stored result or the stored input; the engine is never called, and
no number originates here. Both formats are byte-deterministic — document
timestamps derive from the assessment's ``created_at``, never from the clock.
"""

from nature_cooling.report.pdf import build_pdf_report
from nature_cooling.report.xlsx import build_xlsx_report

__all__ = ["build_pdf_report", "build_xlsx_report"]
