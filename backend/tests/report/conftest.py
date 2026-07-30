"""Report test fixtures: stored-shaped assessments built from the golden set.

The builders render stored data verbatim, so the fixtures are what storage
holds — a project name, a label, a ``created_at`` stamp, the input JSON, and
the result JSON an engine run produced. Tests may edit the JSON copies
directly (adding warnings, blanking assumptions): the builder's contract is
the stored document, not the engine.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from nature_cooling.engine import run_assessment
from nature_cooling.engine.config import MethodologyConfig
from nature_cooling.engine.models import AssessmentInput

SCENARIO_DIR = Path(__file__).parent.parent / "scenarios"
SCENARIO_NAMES = sorted(path.stem for path in SCENARIO_DIR.glob("*.json"))

CREATED_AT = "2026-07-30T20:22:54.541303+00:00"
PROJECT_NAME = "Riverside school quarter"


@pytest.fixture(scope="session")
def scenarios(config: MethodologyConfig) -> dict[str, dict[str, Any]]:
    """Every golden scenario as a stored assessment: input plus result JSON."""
    stored = {}
    for name in SCENARIO_NAMES:
        document = json.loads((SCENARIO_DIR / f"{name}.json").read_text(encoding="utf-8"))
        inp: dict[str, Any] = document["input"]
        result = run_assessment(AssessmentInput.model_validate(inp), config)
        stored[name] = {"input": inp, "result": result.model_dump(mode="json")}
    return stored


@pytest.fixture(scope="session")
def render_args(scenarios: dict[str, dict[str, Any]]) -> Any:
    """Keyword arguments for one scenario's report build."""

    def args(name: str) -> dict[str, Any]:
        return {
            "project_name": PROJECT_NAME,
            "label": name,
            "created_at": CREATED_AT,
            "inp": dict(scenarios[name]["input"]),
            "result": json.loads(json.dumps(scenarios[name]["result"])),
        }

    return args
