#!/usr/bin/env python3
"""The runtime half of the no-third-party-request gate (v2.2, D-049.8).

The static check (check_no_third_party_requests.sh) proves no third-party URL
sits in the build output in a position the browser fetches. Since D-049 the
sentence that actually needs proving is about *runtime*: an unconfigured
deployment makes no third-party request while being used, and a configured one
requests tiles from exactly the configured host and nowhere else. Greps cannot
state either claim; a browser can. This script drives the built application
headlessly through the installed system Chrome (Playwright, channel="chrome",
no browser download — the technique the v2.1 review used) and asserts three
things:

  A. UNCONFIGURED: a complete assessment — entry screen, project creation, the
     map step INCLUDING a map click and applying its autofill, the
     questionnaire, typology selection INCLUDING opening an example-image
     dialog (v2.3, D-051: the photograph must come from the application's own
     origin, never a third-party image host), evaluation, results — makes
     zero requests to any origin but the application's own.

  B. CONFIGURED: with a tile source configured (a second local port standing
     in for the third party, so this check itself stays offline), tile
     requests reach that host and only that host, and the source's credit is
     rendered on the map.

  C. UNREACHABLE: with a tile source configured but dead (a closed port), the
     map degrades to the bundled outlines, says so, and the questionnaire
     remains fully usable — the D-049.1 promise to restricted-network
     deployments that were configured optimistically.

Usage (checkout: serves frontend/dist through the checkout backend):

    python3 -m venv /tmp/pw && /tmp/pw/bin/pip install playwright
    /tmp/pw/bin/python tools/check_runtime_requests.py \
        --server-python backend/.venv/bin/python --dist frontend/dist

Against an installed wheel (CI: the artefact that actually ships), pass the
wheel venv's python and `--dist -` to use the webapp embedded in the wheel:

    /tmp/pw/bin/python tools/check_runtime_requests.py \
        --server-python /tmp/smoke/bin/python --dist -
"""

from __future__ import annotations

import argparse
import base64
import http.server
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import Any

# A valid 1x1 PNG, served for every mock tile request.
TILE_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
)

MOCK_ATTRIBUTION = "© OpenStreetMap contributors © Mock Tiles CI"


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class TileHandler(http.server.BaseHTTPRequestHandler):
    """Serves a PNG for any path and records what it served."""

    served: list[str] = []

    def do_GET(self) -> None:  # noqa: N802 - http.server's naming
        TileHandler.served.append(self.path)
        self.send_response(200)
        self.send_header("Content-Type", "image/png")
        self.send_header("Content-Length", str(len(TILE_PNG)))
        self.end_headers()
        self.wfile.write(TILE_PNG)

    def log_message(self, *args: object) -> None:
        pass


SERVER_BOOTSTRAP = """
import sys
from pathlib import Path
import uvicorn
from nature_cooling.api.main import create_app

dist = sys.argv[1]
app = create_app(webapp_dir=None if dist == "-" else Path(dist))
uvicorn.run(app, host="127.0.0.1", port=int(sys.argv[2]), log_level="warning")
"""


class Server:
    """The application under test, one process per tile configuration."""

    def __init__(self, python: str, dist: str, port: int, env: dict[str, str]):
        self.origin = f"http://127.0.0.1:{port}"
        # The parent's own shell must not leak a tile configuration in.
        clean = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith("NATURE_COOLING_")
        }
        self.process = subprocess.Popen(
            [python, "-c", SERVER_BOOTSTRAP, dist, str(port)],
            env={**clean, **env},
        )
        deadline = time.time() + 30
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(f"{self.origin}/api/meta", timeout=1):
                    return
            except (urllib.error.URLError, ConnectionError):
                time.sleep(0.3)
        raise SystemExit(f"server on {self.origin} did not come up")

    def stop(self) -> None:
        self.process.terminate()
        self.process.wait(timeout=10)


def allowed_origin(url: str, origins: set[str]) -> bool:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme in ("data", "blob", "about", "chrome-extension"):
        return True
    return f"{parsed.scheme}://{parsed.netloc}" in origins


def open_map_step(page: Any, origin: str, project_name: str) -> None:
    """Entry screen to the wizard's map step."""
    page.goto(origin)
    page.get_by_role("button", name="Start a new assessment").click()
    page.get_by_role("textbox", name="Project name").fill(project_name)
    page.get_by_role("button", name="Create project").click()
    page.get_by_role("application").wait_for()


