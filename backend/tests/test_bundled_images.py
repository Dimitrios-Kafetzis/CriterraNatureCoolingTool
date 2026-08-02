"""The bundled-content licence gate, extended over the example images (v2.3, D-051).

The images are the third body of third-party content to ship inside the wheel,
after the report typefaces and the geographic datasets — and the first whose
licences vary per file. "Wikimedia Commons" is not a licence: every file
carries its own, and the acceptable set is public domain / CC0, CC BY and
CC BY-SA only (this is a commercial product; displaying an unmodified image
with attribution satisfies all three). NC and ND variants are excluded
outright, and this file is where that exclusion is *proved* over the shipped
manifest rather than remembered.

So, in the manner of test_bundled_datasets.py: every shipped file is declared,
every declared image exists and matches its recorded checksum, every licence
is in the accepted set, the attribution document covers every image and states
the coverage honestly, and the whole directory stays inside its size budget.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from nature_cooling.engine.config import MethodologyConfig, default_images_dir, repo_root
from nature_cooling.images import (
    ImageDataError,
    NbsExampleImage,
    image_file_path,
    load_image_manifest,
)

# The ceiling the v2.3 brief sets for everything in data/images/ — images,
# manifest, attribution document. It exists to keep the wheel shippable, and
# like the geo-data ceiling it catches a mistake in kind (an original
# committed un-encoded) rather than policing kilobytes.
TOTAL_BUDGET_BYTES = 5_000_000

# Per-file licence allowlist (D-051.3). Extending this set is a licensing
# decision, not an edit.
ACCEPTED_LICENCES = {
    "public domain",
    "CC0 1.0",
    "CC BY 2.0",
    "CC BY 2.5",
    "CC BY 3.0",
    "CC BY 4.0",
    "CC BY-SA 2.0",
    "CC BY-SA 2.5",
    "CC BY-SA 3.0",
    "CC BY-SA 4.0",
}

ZONES = {"tropical_wet", "tropical_dry", "arid", "semi_arid", "temperate", "other"}


def _manifest_document() -> dict[str, Any]:
    return json.loads(  # type: ignore[no-any-return]
        (default_images_dir() / "manifest.json").read_text(encoding="utf-8")
    )


def _images() -> list[dict[str, Any]]:
    return list(_manifest_document()["images"])


def test_every_shipped_file_is_declared_and_every_declared_file_ships() -> None:
    """A photograph added without a manifest entry — or an entry whose file was
    lost — is the failure the licence gate exists to catch."""
    directory = default_images_dir()
    on_disk = {path.name for path in directory.iterdir() if path.is_file()}
    declared = {image["file"] for image in _images()}
    assert declared | {"manifest.json", "ATTRIBUTION.md"} == on_disk, (
        "every file in data/images/ must be a manifest-declared image, the manifest, "
        "or the attribution document — adding anything else is a licensing decision"
    )


@pytest.mark.parametrize("image", _images(), ids=lambda image: str(image["file"]))
def test_every_image_carries_an_accepted_licence(image: dict[str, Any]) -> None:
    """Per file, never per source: NC and ND variants are provably absent."""
    licence = image["licence"]
    assert licence in ACCEPTED_LICENCES, f"{image['file']}: licence {licence!r} not accepted"
    assert "NC" not in licence and "ND" not in licence


@pytest.mark.parametrize("image", _images(), ids=lambda image: str(image["file"]))
def test_every_image_carries_its_attribution(image: dict[str, Any]) -> None:
    """Author, licence and a source link are what the interface must render
    (D-051.3), so an empty field here is a blank credit on screen."""
    for field in ("author", "licence", "source_page", "place", "caption_subject"):
        assert image[field], f"{image['file']}: empty {field}"
    assert image["source_page"].startswith("https://")
    for field in ("original_sha256", "file_sha256"):
        assert len(image[field]) == 64, f"{image['file']}: {field} is not a SHA-256"


@pytest.mark.parametrize("image", _images(), ids=lambda image: str(image["file"]))
def test_every_image_matches_its_recorded_checksum(image: dict[str, Any]) -> None:
    """The checksum is what makes 'derived from the recorded source' a
    checkable claim rather than an assertion."""
    payload = (default_images_dir() / image["file"]).read_bytes()
    assert hashlib.sha256(payload).hexdigest() == image["file_sha256"]
    assert len(payload) == image["file_bytes"]


@pytest.mark.parametrize("image", _images(), ids=lambda image: str(image["file"]))
def test_every_image_records_its_three_verifications(image: dict[str, Any]) -> None:
    """What each verification found is recorded per image (D-051.4): the
    licence as read from the file page, the depiction as seen, and the zone as
    reproduced from the tool's own bundled grid."""
    verified = image["verified"]
    assert verified["licence"], image["file"]
    assert verified["depiction"], image["file"]
    assert "bundled" in verified["zone"], image["file"]
    assert image["koppen_class"], image["file"]


def test_every_image_attaches_to_a_real_slot(config: MethodologyConfig) -> None:
    """Images inherit as suitability does (D-044.3, D-051.1): the archetype
    must exist, an override must name a real typology of that same archetype,
    and one slot holds at most one image."""
    archetypes = {archetype.archetype for archetype in config.typologies.archetypes}
    by_type = {typology.nbs_type: typology.archetype for typology in config.typologies.typologies}
    seen: set[tuple[str, str]] = set()
    for image in _images():
        assert image["archetype"] in archetypes, image["file"]
        assert image["zone"] in ZONES, image["file"]
        if image["nbs_type"] is not None:
            assert by_type[image["nbs_type"]] == image["archetype"], (
                f"{image['file']}: override {image['nbs_type']!r} does not inherit "
                f"{image['archetype']!r} — the picture would claim an inheritance the "
                "library does not state"
            )
        slot = (image["nbs_type"] or image["archetype"], image["zone"])
        assert slot not in seen, f"duplicate slot {slot}"
        seen.add(slot)


