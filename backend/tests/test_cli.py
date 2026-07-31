"""The ``nature-cooling`` console script (D-035).

uvicorn ships behind the ``serve`` extra and is not part of the dev
environment, so both branches — present and absent — are exercised against
``sys.modules`` stubs rather than a real install.
"""

from __future__ import annotations

import sys
import types

import pytest

from nature_cooling import cli


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
