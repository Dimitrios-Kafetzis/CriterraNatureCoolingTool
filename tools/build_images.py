#!/usr/bin/env python3
"""Derive the bundled NbS example images from their curated sources (v2.3, D-051).

This script runs ONCE, offline, by hand — the tools/build_datasets.py
arrangement applied to photographs. Its outputs are committed to
``data/images/`` and are what the tool actually serves. Nothing in the
application, the test suite or CI invokes it, and the shipped package never
requests an image from anywhere but itself (D-049.1): bundling is the whole
point, because hotlinking upload.wikimedia.org at click-time would be a
third-party request from the default build, and is against Wikimedia's own
hotlinking guidance besides.

The curation record is ``tools/image_sources.json``. Every entry names the
slot the image fills — an (archetype, climate zone) pair, or a per-typology
override where a verified photo shows something visually distinct from its
archetype (the D-044.3 inherit-with-override pattern, applied to pictures) —
and carries the three verifications D-051.4 requires before anything ships:

  (a) LICENCE, read from the actual file page, never from a search result or
      category listing. "Wikimedia Commons" is not a licence; every file
      carries its own. Acceptable: public domain / CC0, CC BY, CC BY-SA.
      NC and ND variants are excluded outright, as is any file whose
      licensing is unclear on its own page. The reading is recorded per
      image in ``verified.licence``.
  (b) DEPICTION, confirmed by looking at the image. A photo captioned
      "green roof" that shows a lawn does not ship. The looking is recorded
      per image in ``verified.depiction``.
  (c) CLIMATE ZONE, verified by this script rather than recorded on trust:
      the image's coordinates (geotag, or a location stated on the file
      page) are run through the tool's OWN bundled Köppen–Geiger grid and
      methodology mapping table, and an entry whose recorded zone does not
      reproduce from the tool's own data REFUSES to build. The feature's
      honesty is checked by the same data the feature serves.

What the script does with a verified entry: downloads the original once,
checks it against the recorded SHA-256 (``--record`` fills the checksum in on
first fetch), re-encodes to a WebP no wider than IMAGE_MAX_EDGE pixels with
metadata stripped (provenance lives in the manifest, not in EXIF), and writes
``data/images/manifest.json`` plus ``data/images/ATTRIBUTION.md`` — the
attribution document, including the honest coverage table of filled and
empty slots. Partial coverage is expected: a slot that cannot be filled
honestly stays empty, and the interface shows no affordance for it.

    backend/.venv/bin/python tools/build_images.py            # verify + build
    backend/.venv/bin/python tools/build_images.py --record   # fill in checksums

Requires Pillow (not a dependency of the tool; it exists only to re-encode
here) and the backend package for the Köppen lookup. The committed runtime
artefacts are WebP files and JSON, read by the stdlib.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "data" / "images"
SOURCES_PATH = REPO_ROOT / "tools" / "image_sources.json"

sys.path.insert(0, str(REPO_ROOT / "backend" / "src"))

# The total ceiling the licence gate enforces (the geo-data ceiling pattern):
# everything in data/images/ — images, manifest, attribution document — must
# fit a wheel-friendly budget. ~800 px WebP photographs run 30–90 KB each,
# so the budget holds roughly fifty to a hundred images; the constraint is
# curation honesty long before it is bytes.
TOTAL_BUDGET_BYTES = 5_000_000

# Longest edge of the re-encoded image. Large enough to read a landscape
# photograph in a dialog, small enough that fifty of them fit the budget.
IMAGE_MAX_EDGE = 800
WEBP_QUALITY = 78

# The six climate zones, exactly as the questionnaire offers them. An image
# slot is (archetype-or-override, zone); the affordance appears only on a
# strict zone match (D-051.5) — no cross-zone substitution.
ZONES = ("tropical_wet", "tropical_dry", "arid", "semi_arid", "temperate", "other")

# Per-file licence allowlist (D-051.3). This is a commercial product, so only
# licences permitting commercial redistribution with attribution qualify; NC
# and ND variants never appear here and the gate asserts their absence again
# over the shipped manifest.
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

COMMONS_API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = (
    "CriterraNatureCoolingTool-image-curation/1.0 "
    "(https://github.com/dkafetzis/CriterraNatureCoolingTool)"
)


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()  # type: ignore[no-any-return]


def _commons_original_url(title: str) -> str:
    """Resolve a Commons file title to its original-file URL via the API."""
    query = urllib.parse.urlencode(
        {
            "action": "query",
            "titles": title,
            "prop": "imageinfo",
            "iiprop": "url",
            "format": "json",
        }
    )
    document = json.loads(_fetch(f"{COMMONS_API}?{query}"))
    pages = document["query"]["pages"]
    (page,) = pages.values()
    if "imageinfo" not in page:
        raise SystemExit(f"{title}: no such file on Commons")
    return str(page["imageinfo"][0]["url"])


def _slot_of(entry: dict[str, Any]) -> tuple[str, str]:
    return (entry.get("nbs_type") or entry["archetype"], entry["zone"])


def _slug(entry: dict[str, Any]) -> str:
    return f"{entry.get('nbs_type') or entry['archetype']}--{entry['zone']}"


def _validate_entry(entry: dict[str, Any], archetypes: set[str], nbs_types: set[str]) -> None:
    slug = _slug(entry)
    if entry["archetype"] not in archetypes:
        raise SystemExit(f"{slug}: unknown archetype {entry['archetype']!r}")
    if entry.get("nbs_type") is not None and entry["nbs_type"] not in nbs_types:
        raise SystemExit(f"{slug}: unknown nbs_type {entry['nbs_type']!r}")
    if entry["zone"] not in ZONES:
        raise SystemExit(f"{slug}: unknown climate zone {entry['zone']!r}")
    licence = entry["licence"]
    if licence not in ACCEPTED_LICENCES:
        raise SystemExit(f"{slug}: licence {licence!r} is not in the accepted set")
    for fragment in ("NC", "ND"):
        if fragment in licence:
            raise SystemExit(f"{slug}: {licence!r} is a {fragment} variant and never ships")
    for key in ("source_page", "author", "place", "caption_subject", "coordinates_from"):
        if not entry.get(key):
            raise SystemExit(f"{slug}: missing {key}")
    verified = entry.get("verified") or {}
    for check in ("licence", "depiction"):
        if not verified.get(check):
            raise SystemExit(
                f"{slug}: verification note {check!r} is empty — an unverified image "
                "does not ship (D-051.4)"
            )


def _verify_zone(entry: dict[str, Any], config: Any, grid: Any) -> str:
    """Run the entry's coordinates through the tool's own climate data (c)."""
    from nature_cooling.geo.lookup import look_up_climate

    climate = look_up_climate(entry["latitude"], entry["longitude"], config, grid)
    if climate.zone != entry["zone"]:
        raise SystemExit(
            f"{_slug(entry)}: recorded zone {entry['zone']!r} does not reproduce from "
            f"the bundled grid — ({entry['latitude']}, {entry['longitude']}) is "
            f"{climate.koppen_class} -> {climate.zone!r}. The image does not ship."
        )
    return str(climate.koppen_class)


def _encode(payload: bytes) -> tuple[bytes, int, int]:
    from PIL import Image, ImageOps

    image = Image.open(io.BytesIO(payload))
    image = ImageOps.exif_transpose(image)
    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")
    image.thumbnail((IMAGE_MAX_EDGE, IMAGE_MAX_EDGE))
    out = io.BytesIO()
    # No EXIF, no ICC: provenance lives in the manifest, and a stripped
    # re-encode is also what keeps fifty photographs inside the budget.
    image.save(out, format="WEBP", quality=WEBP_QUALITY, method=6)
    return out.getvalue(), image.width, image.height


def _attribution_document(manifest: dict[str, Any], archetype_names: dict[str, str]) -> str:
    """The attribution document, generated so it cannot drift from the manifest."""
    images: list[dict[str, Any]] = manifest["images"]
    by_slot = {(image["nbs_type"] or image["archetype"], image["zone"]): image for image in images}

    lines = [
        "# Bundled NbS example images",
        "",
        "<!-- GENERATED by tools/build_images.py from tools/image_sources.json.",
        "     Do not edit by hand: rerun the script. -->",
        "",
        "Each intervention card in the picker can show one photograph of a real",
        "implementation of that kind of NbS, matched to the project's climate zone.",
        "The photographs ship inside the package (D-049.1: the default build makes",
        "no third-party request, and hotlinking Wikimedia's servers is against",
        "their own guidance). They are **illustrative examples, not evidence**:",
        "no methodology value, score, or stored result derives from any image,",
        "and captions state place and climate zone only — never degrees,",
        "performance, or cost (D-051.6).",
        "",
        "Images attach at (cooling archetype × climate zone), inherited by the",
        "catalogue entries exactly as their performance values are (D-044,",
        "D-051.1), with per-typology overrides only where a verified photo shows",
        "something visually distinct from its archetype. A slot with no honestly",
        "verified image stays empty and shows no affordance — absence is the",
        "honest state, not a placeholder.",
        "",
        "Every image passed three verifications before shipping (D-051.4):",
        "the **licence** was read from the actual source file page (never from a",
        "search result); the image was **looked at** and confirmed to depict that",
        "NbS; and the **climate zone** was verified by running the photograph's",
        "coordinates through the tool's own bundled Köppen–Geiger grid and",
        "methodology mapping table — `tools/build_images.py` refuses to build an",
        "entry whose zone does not reproduce. What each verification found is",
        "recorded below.",
        "",
        "Licences are per file: public domain / CC0, CC BY, or CC BY-SA only.",
        "No NC or ND variant ships, and no file whose licensing was unclear on",
        "its own page. Attribution (author, licence, link to the source page) is",
        "rendered in the interface wherever an image is shown, and repeated here.",
        "",
        "## Coverage",
        "",
        f"{sum(1 for image in images if image['nbs_type'] is None)} of "
        f"{18 * len(ZONES)} (archetype × zone) slots are filled, plus "
        f"{sum(1 for image in images if image['nbs_type'] is not None)} per-typology "
        "override images. An empty cell means no verified photograph of that",
        "archetype in that zone has been found yet — the interface shows no",
        "affordance there. An 'override only' cell serves exactly the named",
        "typology; the archetype's other entries in that zone still show nothing.",
        "",
    ]

    header = "| Archetype | " + " | ".join(zone.replace("_", " ") for zone in ZONES) + " |"
    lines += [header, "|" + "---|" * (len(ZONES) + 1)]
    for archetype, display in archetype_names.items():
        cells = []
        for zone in ZONES:
            filled = (archetype, zone) in by_slot
            override = any(
                image["nbs_type"] is not None
                and image["archetype"] == archetype
                and image["zone"] == zone
                for image in images
            )
            if filled and override:
                cells.append("✓ +override")
            elif filled:
                cells.append("✓")
            elif override:
                cells.append("override only")
            else:
                cells.append("—")
        lines.append(f"| {display} | " + " | ".join(cells) + " |")

    overrides = [image for image in images if image["nbs_type"] is not None]
    if overrides:
        lines += [
            "",
            "Per-typology overrides (a verified photo visually distinct from its "
            "archetype, D-051.1):",
            "",
        ]
        lines += [f"- `{image['nbs_type']}` ({image['zone']}): {image['file']}" for image in overrides]

    lines += ["", "## The images", ""]
    for image in images:
        verified = image["verified"]
        lines += [
            f"### {image['file']}",
            "",
            f"**{image['caption_subject']}** in {image['place']} "
            f"({image['zone'].replace('_', ' ')}; Köppen {image['koppen_class']}).",
            "",
            f"- Slot: `{image['nbs_type'] or image['archetype']}` × `{image['zone']}`",
            f"- Author: {image['author']}",
            f"- Licence: **{image['licence']}** — <{image['licence_url']}>"
            if image["licence_url"]
            else f"- Licence: **{image['licence']}**",
            f"- Source: <{image['source_page']}>",
            f"- Original SHA-256: `{image['original_sha256']}`",
            f"- Bundled file SHA-256: `{image['file_sha256']}` "
            f"({image['file_bytes']} bytes, {image['width']}×{image['height']})",
            f"- Coordinates: {image['latitude']}, {image['longitude']} "
            f"({image['coordinates_from']})",
            f"- Verified — licence: {verified['licence']}",
            f"- Verified — depiction: {verified['depiction']}",
            f"- Verified — zone: {verified['zone']}",
            "",
        ]
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--record",
        action="store_true",
        help="fill in a missing original_sha256 from the first fetch instead of failing",
    )
    parser.add_argument(
        "--cache",
        type=Path,
        default=Path("/tmp/nbs-image-originals"),
        help="directory holding downloaded originals, keyed by source checksum",
    )
    args = parser.parse_args()

    from nature_cooling.engine.config import get_config
    from nature_cooling.geo import load_koppen

    config = get_config()
    grid = load_koppen()
    archetype_names = {
        archetype.archetype: archetype.display_name for archetype in config.typologies.archetypes
    }
    nbs_types = {typology.nbs_type for typology in config.typologies.resolved}

    sources = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
    entries: list[dict[str, Any]] = sources["images"]

    seen: set[tuple[str, str]] = set()
    for entry in entries:
        _validate_entry(entry, set(archetype_names), nbs_types)
        slot = _slot_of(entry)
        if slot in seen:
            raise SystemExit(f"duplicate slot {slot}: one image per slot")
        seen.add(slot)

    args.cache.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for stale in OUTPUT_DIR.glob("*.webp"):
        stale.unlink()

    manifest_images: list[dict[str, Any]] = []
    total_image_bytes = 0
    for entry in entries:
        slug = _slug(entry)
        koppen_class = _verify_zone(entry, config, grid)

        recorded = entry.get("original_sha256")
        cached = args.cache / f"{slug}.orig" if recorded is None else args.cache / recorded
        if cached.is_file():
            payload = cached.read_bytes()
        else:
            url = entry.get("download_url") or _commons_original_url(entry["title"])
            print(f"  fetching {slug} from {url}")
            payload = _fetch(url)
            (args.cache / _sha256(payload)).write_bytes(payload)

        actual = _sha256(payload)
        if recorded is None:
            if not args.record:
                raise SystemExit(f"{slug}: no original_sha256 recorded; rerun with --record")
            entry["original_sha256"] = actual
        elif actual != recorded:
            raise SystemExit(
                f"{slug}: downloaded original {actual} does not match the recorded {recorded}"
            )

        encoded, width, height = _encode(payload)
        file_name = f"{slug}.webp"
        (OUTPUT_DIR / file_name).write_bytes(encoded)
        total_image_bytes += len(encoded)

        manifest_images.append(
            {
                "file": file_name,
                "archetype": entry["archetype"],
                "nbs_type": entry.get("nbs_type"),
                "zone": entry["zone"],
                "place": entry["place"],
                "latitude": entry["latitude"],
                "longitude": entry["longitude"],
                "koppen_class": koppen_class,
                "coordinates_from": entry["coordinates_from"],
                "caption_subject": entry["caption_subject"],
                "author": entry["author"],
                "licence": entry["licence"],
                "licence_url": entry.get("licence_url"),
                "source_page": entry["source_page"],
                "original_sha256": entry["original_sha256"],
                "file_sha256": _sha256(encoded),
                "file_bytes": len(encoded),
                "width": width,
                "height": height,
                "verified": {
                    **entry["verified"],
                    "zone": (
                        f"({entry['latitude']}, {entry['longitude']}) -> Köppen "
                        f"{koppen_class} -> {entry['zone']} via the bundled Beck et al. "
                        "(2023) grid and config/climate_classification.yaml"
                    ),
                },
            }
        )
        print(f"  {file_name}: {len(encoded)} bytes, {width}x{height}, {entry['licence']}")

    manifest = {
        "dataset": "nbs_example_images",
        "purpose": (
            "Photographs of real NbS implementations, shown as illustrative examples "
            "in the intervention picker. Not evidence: no methodology value, score or "
            "stored result derives from any image (D-051.6)."
        ),
        "budget_bytes": TOTAL_BUDGET_BYTES,
        "images": manifest_images,
    }
    manifest_path = OUTPUT_DIR / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    attribution_path = OUTPUT_DIR / "ATTRIBUTION.md"
    attribution_path.write_text(
        _attribution_document(manifest, archetype_names), encoding="utf-8"
    )

    if args.record:
        SOURCES_PATH.write_text(
            json.dumps(sources, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    total = sum(path.stat().st_size for path in OUTPUT_DIR.iterdir())
    print(
        f"wrote {len(manifest_images)} images ({total_image_bytes} bytes), "
        f"data/images totals {total} bytes of the {TOTAL_BUDGET_BYTES} budget"
    )
    if total > TOTAL_BUDGET_BYTES:
        raise SystemExit("over budget: remove or re-encode images")
    return 0


if __name__ == "__main__":
    sys.exit(main())
