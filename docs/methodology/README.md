# Methodology & Evidence Base

This directory holds the scientific backbone of the tool, produced and maintained in Phase 1 and kept in lock-step with `config/` (matching version stamps).

## Contents

| Document | Purpose |
|---|---|
| **[METHODOLOGY.md](METHODOLOGY.md)** | The expert-facing Methodology Report — the document to send to external reviewers |
| **[EVIDENCE-TABLES.md](EVIDENCE-TABLES.md)** | Per-typology derivations: evidence consulted → value adopted → reasoning |
| **[BIBLIOGRAPHY.md](BIBLIOGRAPHY.md)** | Every source with its verification status |

## The Methodology Report (`METHODOLOGY.md`) — delivered 2026-07-30

A standalone, expert-facing document — required by UNEP — that describes the complete methodology and how the calculation engine works, written so it can be sent to external reviewers as-is. **Every quantitative claim carries a citation to peer-reviewed literature or an authoritative institutional source.** No value in the tool exists that this report does not derive and defend.

Structure:

1. **Purpose, scope, and positioning** — screening-level instrument; what it is and is not; intended use and users.
2. **Conceptual framework** — three-layer structure (baseline → NbS performance → impact & feasibility); relation to published prioritisation frameworks (e.g., Norton et al. 2015) and composite-indicator practice (OECD/JRC Handbook).
3. **Indicators and scoring** — every input, its normalisation, and every formula: heat exposure (data-rich and data-poor paths), vulnerability, Heat Priority Index, suitability, adjustment factors, cooling potential, energy/GHG, costs and payback, co-benefits, gender & equity, final aggregation. Includes the **effective-weights table** (declaring the deliberate equity-forward weighting, decision D-007).
4. **The NbS typology library** — the 18 cooling archetypes with their evidence tables (see below) and the 110 catalogue typologies inheriting them; derivation of every cooling range, energy factor, and cost default; the suitability matrix (D-009); the package combination rules.
5. **Uncertainty and confidence** — ranges-not-points principle; the °C literature-envelope clipping rule (D-008); branched confidence model; treatment of missing data and defaults.
6. **Sensitivity analysis** — weight variation (±25%) and ranking stability across the golden scenarios (D-013).
7. **Limitations and responsible use** — explicit boundary with microclimate simulation and detailed design; misuse cases.
8. **References** — full bibliography with DOIs.

## Evidence tables (`EVIDENCE-TABLES.md`) — delivered 2026-07-30

For each of the 18 cooling archetypes: evidence consulted (with the metric each source measures) → adopted value → the reasoning connecting them → applicability caveats. Every one of the 110 catalogue typologies inherits exactly one archetype, and every result names the evidence class its numbers came from. Where studies conflict, the conservative range is adopted and the conflict is documented rather than smoothed over. These tables are the direct source for the `sources:` arrays in [`config/nbs_typologies.yaml`](../../config/nbs_typologies.yaml).

Delivered as a single consolidated document rather than 14 separate files: the tables are short, they are read comparatively, and the per-value citations live in configuration anyway.

## Working rules

- Citations are verified against the publisher record, an institutional repository, or an indexing service before inclusion — never cited from memory or second-hand. [BIBLIOGRAPHY.md](BIBLIOGRAPHY.md) records the verification level of each entry, and configuration confidence reflects it.
- Where evidence for a value could not be found, the tool either omits the value (costs) or ships it with an explicit low-confidence flag (green façade, bioswale, courtyard greening). Gaps are stated, not filled.
- The report is versioned with the methodology: config `version:` and report version move together, enforced by `tests/test_config.py` (D-012).
- Citation integrity is machine-checked: every `sources[].key` in configuration must exist in the bibliography, or the configuration fails to load and CI fails.
