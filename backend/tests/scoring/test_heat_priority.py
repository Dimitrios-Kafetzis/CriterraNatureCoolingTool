"""Unit tests for the Heat Priority Index (Methodology Report 5.3)."""

from __future__ import annotations

import pytest

from nature_cooling.engine.scoring import heat_priority


def test_worked_example(config):
    """Hand-derived: 0.60*66.25 + 0.40*80.00 = 71.75, High band."""
    block = heat_priority.compute(66.25, 80.0, config)
    assert block.score == 71.75
    assert block.category == "high"


@pytest.mark.parametrize(
    ("heat", "vuln", "expected_score", "expected_category"),
    [
        (0.0, 0.0, 0.0, "low"),
        (30.0, 30.0, 30.0, "low"),
        (50.0, 50.0, 50.0, "medium"),
        (60.0, 60.0, 60.0, "medium"),
        (80.0, 80.0, 80.0, "high"),
        (100.0, 100.0, 100.0, "critical"),
        (90.0, 75.0, 84.0, "critical"),
    ],
)
def test_bands_and_boundaries(config, heat, vuln, expected_score, expected_category):
    block = heat_priority.compute(heat, vuln, config)
    assert block.score == expected_score
    assert block.category == expected_category
