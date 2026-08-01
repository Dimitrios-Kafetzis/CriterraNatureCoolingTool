#!/usr/bin/env python3
"""Derive the two bundled geographic datasets from their published sources.

This script runs ONCE, offline, by hand; its outputs are committed to `data/`
and are what the tool actually reads. Nothing in the application, the test
suite or CI invokes it. That is the same arrangement as the report fonts, which
were subset offline with fonttools and committed as `.ttf`/`.woff2`: the
derivation is recorded and repeatable, but the build does not depend on
downloading 130 MB from a research archive.

It is kept in the repository so the derivation is auditable — a reader can see
exactly which published file each bundled byte came from, what was discarded,
and why. The recorded checksums make the claim checkable rather than asserted.

    python3 -m venv /tmp/geo && /tmp/geo/bin/pip install pillow numpy
    /tmp/geo/bin/python tools/build_datasets.py --sources /path/to/downloads

Sources (all redistributable; see NOTICE and data/geo/ATTRIBUTION.md):

  ne_50m_admin_0_countries.geojson
      Natural Earth, admin-0 countries, 1:50m, release v5.1.2. Public domain.
      The layer the country LOOKUP reads.
      https://github.com/nvkelso/natural-earth-vector/raw/v5.1.2/geojson/ne_50m_admin_0_countries.geojson

  ne_110m_admin_0_countries.geojson
      The same, at 1:110m. The layer the offline BASEMAP draws.
      https://github.com/nvkelso/natural-earth-vector/raw/v5.1.2/geojson/ne_110m_admin_0_countries.geojson

  koppen_geiger_tif.zip  (member 1991_2020/koppen_geiger_0p1.tif)
      Beck et al. (2023), Scientific Data 10, 724. CC BY 4.0.
      https://ndownloader.figshare.com/files/61012822

Two scales of the same layer are bundled because the two jobs want opposite
things. The lookup must be RIGHT: at 1:110m, Natural Earth omits every country
smaller than about a thousand square kilometres, so a click on Singapore falls
through to Malaysia and a click on Monaco to France — a wrong country stated
confidently, which is worse than no country at all, and wrong for precisely the
dense hot cities this tool exists to serve. The basemap must be FAST and is
drawn at world zoom, where 1:50m detail is invisible and its ten-times vertex
count is pure cost. The lookup layer is therefore 1:50m and compressed; the
basemap layer is 1:110m and served as-is.

Requires Pillow and numpy, which are NOT dependencies of the tool — they exist
only to read a GeoTIFF here. The committed runtime formats are plain JSON and
zlib, both stdlib, so the package itself needs nothing geospatial (D-033: pure
Python, no system libraries).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
import zlib
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "data" / "geo"

# Two decimal places is roughly 1.1 km at the equator, at or below Natural
# Earth's own vertex spacing at these scales. It is far finer than either use
# needs — a country identification tolerant of a kilometre at the border, and a
# world-zoom outline — and it halves the stored size. No ring in either layer
# collapses below a triangle at this precision.
COORDINATE_PRECISION = 2

NATURAL_EARTH_RELEASE = "v5.1.2"
NATURAL_EARTH_50M_SHA256 = "3e458fc036ad0a66411f2c1e6cac49c5d7bfb81cb1123bc513b22511a2b7fdeb"
NATURAL_EARTH_110M_SHA256 = "6866c877d39cba9c357620878839b336d569f8c662d3cfab4cb1dbe2d39c977f"
KOPPEN_ARCHIVE_MD5 = "7fc2f5a15d4f5fe0ce59c9a9b502aa09"
KOPPEN_MEMBER = "1991_2020/koppen_geiger_0p1.tif"

# The 30 Koppen-Geiger classes, in the numbering used by the published raster.
# Copied from the archive's legend.txt; the mapping onto the tool's six zones
# is NOT here — it is a methodology value and lives in
# config/climate_classification.yaml with its citation and rationale.
KOPPEN_CLASSES = [
    "Af", "Am", "Aw", "BWh", "BWk", "BSh", "BSk",
    "Csa", "Csb", "Csc", "Cwa", "Cwb", "Cwc", "Cfa", "Cfb", "Cfc",
    "Dsa", "Dsb", "Dsc", "Dsd", "Dwa", "Dwb", "Dwc", "Dwd",
    "Dfa", "Dfb", "Dfc", "Dfd", "ET", "EF",
]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _md5(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _round_ring(ring: list[list[float]]) -> list[list[float]]:
    """Round a ring's coordinates and drop points the rounding made duplicate."""
    out: list[list[float]] = []
    for point in ring:
        rounded = [round(point[0], COORDINATE_PRECISION), round(point[1], COORDINATE_PRECISION)]
        if not out or out[-1] != rounded:
            out.append(rounded)
    return out


