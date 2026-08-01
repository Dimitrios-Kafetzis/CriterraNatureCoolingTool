# Methodology Configuration

This directory is the tool's methodology expressed **as data**. Every scoring rule the engine applies — typology performance values, aggregation weights, adjustment factors, qualitative mappings, country defaults, recommendation templates — lives here as schema-validated, versioned YAML. Code never hard-codes a methodology value.

**Populated in Phase 1** (literature-grounding phase), in lock-step with the [Methodology Report](../docs/methodology/README.md).

Since `2026.08.04` the typology library has **two levels** (D-044). An **archetype** is a cited evidence class carrying every performance value and the citations behind it; a **typology** is one of the 110 curated catalogue entries, carrying identity, family, availability and the one archetype it inherits — and no performance value of its own. Rule 2 below is therefore enforced on the *resolved* library: an entry's numbers must be cited wherever they actually come from.

Rules that CI will enforce:

1. Every file carries a top-level `version:` (date-stamped, e.g. `2026.08.01`); any change bumps it.
2. Every performance value (cooling ranges, energy factors, cost defaults, emission factors) carries a `sources:` array — citation, DOI/URL, and the quantitative finding it supports. **Uncited values fail CI.**
3. Schemas are validated at engine load and in CI; the engine refuses to start on an invalid config.
4. A methodology `version` change must be accompanied by a matching update to the Methodology Report.

Files: `nbs_typologies.yaml` (archetypes + entries) · `availability.yaml` (which entries are offered, and what an unanswered question means) · `weights.yaml` · `adjustment_factors.yaml` · `input_mapping.yaml` · `derived_scores.yaml` · `energy_model.yaml` · `country_defaults.yaml` · `recommendation_templates.yaml`

**Availability is configuration, not code.** Which interventions a site is offered is decided by the per-entry conditions in `nbs_typologies.yaml` and the per-condition policy in `availability.yaml`; the engine holds the mechanism and the frontend computes no rule of its own. Availability gates selection and **feeds no score** (D-044.1) — a property the test suite asserts by scoring one site twice, with every availability question answered and with none of them answered, and requiring byte-identical output.
