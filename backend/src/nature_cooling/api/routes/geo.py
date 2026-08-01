"""Map-picker endpoints: the offline basemap, and the three-input lookup.

Both are served from files inside the package. Nothing here reaches the
network, and the default build makes no third-party request of any kind
(D-030, D-047.1) — the basemap the browser draws is bundled, and the two
lookups are answered from bundled data. External tiles, where a user chooses to
enable them, are requested by the browser from a source that user named; the
server never proxies or fetches them, so a deployment inside a restricted
network keeps working exactly as it does today.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request

from nature_cooling.api.schemas import (
    GeoClimate,
    GeoCountry,
    GeoLookupRequest,
    GeoLookupResponse,
)
from nature_cooling.engine.config import MethodologyConfig
from nature_cooling.geo import GeoDataError, look_up_site
from nature_cooling.geo.datasets import load_basemap

router = APIRouter(prefix="/geo", tags=["geo"])


def _config(request: Request) -> MethodologyConfig:
    config: MethodologyConfig = request.app.state.config
    return config


@router.get("/basemap")
def basemap() -> dict[str, Any]:
    """Return the bundled 1:110m country outlines the offline map draws."""
    try:
        return load_basemap()
    except GeoDataError as exc:  # pragma: no cover - defensive; see test_geo_routes
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/lookup")
def lookup(payload: GeoLookupRequest, request: Request) -> GeoLookupResponse:
    """Answer the three questions a map may answer about a location.

    Returns suggestions, not answers. The caller applies each one only where
    the user has not already answered, and marks what it applies as autofilled
    (D-047.2) — an autofilled value never overwrites an answer already given.
    """
    try:
        site = look_up_site(
            payload.latitude,
            payload.longitude,
            _config(request),
            boundary=payload.boundary,
        )
    except GeoDataError as exc:  # pragma: no cover - defensive; see test_geo_routes
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return GeoLookupResponse(
        latitude=site.latitude,
        longitude=site.longitude,
        site_area_m2=site.site_area_m2,
        country=GeoCountry(
            iso_a2=site.country.iso_a2,
            iso_a3=site.country.iso_a3,
            name=site.country.name,
            matched=site.country.matched,
            source_key=site.country.source_key,
            attribution=site.country.attribution,
        ),
        climate=GeoClimate(
            zone=site.climate.zone,
            koppen_class=site.climate.koppen_class,
            source_key=site.climate.source_key,
            attribution=site.climate.attribution,
            note=site.climate.note,
            resolution_caveat=site.climate.resolution_caveat,
        ),
    )