def phase_unconfigured(page: Any, requests: list[str], origin: str, origins: set[str]) -> list[str]:
    """A complete assessment, driven through the interface as a user would."""
    open_map_step(page, origin, "Runtime gate walkthrough")

    # Navigate by name (D-049.6) — which also gets the map to a zoom where a
    # drawn triangle is a site rather than a province (the server refuses to
    # call an implausibly large polygon a site area).
    page.get_by_role("searchbox", name="Find a place by name").fill("athens")
    page.get_by_role("button", name="Athens, Greece").click()
    page.wait_for_timeout(1500)  # the flyTo animation

    # Draw a small site boundary, which offers all three answers (D-047) —
    # area from the ring, country and climate zone from its centroid.
    page.get_by_role("button", name="Draw the site boundary").click()
    application = page.get_by_role("application")
    for x, y in ((430, 160), (438, 160), (434, 168)):
        application.click(position={"x": x, "y": y})
    page.get_by_role("heading", name="What this location tells us").wait_for()
    page.get_by_role("button", name="Use these answers", exact=True).click()
    page.get_by_role("button", name="Continue").click()

    # Project information: the one required field the map cannot answer.
    page.get_by_label("Assessment scale", exact=True).select_option("neighbourhood")
    page.get_by_role("button", name="Continue").click()

    # Site, climate, vulnerability: everything required is filled or optional.
    for _ in range(3):
        page.get_by_role("button", name="Continue").click()

    # Intervention: pick one typology from the availability-gated picker.
    import re

    search = page.get_by_role("searchbox", name="Filter by name")
    search.wait_for()
    search.fill("tree avenue")

    # The example-image dialog (v2.3, D-051): the site's climate zone was
    # autofilled as temperate, and the street_tree_canopy × temperate slot
    # ships an image, so the Tree Avenue card carries the affordance. The
    # photograph it opens is bundled — the zero-external-requests assertion
    # below is what proves the dialog touched no third-party image host.
    page.get_by_role("button", name="See a real example of Tree Avenue").click()
    page.locator(".example-dialog img").wait_for()
    page.get_by_role("button", name="Close", exact=True).click()

    page.get_by_role("button", name=re.compile("Tree Avenue")).first.click()
    page.get_by_role("button", name="Continue").click()

    # Cost is entirely optional; run the assessment.
    page.get_by_role("button", name="Run assessment").click()
    page.get_by_role("heading", name="Results").first.wait_for(timeout=20_000)

    offenders = sorted({url for url in requests if not allowed_origin(url, origins)})
    if offenders:
        return [f"external request(s) from an UNCONFIGURED deployment: {offenders}"]
    print(f"  {len(requests)} browser requests, all to {origin}")
    return []


def phase_configured(page: Any, requests: list[str], origin: str, origins: set[str]) -> list[str]:
    TileHandler.served.clear()
    open_map_step(page, origin, "Configured tiles")
    deadline = time.time() + 15
    while time.time() < deadline and not TileHandler.served:
        time.sleep(0.3)

    problems: list[str] = []
    if not TileHandler.served:
        problems.append("no tile request reached the configured host")
    offenders = sorted({url for url in requests if not allowed_origin(url, origins)})
    if offenders:
        problems.append(f"request(s) to hosts other than the configured source: {offenders}")
    credit = page.locator(".leaflet-control-attribution").text_content() or ""
    if MOCK_ATTRIBUTION not in credit:
        problems.append("the configured source's credit is not rendered on the map")
    if not problems:
        print(f"  {len(TileHandler.served)} tile requests, to the configured host only")
    return problems


def phase_unreachable(page: Any, requests: list[str], origin: str, origins: set[str]) -> list[str]:
    open_map_step(page, origin, "Unreachable tiles")
    problems: list[str] = []
    try:
        page.get_by_text("could not be reached").wait_for(timeout=20_000)
    except Exception:
        problems.append("no degradation notice after the tile source failed")
    if page.locator(".sitemap__land").count() == 0:
        problems.append("bundled outlines not rendered after tile failure")
    # The questionnaire must remain fully usable (D-049.1).
    page.get_by_role("button", name="Skip the map").click()
    try:
        page.get_by_role("heading", name="Project information").wait_for(timeout=5_000)
    except Exception:
        problems.append("questionnaire not reachable after tile failure")
    if not problems:
        print("  degraded to the bundled outlines; questionnaire usable")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-python", required=True, help="python with the app installed")
    parser.add_argument(
        "--dist", required=True, help="frontend build to serve, or '-' for the wheel's own"
    )
    args = parser.parse_args()

    from playwright.sync_api import sync_playwright

    tile_port = free_port()
    tile_server = http.server.ThreadingHTTPServer(("127.0.0.1", tile_port), TileHandler)
    threading.Thread(target=tile_server.serve_forever, daemon=True).start()
    tile_origin = f"http://127.0.0.1:{tile_port}"
    dead_origin = f"http://127.0.0.1:{free_port()}"  # bound to nothing: connection refused

    phases: list[tuple[str, Callable[..., list[str]], dict[str, str], set[str]]] = [
        (
            "A: unconfigured — complete assessment, zero external requests",
            phase_unconfigured,
            {},
            set(),
        ),
        (
            "B: configured — tiles from the configured host, and only it",
            phase_configured,
            {
                "NATURE_COOLING_TILE_URL": f"{tile_origin}/{{z}}/{{x}}/{{y}}.png",
                "NATURE_COOLING_TILE_ATTRIBUTION": MOCK_ATTRIBUTION,
            },
            {tile_origin},
        ),
        (
            "C: unreachable — degrades to the bundled outlines",
            phase_unreachable,
            {
                "NATURE_COOLING_TILE_URL": f"{dead_origin}/{{z}}/{{x}}/{{y}}.png",
                "NATURE_COOLING_TILE_ATTRIBUTION": MOCK_ATTRIBUTION,
            },
            {dead_origin},
        ),
    ]

    failures: list[str] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", headless=True)
        for title, phase, env, extra_origins in phases:
            print(f"Phase {title}")
            with tempfile.TemporaryDirectory() as data_dir:
                server = Server(
                    args.server_python,
                    args.dist,
                    free_port(),
                    {**env, "XDG_DATA_HOME": data_dir},
                )
                try:
                    context = browser.new_context()
                    page = context.new_page()
                    requests: list[str] = []
                    page.on("request", lambda request, log=requests: log.append(request.url))
                    failures.extend(
                        f"{title}: {problem}"
                        for problem in phase(
                            page, requests, server.origin, extra_origins | {server.origin}
                        )
                    )
                    context.close()
                finally:
                    server.stop()
        browser.close()
    tile_server.shutdown()

    if failures:
        print("\nFAIL: the runtime request gate found:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1
    print("\nOK: runtime request gate passed all three phases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