def test_the_attribution_document_covers_every_image_and_states_coverage() -> None:
    """The attribution document is generated from the same record as the
    manifest, and must name every shipped file, its licence, and the honest
    coverage count — filled and empty slots alike (D-051.4)."""
    attribution = (default_images_dir() / "ATTRIBUTION.md").read_text(encoding="utf-8")
    images = _images()
    for image in images:
        assert image["file"] in attribution
        assert image["author"] in attribution
    assert "## Coverage" in attribution
    archetype_level = sum(1 for image in images if image["nbs_type"] is None)
    overrides = len(images) - archetype_level
    assert f"{archetype_level} of 108" in attribution
    assert f"{overrides} per-typology" in attribution
    assert "illustrative examples, not evidence" in attribution
    assert "tools/build_images.py" in attribution


def test_the_notice_file_names_the_example_images() -> None:
    notice = (repo_root() / "NOTICE").read_text(encoding="utf-8")
    assert "example images" in notice.lower()
    assert "data/images/ATTRIBUTION.md" in notice


def test_the_bundled_images_stay_inside_their_budget() -> None:
    """~800 px WebP re-encodes run 30–90 KB; the ceiling catches an original
    committed un-encoded, which is a mistake in kind."""
    total = sum(path.stat().st_size for path in default_images_dir().iterdir())
    assert total < TOTAL_BUDGET_BYTES, f"bundled example images total {total} bytes"


def test_no_openstreetmap_content_ships_among_the_images() -> None:
    """D-049.7 extends here unchanged: nothing ODbL-licensed enters the wheel,
    and a map screenshot smuggled in as an 'example photo' would be exactly
    that. The manifest's licence allowlist already excludes ODbL; this checks
    the recorded source pages point nowhere near a tile server."""
    for image in _images():
        assert "openstreetmap" not in image["source_page"].lower(), image["file"]
        assert "tile" not in image["file"], image["file"]


# ---- the loader the routes read (nature_cooling/images.py) ----


def test_the_loader_round_trips_the_manifest() -> None:
    manifest = load_image_manifest()
    document = _manifest_document()
    assert manifest.purpose == document["purpose"]
    assert len(manifest.images) == len(document["images"])
    first = manifest.images[0]
    assert isinstance(first, NbsExampleImage)
    assert image_file_path(first.file) == default_images_dir() / first.file


def test_a_missing_manifest_is_an_empty_manifest_not_an_error(tmp_path: Path) -> None:
    """Zero coverage is an expected state of this feature; the honest answer
    is an empty manifest and no affordance, not a 500 (D-051.4)."""
    manifest = load_image_manifest(tmp_path / "nowhere")
    assert manifest.images == ()
    assert manifest.purpose == ""
    assert image_file_path("anything.webp", tmp_path / "nowhere") is None


def test_a_corrupt_manifest_is_a_real_defect_and_raises(tmp_path: Path) -> None:
    (tmp_path / "manifest.json").write_text("not json", encoding="utf-8")
    with pytest.raises(ImageDataError, match="invalid JSON"):
        load_image_manifest(tmp_path)

    top_level = tmp_path / "list"
    top_level.mkdir()
    (top_level / "manifest.json").write_text("[]", encoding="utf-8")
    with pytest.raises(ImageDataError, match="JSON object"):
        load_image_manifest(top_level)

    incomplete = tmp_path / "incomplete"
    incomplete.mkdir()
    (incomplete / "manifest.json").write_text(
        json.dumps({"images": [{"file": "x.webp"}]}), encoding="utf-8"
    )
    with pytest.raises(ImageDataError, match="missing"):
        load_image_manifest(incomplete)


def test_a_declared_but_absent_file_resolves_to_none(tmp_path: Path) -> None:
    """The manifest names it, the disk lacks it: answered like a missing
    image, never a traversal opportunity."""
    document = {
        "purpose": "test",
        "images": [dict(_images()[0], file="gone.webp")],
    }
    (tmp_path / "manifest.json").write_text(json.dumps(document), encoding="utf-8")
    assert image_file_path("gone.webp", tmp_path) is None
    assert image_file_path("undeclared.webp", tmp_path) is None


def test_the_wheel_stages_the_images_with_the_data_directory() -> None:
    """The same `cp -r data` that carries the geographic datasets carries the
    images; a wheel layout resolves them from the bundled copy."""
    script = (repo_root() / "tools" / "build_wheel.sh").read_text(encoding="utf-8")
    assert 'cp -r "$root/data" "$bundled/data"' in script


def test_a_wheel_layout_resolves_the_images_from_the_bundled_copy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from nature_cooling.engine import config as config_module

    monkeypatch.setattr(config_module, "repo_root", lambda: tmp_path / "no-repo-here")
    monkeypatch.setattr(config_module, "bundled_data_dir", lambda: tmp_path / "_bundled")
    assert config_module.default_images_dir() == tmp_path / "_bundled" / "data" / "images"
