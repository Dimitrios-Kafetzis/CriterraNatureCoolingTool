"""Golden-scenario regression tests.

Each JSON file in ``tests/scenarios/`` stores one realistic input, a set of
expected outputs derived independently of the engine, and the derivation that
produced them. The expected values were computed from the Methodology Report's
formulas and the configuration files by a second implementation — never by
recording the engine's own output — so these tests are armour against
unintended methodology drift, not a tautology. Every value in every scenario is
one on which two independent implementations agree.

``expected`` maps dotted result paths (with integer list indices) to exact
values, compared with strict equality against the engine's rounded outputs.

The final tests in this module are not regression tests but **guards**: they
assert the two retrieval findings of the 2026.08.04 library directly, so that a
future edit cannot quietly undo them by changing a configuration value that no
individual scenario happens to notice.
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
    assert len(SCENARIOS) == 24


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


# --- Guards on the 2026.08.04 retrieval findings ---------------------------


def test_small_constructed_water_is_never_interpolated_toward_large_water(config):
    """The two water archetypes are separate bodies of study (D-044, D-045).

    ``jacobs2020``, ``yao2023b`` and ``ampatzidis2020`` establish small
    constructed features at a few tenths of a degree; ``volker2013`` and
    ``keravec2026`` put open water an order of magnitude higher. The
    size-threshold literature connecting them is land-surface-temperature only,
    so no published curve joins the two on air temperature — and the engine
    must therefore never move an entry from one band toward the other because
    its site is large. This test fails the moment anyone adds an area-based
    interpolation, however reasonable it looks.
    """
    small = config.typologies.by_type("constructed_wetland")
    large = config.typologies.by_type("urban_lake_restoration")
    assert small.archetype == "small_constructed_water"
    assert large.archetype == "large_water_body"
    assert (small.temp_reduction_min_c, small.temp_reduction_max_c) == (0.0, 1.0)

    tiny = run_assessment(
        AssessmentInput(
            assessment_scale="site",
            site_area_m2=200,
            climate_zone="temperate",
            nbs_type=["constructed_wetland"],
        ),
        config,
    )
    enormous = run_assessment(
        AssessmentInput(
            assessment_scale="site",
            site_area_m2=500_000,
            climate_zone="temperate",
            nbs_type=["constructed_wetland"],
        ),
        config,
    )
    # A site 2 500 times larger must not raise the ceiling at all: area moves
    # the suitability sub-score, never the evidence class.
    assert tiny.cooling.delta_t_max_c == enormous.cooling.delta_t_max_c
    assert enormous.cooling.delta_t_max_c <= 1.0
    assert enormous.cooling.delta_t_max_c < large.temp_reduction_max_c


def test_shading_devices_figure_does_not_transfer_to_pergola_scale(config):
    """``keravec2026``'s 2.0 C shading-devices figure is area-scale (D-044).

    It aggregates shading over areas where the cooled air volume persists
    against advection; a pergola shades roughly 10 m². Adopting it here would
    rate a pergola above tree canopy measured at 1.42 C by ``ouyang2024``. The
    vegetated shade structure therefore takes its ceiling from ``chafer2020``'s
    measured vine-against-bare-frame comparison and stays low confidence.
    """
    pergola = config.typologies.archetype_by_name("vegetated_shade_structure")
    assert (pergola.temp_reduction_min_c, pergola.temp_reduction_max_c) == (0.0, 2.5)
    assert pergola.evidence_confidence == "low"

    cited = {source.key for source in pergola.sources}
    assert "keravec2026" not in cited, (
        "the area-scale shading-devices figure must not be cited for pergola scale"
    )
    assert {"chafer2020", "ouyang2024", "colter2019"} <= cited

    # The same figure IS admissible at plaza scale, where the scale matches.
    plaza = config.typologies.archetype_by_name("permeable_shaded_hardscape")
    assert "keravec2026" in {source.key for source in plaza.sources}


def test_a_package_temperature_is_never_the_sum_of_its_components(config):
    """The capped-never-summed rule, stated as a property (D-038, D-044.4).

    Checked across every scenario rather than on one example: for any package,
    the reported range must equal exactly one component's, and must never
    exceed the widest component's ceiling.
    """
    for path in SCENARIOS:
        scenario = json.loads(path.read_text(encoding="utf-8"))
        result = run_assessment(AssessmentInput(**scenario["input"]), config)
        ceilings = [component.cooling.delta_t_max_c for component in result.components]
        assert result.cooling.delta_t_max_c == max(
            c for c in ceilings if c == result.cooling.delta_t_max_c
        ), path.stem
        assert result.cooling.delta_t_max_c <= max(ceilings), path.stem
        if len(ceilings) > 1:
            assert result.cooling.delta_t_max_c < sum(ceilings), path.stem
