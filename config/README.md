# Methodology Configuration

This directory is the tool's methodology expressed **as data**. Every scoring rule the engine applies — typology performance values, aggregation weights, adjustment factors, qualitative mappings, country defaults, recommendation templates — lives here as schema-validated, versioned YAML. Code never hard-codes a methodology value.

**Populated in Phase 1** (literature-grounding phase), in lock-step with the [Methodology Report](../docs/methodology/README.md).

Rules that CI will enforce:

1. Every file carries a top-level `version:` (date-stamped, e.g. `2026.08.01`); any change bumps it.
2. Every performance value (cooling ranges, energy factors, cost defaults, emission factors) carries a `sources:` array — citation, DOI/URL, and the quantitative finding it supports. **Uncited values fail CI.**
3. Schemas are validated at engine load and in CI; the engine refuses to start on an invalid config.
4. A methodology `version` change must be accompanied by a matching update to the Methodology Report.

Planned files: `nbs_typologies.yaml` · `weights.yaml` · `adjustment_factors.yaml` · `input_mapping.yaml` · `country_defaults.yaml` · `recommendation_templates.yaml`
