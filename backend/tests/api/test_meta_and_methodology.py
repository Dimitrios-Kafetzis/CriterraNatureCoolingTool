"""Contract tests: /api/meta, /api/typologies, /api/methodology."""

from __future__ import annotations

from fastapi.testclient import TestClient

import nature_cooling
from nature_cooling.engine.config import MethodologyConfig


def test_meta_reports_versions_and_licence(client: TestClient, config: MethodologyConfig) -> None:
    response = client.get("/api/meta")
    assert response.status_code == 200
    assert response.json() == {
        "engine_version": nature_cooling.__version__,
        "methodology_version": config.version,
        "license": "Apache-2.0",
    }


def test_typologies_returns_the_full_library(client: TestClient, config: MethodologyConfig) -> None:
    response = client.get("/api/typologies")
    assert response.status_code == 200
    body = response.json()
    assert body["version"] == config.version
    assert len(body["typologies"]) == len(config.typologies.typologies)
    first = body["typologies"][0]
    assert first["suitability"]["minimum_site_area_m2"] > 0
    assert first["sources"], "typology citations must be served"


def test_methodology_serves_the_loaded_configuration(
    client: TestClient, config: MethodologyConfig
) -> None:
    response = client.get("/api/methodology")
    assert response.status_code == 200
    body = response.json()
    assert body["version"] == config.version
    assert body["weights"] == config.weights
    assert body["adjustment_factors"] == config.adjustment_factors
    assert body["input_mapping"] == config.input_mapping
    assert body["energy_model"] == config.energy_model
    assert body["country_defaults"] == config.country_defaults
    assert body["derived_scores"] == config.derived_scores
    assert body["recommendation_templates"] == config.recommendation_templates