def build_countries(source: Path, scale: str, sha256: str) -> dict[str, Any]:
    """Reduce a Natural Earth countries layer to codes, names and outlines."""
    raw = json.loads(source.read_text(encoding="utf-8"))
    countries: list[dict[str, Any]] = []
    unassigned: list[dict[str, Any]] = []
    skipped: list[str] = []

    for feature in raw["features"]:
        properties = feature["properties"]
        # ISO_A2_EH / ISO_A3_EH carry the codes for the countries whose plain
        # ISO_A2 / ISO_A3 fields Natural Earth leaves as "-99" — Norway and
        # France, which would otherwise be unidentifiable. Territories that
        # carry no ISO code in either field — Northern Cyprus, Somaliland,
        # Kosovo — are not assigned to the state that claims them: doing so
        # would make the tool assert a sovereignty question it has no business
        # answering, and the honest failure (no country identified, type the
        # code yourself) is one the user corrects in a single field.
        #
        # Their OUTLINES are kept, under `unassigned`, rather than simply
        # dropped. Dropping them leaves a hole in the map, and the lookup's
        # coastal tolerance would then attribute a site in Northern Cyprus to
        # Cyprus by sheer proximity — reintroducing through a fallback exactly
        # the claim the omission was making a point of not stating. Kept as
        # explicit exclusion zones, "we do not answer this" is what the code
        # actually does.
        iso_a2 = str(properties.get("ISO_A2_EH") or "-99")
        iso_a3 = str(properties.get("ISO_A3_EH") or "-99")
        unassigned_territory = iso_a2 == "-99" or iso_a3 == "-99"

        geometry = feature["geometry"]
        polygons = (
            [geometry["coordinates"]]
            if geometry["type"] == "Polygon"
            else geometry["coordinates"]
        )
        rings: list[list[list[list[float]]]] = []
        for polygon in polygons:
            reduced = [_round_ring(ring) for ring in polygon]
            # A ring that rounding collapsed below a triangle bounds no area.
            reduced = [ring for ring in reduced if len(ring) >= 4]
            if reduced:
                rings.append(reduced)
        if not rings:
            skipped.append(str(properties.get("NAME")))
            continue

        flat = [point for polygon in rings for ring in polygon for point in ring]
        bbox = [
            min(p[0] for p in flat), min(p[1] for p in flat),
            max(p[0] for p in flat), max(p[1] for p in flat),
        ]
        entry = {
            "iso_a2": iso_a2,
            "iso_a3": iso_a3,
            "name": str(properties["NAME"]),
            "bbox": bbox,
            "polygons": rings,
        }
        if unassigned_territory:
            skipped.append(str(properties.get("NAME")))
            entry.pop("iso_a2")
            entry.pop("iso_a3")
            unassigned.append(entry)
        else:
            countries.append(entry)

    countries.sort(key=lambda item: item["iso_a2"])
    unassigned.sort(key=lambda item: item["name"])
    print(
        f"  {scale}: kept {len(countries)}; "
        f"held as unassigned (no ISO code): {sorted(skipped)}"
    )
    return {
        "dataset": f"natural_earth_admin_0_countries_{scale.replace('1:', '')}",
        "source_key": "naturalearth",
        "source_release": NATURAL_EARTH_RELEASE,
        "source_sha256": sha256,
        "scale": scale,
        "licence": "public domain",
        "attribution": "Country boundaries from Natural Earth (public domain).",
        "coordinate_precision_decimals": COORDINATE_PRECISION,
        "codes_omitted": sorted(skipped),
        "countries": countries,
        "unassigned": unassigned,
    }


