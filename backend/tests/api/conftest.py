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
    # tiles=None pins the unconfigured deployment (D-049.1) regardless of what
    # the developer's shell exports; the configured cases build their own app.
    return TestClient(create_app(config=config, storage_root=storage_root, tiles=None))


# A draft touching every duplication group: carried site/climate/vulnerability
# fields — including the four availability-only answers added by D-044.1, which
# describe the site and therefore travel with a duplicate — plus blanked
# intervention, co-benefit override, and cost/energy ones.
#
# ``nbs_type`` is a list since D-044.2: an assessment may propose a package.
# ``tree_avenue`` inherits the street_tree_canopy archetype, the same cited
# values the retired ``street_tree_planting`` typology carried, and is offered
# at neighbourhood scale for residential land use, so the fixture raises no
# availability warning of its own.
FULL_DRAFT: dict[str, object] = {
    "project_name": "Riverside pilot",
    "assessment_scale": "neighbourhood",
    "country": "GR",
    "site_area_m2": 6000.0,
    "existing_tree_canopy_percent": 15.0,
    "land_use": "residential",
    "climate_zone": "temperate",
    "includes_railway": "no",
    "existing_woodland": "unknown",
    "waterfront_type": "river",
    "productive_governance": ["community"],
    "heat_exposure_level": "high",
    "population_density": "high",
    "vulnerable_population_presence": "medium",
    "nbs_type": ["tree_avenue"],
    "intervention_area_m2": 900.0,
    "expected_maturity_period_years": 6.0,
    "implementation_complexity": "medium",
    "maintenance_intensity": "medium",
    "co_benefit_biodiversity": "high",
    "nearby_building_cooling_demand_relevant": "yes",
    "annual_cooling_energy_demand_kwh": 120000.0,
    "energy_price_per_kwh": 0.2,
    "capital_cost": 90000.0,
    "currency": "EUR",
}


@pytest.fixture()
def full_draft() -> dict[str, object]:
    return dict(FULL_DRAFT)


MINIMAL_INPUT: dict[str, object] = {
    "assessment_scale": "neighbourhood",
    "site_area_m2": 6000.0,
    "climate_zone": "temperate",
    "nbs_type": ["tree_avenue"],
}


@pytest.fixture()
def minimal_input() -> dict[str, object]:
    return dict(MINIMAL_INPUT)


# A three-component package (D-044.2): every entry is offered at neighbourhood
# scale for residential land use, so the package itself is what the assessment
# exercises, not an availability warning.
PACKAGE_DRAFT: dict[str, object] = {
    **FULL_DRAFT,
    "nbs_type": ["tree_avenue", "neighbourhood_park", "green_playground"],
}


@pytest.fixture()
def package_draft() -> dict[str, object]:
    return dict(PACKAGE_DRAFT)
