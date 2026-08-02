"""The deployment tile configuration (v2.2, D-049.2).

The contract under test: an unconfigured deployment serves no tile source and
therefore makes no third-party request; a configured one serves the template
*with* the credit its licence requires; and a half-configuration — a URL
without its attribution, or a template the browser could not expand — refuses
to start rather than serving an uncredited or silently broken map.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from nature_cooling.api import create_app
from nature_cooling.api.tiles import (
    TILE_ATTRIBUTION_VAR,
    TILE_URL_VAR,
    TileConfig,
    TileConfigError,
    tile_config_from_env,
)
from nature_cooling.engine.config import MethodologyConfig

TEMPLATE = "https://tiles.example.com/{z}/{x}/{y}.png?key=abc"
CREDIT = "© OpenStreetMap contributors © ExampleTiles"


def test_no_environment_means_no_tile_source() -> None:
    assert tile_config_from_env({}) is None


def test_a_full_configuration_is_returned_verbatim() -> None:
    config = tile_config_from_env({TILE_URL_VAR: TEMPLATE, TILE_ATTRIBUTION_VAR: CREDIT})
    assert config == TileConfig(url_template=TEMPLATE, attribution=CREDIT)


def test_whitespace_only_values_count_as_unset() -> None:
    assert tile_config_from_env({TILE_URL_VAR: "  ", TILE_ATTRIBUTION_VAR: "\t"}) is None


def test_a_url_without_its_attribution_refuses_to_start() -> None:
    """The v2.1 attribution defect, ruled out structurally (D-049.2)."""
    with pytest.raises(TileConfigError, match="attribution"):
        tile_config_from_env({TILE_URL_VAR: TEMPLATE})


def test_an_attribution_without_a_url_refuses_to_start() -> None:
    with pytest.raises(TileConfigError, match="Set both, or neither"):
        tile_config_from_env({TILE_ATTRIBUTION_VAR: CREDIT})


def test_a_non_http_url_is_refused() -> None:
    with pytest.raises(TileConfigError, match="http"):
        tile_config_from_env(
            {TILE_URL_VAR: "ftp://tiles.example.com/{z}/{x}/{y}.png", TILE_ATTRIBUTION_VAR: CREDIT}
        )


@pytest.mark.parametrize(
    "template",
    [
        "https://tiles.example.com/static.png",
        "https://tiles.example.com/{z}/{x}.png",
        "https://tiles.example.com/{x}/{y}.png",
    ],
)
def test_a_template_missing_placeholders_is_refused(template: str) -> None:
    with pytest.raises(TileConfigError, match="placeholders"):
        tile_config_from_env({TILE_URL_VAR: template, TILE_ATTRIBUTION_VAR: CREDIT})


def test_the_app_factory_reads_the_environment_once(
    config: MethodologyConfig,
    storage_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(TILE_URL_VAR, TEMPLATE)
    monkeypatch.setenv(TILE_ATTRIBUTION_VAR, CREDIT)
    client = TestClient(create_app(config=config, storage_root=storage_root))
    body = client.get("/api/meta").json()
    assert body["tiles"] == {"url_template": TEMPLATE, "attribution": CREDIT}


def test_meta_serves_an_explicitly_injected_configuration(
    config: MethodologyConfig, storage_root: Path
) -> None:
    """The browser learns the deployer's choice from /api/meta (D-049.2); the
    server itself never requests a tile (D-049.3)."""
    app = create_app(
        config=config,
        storage_root=storage_root,
        tiles=TileConfig(url_template=TEMPLATE, attribution=CREDIT),
    )
    body = TestClient(app).get("/api/meta").json()
    assert body["tiles"] == {"url_template": TEMPLATE, "attribution": CREDIT}


def test_a_broken_environment_fails_the_app_at_creation(
    config: MethodologyConfig,
    storage_root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Startup is the right time to fail: a deployment misconfigured into
    uncredited imagery must never come up quietly."""
    monkeypatch.setenv(TILE_URL_VAR, TEMPLATE)
    monkeypatch.delenv(TILE_ATTRIBUTION_VAR, raising=False)
    with pytest.raises(TileConfigError):
        create_app(config=config, storage_root=storage_root)
