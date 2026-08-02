"""Deployment-level tile configuration (v2.2, D-049).

This is the first runtime configuration this application has ever had, and it
is deliberately the smallest one that serves the deployment model: an operator
who runs this tool for their own users may name a raster tile source once, for
the whole deployment, instead of every user pasting a URL per visit. An
operator who configures nothing gets exactly the v2.1 behaviour — the bundled
offline map, a per-user opt-in, and **no third-party request of any kind**
(D-049.1).

Two environment variables, read once at application creation (D-049.2):

    NATURE_COOLING_TILE_URL          a {z}/{x}/{y} template, e.g.
                                     https://tiles.example.com/{z}/{x}/{y}.png?key=…
    NATURE_COOLING_TILE_ATTRIBUTION  the credit line that source requires, e.g.
                                     "© OpenStreetMap contributors © ExampleTiles"

The attribution is not optional. A tile URL without its credit refuses to
start: most configurable sources are OpenStreetMap-derived, ODbL §4.3 requires
a notice on public use, and v2.1 shipped the defect this rules out — imagery
on screen with no credit anywhere. Carrying the credit beside the URL in one
configuration unit is what makes it impossible to omit (D-049.2).

The server itself never requests a tile. The template is handed to the
browser through ``GET /api/meta``, and the browser talks to the tile host
directly (D-049.3) — the backend has never made an outbound network request
and still never does.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

TILE_URL_VAR = "NATURE_COOLING_TILE_URL"
TILE_ATTRIBUTION_VAR = "NATURE_COOLING_TILE_ATTRIBUTION"


class TileConfigError(ValueError):
    """The deployment's tile configuration is unusable, and says why."""


@dataclass(frozen=True)
class TileConfig:
    """A deployer-configured tile source: the template and its required credit."""

    url_template: str
    attribution: str


def tile_config_from_env(environ: dict[str, str] | None = None) -> TileConfig | None:
    """Read and validate the deployment's tile configuration, if any.

    Returns ``None`` for the unconfigured deployment — the default, in which
    the application makes no third-party request. Raises ``TileConfigError``
    rather than serving a half-configuration: a URL without its attribution
    would recreate the v2.1 attribution defect at deployment scale, and a
    template the browser cannot expand would fail silently per tile.
    """
    env = environ if environ is not None else dict(os.environ)
    url = env.get(TILE_URL_VAR, "").strip()
    attribution = env.get(TILE_ATTRIBUTION_VAR, "").strip()

    if not url and not attribution:
        return None
    if url and not attribution:
        raise TileConfigError(
            f"{TILE_URL_VAR} is set but {TILE_ATTRIBUTION_VAR} is not. The attribution "
            f"is the credit line your tile source requires on the map (for "
            f"OpenStreetMap-derived tiles, at least '© OpenStreetMap contributors'); "
            f"it is required so that configured imagery is never displayed uncredited. "
            f"See docs/HOSTING.md."
        )
    if attribution and not url:
        raise TileConfigError(
            f"{TILE_ATTRIBUTION_VAR} is set but {TILE_URL_VAR} is not; nothing would "
            f"display the credit. Set both, or neither."
        )
    if not url.startswith(("https://", "http://")):
        raise TileConfigError(f"{TILE_URL_VAR} must be an http(s) URL template; got {url!r}.")
    missing = [token for token in ("{z}", "{x}", "{y}") if token not in url]
    if missing:
        raise TileConfigError(
            f"{TILE_URL_VAR} must contain the {{z}}, {{x}} and {{y}} placeholders the "
            f"browser expands per tile; {url!r} is missing {', '.join(missing)}."
        )
    return TileConfig(url_template=url, attribution=attribution)
