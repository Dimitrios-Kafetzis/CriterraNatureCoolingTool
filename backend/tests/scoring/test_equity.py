"""Unit tests for the Equity Score (D-022)."""

from __future__ import annotations

from nature_cooling.engine.scoring import equity


def test_all_missing_is_neutral_with_notes(config, build_input):
    block, assumptions = equity.compute(build_input(), config)
    assert block.score == 50.0
    assert len(assumptions) == 4


def test_worked_example_partial(config, build_input):
    """0.35*75 + 0.25*50 + 0.20*50 + 0.20*50 = 58.75."""
    block, assumptions = equity.compute(build_input(vulnerable_population_presence="high"), config)
    assert block.score == 58.75
    assert block.vulnerable_user_benefit == 75.0
    assert len(assumptions) == 3


def test_full_inputs(config, build_input):
    """0.35*100 + 0.25*75 + 0.20*75 + 0.20*50 = 78.75."""
    block, assumptions = equity.compute(
        build_input(
            vulnerable_population_presence="very_high",
            public_accessibility="high",
            safety_concern="high",
            community_participation="medium",
        ),
        config,
    )
    assert block.score == 78.75
    assert assumptions == []


def test_safety_concern_uses_deficit_reading(config, build_input):
    """Greater safety concern raises the equity relevance of the intervention."""
    high, _ = equity.compute(build_input(safety_concern="very_high"), config)
    low, _ = equity.compute(build_input(safety_concern="low"), config)
    assert high.safety_comfort == 100.0
    assert low.safety_comfort == 25.0
    assert high.score > low.score
