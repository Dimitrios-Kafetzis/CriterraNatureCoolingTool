"""Packaged web application serving (D-035).

The distributable wheel embeds the production frontend build under
``nature_cooling/_bundled/webapp``; the app factory serves it at ``/`` from
the same origin as ``/api``, completing the D-030 same-origin model with no
CORS middleware. In a repository checkout the directory does not exist and
the API serves alone, with the Vite dev server proxying ``/api`` to it.
"""

from __future__ import annotations

from pathlib import Path

from starlette.exceptions import HTTPException
from starlette.responses import Response
from starlette.staticfiles import StaticFiles
from starlette.types import Scope

from nature_cooling.engine.config import bundled_data_dir


def default_webapp_dir() -> Path | None:
    """Return the embedded frontend build, when this installation carries one."""
    webapp = bundled_data_dir() / "webapp"
    return webapp if webapp.is_dir() else None


class SinglePageStaticFiles(StaticFiles):
    """Static files with the single-page-application fallback.

    Client-side routes (``/projects/…``) name no file in the build; they must
    serve ``index.html`` and let the frontend router resolve them, so a deep
    link or a reload lands on the app rather than a 404. Unmatched ``/api``
    paths are exempt: an API typo stays an API 404, never the app shell.
    """

    async def get_response(self, path: str, scope: Scope) -> Response:
        try:
            return await super().get_response(path, scope)
        except HTTPException as exc:
            if exc.status_code == 404 and not path.startswith("api/"):
                return await super().get_response("index.html", scope)
            raise