def build_koppen(archive: Path) -> tuple[dict[str, Any], bytes]:
    """Extract the 0.1-degree present-day layer as a compressed class grid."""
    import numpy as np  # noqa: PLC0415 - offline tooling dependency only
    from PIL import Image  # noqa: PLC0415

    Image.MAX_IMAGE_PIXELS = None

    with zipfile.ZipFile(archive) as bundle:
        with bundle.open(KOPPEN_MEMBER) as member:
            grid = np.array(Image.open(member))

    rows, cols = grid.shape
    if (rows, cols) != (1800, 3600):
        raise SystemExit(f"unexpected raster shape {grid.shape}; expected (1800, 3600)")
    if int(grid.max()) > len(KOPPEN_CLASSES):
        raise SystemExit(f"raster holds class {grid.max()}, beyond the 30-class legend")

    payload = zlib.compress(grid.tobytes(), 9)
    meta = {
        "dataset": "koppen_geiger_present_day_0p1deg",
        "source_key": "beck2023",
        "source_member": KOPPEN_MEMBER,
        "source_archive_md5": KOPPEN_ARCHIVE_MD5,
        "period": "1991-2020",
        "licence": "CC BY 4.0",
        "attribution": (
            "Koppen-Geiger climate classification from Beck et al. (2023), "
            "Scientific Data 10, 724, doi:10.1038/s41597-023-02549-6 (CC BY 4.0)."
        ),
        # Why 0.1 degrees and not the published 1 km layer: the coarsest layer
        # that still classifies correctly is the one to ship (V2.1 brief). Over
        # 75 world cities, the 0.1-degree layer reproduces the 1 km layer's
        # six-zone answer 71 times, the 0.5-degree layer 69 times and the
        # 1-degree layer 68 times; 0.5 degrees is where the errors start
        # landing on ordinary cities (Denver, Nairobi) rather than on
        # coastlines and steep gradients. 0.1 degrees costs 162 KB, the 1 km
        # layer 12 MB, for four cities in seventy-five.
        "resolution_degrees": 0.1,
        "rows": rows,
        "cols": cols,
        # Row 0 spans 90..89.9 N, column 0 spans 180..179.9 W.
        "bounds": {"north": 90.0, "south": -90.0, "west": -180.0, "east": 180.0},
        "grid_file": "koppen_geiger_1991_2020_0p1.bin.z",
        "grid_sha256": hashlib.sha256(payload).hexdigest(),
        "grid_bytes": len(payload),
        "ocean_value": 0,
        "classes": {str(index): name for index, name in enumerate(KOPPEN_CLASSES, start=1)},
    }
    land = int((grid > 0).sum())
    print(f"  koppen grid: {rows}x{cols}, {land} land cells, {len(payload)} bytes compressed")
    return meta, payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sources",
        type=Path,
        required=True,
        help="directory holding the two downloaded source files",
    )
    args = parser.parse_args()

    lookup_source = args.sources / "ne_50m_admin_0_countries.geojson"
    basemap_source = args.sources / "ne_110m_admin_0_countries.geojson"
    koppen_source = args.sources / "koppen_geiger_tif.zip"
    for path in (lookup_source, basemap_source, koppen_source):
        if not path.is_file():
            raise SystemExit(f"missing source file: {path}")

    for path, expected in (
        (lookup_source, NATURAL_EARTH_50M_SHA256),
        (basemap_source, NATURAL_EARTH_110M_SHA256),
    ):
        actual = _sha256(path)
        if actual != expected:
            raise SystemExit(
                f"{path.name} checksum {actual} does not match the recorded {expected}; "
                f"the pinned release is {NATURAL_EARTH_RELEASE}"
            )
    actual_md5 = _md5(koppen_source)
    if actual_md5 != KOPPEN_ARCHIVE_MD5:
        raise SystemExit(
            f"Koppen archive checksum {actual_md5} does not match the recorded "
            f"{KOPPEN_ARCHIVE_MD5}"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Natural Earth admin-0 countries:")
    # The lookup layer is compressed: it is read once into memory at startup and
    # never served, so its on-disk size is all it costs.
    lookup = build_countries(lookup_source, "1:50m", NATURAL_EARTH_50M_SHA256)
    lookup_bytes = zlib.compress(
        json.dumps(lookup, ensure_ascii=False, separators=(",", ":")).encode("utf-8"), 9
    )
    lookup_path = OUTPUT_DIR / "countries.json.z"
    lookup_path.write_bytes(lookup_bytes)
    print(f"  wrote {lookup_path} ({lookup_path.stat().st_size} bytes)")

    # The basemap layer is served to the browser as-is, so it stays plain JSON
    # and carries outlines only — no ISO codes, no names, nothing the drawing
    # does not use.
    basemap = build_countries(basemap_source, "1:110m", NATURAL_EARTH_110M_SHA256)
    basemap["countries"] = [
        {"iso_a2": entry["iso_a2"], "polygons": entry["polygons"]}
        for entry in basemap["countries"]
    ]
    # The unassigned territories are drawn too — leaving holes in the world map
    # would be a stranger statement than drawing the outlines.
    basemap["unassigned"] = [
        {"polygons": entry["polygons"]} for entry in basemap["unassigned"]
    ]
    basemap_path = OUTPUT_DIR / "basemap.json"
    basemap_path.write_text(
        json.dumps(basemap, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(f"  wrote {basemap_path} ({basemap_path.stat().st_size} bytes)")

    print("Koppen-Geiger present-day classification:")
    meta, payload = build_koppen(koppen_source)
    grid_path = OUTPUT_DIR / meta["grid_file"]
    grid_path.write_bytes(payload)
    meta_path = OUTPUT_DIR / "koppen_geiger.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  wrote {grid_path} ({grid_path.stat().st_size} bytes)")
    print(f"  wrote {meta_path} ({meta_path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
