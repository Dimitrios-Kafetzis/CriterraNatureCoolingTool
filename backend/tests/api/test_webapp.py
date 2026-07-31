"""The packaged web application: static serving and the SPA fallback (D-035).

The wheel embeds the production frontend build; ``create_app`` serves it at
``/`` beside ``/api`` on one origin (D-030). A repository checkout carries no
build, so the API serves alone — both discovery branches are covered here.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from nature_cooling.api import create_app
from nature_cooling.api import main as main_module
from nature_cooling.api import webapp as webapp_module
from nature_cooling.engine.config import MethodologyConfig

APP_SHELL = '<!doctype html><div id="root"></div>'


@pytest.fixture()
def webapp_dir(tmp_path: Path) -> Path:
    build = tmp_path / "webapp"
    (build / "assets").mkdir(parents=True)
    (build / "index.html").write_text(APP_SHELL, encoding="utf-8")
    (build / "assets" / "app.js").write_text("console.log('app');", encoding="utf-8")
    return build


@pytest.fixture()
def packaged_client(config: MethodologyConfig, tmp_path: Path, webapp_dir: Path) -> TestClient:
    app = create_app(config=config, storage_root=tmp_path / "projects", webapp_dir=webapp_dir)
    return TestClient(app)


def test_root_serves_the_app_shell(packaged_client: TestClient) -> None:
    response = packaged_client.get("/")
    assert response.status_code == 200
    assert 'id="root"' in response.text


def test_build_assets_are_served(packaged_client: TestClient) -> None:
    response = packaged_client.get("/assets/app.js")
    assert response.status_code == 200
    assert "console.log" in response.text


def test_client_side_routes_fall_back_to_the_shell(packaged_client: TestClient) -> None:
    """A deep link or reload on a frontend route must land on the app, not a 404."""
    response = packaged_client.get("/projects/3f6a2b52-0000-0000-0000-000000000000")
    assert response.status_code == 200
    assert 'id="root"' in response.text


def test_api_routes_are_unaffected_by_the_mount(packaged_client: TestClient) -> None:
    response = packaged_client.get("/api/meta")
    assert response.status_code == 200
    assert response.json()["methodology_version"]


def test_unknown_api_paths_stay_api_404s(packaged_client: TestClient) -> None:
    """An API typo must never be answered with the app shell."""
    response = packaged_client.get("/api/nonexistent")
    assert response.status_code == 404
    assert 'id="root"' not in response.text


def test_non_get_methods_are_not_swallowed_by_the_fallback(
    packaged_client: TestClient,
) -> None:
    assert packaged_client.post("/").status_code == 405


def test_checkout_carries_no_webapp(config: MethodologyConfig, tmp_path: Path) -> None:
    """Without an embedded build the API serves alone, as in development."""
    assert webapp_module.default_webapp_dir() is None
    client = TestClient(create_app(config=config, storage_root=tmp_path / "projects"))
    assert client.get("/").status_code == 404
    assert client.get("/api/meta").status_code == 200


def test_installed_wheel_discovers_the_embedded_build(
    config: MethodologyConfig,
    tmp_path: Path,
    webapp_dir: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(webapp_module, "bundled_data_dir", lambda: webapp_dir.parent)
    assert webapp_module.default_webapp_dir() == webapp_dir

    monkeypatch.setattr(main_module, "default_webapp_dir", lambda: webapp_dir)
    client = TestClient(create_app(config=config, storage_root=tmp_path / "projects"))
    response = client.get("/")
    assert response.status_code == 200
    assert 'id="root"' in response.text
