"""Tests for methodology configuration loading, validation, and evidence rules.

These tests are the automated half of the project's evidence policy: they fail
the build if a methodology value loses its citation, if the configuration files
drift out of version lock-step, or if the typology library stops matching what
the Methodology Report documents.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from nature_cooling.engine.config import (
    ConfigError,
    TypologyLibrary,
    bibliography_keys,
    collect_source_keys,
    default_config_dir,
    load_config,
)

EXPECTED_TYPOLOGY_COUNT = 14


@pytest.fixture(scope="module")
def config():
    return load_config()


def test_config_loads(config) -> None:
    assert config.version
    assert len(config.typologies.typologies) == EXPECTED_TYPOLOGY_COUNT


def test_all_config_files_share_one_version(config) -> None:
    """A methodology version must move as a single unit across every file."""
    for path in default_config_dir().glob("*.yaml"):
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert document["version"] == config.version, f"{path.name} is out of version lock-step"


def test_every_typology_is_cited(config) -> None:
    """No performance value may ship without a source (decision D-012)."""
    for typology in config.typologies.typologies:
        assert typology.sources, f"{typology.nbs_type} has no sources"
        for source in typology.sources:
            assert source.key.strip(), f"{typology.nbs_type} has an empty source key"
            assert source.finding.strip(), (
                f"{typology.nbs_type} cites {source.key} without a finding"
            )


def test_every_citation_exists_in_the_bibliography(config) -> None:
    """A citation may not point at a source the bibliography does not record."""
    known = bibliography_keys()
    cited = collect_source_keys(
        {
            "typologies": config.typologies.model_dump(),
            "weights": config.weights,
            "adjustment_factors": config.adjustment_factors,
            "input_mapping": config.input_mapping,
            "energy_model": config.energy_model,
            "country_defaults": config.country_defaults,
        }
    )
    assert cited, "configuration contains no citations at all"
    assert cited <= known, f"uncited sources: {sorted(cited - known)}"


def test_temperature_envelopes_are_ordered_and_plausible(config) -> None:
    """Envelopes must be ordered, and no typology may claim more than 3.5 C.

    The upper guard encodes a methodology decision: no retrieved source supports
    a daytime pedestrian-level air temperature reduction above roughly 3 C for a
    single site-level intervention, so a larger value in configuration indicates
    a calibration error rather than new evidence.
    """
    for typology in config.typologies.typologies:
        assert typology.temp_reduction_min_c <= typology.temp_reduction_max_c
        assert typology.temp_reduction_max_c <= 3.5, (
            f"{typology.nbs_type} claims {typology.temp_reduction_max_c} C, "
            "beyond the literature envelope"
        )


def test_low_confidence_typologies_are_declared(config) -> None:
    """Typologies with thin or conflicting evidence must say so.

    Guards against a future edit quietly promoting a weakly evidenced typology.
    """
    low_confidence = {
        typology.nbs_type
        for typology in config.typologies.typologies
        if typology.evidence_confidence == "low"
    }
    assert {"green_facade", "rain_garden_bioswale", "courtyard_greening"} <= low_confidence


def test_no_default_costs_are_shipped(config) -> None:
    """The cost policy (Methodology Report 5.8) must hold in configuration."""
    assert config.country_defaults["countries"] in (None, {}), (
        "country_defaults must ship no cost or emission values until each is verified"
    )
    serialised = yaml.safe_dump(config.typologies.model_dump())
    assert "cost_per_m2" not in serialised, "typology library must not carry default unit costs"


def test_lookup_by_type(config) -> None:
    assert config.typologies.by_type("urban_forest").base_cooling_score == 90
    with pytest.raises(ConfigError, match="unknown nbs_type"):
        config.typologies.by_type("teleportation_grove")


def test_missing_configuration_directory_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="missing configuration file"):
        load_config(config_dir=tmp_path)


def test_unknown_citation_is_rejected(tmp_path: Path, config) -> None:
    """A citation pointing at an unrecorded source must fail the load."""
    for path in default_config_dir().glob("*.yaml"):
        (tmp_path / path.name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

    library = yaml.safe_load((tmp_path / "nbs_typologies.yaml").read_text(encoding="utf-8"))
    library["typologies"][0]["sources"].append(
        {"key": "nonexistent2099", "finding": "invented"},
    )
    (tmp_path / "nbs_typologies.yaml").write_text(yaml.safe_dump(library), encoding="utf-8")

    with pytest.raises(ConfigError, match="absent from the bibliography"):
        load_config(config_dir=tmp_path)


def test_version_mismatch_is_rejected(tmp_path: Path) -> None:
    for path in default_config_dir().glob("*.yaml"):
        (tmp_path / path.name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

    weights = yaml.safe_load((tmp_path / "weights.yaml").read_text(encoding="utf-8"))
    weights["version"] = "1999.01.01"
    (tmp_path / "weights.yaml").write_text(yaml.safe_dump(weights), encoding="utf-8")

    with pytest.raises(ConfigError, match="version mismatch"):
        load_config(config_dir=tmp_path)


def test_uncited_typology_is_rejected() -> None:
    with pytest.raises(ValueError):
        TypologyLibrary.model_validate(
            {
                "version": "2026.07.30",
                "typologies": [
                    {
                        "nbs_id": "99",
                        "nbs_type": "uncited",
                        "display_name": "Uncited",
                        "category": "green",
                        "base_cooling_score": 50,
                        "temp_reduction_min_c": 0.1,
                        "temp_reduction_max_c": 1.0,
                        "evidence_confidence": "low",
                        "primary_cooling_mechanism": "none",
                        "building_energy_applicable": False,
                        "typical_use_context": [],
                        "suitability": {
                            "minimum_site_area_m2": 10,
                            "requires_soil": "none",
                            "requires_irrigation": "none",
                            "unsuitable_climate_zones": [],
                        },
                        "co_benefit_defaults": {},
                        "sources": [],
                    }
                ],
            }
        )


def test_inverted_temperature_envelope_is_rejected() -> None:
    with pytest.raises(ValueError, match="must be >="):
        TypologyLibrary.model_validate(
            {
                "version": "2026.07.30",
                "typologies": [
                    {
                        "nbs_id": "98",
                        "nbs_type": "inverted",
                        "display_name": "Inverted",
                        "category": "green",
                        "base_cooling_score": 50,
                        "temp_reduction_min_c": 2.0,
                        "temp_reduction_max_c": 0.5,
                        "evidence_confidence": "low",
                        "primary_cooling_mechanism": "none",
                        "building_energy_applicable": False,
                        "typical_use_context": [],
                        "suitability": {
                            "minimum_site_area_m2": 10,
                            "requires_soil": "none",
                            "requires_irrigation": "none",
                            "unsuitable_climate_zones": [],
                        },
                        "co_benefit_defaults": {},
                        "sources": [{"key": "bowler2010", "finding": "x"}],
                    }
                ],
            }
        )
