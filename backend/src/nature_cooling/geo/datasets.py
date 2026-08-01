"""Loading the two bundled geographic datasets.

Both are read from ``data/geo/`` — the repository's copy in a checkout, the
wheel's embedded copy in an installed package, resolved by
``default_geo_data_dir()`` exactly as ``config/`` and the bibliography are
(D-036). Both loads are cached process-wide: the country outlines are ~190 KB
of JSON and the class grid decompresses to 6.5 MB, neither of which should be
re-read per request.

The runtime formats are plain JSON and zlib, both stdlib, because the wheel
must install with one command and no system libraries (D-033). The GeoTIFF and
shapefile the publishers ship were converted offline by
``tools/build_datasets.py``, which records what each bundled byte came from.
"""

from __future__ import annotations

import json
import zlib
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from nature_cooling.engine.config import default_geo_data_dir

# The lookup layer (1:50m, zlib-compressed) and the basemap layer (1:110m,
# plain JSON) are two scales of the same public-domain source, bundled
# separately because the lookup must be right about small countries and the
# basemap must be quick to draw at world zoom. See tools/build_datasets.py.
COUNTRIES_FILE = "countries.json.z"
BASEMAP_FILE = "basemap.json"
KOPPEN_META_FILE = "koppen_geiger.json"


class GeoDataError(RuntimeError):
    """A bundled geographic dataset is missing or unreadable."""


# A ring is a closed list of (lon, lat) pairs; a polygon is an outer ring
# followed by any holes; a country is one or more polygons plus a bounding box.
Ring = list[list[float]]
Polygon = list[Ring]


@dataclass(frozen=True)
class Country:
    """One country's ISO codes, display name, bounding box and outlines."""

    iso_a2: str
    iso_a3: str
    name: str
    bbox: tuple[float, float, float, float]
    polygons: tuple[Polygon, ...]


@dataclass(frozen=True)
class Territory:
    """An outline the source carries no ISO code for.

    Held so the lookup can decline to name a country for a point inside one,
    rather than letting its coastal tolerance attribute the point to whichever
    recognised state happens to be nearest.
    """

    name: str
    bbox: tuple[float, float, float, float]
    polygons: tuple[Polygon, ...]


@dataclass(frozen=True)
class CountryBoundaries:
    """The Natural Earth admin-0 layer, reduced to what the lookup needs."""

    countries: tuple[Country, ...]
    unassigned: tuple[Territory, ...]
    source_key: str
    source_release: str
    licence: str
    attribution: str
    scale: str
    codes_omitted: tuple[str, ...]


@dataclass(frozen=True)
class KoppenGrid:
    """The Köppen–Geiger class grid and the legend that names its values.

    ``values`` is a row-major grid of class indices, one byte per cell, with
    row 0 at the north pole and column 0 at 180° W. ``0`` means ocean — the
    publisher's no-data value, not a class.
    """

    values: bytes
    rows: int
    cols: int
    resolution_degrees: float
    classes: dict[int, str]
    ocean_value: int
    source_key: str
    period: str
    licence: str
    attribution: str
    resolution_caveat_key: str = "resolution_caveat"


def _require(path: Path) -> bytes:
    if not path.is_file():
        raise GeoDataError(
            f"missing bundled geographic dataset: {path}. In a checkout these files "
            f"live in data/geo/; in an installed wheel they are staged by "
            f"tools/build_wheel.sh."
        )
    return path.read_bytes()


def _parse_json(raw: bytes, path: Path) -> dict[str, Any]:
    try:
        loaded = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise GeoDataError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise GeoDataError(f"{path} must contain a JSON object at the top level")
    return loaded


def _read_json(path: Path) -> dict[str, Any]:
    return _parse_json(_require(path), path)


def _read_compressed_json(path: Path) -> dict[str, Any]:
    raw = _require(path)
    try:
        decompressed = zlib.decompress(raw)
    except zlib.error as exc:
        raise GeoDataError(f"corrupt compressed dataset {path}: {exc}") from exc
    return _parse_json(decompressed, path)


def _countries_from(document: dict[str, Any], path: Path) -> tuple[Country, ...]:
    countries = tuple(
        Country(
            iso_a2=entry["iso_a2"],
            iso_a3=entry["iso_a3"],
            name=entry["name"],
            bbox=(entry["bbox"][0], entry["bbox"][1], entry["bbox"][2], entry["bbox"][3]),
            polygons=tuple(entry["polygons"]),
        )
        for entry in document["countries"]
    )
    if not countries:
        raise GeoDataError(f"{path} declares no countries")
    return countries


@lru_cache(maxsize=1)
def load_countries(data_dir: Path | None = None) -> CountryBoundaries:
    """Load the 1:50m country boundaries the point-in-polygon lookup reads."""
    directory = data_dir or default_geo_data_dir()
    path = directory / COUNTRIES_FILE
    document = _read_compressed_json(path)
    return CountryBoundaries(
        countries=_countries_from(document, path),
        unassigned=tuple(
            Territory(
                name=entry["name"],
                bbox=(entry["bbox"][0], entry["bbox"][1], entry["bbox"][2], entry["bbox"][3]),
                polygons=tuple(entry["polygons"]),
            )
            for entry in document.get("unassigned", ())
        ),
        source_key=document["source_key"],
        source_release=document["source_release"],
        licence=document["licence"],
        attribution=document["attribution"],
        scale=document["scale"],
        codes_omitted=tuple(document.get("codes_omitted", ())),
    )


@lru_cache(maxsize=1)
def load_basemap(data_dir: Path | None = None) -> dict[str, Any]:
    """Load the 1:110m outlines the offline basemap draws.

    Returned as the parsed document rather than as models: the frontend is its
    only consumer and it draws the outlines without interpreting them.
    """
    directory = data_dir or default_geo_data_dir()
    path = directory / BASEMAP_FILE
    document = _read_json(path)
    if not document.get("countries"):
        raise GeoDataError(f"{path} declares no outlines")
    return document


@lru_cache(maxsize=1)
def load_koppen(data_dir: Path | None = None) -> KoppenGrid:
    """Load and decompress the bundled Köppen–Geiger class grid."""
    directory = data_dir or default_geo_data_dir()
    meta = _read_json(directory / KOPPEN_META_FILE)

    grid_path = directory / meta["grid_file"]
    if not grid_path.is_file():
        raise GeoDataError(f"missing bundled climate grid: {grid_path}")
    try:
        values = zlib.decompress(grid_path.read_bytes())
    except zlib.error as exc:
        raise GeoDataError(f"corrupt climate grid {grid_path}: {exc}") from exc

    rows = int(meta["rows"])
    cols = int(meta["cols"])
    if len(values) != rows * cols:
        raise GeoDataError(
            f"{grid_path} decompressed to {len(values)} bytes, but {KOPPEN_META_FILE} "
            f"declares a {rows}x{cols} grid ({rows * cols} bytes)"
        )

    return KoppenGrid(
        values=values,
        rows=rows,
        cols=cols,
        resolution_degrees=float(meta["resolution_degrees"]),
        classes={int(index): name for index, name in meta["classes"].items()},
        ocean_value=int(meta["ocean_value"]),
        source_key=meta["source_key"],
        period=meta["period"],
        licence=meta["licence"],
        attribution=meta["attribution"],
    )
