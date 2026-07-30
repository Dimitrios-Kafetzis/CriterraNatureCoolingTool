# Methodology & Evidence Base

This directory holds the scientific backbone of the tool, produced and maintained in Phase 1 and kept in lock-step with `config/` (matching version stamps).

## The Methodology Report (`METHODOLOGY.md` — Phase 1 deliverable)

A standalone, expert-facing document — required by UNEP — that describes the complete methodology and how the calculation engine works, written so it can be sent to external reviewers as-is. **Every quantitative claim carries a citation to peer-reviewed literature or an authoritative institutional source.** No value in the tool exists that this report does not derive and defend.

Planned structure:

1. **Purpose, scope, and positioning** — screening-level instrument; what it is and is not; intended use and users.
2. **Conceptual framework** — three-layer structure (baseline → NbS performance → impact & feasibility); relation to published prioritisation frameworks (e.g., Norton et al. 2015) and composite-indicator practice (OECD/JRC Handbook).
3. **Indicators and scoring** — every input, its normalisation, and every formula: heat exposure (data-rich and data-poor paths), vulnerability, Heat Priority Index, suitability, adjustment factors, cooling potential, energy/GHG, costs and payback, co-benefits, gender & equity, final aggregation. Includes the **effective-weights table** (declaring the deliberate equity-forward weighting, decision D-007).
4. **The NbS typology library** — the 14 typologies with their evidence tables (see below); derivation of every cooling range, energy factor, and cost default; the suitability matrix (D-009).
5. **Uncertainty and confidence** — ranges-not-points principle; the °C literature-envelope clipping rule (D-008); branched confidence model; treatment of missing data and defaults.
6. **Sensitivity analysis** — weight variation (±25%) and ranking stability across the golden scenarios (D-013).
7. **Limitations and responsible use** — explicit boundary with microclimate simulation and detailed design; misuse cases.
8. **References** — full bibliography with DOIs.

## Evidence tables (`evidence/` — Phase 1 deliverable)

One file per typology (14 total): adopted value → supporting studies with their quantitative findings and DOIs → applicability caveats (climate zone, scale, maturity). Where studies conflict, the conservative range is adopted and the conflict is documented. These tables are the direct source for the `sources:` arrays in `config/nbs_typologies.yaml`.

## Working rules

- Citations must be verified against the actual publications before inclusion — never cited from memory or second-hand.
- Anchor candidates identified at project kickoff (to be verified in Phase 1): meta-analyses and reviews of urban green/blue space cooling (Bowler et al. 2010; Knight et al. 2021; Gunawardena et al. 2017; Santamouris 2014; Rahman et al. 2020; Zölch et al. 2016), NbS–energy linkages (Akbari et al. 2001; Ko 2018; Besir & Cuce 2018), heat vulnerability indices (Reid et al. 2009; Cutter et al. 2003), IPCC AR6 WGII (urban risk framing), and NbS costing catalogues (World Bank 2021).
- The report is versioned with the methodology: config `version:` and report version move together (D-012).
