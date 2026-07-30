"""Unit tests for the deterministic recommendation composer (D-011/OQ-12)."""

from __future__ import annotations

from nature_cooling.engine import recommendation


def _compose(
    config, build_input, *, nbs_type="street_tree_planting", input_overrides=None, **overrides
):
    defaults = dict(
        heat_priority_category="high",
        opportunity_category="strong",
        delta_t_min_c=0.5,
        delta_t_max_c=2.85,
        suitability_flags=[],
        energy_status="calculated",
        energy_status_message="Energy savings derived from estimated cooling effect.",
        annual_savings_status="calculated",
        payback_status="calculated",
        overall_confidence="high",
    )
    defaults.update(overrides)
    inp = build_input(nbs_type=nbs_type, **(input_overrides or {}))
    typology = config.typologies.by_type(nbs_type)
    return recommendation.compose(inp, typology, config=config, **defaults)


def test_baseline_composition(config, build_input):
    text = _compose(config, build_input)
    assert text.startswith("This site shows a high heat priority.")
    assert "strong NbS cooling opportunity" in text
    assert (
        "Street tree planting is expected to deliver an indicative daytime air "
        "temperature reduction of 0.5-2.85 C at pedestrian level, principally "
        "through shade and evapotranspiration." in text
    )
    assert "IMPORTANT" not in text
    assert "not calculated" not in text


def test_temperature_formatting_keeps_one_decimal(config, build_input):
    text = _compose(config, build_input, delta_t_min_c=1.0, delta_t_max_c=3.0)
    assert "1.0-3.0 C" in text


def test_not_suitable_flag_lists_reasons(config, build_input):
    text = _compose(
        config,
        build_input,
        suitability_flags=["reason one", "reason two"],
    )
    assert "IMPORTANT: this typology is not suitable for this site" in text
    assert "(reason one; reason two)" in text


def test_low_evidence_flag_for_green_facade(config, build_input):
    text = _compose(config, build_input, nbs_type="green_facade")
    assert "published evidence for this typology is limited or inconsistent" in text


def test_green_roof_street_level_caveat(config, build_input):
    text = _compose(config, build_input, nbs_type="green_roof")
    assert "concentrated at roof level" in text


def test_blue_humidity_caveat_fires_only_in_tropical_wet(config, build_input):
    wet = _compose(
        config,
        build_input,
        nbs_type="blue_green_corridor",
        input_overrides={"climate_zone": "tropical_wet"},
    )
    assert "add humidity" in wet
    temperate = _compose(config, build_input, nbs_type="blue_green_corridor")
    assert "add humidity" not in temperate


def test_energy_not_calculated_flag_carries_reason(config, build_input):
    text = _compose(
        config,
        build_input,
        energy_status="missing_energy_demand",
        energy_status_message="Annual cooling energy demand was not provided.",
        annual_savings_status="energy_not_calculated",
        payback_status="missing_capital_cost",
    )
    assert (
        "Cooling-energy savings were not calculated "
        "(annual cooling energy demand was not provided)." in text
    )
    assert "no cost input was supplied" in text  # capital absent -> cost flag


def test_payback_not_estimated_when_capital_present(config, build_input):
    text = _compose(
        config,
        build_input,
        input_overrides={"capital_cost": 10000.0},
        energy_status="typology_not_applicable",
        energy_status_message="This typology's benefit is principally amenity-level.",
        annual_savings_status="energy_not_calculated",
        payback_status="annual_savings_unavailable",
    )
    assert "A capital cost was supplied" in text
    assert "energy savings were not calculated" in text
    assert "no cost input was supplied" not in text


def test_payback_not_estimated_missing_price(config, build_input):
    text = _compose(
        config,
        build_input,
        input_overrides={"capital_cost": 10000.0},
        annual_savings_status="missing_energy_price",
        payback_status="annual_savings_unavailable",
    )
    assert "no energy price was supplied" in text


def test_payback_not_estimated_fallback_reason(config, build_input):
    text = _compose(
        config,
        build_input,
        input_overrides={"capital_cost": 10000.0},
        annual_savings_status="calculated",
        payback_status="annual_savings_unavailable",
    )
    assert "annual cost savings are unavailable" in text


def test_low_confidence_flag(config, build_input):
    text = _compose(config, build_input, overall_confidence="low")
    assert "treat the result as a screening signal" in text


def test_method_note_contains_both_closings(config):
    note = recommendation.method_note(config)
    assert "screening-level estimates" in note
    assert "daytime values" in note
