"""Service metadata."""

from __future__ import annotations

from importlib.metadata import metadata

from fastapi import APIRouter, Request

import nature_cooling
from nature_cooling.api.schemas import MetaResponse, TileSource
from nature_cooling.api.tiles import TileConfig

router = APIRouter(tags=["meta"])


@router.get("/meta")
def meta(request: Request) -> MetaResponse:
    """Engine version, methodology version, licence, and tile configuration.

    ``tiles`` is how the browser learns what the deployer configured
    (D-049.2): the server never requests a tile itself, it only relays the
    template and the credit that must accompany it (D-049.3).
    """
    tiles: TileConfig | None = request.app.state.tiles
    return MetaResponse(
        engine_version=nature_cooling.__version__,
        methodology_version=request.app.state.config.version,
        license=metadata("criterra-nature-cooling")["License-Expression"],
        tiles=None
        if tiles is None
        else TileSource(url_template=tiles.url_template, attribution=tiles.attribution),
    )
