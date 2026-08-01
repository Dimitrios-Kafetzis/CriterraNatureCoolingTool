"""Unit tests for the Co-benefit Score (OQ-18)."""

from __future__ import annotations

from nature_cooling.engine.runner import run_assessment
from nature_cooling.engine.scoring import co_benefits


def test_worked_example_defaults(config, build_input):
    """Street trees: 0.25*50 + 0.25*50 + 0.20*75 + 0.15*50 + 0.15*75 = 58.75."""
    block, assumptions = co_benefits.compute(
        build_input(), config.typologies.by_type("tree_avenue"), config
    )
    assert block.score == 58.75
    assert block.social_inclusion == 50.0
    assert any("social_inclusion" in note and "no typology default" in note for note in assumptions)
    assert sum("taken from the typology default" in note for note in assumptions) == 4


def test_user_override_beats_default(config, build_input):
    inp = build_input(co_benefit_biodiversity="very_high", co_benefit_social_inclusion="high")
    block, assumptions = co_benefits.compute(inp, config.typologies.by_type("tree_avenue"), config)
    assert block.biodiversity == 100.0
    assert block.social_inclusion == 75.0
    # 0.25*100 + 0.25*50 + 0.20*75 + 0.15*75 + 0.15*75 = 75.0
    assert block.score == 75.0
    assert not any("biodiversity" in note for note in assumptions)


def test_explicit_unknown_override_falls_back_to_default(config, build_input):
    inp = build_input(co_benefit_biodiversity="unknown")
    block, assumptions = co_benefits.compute(inp, config.typologies.by_type("tree_avenue"), config)
    assert block.biodiversity == 50.0  # street-tree default 'medium'
    assert any("biodiversity" in note and "typology default" in note for note in assumptions)


def test_high_breadth_package_takes_the_union_of_its_components(config, build_input):
    """D-038: a package's co-benefits are the maximum per dimension, not a mean.

    Breadth is the advantage a package genuinely has, since it is not permitted
    to claim additional degrees. Three components, none of which reaches 'high'
    on every dimension on its own:

      tree avenue        bio medium, storm medium, health high, quality high
      rain garden        bio medium, storm high,   health low,  quality medium
      neighbourhood park bio high,   storm medium, health high, quality high

    Union: 75/75/75/-/75 with social inclusion at the neutral 50 (no typology
    carries a default for it), giving
    0.25*75 + 0.25*75 + 0.20*75 + 0.15*50 + 0.15*75 = 71.25.
    """
    result = run_assessment(
        build_input(nbs_type=["tree_avenue", "rain_garden", "neighbourhood_park"]), config
    )
    assert result.co_benefits.score == 71.25
    assert result.co_benefits.social_inclusion == 50.0
    # No component reaches 71.25 alone: the union is strictly broader than the
    # best single member, and is never a sum of them either.
    component_scores = [component.co_benefits.score for component in result.components]
    assert max(component_scores) < result.co_benefits.score
    assert result.co_benefits.score < sum(component_scores)
