"""The bundled-dataset licence gate (v2.1 brief, Gates).

Two datasets now ship inside the wheel, and one of them ships under a licence
that *requires* attribution. Until this release the repository's licence
notices were maintained by hand and checked by nobody — the font OFL texts have
never had a test. That was tolerable while the only redistributed third-party
content was three typefaces added once. It stops being tolerable when a build
script copies a directory: a `cp` that silently stops copying, or a dataset
added without its notice, is a licence breach that no other gate would catch.

So this file asserts the boring things: that every bundled dataset is present,
that its licence text travels with it, that the attribution CC BY 4.0 requires
is actually written down in the places that claim to carry it, and that what
`NOTICE` says about the datasets matches what is on disk.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from nature_cooling.engine.config import default_geo_data_dir, repo_root
from nature_cooling.geo import load_countries, load_koppen, load_places

# Every file the geographic datasets consist of, and what it is for.
REQUIRED_FILES = {
    "countries.json.z": "the 1:50m country boundaries the lookup reads",
    "basemap.json": "the 1:110m outlines the offline basemap draws",
    "koppen_geiger.json": "the climate grid's metadata and legend",
    "koppen_geiger_1991_2020_0p1.bin.z": "the climate class grid itself",
    "places.json.z": "the populated-places index the offline search reads (v2.2)",
    "LICENCE-naturalearth.txt": "Natural Earth's terms of use",
    "LICENCE-koppen-CC-BY-4.0.txt": "the CC BY 4.0 text the climate grid ships under",
    "ATTRIBUTION.md": "what each dataset is, what was changed, and under what licence",
}


@pytest.mark.parametrize(("filename", "purpose"), sorted(REQUIRED_FILES.items()))
def test_every_bundled_dataset_file_is_present_and_not_empty(filename: str, purpose: str) -> None:
    path = default_geo_data_dir() / filename
    assert path.is_file(), f"missing {filename}: {purpose}"
    assert path.stat().st_size > 0, f"empty {filename}: {purpose}"


def test_no_undeclared_file_ships_in_the_dataset_directory() -> None:
    """A dataset added without a licence notice is the failure this catches."""
    present = {path.name for path in default_geo_data_dir().iterdir() if path.is_file()}
    assert present == set(REQUIRED_FILES), (
        "every file shipped in data/geo/ must be declared here, with its purpose, "
        "so that adding a dataset forces a decision about its licence"
    )


def test_the_climate_grid_carries_the_attribution_its_licence_requires() -> None:
    """CC BY 4.0 is not public domain: attribution is a condition of the grant."""
    grid = load_koppen()
    assert grid.licence == "CC BY 4.0"
    for required in ("Beck", "2023", "Scientific Data", "10.1038/s41597-023-02549-6"):
        assert required in grid.attribution, required


def test_the_licence_files_carry_the_real_licence_text_not_a_summary() -> None:
    directory = default_geo_data_dir()

    cc_by = (directory / "LICENCE-koppen-CC-BY-4.0.txt").read_text(encoding="utf-8")
    assert "Creative Commons Attribution 4.0 International Public License" in cc_by
    assert "Section 3 -- License Conditions" in cc_by
    assert "10.1038/s41597-023-02549-6" in cc_by, "and names the work it applies to"

    natural_earth = (directory / "LICENCE-naturalearth.txt").read_text(encoding="utf-8")
    assert "public domain" in natural_earth
    assert "No permission is needed to use Natural Earth" in natural_earth


def test_the_notice_file_names_both_datasets_and_their_licences() -> None:
    """NOTICE is the repository-level roll-up; it must agree with the data."""
    notice = (repo_root() / "NOTICE").read_text(encoding="utf-8")
    assert "Natural Earth" in notice
    assert "Köppen-Geiger" in notice or "Koppen-Geiger" in notice
    assert "CC BY 4.0" in notice
    assert "10.1038/s41597-023-02549-6" in notice
    for filename in ("LICENCE-naturalearth.txt", "LICENCE-koppen-CC-BY-4.0.txt"):
        assert filename in notice, f"NOTICE must point at {filename}"


def test_the_attribution_document_states_what_was_changed() -> None:
    """Neither bundled file is the publisher's original, and saying so is part
    of redistributing honestly — CC BY 4.0 requires indicating modifications."""
    attribution = (default_geo_data_dir() / "ATTRIBUTION.md").read_text(encoding="utf-8")
    assert "What was changed" in attribution
    assert "tools/build_datasets.py" in attribution
    assert "1991-2020" in attribution or "1991–2020" in attribution


def test_the_datasets_declare_the_bibliography_keys_the_methodology_cites(config) -> None:
    """The report cites a source key; the dataset must be that same source."""
    assert load_koppen().source_key == "beck2023"
    assert load_countries().source_key == "naturalearth"
    assert load_places().source_key == "naturalearth"
    table = config.climate_classification
    assert table["koppen_to_zone"]["source_dataset"] == "beck2023"
    assert table["country_lookup"]["source_dataset"] == "naturalearth"


def test_the_grid_matches_the_checksum_its_metadata_records() -> None:
    """The metadata's checksum is what makes 'derived from the published
    archive' a checkable claim rather than an assertion."""
    import hashlib

    directory = default_geo_data_dir()
    meta = json.loads((directory / "koppen_geiger.json").read_text(encoding="utf-8"))
    payload = (directory / meta["grid_file"]).read_bytes()
    assert hashlib.sha256(payload).hexdigest() == meta["grid_sha256"]
    assert len(payload) == meta["grid_bytes"]


