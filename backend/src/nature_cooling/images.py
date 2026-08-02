"""The bundled NbS example images and their manifest (v2.3, D-051).

Each intervention card in the picker can show one photograph of a real
implementation of that kind of NbS, matched to the project's climate zone.
The photographs ship inside the package — hotlinking an image host at
click-time would be a third-party request from the default build, which
D-049.1 forbids — and were derived from their openly licensed sources by
``tools/build_images.py``, which records per image the source page, author,
exact licence, and checksums, and refuses any image whose three verifications
(licence read from the file page, depiction confirmed by looking, climate
zone reproduced from the tool's own bundled Köppen grid) do not hold.

The images are illustrative examples, NOT evidence (D-051.6): nothing here is
read by the engine, no methodology value derives from any image, and captions
state place and climate zone only. An (archetype-or-override, zone) slot with
no verified image is simply absent from the manifest, and the interface shows
no affordance for it — absence is the honest state, not a placeholder.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from nature_cooling.engine.config import default_images_dir

MANIFEST_FILE = "manifest.json"


class ImageDataError(RuntimeError):
    """The bundled image manifest is unreadable or inconsistent."""


@dataclass(frozen=True)
class NbsExampleImage:
    """One shipped photograph and the attribution its licence requires.

    ``nbs_type`` is ``None`` for an archetype-level image, which every entry
    inheriting that archetype shows; it names a typology only for a
    per-typology override — a verified photo visually distinct from its
    archetype (the D-044.3 inherit-with-override pattern, applied to
    pictures).
    """

    file: str
    archetype: str
    nbs_type: str | None
    zone: str
    place: str
    caption_subject: str
    author: str
    licence: str
    licence_url: str | None
    source_page: str
    width: int
    height: int


@dataclass(frozen=True)
class ImageManifest:
    """Every image shipped in ``data/images/``, with where it came from."""

    purpose: str
    images: tuple[NbsExampleImage, ...]
    directory: Path


def _image_from(entry: dict[str, Any], path: Path) -> NbsExampleImage:
    try:
        return NbsExampleImage(
            file=str(entry["file"]),
            archetype=str(entry["archetype"]),
            nbs_type=None if entry["nbs_type"] is None else str(entry["nbs_type"]),
            zone=str(entry["zone"]),
            place=str(entry["place"]),
            caption_subject=str(entry["caption_subject"]),
            author=str(entry["author"]),
            licence=str(entry["licence"]),
            licence_url=None if entry["licence_url"] is None else str(entry["licence_url"]),
            source_page=str(entry["source_page"]),
            width=int(entry["width"]),
            height=int(entry["height"]),
        )
    except KeyError as exc:
        raise ImageDataError(f"image entry in {path} is missing {exc}") from exc


@lru_cache(maxsize=4)
def load_image_manifest(data_dir: Path | None = None) -> ImageManifest:
    """Load the bundled image manifest.

    A missing directory or manifest is an *empty* manifest, not an error:
    partial — or zero — coverage is an expected state of this feature, and
    the interface's honest answer to it is to show no affordance (D-051.4).
    A manifest that exists but cannot be parsed is a real defect and raises.
    """
    directory = data_dir if data_dir is not None else default_images_dir()
    path = directory / MANIFEST_FILE
    if not path.is_file():
        return ImageManifest(purpose="", images=(), directory=directory)
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ImageDataError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise ImageDataError(f"{path} must contain a JSON object at the top level")
    images = tuple(_image_from(entry, path) for entry in loaded.get("images", []))
    return ImageManifest(purpose=str(loaded.get("purpose", "")), images=images, directory=directory)


def image_file_path(file_name: str, data_dir: Path | None = None) -> Path | None:
    """Resolve a manifest-declared file name to its path, or ``None``.

    Only names the manifest declares are ever resolved — the manifest is the
    complete statement of what this package serves, so an undeclared name
    (or a traversal attempt) is answered exactly like a missing image.
    """
    manifest = load_image_manifest(data_dir)
    for image in manifest.images:
        if image.file == file_name:
            path = manifest.directory / image.file
            return path if path.is_file() else None
    return None
