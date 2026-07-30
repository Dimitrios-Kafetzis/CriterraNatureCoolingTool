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

## D-014 — Typology values recalibrated against the literature (2026-07-30, Phase 1)

The draft typology values inherited from the architecture specification were uncited. Phase 1 re-derived every value from retrieved sources; see [methodology/EVIDENCE-TABLES.md](methodology/EVIDENCE-TABLES.md). Notable changes:

- **Mixed NbS package capped at 3.0 °C** (was 3.5 °C). No retrieved source quantifies super-additive cooling from combined measures; claiming a package beats its strongest component would be an unsourced assumption.
- **Street trees and shaded corridors raised to a 3.0 °C ceiling** (was 2.0/2.5 °C), supported by climate-differentiated estimates in `keravec2026`.
- **Green façade widened to 0.3–2.0 °C and marked low confidence** — sources conflict outright on this typology.
- **Green roof set to 0.1–1.0 °C** with an explicit street-level caveat: the larger published figures describe city-scale deployment, not one roof on one building.
- **Rain garden/bioswale marked low confidence** — no source quantifies its air-temperature cooling; its documented benefits are stormwater and biodiversity.
- All values are declared as **daytime, pedestrian-level air temperature**, never mixed with surface temperature or comfort indices.

## D-015 — Energy savings derived from cooling, not stored per typology (2026-07-30)

The draft's per-typology energy reduction factors (2–15%) had no traceable source and were removed. Cooling-energy savings are now derived: `demand × ΔT × sensitivity`, where sensitivity is 2–4% per °C from `akbari2001`. This makes energy outputs sourced, internally consistent with the tool's own cooling estimate, and responsive to site conditions. Transferability of a predominantly North American sensitivity is flagged as a known limitation and a review question.

## D-016 — No default cost values ship with the tool (2026-07-30)

`worldbank2021` documents order-of-magnitude cost variation between contexts, and no source was found giving globally applicable unit costs. Shipping an invented default per-m² cost would generate the assessment's most decision-relevant output — payback — from a fabricated input, which no confidence rating could adequately qualify. The tool therefore reports capital cost, payback, and cost feasibility as *not estimated* unless the user supplies figures. Locally calibrated cost tables are a documented extension point.

## D-017 — Evidence rules are machine-enforced (2026-07-30)

Configuration loading fails, and CI fails, if: a typology carries no citation; any `sources[].key` is absent from the bibliography; the methodology files fall out of version lock-step; a temperature envelope is inverted or exceeds the literature ceiling; or the low-confidence typology declarations are removed. Evidence policy is a build gate, not a review convention.

## D-018 — Single guided questionnaire flow (2026-07-30)

One path through all six input steps — no quick/full mode split. Optional fields are skippable in one click; a live per-block confidence meter shows what skipping costs and names the single field that would most improve confidence. Rationale: a mode split adds a concept users must understand and a second path to test, while the confidence meter already gives users control over their own depth/effort trade-off.

## D-019 — Suitability guides selection but never blocks it (2026-07-30)

The intervention picker sorts and annotates the 14 typology cards using the site data already entered ("Well suited" / "Needs reliable irrigation" / "Not suitable — no water feature on site"). Unsuitable typologies remain fully selectable, and the flag carries into results and the report. Rationale: the suitability matrix is most valuable as guidance *at the moment of choice* rather than as a post-hoc verdict after 45 questions; blocking would override the professional judgment of a user who is deliberately testing a hypothesis. Implements D-009 in the interface.

## D-020 — Auto-save locally, resume anytime (2026-07-30)

Assessments persist automatically to the local project store as the user progresses; a projects list allows reopening, duplicating, and comparing. Rationale: matches the local-first architecture, makes A/B/C comparison durable rather than session-bound, and avoids losing 45 answers to a closed tab. No account or authentication in v1.

## D-021 — Comparison carries the site forward (2026-07-30)

"Compare another option" duplicates the full site description and re-asks only the intervention step (and cost/energy where used) — roughly 9 questions instead of 45. Rationale: site conditions are a property of the place, not of the option; re-asking would be tedious and would introduce inconsistency between variants that the comparison is meant to isolate.

