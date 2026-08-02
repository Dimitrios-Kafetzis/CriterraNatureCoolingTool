"""FastAPI application factory.

The app carries exactly two pieces of state, both injected so tests can
substitute them: the loaded methodology configuration and the project store.
Run locally with the ``serve`` extra installed:

    uvicorn nature_cooling.api.main:app

An installed wheel additionally embeds the production frontend build, served
at ``/`` from the same origin as ``/api`` (D-030/D-035); ``nature-cooling
serve`` wraps the same app.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI

import nature_cooling
from nature_cooling.api.routes import api_router
from nature_cooling.api.storage import ProjectStore, default_storage_root
from nature_cooling.api.tiles import TileConfig, tile_config_from_env
from nature_cooling.api.webapp import SinglePageStaticFiles, default_webapp_dir
from nature_cooling.engine import MethodologyConfig, get_config

# Passed for `tiles` to mean "read the environment" while keeping None
# available to tests as an explicit "unconfigured deployment".
_TILES_FROM_ENV = object()


def create_app(
    *,
    config: MethodologyConfig | None = None,
    storage_root: Path | None = None,
    webapp_dir: Path | None = None,
    tiles: TileConfig | object | None = _TILES_FROM_ENV,
) -> FastAPI:
    """Build the service around one methodology configuration and one store."""
    app = FastAPI(
        title="Nature for Cooling Rapid Assessment Tool",
        version=nature_cooling.__version__,
        license_info={"name": "Apache-2.0", "url": "https://www.apache.org/licenses/LICENSE-2.0"},
    )
    app.state.config = config if config is not None else get_config()
    app.state.store = ProjectStore(
        storage_root if storage_root is not None else default_storage_root()
    )
    # The deployment's tile configuration (v2.2, D-049.2): read once, here, so
    # a broken configuration fails the process at startup with its reason
    # rather than serving an uncredited or half-working map.
    app.state.tiles = tiles if tiles is not _TILES_FROM_ENV else tile_config_from_env()
    app.include_router(api_router, prefix="/api")
    webapp = webapp_dir if webapp_dir is not None else default_webapp_dir()
    if webapp is not None:
        app.mount("/", SinglePageStaticFiles(directory=webapp, html=True), name="webapp")
    return app


app = create_app()
