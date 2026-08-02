"""Command-line entry point (D-035, D-049.2).

``nature-cooling serve`` starts the packaged application — the API and the
embedded web app on one origin — by wrapping uvicorn, which ships behind the
``serve`` extra so the core package keeps its runtime dependencies unchanged.

The two ``--tile-*`` flags are the CLI convenience form of the deployment
tile configuration (D-049.2): they set the corresponding environment
variables before handing off to uvicorn, which is the single place the
application reads the setting from, so a local run with imagery is one
command and there is exactly one configuration mechanism underneath.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence

from nature_cooling.api.tiles import (
    TILE_ATTRIBUTION_VAR,
    TILE_URL_VAR,
    TileConfigError,
    tile_config_from_env,
)

_MISSING_SERVE_EXTRA = (
    "uvicorn is not installed. The server ships behind the 'serve' extra:\n"
    '    pip install "criterra-nature-cooling[serve]"'
)


def main(argv: Sequence[str] | None = None) -> int:
    """Parse arguments and dispatch; returns the process exit code."""
    parser = argparse.ArgumentParser(
        prog="nature-cooling",
        description="Nature for Cooling Rapid Assessment Tool.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)
    serve = subcommands.add_parser(
        "serve",
        help="Start the application: API and web app on one origin.",
        description="Start the application: API and web app on one origin.",
    )
    serve.add_argument("--host", default="127.0.0.1", help="bind address (default: 127.0.0.1)")
    serve.add_argument("--port", type=int, default=8000, help="port (default: 8000)")
    serve.add_argument(
        "--tile-url",
        default=None,
        help=f"map-imagery tile URL template with {{z}}/{{x}}/{{y}} placeholders; "
        f"equivalent to setting {TILE_URL_VAR}. Requires --tile-attribution. "
        f"Without it the map uses the bundled offline outlines and the "
        f"application makes no third-party request (see docs/HOSTING.md).",
    )
    serve.add_argument(
        "--tile-attribution",
        default=None,
        help=f"the credit line the tile source requires on the map; equivalent "
        f"to setting {TILE_ATTRIBUTION_VAR}.",
    )
    arguments = parser.parse_args(argv)
    return _serve(
        arguments.host,
        arguments.port,
        tile_url=arguments.tile_url,
        tile_attribution=arguments.tile_attribution,
    )


def _serve(
    host: str,
    port: int,
    *,
    tile_url: str | None = None,
    tile_attribution: str | None = None,
) -> int:
    # The flags become the environment variables the app factory reads
    # (D-049.2) — one mechanism underneath, two spellings on top.
    if tile_url is not None:
        os.environ[TILE_URL_VAR] = tile_url
    if tile_attribution is not None:
        os.environ[TILE_ATTRIBUTION_VAR] = tile_attribution
    # Validate here for a clean one-line error, rather than letting the app
    # factory raise through uvicorn's startup traceback.
    try:
        tile_config_from_env()
    except TileConfigError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    try:
        import uvicorn
    except ImportError:
        print(_MISSING_SERVE_EXTRA, file=sys.stderr)
        return 1
    uvicorn.run("nature_cooling.api.main:app", host=host, port=port)
    return 0
