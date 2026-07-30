"""Service metadata."""

from __future__ import annotations

from importlib.metadata import metadata

from fastapi import APIRouter, Request

import nature_cooling
from nature_cooling.api.schemas import MetaResponse

router = APIRouter(tags=["meta"])


@router.get("/meta")
def meta(request: Request) -> MetaResponse:
    """Engine version, methodology version, and licence."""
    return MetaResponse(
        engine_version=nature_cooling.__version__,
        methodology_version=request.app.state.config.version,
        license=metadata("criterra-nature-cooling")["License-Expression"],
    )
