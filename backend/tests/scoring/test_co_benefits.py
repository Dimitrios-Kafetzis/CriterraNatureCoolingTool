"""Unit tests for the Co-benefit Score (OQ-18)."""

from __future__ import annotations

from nature_cooling.engine.scoring import co_benefits


def test_worked_example_defaults(config, build_input):
    """Street trees: 0.25*50 + 0.25*50 + 0.20*75 + 0.15*50 + 0.15*75 = 58.75."""
    block, assumptions = co_benefits.compute(
        build_input(), config.typologies.by_type("street_tree_planting"), config
    )
    assert block.score == 58.75
    assert block.social_inclusion == 50.0
    assert any("social_inclusion" in note and "no typology default" in note for note in assumptions)
    assert sum("taken from the typology default" in note for note in assumptions) == 4


def test_user_override_beats_default(config, build_input):
    inp = build_input(co_benefit_biodiversity="very_high", co_benefit_social_inclusion="high")
    block, assumptions = co_benefits.compute(
        inp, config.typologies.by_type("street_tree_planting"), config
    )
    assert block.biodiversity == 100.0
    assert block.social_inclusion == 75.0
    # 0.25*100 + 0.25*50 + 0.20*75 + 0.15*75 + 0.15*75 = 75.0
    assert block.score == 75.0
    assert not any("biodiversity" in note for note in assumptions)


def test_explicit_unknown_override_falls_back_to_default(config, build_input):
    inp = build_input(co_benefit_biodiversity="unknown")
    block, assumptions = co_benefits.compute(
        inp, config.typologies.by_type("street_tree_planting"), config
    )
    assert block.biodiversity == 50.0  # street-tree default 'medium'
    assert any("biodiversity" in note and "typology default" in note for note in assumptions)


def test_high_breadth_package(config, build_input):
    """Mixed package: 0.25*75 + 0.25*75 + 0.20*75 + 0.15*50 + 0.15*75 = 71.25."""
    block, _ = co_benefits.compute(
        build_input(nbs_type="mixed_nbs_package"),
        config.typologies.by_type("mixed_nbs_package"),
        config,
    )
    assert block.score == 71.25
