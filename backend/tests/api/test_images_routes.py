"""The example-image endpoints (v2.3, D-051): the manifest, and the files.

One manifest request tells the picker every (archetype-or-override, zone)
pair a verified image exists for; the file endpoint serves exactly the
manifest-declared files and nothing else. Everything is answered from inside
the package — these routes are part of why the unconfigured deployment makes
zero external requests with the image dialog open (D-049.8, extended by the
v2.3 runtime gate walkthrough).
"""

from __future__ import annotations

import hashlib

from fastapi.testclient import TestClient

from nature_cooling.engine.config import default_images_dir
from nature_cooling.images import load_image_manifest


def test_the_manifest_lists_every_bundled_image_with_its_attribution(
    client: TestClient,
) -> None:
    response = client.get("/api/images/manifest")
    assert response.status_code == 200
    document = response.json()
    manifest = load_image_manifest()
    assert len(document["images"]) == len(manifest.images)
    served = {image["file"] for image in document["images"]}
    assert served == {image.file for image in manifest.images}
    for image in document["images"]:
        # The dialog renders author, licence name, and the source link
        # (D-051.3); the caption is built from subject, place and zone
        # (D-051.6) — every field must arrive non-empty.
        assert image["author"]
        assert image["licence"]
        assert image["source_page"].startswith("https://")
        assert image["place"]
        assert image["caption_subject"]
        assert image["zone"]
        assert image["archetype"]
        assert image["width"] > 0 and image["height"] > 0


def test_the_manifest_holds_the_slot_the_runtime_gate_walks_through(
    client: TestClient,
) -> None:
    """The runtime request gate opens the example dialog on the Tree Avenue
    card for a temperate site (D-049.8, v2.3); that card's archetype-level
    slot must exist, or the gate would silently stop proving anything."""
    document = client.get("/api/images/manifest").json()
    slots = {
        (image["nbs_type"] or image["archetype"], image["zone"]) for image in document["images"]
    }
    assert ("street_tree_canopy", "temperate") in slots


def test_an_image_file_is_served_byte_identical_with_caching_headers(
    client: TestClient,
) -> None:
    manifest = load_image_manifest()
    image = manifest.images[0]
    response = client.get(f"/api/images/{image.file}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/webp"
    assert response.headers["cache-control"] == "public, max-age=86400"
    on_disk = (default_images_dir() / image.file).read_bytes()
    assert hashlib.sha256(response.content).hexdigest() == hashlib.sha256(on_disk).hexdigest()


def test_an_undeclared_file_name_is_a_404_never_a_disk_read(client: TestClient) -> None:
    """Only manifest-declared names resolve: an arbitrary name — or a
    traversal spelling — is answered exactly like a missing image."""
    for attempt in ("nonexistent.webp", "..%2Fmanifest.json", "manifest.json%00.webp"):
        response = client.get(f"/api/images/{attempt}")
        assert response.status_code == 404, attempt


def test_the_manifest_route_is_not_shadowed_by_the_file_route(client: TestClient) -> None:
    """`manifest` is a reserved name by construction — image files always end
    `.webp` — but route ordering is what actually keeps it reachable."""
    response = client.get("/api/images/manifest")
    assert response.headers["content-type"].startswith("application/json")
