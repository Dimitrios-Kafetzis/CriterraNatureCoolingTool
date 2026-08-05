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

EXPECTED_ARCHETYPE_COUNT = 18
EXPECTED_TYPOLOGY_COUNT = 121


@pytest.fixture(scope="module")
def config():
    return load_config()


def test_config_loads(config) -> None:
    """The two-level library loads and resolves (D-044).

    18 cited evidence classes, 110 catalogue entries, and one resolved view per
    entry — the flat shape every scoring module consumes.
    """
    assert config.version
    assert len(config.typologies.archetypes) == EXPECTED_ARCHETYPE_COUNT
    assert len(config.typologies.typologies) == EXPECTED_TYPOLOGY_COUNT
    assert len(config.typologies.resolved) == EXPECTED_TYPOLOGY_COUNT


def test_all_config_files_share_one_version(config) -> None:
    """A methodology version must move as a single unit across every file."""
    for path in default_config_dir().glob("*.yaml"):
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert document["version"] == config.version, f"{path.name} is out of version lock-step"


def test_every_typology_is_cited(config) -> None:
    """No performance value may ship without a source (decision D-012).

    Checked on the RESOLVED library, because values are inherited: the question
    is whether the numbers a typology reports are cited, not whether the file
    that names it happens to carry a citation of its own.
    """
    for typology in config.typologies.resolved:
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
    for typology in config.typologies.resolved:
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
        archetype.archetype
        for archetype in config.typologies.archetypes
        if archetype.evidence_confidence == "low"
    }
    assert {
        "green_facade_living_wall",
        "bioretention",
        "enclosed_courtyard",
        # The classes retrieved or derived for 2026.08.04 whose evidence is
        # thin by construction, and must stay declared as such (D-044).
        "vegetated_shade_structure",
        "productive_canopy",
        "productive_non_canopy",
    } <= low_confidence


def test_no_default_costs_are_shipped(config) -> None:
    """The cost policy (Methodology Report 5.8) must hold in configuration."""
    assert config.country_defaults["countries"] in (None, {}), (
        "country_defaults must ship no cost or emission values until each is verified"
    )
    serialised = yaml.safe_dump(config.typologies.model_dump())
    assert "cost_per_m2" not in serialised, "typology library must not carry default unit costs"


def test_lookup_by_type(config) -> None:
    """Lookup returns the resolved entry, carrying its archetype's values."""
    woodland = config.typologies.by_type("urban_woodland_site")
    assert woodland.archetype == "dense_tree_canopy"
    assert woodland.base_cooling_score == 90
    # D-043.4: the site reading is kept and its minimum area is unmoved.
    assert woodland.suitability.minimum_site_area_m2 == 2000
    with pytest.raises(ConfigError, match="unknown nbs_type"):
        config.typologies.by_type("teleportation_grove")
    with pytest.raises(ConfigError, match="unknown archetype"):
        config.typologies.archetype_by_name("teleportation")


def test_missing_configuration_directory_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="missing configuration file"):
        load_config(config_dir=tmp_path)


