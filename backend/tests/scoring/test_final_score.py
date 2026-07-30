"""Unit tests for the final aggregation and weight redistribution (5.9)."""

from __future__ import annotations

import pytest

from nature_cooling.engine.scoring import final_score

FULL = {
    "heat_priority_index": 71.75,
    "cooling_potential": 71.25,
    "nbs_suitability": 76.25,
    "vulnerability": 80.0,
    "co_benefits": 58.75,
    "cost_feasibility": 60.0,
}


def test_all_components_present_uses_nominal_weights(config):
    block = final_score.compute(dict(FULL), config)
    # 0.25*71.75 + 0.25*71.25 + 0.15*76.25 + 0.15*80 + 0.10*58.75 + 0.10*60
    assert block.score == 71.06
    assert block.excluded_components == []
    weights = {c.name: c.applied_weight for c in block.components}
    assert weights["heat_priority_index"] == 0.25
    assert weights["cost_feasibility"] == 0.1


def test_missing_cost_feasibility_redistributes_proportionally(config):
    """Worked example: sum(w_i * s_i)/0.90 = 65.0625/0.9 = 72.29."""
    block = final_score.compute({**FULL, "cost_feasibility": None}, config)
    assert block.score == 72.29
    assert block.excluded_components == ["cost_feasibility"]
    applied = {c.name: c.applied_weight for c in block.components}
    assert applied["heat_priority_index"] == 0.2778
    assert applied["nbs_suitability"] == 0.1667
    assert "cost_feasibility" not in applied


def test_applied_weights_sum_to_one(config):
    """Property: redistribution must always renormalise to a unit sum."""
    for missing in (None, "cost_feasibility"):
        scores = dict(FULL)
        if missing:
            scores[missing] = None
        block = final_score.compute(scores, config)
        total = sum(c.nominal_weight for c in block.components)
        exact = sum(c.nominal_weight / total for c in block.components)
        assert exact == pytest.approx(1.0, abs=1e-12)


@pytest.mark.parametrize(
    ("value", "category"),
    [(20.0, "low"), (30.0, "low"), (45.0, "moderate"), (61.0, "strong"), (95.0, "high_priority")],
)
def test_categories(config, value, category):
    scores = {name: value for name in FULL}
    block = final_score.compute(scores, config)
    assert block.score == value
    assert block.category == category


def test_score_stays_within_bounds(config):
    for value in (0.0, 100.0):
        block = final_score.compute({name: value for name in FULL}, config)
        assert 0.0 <= block.score <= 100.0