def test_the_bundled_data_stays_small_enough_to_ship() -> None:
    """The datasets travel inside the wheel and the container image.

    The ceiling is generous and exists to catch a mistake in kind — the 1 km
    climate layer or the 1:10m boundary set landing here by accident — rather
    than to police kilobytes.
    """
    total = sum(path.stat().st_size for path in default_geo_data_dir().iterdir())
    assert total < 2_000_000, f"bundled geographic data is {total} bytes"


def test_the_build_script_stages_the_datasets_into_the_wheel() -> None:
    """An installed wheel has no repository around it, so the `cp` is the only
    thing standing between a released package and a missing dataset."""
    script = (repo_root() / "tools" / "build_wheel.sh").read_text(encoding="utf-8")
    assert 'cp -r "$root/data" "$bundled/data"' in script


def test_a_wheel_layout_resolves_the_datasets_from_the_bundled_copy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The repository-first resolver must fall back, or an installed wheel
    silently has no map."""
    from nature_cooling.engine import config as config_module

    monkeypatch.setattr(config_module, "repo_root", lambda: tmp_path / "no-repo-here")
    monkeypatch.setattr(config_module, "bundled_data_dir", lambda: tmp_path / "_bundled")
    assert config_module.default_geo_data_dir() == tmp_path / "_bundled" / "data" / "geo"


def test_the_attribution_document_covers_the_place_index() -> None:
    """A dataset added without its attribution section is the failure the
    licence gate exists to catch (v2.1 brief, Gates; extended by D-049.6)."""
    attribution = (default_geo_data_dir() / "ATTRIBUTION.md").read_text(encoding="utf-8")
    assert "Populated places" in attribution
    assert "places.json.z" in attribution
    assert "fills in no answer" in attribution


def test_the_notice_file_names_the_place_index() -> None:
    notice = (repo_root() / "NOTICE").read_text(encoding="utf-8")
    assert "Populated Places" in notice


# ---- the redistributed map library (v2.2, D-049.5) ----
#
# Leaflet ships inside the wheel as part of the frontend bundle — the first
# runtime dependency beyond React and react-router — so the licence gate
# extends over it exactly as it covers the fonts and the datasets: the BSD-2
# text must travel with the build, and NOTICE must say so.


def test_the_map_library_ships_with_its_licence_text() -> None:
    licence = repo_root() / "frontend" / "public" / "LICENCE-leaflet.txt"
    assert licence.is_file(), "Leaflet's BSD-2 text must ship beside the build (D-049.5)"
    text = licence.read_text(encoding="utf-8")
    assert "BSD 2-Clause License" in text
    assert "Volodymyr Agafonkin" in text


def test_the_notice_file_names_the_map_library() -> None:
    notice = (repo_root() / "NOTICE").read_text(encoding="utf-8")
    assert "Leaflet" in notice
    assert "BSD 2-Clause" in notice
    assert "LICENCE-leaflet.txt" in notice


def test_the_map_library_is_the_declared_dependency_not_a_vendored_copy() -> None:
    """The licence text must describe what is actually bundled: the package
    named in package.json, not a drifted vendored snapshot."""
    import re

    package_json = json.loads(
        (repo_root() / "frontend" / "package.json").read_text(encoding="utf-8")
    )
    declared = package_json["dependencies"]
    assert "leaflet" in declared
    # The frontend's runtime dependencies stay enumerable and deliberate
    # (D-048.5's spirit survives D-049.5): React, its DOM binding, the router,
    # and the map library. A fifth entry here is a decision, not an accident.
    assert set(declared) == {"react", "react-dom", "react-router", "leaflet"}
    assert re.match(r"[\^~]?1\.", declared["leaflet"])


def test_no_openstreetmap_data_is_bundled() -> None:
    """D-049.7: the package contains no ODbL content. The datasets directory
    must never quietly gain an OSM extract — a tile source is configured at
    runtime and requested by the browser, never redistributed."""
    for path in default_geo_data_dir().iterdir():
        if path.suffix in {".txt", ".md"}:
            continue
        head = path.read_bytes()[:4096].lower()
        assert b"openstreetmap" not in head, path.name
