"""The bundled NbS example images (v2.3, D-051).

Both endpoints answer from files inside the package, like the basemap and the
place index: the manifest is one request that tells the picker every
(archetype-or-override, climate zone) pair a verified image exists for, and
the file endpoint serves those images and nothing else. Nothing here reaches
the network, and the default build makes no third-party request (D-049.1) —
bundling the photographs, rather than hotlinking their source, is the point.

The images are illustrative examples, not evidence (D-051.6): no methodology
value, score, or stored result derives from any of them, which is why these
routes read no configuration and touch no engine state.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, Response

from nature_cooling.api.schemas import NbsImage, NbsImageManifest
from nature_cooling.images import image_file_path, load_image_manifest

router = APIRouter(prefix="/images", tags=["images"])


@router.get("/manifest")
def manifest() -> NbsImageManifest:
    """Which example images exist, and the attribution each must carry."""
    loaded = load_image_manifest()
    return NbsImageManifest(
        purpose=loaded.purpose,
        images=[
            NbsImage(
                file=image.file,
                archetype=image.archetype,
                nbs_type=image.nbs_type,
                zone=image.zone,
                place=image.place,
                caption_subject=image.caption_subject,
                author=image.author,
                licence=image.licence,
                licence_url=image.licence_url,
                source_page=image.source_page,
                width=image.width,
                height=image.height,
            )
            for image in loaded.images
        ],
    )


@router.get(
    "/{file_name}",
    response_class=Response,
    responses={200: {"content": {"image/webp": {}}}},
)
def image_file(file_name: str) -> FileResponse:
    """One bundled image. Only manifest-declared names are ever served."""
    path = image_file_path(file_name)
    if path is None:
        raise HTTPException(status_code=404, detail=f"no bundled image named {file_name!r}")
    # The file name carries its content hash's provenance in the manifest and
    # changes when the image does, so a day of caching risks nothing.
    return FileResponse(
        path, media_type="image/webp", headers={"Cache-Control": "public, max-age=86400"}
    )
