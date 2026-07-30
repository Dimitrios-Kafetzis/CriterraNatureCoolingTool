"""Golden-scenario regression tests.

Each JSON file in ``tests/scenarios/`` stores one realistic input, a
hand-derived set of expected outputs, and the derivation that produced them.
The expected values were computed by hand from the Methodology Report and the
configuration — never by running the engine — so these tests are armour
against unintended methodology drift, not a tautology.

``expected`` maps dotted result paths (with integer list indices) to exact
values, compared with strict equality against the engine's rounded outputs.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from nature_cooling.engine import AssessmentInput, run_assessment

SCENARIO_DIR = Path(__file__).parent / "scenarios"
SCENARIOS = sorted(SCENARIO_DIR.glob("*.json"))


def _dig(tree: Any, dotted: str) -> Any:
    node = tree
    for part in dotted.split("."):
        node = node[int(part)] if isinstance(node, list) else node[part]
    return node


def test_scenario_set_is_complete():
    assert len(SCENARIOS) == 20


@pytest.mark.parametrize("path", SCENARIOS, ids=lambda p: p.stem)
def test_scenario(path: Path, config):
    scenario = json.loads(path.read_text(encoding="utf-8"))
    result = run_assessment(AssessmentInput(**scenario["input"]), config)
    dumped = result.model_dump()

    mismatches = []
    for dotted, expected in scenario["expected"].items():
        actual = _dig(dumped, dotted)
        if actual != expected:
            mismatches.append(f"{dotted}: expected {expected!r}, engine produced {actual!r}")
    assert not mismatches, f"{path.stem}:\n" + "\n".join(mismatches)

    for fragment in scenario.get("recommendation_contains", []):
        assert fragment in result.recommendation, (
            f"{path.stem}: recommendation missing {fragment!r}"
        )
    for fragment in scenario.get("recommendation_not_contains", []):
        assert fragment not in result.recommendation, (
            f"{path.stem}: recommendation unexpectedly contains {fragment!r}"
        )
