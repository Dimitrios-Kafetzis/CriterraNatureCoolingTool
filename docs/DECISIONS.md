# Decision Log

Every load-bearing decision for the Nature for Cooling Rapid Assessment Tool, with rationale. Decisions are numbered and never deleted; superseding a decision requires a new entry referencing the old one.

Source material: the Criterra architecture specification and methodology discussion archive (April–May 2026), which catalogued 36 open questions (OQ-01…OQ-36). Decisions below resolve the ones relevant to v1.

---

## D-001 — Standalone global tool (2026-07-30)

The tool is a Criterra-owned, open tool usable for **any city worldwide**. The UNEP Nature for Cooling Challenge pilot countries (Brazil, Cambodia, Côte d'Ivoire) are supported through optional country-default configuration, not hard-coded scope. *(Resolves the pilot-scoping ambiguity left by the v2 design deck.)*

## D-002 — GIS workflow deferred from v1 (2026-07-30)

The city-scale GIS hotspot workflow (heat exposure / vulnerability / combined priority maps) is **not** part of the v1 codebase. The engine retains the `lst_anomaly_c` input so GIS-derived data can feed site assessments. See [V2-VISION.md](V2-VISION.md).

## D-003 — Tech stack: Python engine + FastAPI + React/TypeScript (2026-07-30)

- **Calculation engine:** pure Python 3.11+, pip-installable, config-driven, no I/O in scoring code, 100% test coverage target. *(Supersedes the original spec's Streamlit assumption — OQ-25.)*
- **API:** FastAPI, a thin stateless wrapper over the engine.
- **Frontend:** React + TypeScript (Vite), styled with the criterra.eu design tokens.
- Rationale: a proper product-grade web app was requested; the engine stays independently usable (Python API, CLI, future Excel parity).

## D-004 — License: Apache-2.0 (2026-07-30)

Permissive with patent grant; institution-friendly. Criterra's differentiation is calibration expertise and delivery, not code secrecy. *(Resolves OQ-33.)*

## D-005 — v1 scope boundaries (2026-07-30)

**In v1:** single-site assessment; **same-site intervention comparison (A/B/C side by side)** (resolves OQ-02 for UC-2); three personas — planner, developer/consultant, researcher/NGO (OQ-01: funder view deferred); local-first storage.
**Deferred to v2** (documented in [V2-VISION.md](V2-VISION.md)): climate-responsive planting/species guidance; multi-site portfolio mode (UC-3); batch CSV ingestion (UC-7, OQ-03); GIS workflow; multilingual UI (OQ-35); multi-user/cloud storage (OQ-31); funder report view; map-click prefill (OQ-24).

## D-006 — v2 vision is a maintained document (2026-07-30)

Deferred scope is not just a backlog: [V2-VISION.md](V2-VISION.md) is kept presentation-ready so the v2 vision can be communicated to investors and funders at any time.

## D-007 — Equity-forward weighting, openly documented (2026-07-30)

Vulnerability contributes to the final score twice by design: inside the Heat Priority Index (0.40 weight) and directly (0.15). Effective final-score weights are therefore **vulnerability 0.25 vs heat exposure 0.15**. This is a deliberate values choice — the tool prioritises *who is affected* slightly above *how hot it is* — and is declared, with the effective-weights table, in the Methodology Report. No hidden double counting.

## D-008 — Temperature ranges are clipped to the literature envelope (2026-07-30)

The site adjustment factor (0.5–1.2) scales the 0–100 Cooling Potential Score, but the reported °C reduction range is always **clipped to the typology's literature-supported envelope**. Site conditions can degrade performance below the envelope; they can never produce a °C claim exceeding published evidence. *(Fixes the inflation defect in the original formula §10.10.)*

## D-009 — Hard suitability flags: warn, never silently score (2026-07-30)

Each typology has a suitability matrix (minimum area, soil, water, climate zones — resolves OQ-14). Disqualifying conditions trigger a prominent **"Not suitable for this site — [reason]"** flag in results and recommendation text. The assessment still computes transparently, but an unsuitable intervention is never presented as a plain score.

## D-010 — Cost feasibility is derived, not user-entered (2026-07-30)

`cost_feasibility_score` = documented function of simple-payback bracket × implementation complexity × maintenance intensity. No new user input. *(Resolves OQ-19.)*

## D-011 — Methodology open-question resolutions (2026-07-30)

| OQ | Resolution |
|---|---|
| OQ-05 | LST anomaly → score: linear, 0 °C → 0, +10 °C → 100, clamped |
| OQ-06 | No maturity discount in v1; add a **time-to-benefit** output derived from `expected_maturity_period` |
| OQ-09 | **Branched confidence**: separate confidence per output block (cooling / energy / economic / equity) |
| OQ-10 | Heat-index improvement buckets: <0.5 °C low, 0.5–1.5 medium, >1.5 high (midpoint of adjusted range) |
| OQ-11 | Investment readiness derived: payback bracket × complexity × energy confidence |
| OQ-16/17 | All adjustment conditions (canopy, soil-water, scale, climate) and space suitability **derived from existing inputs** via documented rules — no new user-facing fields |
| OQ-18 | Co-benefit sub-scores: typology defaults (each cited) with user override |
| OQ-12 | Recommendation text: deterministic template composer — no LLM in the scoring/reporting path |
| OQ-29 | Single global weight set in v1 + published sensitivity analysis (±25% weight variation, ranking stability over golden scenarios) |
| OQ-15 | Methodology version changes require explicit re-run; results always display their methodology version |
| OQ-04/08 | Cover-percentage sum >105% warns, doesn't block; validation severities: errors + warnings only |
| OQ-13 | Report: 2-page PDF (summary + detail) |

## D-012 — Expert Methodology Report is a first-class deliverable (2026-07-30)

Required by UNEP: a standalone, expert-facing Methodology Report — fully cited with peer-reviewed sources — describing the methodology and how the engine works, shareable with external reviewers. Produced in Phase 1, versioned in [docs/methodology/](methodology/), kept in lock-step with `config/` (same version stamp). *(Resolves OQ-20 as a hard requirement.)*

## D-013 — Weights are expert-calibrated and defended by sensitivity analysis (2026-07-30)

Aggregation weights cannot be "derived" from literature and we do not pretend otherwise. They are declared as expert judgment following composite-indicator practice (OECD/JRC Handbook), and defended empirically via the published sensitivity analysis (see D-011/OQ-29).