def test_unknown_citation_is_rejected(tmp_path: Path, config) -> None:
    """A citation pointing at an unrecorded source must fail the load."""
    for path in default_config_dir().glob("*.yaml"):
        (tmp_path / path.name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

    library = yaml.safe_load((tmp_path / "nbs_typologies.yaml").read_text(encoding="utf-8"))
    library["archetypes"][0]["sources"].append(
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


def test_non_dated_version_is_rejected() -> None:
    with pytest.raises(ValueError, match="date-stamped"):
        TypologyLibrary.model_validate({**_library(), "version": "v1.2"})


def test_duplicate_identifiers_are_rejected() -> None:
    payload = _typology_payload()
    with pytest.raises(ValueError, match="duplicate"):
        TypologyLibrary.model_validate(_library(typologies=[payload, payload]))
    archetype = _archetype_payload()
    with pytest.raises(ValueError, match="duplicate archetype"):
        TypologyLibrary.model_validate(_library([archetype, archetype]))


def test_non_mapping_yaml_is_rejected(tmp_path: Path) -> None:
    for path in default_config_dir().glob("*.yaml"):
        (tmp_path / path.name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "weights.yaml").write_text("- just\n- a\n- list\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="YAML mapping"):
        load_config(config_dir=tmp_path)


def test_missing_bibliography_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="missing bibliography"):
        bibliography_keys(path=tmp_path / "nowhere.md")


def test_get_config_is_cached() -> None:
    from nature_cooling.engine.config import get_config

    assert get_config() is get_config()


def _archetype_payload(**overrides: object) -> dict:
    payload = {
        "archetype": "payload_class",
        "display_name": "Payload class",
        "provenance": "existing",
        "category": "green",
        "base_cooling_score": 50,
        "temp_reduction_min_c": 0.1,
        "temp_reduction_max_c": 1.0,
        "evidence_confidence": "low",
        "building_energy_applicable": False,
        "suitability": {
            "minimum_site_area_m2": 10,
            "requires_soil": "none",
            "requires_irrigation": "none",
            "unsuitable_climate_zones": [],
        },
        "co_benefit_defaults": {},
        "sources": [{"key": "bowler2010", "finding": "x"}],
    }
    payload.update(overrides)
    return payload


def _typology_payload(**overrides: object) -> dict:
    payload = {
        "nbs_id": "97",
        "nbs_type": "payload",
        "display_name": "Payload",
        "archetype": "payload_class",
        "family": "tree_based",
        "kind": "element",
        "primary_cooling_mechanism": "none",
        "availability": {"scales": ["site"], "land_uses": "all"},
    }
    payload.update(overrides)
    return payload


def _library(archetypes: list[dict] | None = None, typologies: list[dict] | None = None) -> dict:
    return {
        "version": "2026.08.04",
        "archetypes": archetypes if archetypes is not None else [_archetype_payload()],
        "typologies": typologies if typologies is not None else [_typology_payload()],
    }


def test_uncited_archetype_is_rejected() -> None:
    """An evidence class with no citation cannot exist (D-012, D-017)."""
    with pytest.raises(ValueError):
        TypologyLibrary.model_validate(_library([_archetype_payload(sources=[])]))


def test_inverted_temperature_envelope_is_rejected() -> None:
    with pytest.raises(ValueError, match="must be >="):
        TypologyLibrary.model_validate(
            _library([_archetype_payload(temp_reduction_min_c=2.0, temp_reduction_max_c=0.5)])
        )


def test_typology_naming_an_unknown_archetype_is_rejected() -> None:
    """A dangling inheritance must fail at load, not at scoring time."""
    with pytest.raises(ValueError, match="unknown archetypes"):
        TypologyLibrary.model_validate(
            _library(typologies=[_typology_payload(archetype="no_such_class")])
        )


def test_an_archetype_nothing_inherits_from_is_rejected() -> None:
    """An unused evidence class is a citation with no consumer."""
    with pytest.raises(ValueError, match="no typology inherits"):
        TypologyLibrary.model_validate(
            _library([_archetype_payload(), _archetype_payload(archetype="orphan")])
        )


def test_availability_naming_an_unknown_land_use_is_rejected() -> None:
    """The availability matrix and the land-use enumeration must not drift."""
    with pytest.raises(ValueError, match="unknown land uses"):
        TypologyLibrary.model_validate(
            _library(
                typologies=[
                    _typology_payload(availability={"scales": ["site"], "land_uses": ["atlantis"]})
                ]
            )
        )


def test_suitability_overrides_replace_only_what_they_name(config) -> None:
    """Inheritance with evidence-based overrides only (D-044.3).

    A microforest borrows the dense-canopy cooling evidence but not its 2 000 m2
    woodland footprint, because the source describes a small patch on a
    constrained site. Everything the override does not name is still inherited.
    """
    microforest = config.typologies.by_type("microforest")
    dense = config.typologies.archetype_by_name("dense_tree_canopy")
    assert microforest.archetype == "dense_tree_canopy"
    assert microforest.suitability_inherited is False
    assert microforest.suitability.minimum_site_area_m2 == 200
    assert dense.suitability.minimum_site_area_m2 == 2000
    assert microforest.suitability.requires_soil == dense.suitability.requires_soil
    assert microforest.temp_reduction_max_c == dense.temp_reduction_max_c


def test_most_entries_inherit_their_suitability_unchanged(config) -> None:
    """Overrides are the exception, and the test says how exceptional.

    Inventing a minimum area for each of 110 entries would manufacture
    precision the catalogue does not contain (D-044.3), so the override list is
    deliberately small; if it grows large, that ruling has quietly been
    abandoned and this test should be the thing that notices.
    """
    overridden = [t.nbs_type for t in config.typologies.resolved if not t.suitability_inherited]
    assert len(overridden) <= 25, f"{len(overridden)} entries override suitability: {overridden}"


def test_an_output_caveat_without_text_is_rejected(tmp_path: Path) -> None:
    """A caveat the evidence requires must have something to say."""
    for path in default_config_dir().glob("*.yaml"):
        (tmp_path / path.name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    library = yaml.safe_load((tmp_path / "nbs_typologies.yaml").read_text(encoding="utf-8"))
    library["archetypes"][0]["output_caveats"] = ["a_caveat_with_no_text"]
    (tmp_path / "nbs_typologies.yaml").write_text(yaml.safe_dump(library), encoding="utf-8")

    with pytest.raises(ConfigError, match="no text in recommendation_templates"):
        load_config(config_dir=tmp_path)


def test_default_paths_prefer_the_repository_checkout() -> None:
    """In a checkout, the live repository files win over any bundled copy."""
    from nature_cooling.engine import config as config_module

    assert config_module.default_config_dir() == config_module.repo_root() / "config"
    assert (
        config_module.default_bibliography_path()
        == config_module.repo_root() / "docs" / "methodology" / "BIBLIOGRAPHY.md"
    )


def test_default_paths_fall_back_to_the_bundled_wheel_data(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """An installed wheel has no repository around it; the embedded data serves (D-035)."""
    from nature_cooling.engine import config as config_module

    monkeypatch.setattr(config_module, "repo_root", lambda: tmp_path)
    bundled = config_module.bundled_data_dir()
    assert bundled.name == "_bundled"
    assert config_module.default_config_dir() == bundled / "config"
    assert config_module.default_bibliography_path() == bundled / "BIBLIOGRAPHY.md"
