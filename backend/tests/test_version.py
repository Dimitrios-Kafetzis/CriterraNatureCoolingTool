"""Phase 0 smoke test: the package imports and declares a semver version."""

import re

import nature_cooling


def test_package_declares_semver_version() -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+([.-].+)?", nature_cooling.__version__)
