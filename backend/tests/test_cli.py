"""The ``nature-cooling`` console script (D-035).

uvicorn ships behind the ``serve`` extra and is not part of the dev
environment, so both branches — present and absent — are exercised against
``sys.modules`` stubs rather than a real install.
"""

from __future__ import annotations

import os
import sys
import types

import pytest

from nature_cooling import cli


@pytest.fixture(autouse=True)
def _clean_tile_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """The developer's shell must not leak a tile configuration into a test."""
    monkeypatch.delenv(cli.TILE_URL_VAR, raising=False)
    monkeypatch.delenv(cli.TILE_ATTRIBUTION_VAR, raising=False)


@pytest.fixture()
def uvicorn_stub(monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    calls: dict[str, object] = {}
    stub = types.ModuleType("uvicorn")

    def run(app: str, *, host: str, port: int) -> None:
        calls.update(app=app, host=host, port=port)

    stub.run = run  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "uvicorn", stub)
    return calls


def test_serve_wraps_uvicorn_with_defaults(uvicorn_stub: dict[str, object]) -> None:
    assert cli.main(["serve"]) == 0
    assert uvicorn_stub == {
        "app": "nature_cooling.api.main:app",
        "host": "127.0.0.1",
        "port": 8000,
    }


def test_serve_honours_host_and_port(uvicorn_stub: dict[str, object]) -> None:
    assert cli.main(["serve", "--host", "0.0.0.0", "--port", "9000"]) == 0
    assert uvicorn_stub["host"] == "0.0.0.0"
    assert uvicorn_stub["port"] == 9000


def test_serve_without_the_extra_names_the_install_command(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setitem(sys.modules, "uvicorn", None)
    assert cli.main(["serve"]) == 1
    assert 'pip install "criterra-nature-cooling[serve]"' in capsys.readouterr().err


def test_a_command_is_required() -> None:
    with pytest.raises(SystemExit) as excinfo:
        cli.main([])
    assert excinfo.value.code == 2


def test_serve_passes_the_tile_flags_through_the_environment(
    uvicorn_stub: dict[str, object], monkeypatch: pytest.MonkeyPatch
) -> None:
    """The flags are sugar over the environment variables (D-049.2): one
    mechanism underneath, two spellings on top."""
    monkeypatch.delenv(cli.TILE_URL_VAR, raising=False)
    monkeypatch.delenv(cli.TILE_ATTRIBUTION_VAR, raising=False)
    template = "https://tiles.example.com/{z}/{x}/{y}.png"
    credit = "© OpenStreetMap contributors © ExampleTiles"
    assert cli.main(["serve", "--tile-url", template, "--tile-attribution", credit]) == 0
    assert os.environ[cli.TILE_URL_VAR] == template
    assert os.environ[cli.TILE_ATTRIBUTION_VAR] == credit
    assert uvicorn_stub["app"] == "nature_cooling.api.main:app"


def test_serve_refuses_a_tile_url_without_its_attribution(
    uvicorn_stub: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A clean one-line error before uvicorn, not a startup traceback."""
    monkeypatch.delenv(cli.TILE_URL_VAR, raising=False)
    monkeypatch.delenv(cli.TILE_ATTRIBUTION_VAR, raising=False)
    exit_code = cli.main(["serve", "--tile-url", "https://t.example.com/{z}/{x}/{y}.png"])
    assert exit_code == 2
    assert "attribution" in capsys.readouterr().err
    assert uvicorn_stub == {}, "uvicorn must never start on a broken configuration"


def test_serve_validates_the_environment_it_did_not_set(
    uvicorn_stub: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A deployer's exported variables get the same startup check as flags."""
    monkeypatch.setenv(cli.TILE_URL_VAR, "https://t.example.com/broken.png")
    monkeypatch.setenv(cli.TILE_ATTRIBUTION_VAR, "© Example")
    assert cli.main(["serve"]) == 2
    assert "placeholders" in capsys.readouterr().err
    assert uvicorn_stub == {}
