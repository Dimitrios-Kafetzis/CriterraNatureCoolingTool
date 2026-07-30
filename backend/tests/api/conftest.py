"""API test fixtures: an app wired to a temporary store, never the real one."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from nature_cooling.api import create_app
from nature_cooling.engine.config import MethodologyConfig


@pytest.fixture()
def storage_root(tmp_path: Path) -> Path:
    return tmp_path / "projects"


@pytest.fixture()
def client(config: MethodologyConfig, storage_root: Path) -> TestClient:
    return TestClient(create_app(config=config, storage_root=storage_root))


MINIMAL_INPUT: dict[str, object] = {
    "assessment_scale": "neighbourhood",
    "site_area_m2": 6000.0,
    "climate_zone": "temperate",
    "nbs_type": "street_tree_planting",
}


@pytest.fixture()
def minimal_input() -> dict[str, object]:
    return dict(MINIMAL_INPUT)