## D-022 — Composite sub-indicator derivation rules fixed (2026-07-30, Phase 2)

The paper at version 2026.07.30 disclosed that the rules mapping inputs to the NbS Suitability and Equity sub-indicators were unspecified and would be fixed alongside the engine, with a version bump. Fixed in `config/derived_scores.yaml` at version `2026.08.01` (Methodology Report §5.10): suitability from space ratio brackets, ordinal requirement-matching for soil and water (never flagging from absent information), inverted maintenance intensity, and land-use context match; equity from a deficit/relevance reading of four indicators, reusing the vulnerable-population input and adding exactly two new optional fields (`public_accessibility`, `community_participation`). Suitability sub-scores of 25 coincide with the D-009 hard flags. The Equity Score remains outside the final aggregation, as previously disclosed.

## D-023 — Cost feasibility brackets, combination rule, and investment readiness (2026-07-30, Phase 2)

Realises D-010 and OQ-11 at version `2026.08.01`. Payback bracket applied to the payback from the **central** energy estimate (bracketing either end of an order-of-magnitude interval would let the least certain extreme drive the score): <5y → 100, 5–10 → 75, 10–20 → 50, ≥20 → 25, boundaries following public-investment screening horizons. Combination: `0.50 payback + 0.25 complexity + 0.25 maintenance` (both inverted; weights in `weights.yaml`). Investment readiness: bracket base level, downgraded once for high complexity and once for low energy-block confidence, floored at low; `not_estimated` whenever feasibility is. Note: with the shipped confidence field lists, calculated energy implies at least medium energy confidence, so the energy-confidence downgrade binds only in deployments that alter those lists.

## D-024 — Confidence field-to-block mapping and overall rule (2026-07-30, Phase 2)

The branched-confidence completeness denominators (D-011/OQ-09) are enumerated in `config/derived_scores.yaml`: 10 cooling slots (LST anomaly and qualitative heat level share one either-of slot), 3 energy, 4 economic, 6 equity. An explicit `unknown` counts as not supplied. Boundaries exact: <40% low, 40–70% medium, >70% high. Overall confidence is the **lower median** of the four block ratings — exact (no rounding rule at half-steps) and conservative. The evidence-confidence cap (low-evidence typology → cooling at most medium) is reported as binding only when it actually lowered the rating.

## D-025 — Sensitivity analysis executed and published (2026-07-30, Phase 2)

The §7 commitment is discharged: `tools/sensitivity_analysis.py` perturbs each aggregation weight ±25% (remainder renormalised) over the 20 golden scenarios. Results at `2026.08.01`: worst-case rank stability 0.9737, pooled mean displacement 0.42 points (max 2.01), 3/240 category migrations, all within ~1.3 points of a band boundary; influence order cooling potential > heat priority > vulnerability > suitability > co-benefits > cost feasibility. Published in the Methodology Report §7 and `docs/methodology/SENSITIVITY-ANALYSIS.md`; must be regenerated with any weight change.

## D-026 — Soil–water condition: honesty must dominate silence (2026-07-30, post-Phase-2)

Engine implementation exposed an incentive defect in the `2026.07.30` soil–water rules: the mapping capped `reliable` irrigation at *good* while `high` soil reached *excellent*, so with high soil the best possible honest irrigation answer (factor 1.0) scored **worse** than leaving the question blank (soil alone → excellent, 1.2) — and *excellent* was unreachable whenever both fields were answered, indicating a calibration oversight rather than intent. Fixed at `2026.08.02` with two rules: (1) `reliable → excellent` — guaranteed irrigation removes the water constraint on evapotranspiration, the top of its scale, parallel to soil `high`; (2) **a condition pair containing an unknown is capped at the neutral factor** (*good*, 1.0) — the §3.2 unknown-neutral principle applied to a derived pair: an unknown must never participate in an above-neutral boost. Result: high soil + reliable → 1.2 > question skipped → 1.0 > occasional → 0.8; complete favourable data strictly dominates silence. Alternatives considered and rejected: levelling `reliable` up alone (leaves silence tying the best honest answer) and removing *excellent* from soil–water (fixes by making the honest answer worthless and falsifies the documented A ∈ [0.5, 1.2] range). Score impact bounded by ΔA = ±0.05 → ≤ ~1.4 points on the Opportunity Score; one golden scenario's outputs shifted (green façade, 62.19 → 62.82, band unchanged) and sensitivity headline figures are unchanged.

