"""Unit tests for the normalisation helpers."""

from __future__ import annotations

import pytest

from nature_cooling.engine.normalisation import (
    clamp,
    clip,
    default_note,
    lst_score,
    pick_bracket,
    qualitative_score,
    score_band,
)


def test_clamp_bounds():
    assert clamp(-5) == 0.0
    assert clamp(50) == 50.0
    assert clamp(120) == 100.0


def test_clip_bounds():
    assert clip(0.475, 0.5, 3.0) == 0.5
    assert clip(3.6, 0.5, 3.0) == 3.0
    assert clip(1.5, 0.5, 3.0) == 1.5


def test_qualitative_score_named_scale(config):
    assert qualitative_score(config, "solar_exposure", "high") == 75.0
    assert qualitative_score(config, "solar_exposure", "very_high") == 100.0
    assert qualitative_score(config, "solar_exposure", None) == 50.0


def test_qualitative_score_inverted_scale_reference(config):
    """access_to_cooled_indoor_space names its scale inside a mapping."""
    assert qualitative_score(config, "access_to_cooled_indoor_space", "low") == 100.0
    assert qualitative_score(config, "access_to_cooled_indoor_space", "high") == 25.0


def test_qualitative_score_inline_table(config):
    assert qualitative_score(config, "soil_availability", "none") == 25.0
    assert qualitative_score(config, "soil_availability", "high") == 100.0
    assert qualitative_score(config, "irrigation_availability", "reliable") == 100.0
    assert qualitative_score(config, "current_shade_level", "very_low") == 25.0


def test_lst_score_linear_and_clamped(config):
    assert lst_score(config, 4.2) == pytest.approx(42.0)
    assert lst_score(config, 12.0) == 100.0
    assert lst_score(config, -2.0) == 0.0
    assert lst_score(config, 0.0) == 0.0


def test_pick_bracket_half_open():
    brackets = [
        {"max_years": 5, "label": "short"},
        {"min_years": 5, "max_years": 10, "label": "medium"},
        {"min_years": 10, "label": "long"},
    ]
    assert pick_bracket(brackets, 4.99, "min_years", "max_years")["label"] == "short"
    assert pick_bracket(brackets, 5.0, "min_years", "max_years")["label"] == "medium"
    assert pick_bracket(brackets, 10.0, "min_years", "max_years")["label"] == "long"


def test_pick_bracket_no_match_raises():
    with pytest.raises(ValueError, match="no bracket contains"):
        pick_bracket([{"min_years": 10, "max_years": 20}], 5.0, "min_years", "max_years")


def test_score_band_upper_inclusive(config):
    assert score_band(config, "heat_priority_index", 30.0) == "low"
    assert score_band(config, "heat_priority_index", 30.01) == "medium"
    assert score_band(config, "opportunity", 80.0) == "strong"
    assert score_band(config, "opportunity", 100.0) == "high_priority"


def test_default_note_wording():
    assert default_note("solar_exposure", None) == (
        "solar_exposure not provided; neutral value 50 applied"
    )
    assert default_note("solar_exposure", "unknown") == (
        "solar_exposure answered 'unknown'; neutral value 50 applied"
    )
