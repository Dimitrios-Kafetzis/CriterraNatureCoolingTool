"""Unit tests for the Heat Exposure Score (Methodology Report 5.1)."""

from __future__ import annotations

from nature_cooling.engine.scoring import heat_exposure


def test_data_rich_path_worked_example(config, build_input):
    """Hand-derived: 0.40*42 + 0.25*85 + 0.20*75 + 0.15*88 = 66.25."""
    inp = build_input(
        lst_anomaly_c=4.2,
        impervious_surface_percent=85,
        solar_exposure="high",
        existing_green_cover_percent=12,
    )
    block, assumptions = heat_exposure.compute(inp, config)
    assert block.score == 66.25
    assert block.path == "data_rich"
    assert assumptions == []


def test_data_rich_missing_components_default_neutral(config, build_input):
    """Missing imperviousness, solar and green cover all enter as 50."""
    inp = build_input(lst_anomaly_c=10.0)
    block, assumptions = heat_exposure.compute(inp, config)
    # 0.40*100 + 0.25*50 + 0.20*50 + 0.15*50 = 70.0
    assert block.score == 70.0
    assert len(assumptions) == 3
    assert any("impervious_surface_percent" in note for note in assumptions)
    assert any("solar_exposure" in note for note in assumptions)
    assert any("existing_green_cover_percent" in note for note in assumptions)


def test_data_poor_path_uses_level_directly(config, build_input):
    block, assumptions = heat_exposure.compute(build_input(heat_exposure_level="very_high"), config)
    assert block.score == 100.0
    assert block.path == "data_poor"
    assert assumptions == []


def test_data_poor_path_missing_level_is_neutral_with_note(config, build_input):
    block, assumptions = heat_exposure.compute(build_input(), config)
    assert block.score == 50.0
    assert assumptions == ["heat_exposure_level not provided; neutral value 50 applied"]


def test_data_poor_path_explicit_unknown_is_noted(config, build_input):
    block, assumptions = heat_exposure.compute(build_input(heat_exposure_level="unknown"), config)
    assert block.score == 50.0
    assert assumptions == ["heat_exposure_level answered 'unknown'; neutral value 50 applied"]