## D-027 — Remaining Phase-2 review items deferred to Phase 4 (2026-07-30)

Three minor findings from engine implementation are recorded and explicitly deferred, with no behaviour change: (1) `heat_index_concern` and `current_shade_level` carry normalisation mappings but feed no formula — the engine accepts them, `current_shade_level` counts toward cooling-block completeness only, and both are disclosed in the paper's field reference; (2) the investment-readiness downgrade on low energy-block confidence (D-023) is unreachable with the shipped confidence field lists and remains specified for deployments that alter them; (3) the UX specification's "planted area" sizing field is consumed by no formula and is not in the input schema. All three are questionnaire-shaped questions, so they are decided when the questionnaire is built (Phase 4): keep, repurpose, or drop each field there, with a methodology version bump if configuration changes.

## D-028 — Phase 3 API design decisions (2026-07-30)

Approved ahead of implementation so Phase 3 implements rather than re-designs.

- **`POST /api/assessments/validate`** returns errors, warnings (OQ-04/08 severities only), a per-block confidence preview (levels + completeness percentages, computed by the engine's confidence module), and the **highest-value missing field hint** the UX confidence panel requires (D-018): for each block, the first unsupplied field group in the configured `derived_scores.yaml` order whose single completion would raise the block's confidence level; if no single completion raises the level, the first unsupplied group in configured order. Deterministic and config-driven; no new methodology values.
- **Storage contract (D-020, OQ-15).** Local-first JSON under the platform user-data directory (`platformdirs`), one file per project: `{schema_version, project_id, name, created_at, updated_at, site fields, assessments[]}`; each stored assessment keeps its full input and its full `AssessmentResult` including `methodology_version` and `engine_version`, and is **never recomputed** — a newer methodology is surfaced as available, re-running is an explicit user action creating a new assessment. UUIDs and timestamps live in the API/storage layer only; the engine stays clock-free and pure.
- **Comparison (D-021).** A duplicate-assessment operation copies the project's site and vulnerability description into a new draft and blanks only the intervention and cost/energy groups.
- The project/assessment CRUD endpoints this implies extend the v1 API table in ARCHITECTURE.md; that table is updated in the same Phase 3 change set.

## D-029 — Phase 3 implementation rulings (2026-07-30)

Recorded during the Phase 3 implementation of D-028; none alters a methodology value.

- **Co-benefit overrides are blanked on duplicate.** D-021 names "the intervention and cost/energy groups"; the co-benefit override fields are typology-specific overrides, so carrying them onto a differently chosen typology would silently misdescribe it. They are treated as part of the intervention group and blanked. (D-027 already defers the questionnaire placement of these fields to Phase 4; this ruling only fixes their duplication behaviour.)
- **An evaluated assessment's input is frozen.** Editing the input after a result exists would detach the stored result from the answers that produced it; the API refuses with 409 (the label stays editable). Evaluating an assessment that already holds a result is likewise refused with 409 — re-running is a new assessment (OQ-15). Evaluation of a stored draft is itself an explicit endpoint (`POST …/evaluate`): results enter storage only from the engine, never from the client.
- **Draft inputs are stored as partial JSON, validated late.** Auto-save (D-020) must accept an incomplete questionnaire, so a stored draft is any subset of the engine's input fields (unknown keys rejected) and is validated as a full `AssessmentInput` only at explicit evaluation. Stored results are held as opaque JSON and never re-validated against later engine schemas, so an engine upgrade cannot make older stored results unreadable.
- **`/validate` previews without a typology assume no evidence cap.** Before step 5 (or with an unknown `nbs_type`, which is reported as a field error) no evidence-confidence cap can be asserted, so the confidence preview is computed uncapped; once a typology resolves, the engine's cap applies and the missing-field hint respects it (a completion that cannot raise a capped level promises nothing).
- **Storage location and format.** `platformdirs` user-data directory for app `criterra-nature-cooling` (author `Criterra`), one pretty-printed UTF-8 JSON file per project named by its UUID, written atomically (temp file + rename), `schema_version: 1`; unsupported schema versions are refused rather than migrated silently. Duplicate labels default to "<source label> (copy)" when the client supplies none.

## D-030 — Phase 4 web application design decisions (2026-07-30)

Approved ahead of implementation so Phase 4 implements rather than re-designs (the D-028 pattern). Scope and screens are fixed by the UX specification (D-018–D-021); these decisions fix the implementation shape.

- **Toolchain.** Vite + React + TypeScript (`strict`), as decided in D-003. Tests with `vitest` + Testing Library; linting with ESLint (typescript-eslint) and Prettier. CI gains a frontend job (lint, format check, `tsc --noEmit`, tests) beside the unchanged backend job.
- **Same-origin integration, no CORS.** The Vite dev server proxies `/api` to the FastAPI service; the packaged app (Phase 6) serves both from one origin. The API gains no CORS middleware — the local-first deployment model never needs cross-origin requests, and not having the middleware is one less security surface to reason about.
- **API types are generated, never hand-written.** TypeScript types for every request/response are generated from the service's OpenAPI schema and committed; CI regenerates and fails on drift. A hand-maintained duplicate of the engine's schemas would be a second source of truth, which D-028's rules forbid in spirit for the frontend as well.
- **No data-fetching or global-state library in v1.** A thin typed `fetch` client plus React state/context; `react-router` for navigation. The app talks to a local API measured in milliseconds; cache-invalidation machinery is unjustified complexity. Auto-save (D-020) is a debounced `PATCH` of the draft input; inline validation and the confidence panel are fed by a debounced `POST /api/assessments/validate` with the full draft payload, errors filtered to the active step's fields. The frontend computes no score, threshold, band, or confidence level — ever (ARCHITECTURE boundary 3).
- **Strings and fonts.** All user-facing strings live in one externalised message catalog (UX specification §9, translation-ready); Newsreader, Hanken Grotesk, and IBM Plex Mono are self-hosted — the app makes no third-party requests.
- **Versioning.** Phase 4 closes with repo tag `v0.4.0`; the backend package and the frontend `package.json` move to 0.4.0 together so the tag and package versions stay aligned (as in Phases 2–3).

## D-031 — D-027 deferrals closed (2026-07-30)

The three questionnaire-shaped findings deferred by D-027 are ruled on ahead of the Phase 4 build. **No methodology value moves; no version bump is required.**

1. **`heat_index_concern` is not asked in the v1 questionnaire.** It feeds no formula and no confidence block, so asking it would cost user effort and change nothing — the UX premise ("show the user exactly what skipping costs") cannot honestly present a field whose cost of skipping is zero. The field stays in the input schema and its mapping stays in configuration, unchanged: data-rich API integrations may still supply it, and removing it from config would force a version bump for no behavioural gain.
2. **`current_shade_level` is asked in step 2 (site characteristics).** It counts toward cooling-block completeness only, as shipped and as disclosed in the paper's field reference. It is retained because the cooling confidence denominators measure how completely the site's cooling context is described — shade is a legitimate part of that description and a documented extension point — and because removing it from the D-024 field lists would be a methodology configuration change (version bump, report §6.2, paper) disproportionate to the finding.
3. **The "planted area" sizing field is dropped from the UX specification.** It is consumed by no formula and exists in no schema; `intervention_area_m2` and `new_canopy_area_at_maturity_m2` already cover intervention sizing. The specification is corrected in the same change set.

D-027's second finding (the investment-readiness downgrade on low energy confidence being unreachable with the shipped confidence lists) needs no Phase 4 action: it remains specified, documented behaviour that binds only in deployments that alter those lists, exactly as D-023 recorded.

## D-013 — Weights are expert-calibrated and defended by sensitivity analysis (2026-07-30)

Aggregation weights cannot be "derived" from literature and we do not pretend otherwise. They are declared as expert judgment following composite-indicator practice (OECD/JRC Handbook), and defended empirically via the published sensitivity analysis (see D-011/OQ-29).
