"""Command-line entry point (D-035).

``nature-cooling serve`` starts the packaged application — the API and the
embedded web app on one origin — by wrapping uvicorn, which ships behind the
``serve`` extra so the core package keeps its runtime dependencies unchanged.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

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
    arguments = parser.parse_args(argv)
    return _serve(arguments.host, arguments.port)


def _serve(host: str, port: int) -> int:
    try:
        import uvicorn
    except ImportError:
        print(_MISSING_SERVE_EXTRA, file=sys.stderr)
        return 1
    uvicorn.run("nature_cooling.api.main:app", host=host, port=port)
    return 0
