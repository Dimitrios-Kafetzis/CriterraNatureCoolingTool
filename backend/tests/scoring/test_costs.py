"""Unit tests for cost outputs: payback, feasibility, readiness (5.8, D-010, D-016)."""

from __future__ import annotations

import pytest

from nature_cooling.engine.models import EnergyBlock
from nature_cooling.engine.scoring import costs


def _energy(min_kwh=4500.0, max_kwh=51300.0, status="calculated"):
    return EnergyBlock(
        status=status,
        status_message="x",
        savings_min_kwh_per_year=min_kwh if status == "calculated" else None,
        savings_max_kwh_per_year=max_kwh if status == "calculated" else None,
    )


def test_no_cost_input_everything_not_estimated(config, build_input):
    block, assumptions = costs.compute(build_input(), _energy(), "high", config)
    assert block.annual_savings_status == "missing_energy_price"
    assert block.payback_status == "missing_capital_cost"
    assert block.cost_feasibility_status == "not_estimated"
    assert block.cost_feasibility_score is None
    assert block.investment_readiness_status == "not_estimated"
    assert assumptions == []


def test_energy_not_calculated_blocks_savings_and_payback(config, build_input):
    inp = build_input(capital_cost=10000, energy_price_per_kwh=0.2)
    block, _ = costs.compute(inp, _energy(status="missing_energy_demand"), "low", config)
    assert block.annual_savings_status == "energy_not_calculated"
    assert block.payback_status == "annual_savings_unavailable"
    assert block.cost_feasibility_status == "not_estimated"


def test_full_cost_case_medium_bracket(config, build_input):
    """Hand-derived from the worked-example energy range with price 0.20:

    annual savings 900-10260; central 5580; payback central 40000/5580 = 7.17
    -> medium bracket (75). Feasibility 0.5*75 + 0.25*50 + 0.25*100 = 75.0.
    """
    inp = build_input(
        capital_cost=40000,
        energy_price_per_kwh=0.2,
        implementation_complexity="medium",
        maintenance_intensity="low",
    )
    block, assumptions = costs.compute(inp, _energy(), "high", config)
    assert block.annual_savings_min == 900.0
    assert block.annual_savings_max == 10260.0
    assert block.payback_years_min == 3.9  # 40000/10260
    assert block.payback_years_max == 44.44  # 40000/900
    assert block.payback_years_central == 7.17
    assert block.payback_bracket == "medium"
    assert block.cost_feasibility_score == 75.0
    assert block.investment_readiness == "medium"
    assert assumptions == []


@pytest.mark.parametrize(
    ("capital", "expected_bracket", "expected_score_term"),
    [
        (5000, "short", 100.0),  # central payback 0.90
        (30000, "medium", 75.0),  # 5.38
        (60000, "long", 50.0),  # 10.75
        (120000, "very_long", 25.0),  # 21.51
    ],
)
def test_payback_brackets(config, build_input, capital, expected_bracket, expected_score_term):
    inp = build_input(
        capital_cost=capital,
        energy_price_per_kwh=0.2,
        implementation_complexity="medium",
        maintenance_intensity="medium",
    )
    block, _ = costs.compute(inp, _energy(), "high", config)
    assert block.payback_bracket == expected_bracket
    # 0.5*bracket + 0.25*50 + 0.25*50
    assert block.cost_feasibility_score == round(0.5 * expected_score_term + 25.0, 2)


def test_defaulted_complexity_and_maintenance_are_itemised(config, build_input):
    inp = build_input(capital_cost=5000, energy_price_per_kwh=0.2)
    block, assumptions = costs.compute(inp, _energy(), "high", config)
    assert block.cost_feasibility_score == 75.0  # 0.5*100 + 0.25*50 + 0.25*50
    assert len(assumptions) == 2


def test_readiness_downgraded_by_high_complexity(config, build_input):
    inp = build_input(
        capital_cost=5000,
        energy_price_per_kwh=0.2,
        implementation_complexity="high",
        maintenance_intensity="low",
    )
    block, _ = costs.compute(inp, _energy(), "high", config)
    assert block.payback_bracket == "short"
    assert block.investment_readiness == "medium"  # high downgraded once


def test_readiness_downgraded_by_low_energy_confidence(config, build_input):
    """Unreachable through the shipped field mapping (calculated energy implies
    at least medium energy confidence) but specified and enforced for
    deployments that alter the confidence field lists."""
    inp = build_input(
        capital_cost=5000,
        energy_price_per_kwh=0.2,
        implementation_complexity="low",
        maintenance_intensity="low",
    )
    block, _ = costs.compute(inp, _energy(), "low", config)
    assert block.investment_readiness == "medium"


def test_readiness_floor_at_low(config, build_input):
    inp = build_input(
        capital_cost=120000,
        energy_price_per_kwh=0.2,
        implementation_complexity="high",
        maintenance_intensity="high",
    )
    block, _ = costs.compute(inp, _energy(), "low", config)
    assert block.investment_readiness == "low"


def test_zero_savings_cannot_produce_payback(config, build_input):
    """Defensive: a zero-width saving must not divide by zero."""
    inp = build_input(capital_cost=10000, energy_price_per_kwh=0.2)
    block, _ = costs.compute(inp, _energy(min_kwh=0.0, max_kwh=0.0), "high", config)
    assert block.annual_savings_status == "calculated"
    assert block.payback_status == "annual_savings_unavailable"
    assert block.cost_feasibility_status == "not_estimated"
