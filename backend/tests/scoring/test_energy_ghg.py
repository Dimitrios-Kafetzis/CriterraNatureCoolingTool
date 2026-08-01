"""Unit tests for the energy derivation and GHG conversion (5.6-5.7, D-015)."""

from __future__ import annotations

from nature_cooling.engine.config import load_config
from nature_cooling.engine.scoring import cooling, energy_ghg


def _cooling_block(config, build_input, factor=0.95):
    return cooling.compute(build_input(), config.typologies.by_type("tree_avenue"), factor, config)


def test_worked_example_range(config, build_input):
    """Hand-derived: 450000*0.50*0.02 = 4500; 450000*2.85*0.04 = 51300."""
    inp = build_input(
        nearby_building_cooling_demand_relevant="yes",
        annual_cooling_energy_demand_kwh=450000,
    )
    block = energy_ghg.compute_energy(
        inp,
        config.typologies.by_type("tree_avenue"),
        _cooling_block(config, build_input),
        config,
    )
    assert block.status == "calculated"
    assert block.savings_min_kwh_per_year == 4500.0
    assert block.savings_max_kwh_per_year == 51300.0


def test_typology_not_applicable_takes_precedence(config, build_input):
    """Pocket park cannot affect building loads, whatever the user supplies."""
    inp = build_input(
        nbs_type=["pocket_park"],
        nearby_building_cooling_demand_relevant="yes",
        annual_cooling_energy_demand_kwh=100000,
    )
    block = energy_ghg.compute_energy(
        inp, config.typologies.by_type("pocket_park"), _cooling_block(config, build_input), config
    )
    assert block.status == "typology_not_applicable"
    assert block.savings_min_kwh_per_year is None


def test_relevance_no(config, build_input):
    inp = build_input(nearby_building_cooling_demand_relevant="no")
    block = energy_ghg.compute_energy(
        inp,
        config.typologies.by_type("tree_avenue"),
        _cooling_block(config, build_input),
        config,
    )
    assert block.status == "not_applicable"


def test_relevance_not_confirmed(config, build_input):
    inp = build_input(annual_cooling_energy_demand_kwh=100000)
    block = energy_ghg.compute_energy(
        inp,
        config.typologies.by_type("tree_avenue"),
        _cooling_block(config, build_input),
        config,
    )
    assert block.status == "relevance_not_confirmed"


def test_missing_demand(config, build_input):
    inp = build_input(nearby_building_cooling_demand_relevant="yes")
    block = energy_ghg.compute_energy(
        inp,
        config.typologies.by_type("tree_avenue"),
        _cooling_block(config, build_input),
        config,
    )
    assert block.status == "missing_energy_demand"
    assert "not provided" in block.status_message


def test_ghg_requires_calculated_energy(config, build_input):
    inp = build_input(grid_emission_factor_kgco2e_per_kwh=0.3)
    energy = energy_ghg.compute_energy(
        inp,
        config.typologies.by_type("tree_avenue"),
        _cooling_block(config, build_input),
        config,
    )
    ghg = energy_ghg.compute_ghg(inp, energy, config)
    assert ghg.status == "energy_not_calculated"


def test_ghg_with_user_supplied_factor(config, build_input):
    """Hand-derived: 4500*0.30 = 1350; 51300*0.30 = 15390."""
    inp = build_input(
        nearby_building_cooling_demand_relevant="yes",
        annual_cooling_energy_demand_kwh=450000,
        grid_emission_factor_kgco2e_per_kwh=0.30,
    )
    energy = energy_ghg.compute_energy(
        inp,
        config.typologies.by_type("tree_avenue"),
        _cooling_block(config, build_input),
        config,
    )
    ghg = energy_ghg.compute_ghg(inp, energy, config)
    assert ghg.status == "calculated"
    assert ghg.avoided_min_kgco2e_per_year == 1350.0
    assert ghg.avoided_max_kgco2e_per_year == 15390.0
    assert ghg.emission_factor_origin == "user_supplied"


def test_ghg_missing_factor_reports_not_calculated(config, build_input):
    inp = build_input(
        nearby_building_cooling_demand_relevant="yes",
        annual_cooling_energy_demand_kwh=450000,
        country="BR",
    )
    energy = energy_ghg.compute_energy(
        inp,
        config.typologies.by_type("tree_avenue"),
        _cooling_block(config, build_input),
        config,
    )
    ghg = energy_ghg.compute_ghg(inp, energy, config)
    assert ghg.status == "missing_emission_factor"
    assert ghg.avoided_min_kgco2e_per_year is None


def test_ghg_with_country_default_factor(config, build_input, tmp_path):
    """A locally deployed country table is honoured, with origin recorded."""
    import yaml

    from nature_cooling.engine.config import default_config_dir

    for path in default_config_dir().glob("*.yaml"):
        (tmp_path / path.name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    defaults = yaml.safe_load((tmp_path / "country_defaults.yaml").read_text(encoding="utf-8"))
    defaults["countries"] = {
        "BR": {
            "currency": "BRL",
            "electricity_emission_factor_kgco2e_per_kwh": {
                "value": 0.1,
                "reference_year": 2025,
                "source_key": "ember",
            },
        }
    }
    (tmp_path / "country_defaults.yaml").write_text(yaml.safe_dump(defaults), encoding="utf-8")
    local_config = load_config(config_dir=tmp_path)

    inp = build_input(
        nearby_building_cooling_demand_relevant="yes",
        annual_cooling_energy_demand_kwh=450000,
        country="BR",
    )
    energy = energy_ghg.compute_energy(
        inp,
        local_config.typologies.by_type("tree_avenue"),
        _cooling_block(local_config, build_input),
        local_config,
    )
    ghg = energy_ghg.compute_ghg(inp, energy, local_config)
    assert ghg.status == "calculated"
    assert ghg.emission_factor_origin == "country_default"
    assert ghg.avoided_min_kgco2e_per_year == 450.0  # 4500 * 0.1
