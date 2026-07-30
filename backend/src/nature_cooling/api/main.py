"""FastAPI application factory.

The app carries exactly two pieces of state, both injected so tests can
substitute them: the loaded methodology configuration and the project store.
Run locally with the ``serve`` extra installed:

    uvicorn nature_cooling.api.main:app
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI

import nature_cooling
from nature_cooling.api.routes import api_router
from nature_cooling.api.storage import ProjectStore, default_storage_root
from nature_cooling.engine import MethodologyConfig, get_config


def create_app(
    *,
    config: MethodologyConfig | None = None,
    storage_root: Path | None = None,
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
    app.include_router(api_router, prefix="/api")
    return app


app = create_app()
