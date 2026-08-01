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

## D-032 — Phase 4 implementation rulings (2026-07-30)

Recorded during the Phase 4 implementation of D-030/D-031; none alters a methodology value, an API contract, or a screen's scope.

- **Co-benefit overrides are asked in step 5, with the intervention they describe.** D-029 fixed their duplication behaviour by ruling them part of the intervention group; the questionnaire follows the same reading. They render as a collapsed disclosure under the sizing fields, labelled as overrides of the typology's cited library defaults, so the common path stays skippable in one action.
- **Picker fit annotations are comparisons of served data, not frontend rules.** The D-019 cards annotate fit by comparing the site answers already entered against each typology's suitability conditions from `GET /api/typologies`, using the ordinal ranks served in `GET /api/methodology` (`derived_scores.suitability_sub_indicators.requirement_match`). No rank, minimum, or threshold exists as a frontend constant. Mirroring D-022, a disqualification is asserted only from a *supplied* answer below a requirement; an unanswered requirement renders as a caution ("Needs reliable irrigation"), never a verdict. The authoritative flags remain the engine's (D-009) and follow into results.
- **The effective-weights table is derived visibly from served weights.** UX §8 requires the D-007 effective-weights table, but the effective values exist in `weights.yaml` only as a comment. The methodology browser therefore shows each effective weight as the product of served weights with its derivation displayed alongside (e.g. `0.15 + 0.25 × 0.4`), keeping the API the sole source of every operand.
- **The step 6 "do you have cost data?" gate is a UI-only disclosure.** It maps to no stored field; the underlying cost/energy fields alone determine what the engine sees, so skipping the step and answering "no" are indistinguishable to the methodology — as OQ-08's two-severity model intends.
- **Score cards carry the overall confidence badge.** UX §6 gives each score card "its category and confidence"; the result schema deliberately has no per-score confidence, so both cards render `confidence.overall` and each output block renders its own block confidence — nothing is invented to fill the gap.
- **Toolchain pinned for Node 18.** The development machine runs Node 18 LTS, so the D-030 toolchain resolves to Vite 6 and Vitest 3 (the last majors supporting Node ≥18; Vite 7 requires Node 20+), React 19, and `react-router` 7 (the package D-030 names; its DOM bindings live in the core package from v7). CI runs Node 22.
- **Contract tests run against recorded responses.** Every fixture under `frontend/src/test/fixtures/` is captured verbatim from the live service (same capture flow as the golden scenarios' spirit); the fetch-boundary mock rejects any request without a recorded route, so a contract drift fails loudly instead of passing against an invented shape.

## D-033 — Phase 5 report-export design decisions (2026-07-30)

Approved ahead of implementation so Phase 5 implements rather than re-designs (the D-028/D-030 pattern). Scope is fixed by OQ-13/D-011 (the 2-page PDF) and the ARCHITECTURE §2 report builder; these decisions fix the implementation shape. Recorded in [PHASE-5-BRIEF.md](PHASE-5-BRIEF.md).

- **Toolchain: `fpdf2` (PDF) + `openpyxl` (XLSX), as core dependencies.** Both are pure Python and pip-installable with no system libraries, preserving the one-command local-first install. WeasyPrint's finer typography was considered and rejected for its Pango/Cairo system dependence; ReportLab for its heavier API. The report is a core deliverable (OQ-13), so neither ships as an optional extra.
- **XLSX ships in Phase 5 alongside the PDF**, as the roadmap has always stated: one workbook (Inputs, Results, Assumptions & Warnings) for users who post-process results.
- **Endpoints render stored results only:** `GET /api/projects/{id}/assessments/{aid}/report.pdf` / `…/report.xlsx`. A stored result is rendered verbatim and never recomputed (OQ-15); rendering a draft is refused with 409, consistent with the D-029 evaluation-state rules. No stateless report endpoint in v1 — API users who need one can evaluate statelessly and render client-side; adding it later is additive.
- **Byte-determinism is a contract:** same stored assessment → byte-identical bytes in both formats. Document metadata timestamps derive from the assessment's `created_at`, never the clock, keeping clocks confined to the storage layer.
- **The PDF embeds TTF builds of the three brand families** (self-contained on any machine, OFL notice alongside); report strings live in one module-level English catalog mirroring the frontend's externalisation contract.
- **PDF tests assert extracted text and structure, never pixels**, via a dev-only extraction dependency, plus determinism tests; the 100% backend coverage gate extends over the report package.

## D-034 — Phase 5 implementation rulings (2026-07-31)

Recorded during the Phase 5 implementation of D-033; none alters a methodology value, an engine schema, or a decided contract.

- **The Inputs sheet's applied-default marker states only what the stored input shows.** A field that is absent, `null`, or an explicit `unknown` is marked *not supplied — methodology fallback applies* (unknowns additionally say they count as not supplied, mirroring D-024); which defaults the engine *actually* applied is not re-derivable per field without recomputation, so the marker never claims it — the engine's own `assumptions_applied` itemisation is reproduced verbatim on the Assumptions & Warnings sheet, and a banner on the Inputs sheet points there.
- **The report catalog corrects one status wording rather than mirroring it.** The web app renders the cooling block's `not_estimated` statuses (shade potential, time to benefit) through the shared `statuses.not_estimated` text, whose wording — "requires cost data" — is wrong for those fields (they depend on intervention sizing inputs). The report catalog gives them a neutral *"Not estimated — the required input was not provided."* The frontend wording is recorded as a known catalog defect to correct in a later frontend change.
- **XLSX determinism is enforced by rewriting the archive.** openpyxl stamps `dcterms:modified` and every ZIP member date with the wall clock at save time, so the builder rewrites the archive with all timestamps derived from the assessment's `created_at` (`dcterms:created`/`modified`, member dates; ZIP dates cannot precede 1980 and clamp to that epoch). This is the D-033 no-clock rule applied to the container format, not just the document properties.
- **The embedded fonts are static instances of the brand variable fonts**, produced with fonttools `varLib.instancer` from the upstream OFL releases: Newsreader 400/600 at optical size 16, Hanken Grotesk 400/700, IBM Plex Mono 400. Each family's complete OFL text ships alongside the TTFs in the report package.
- **The 2-page contract is enforced by test, with layout headroom.** Every golden scenario renders to exactly two pages; the layout was verified against the maximal-assumptions scenario (s19, 20 itemised defaults) with warning lines added on top. The Opportunity Score's component/weight table ships in the XLSX Results sheet only — page 1 keeps the summary the brief specifies, protecting the fixed layout; weight transparency in the app remains the methodology browser's job.
- **Download filenames** are an ASCII slug of "project name – label" (`riverside-pilot-option-a.pdf`), falling back to `assessment` when nothing survives slugging; served via `Content-Disposition: attachment`.
- **Test tooling:** `pypdf` is the dev-only PDF text-extraction dependency (D-033); `types-openpyxl` is added beside the existing `types-PyYAML` stub so `mypy --strict` covers the workbook builder. Both are dev-only; runtime additions remain exactly `fpdf2` and `openpyxl`.

## D-035 — Phase 6 packaging and publication design decisions (2026-07-31)

Approved ahead of implementation so Phase 6 implements rather than re-designs (the D-028/D-030/D-033 pattern). Scope is fixed by ARCHITECTURE §6 (the v1 deployment model) and the roadmap; these decisions fix the implementation shape. Recorded in [PHASE-6-BRIEF.md](PHASE-6-BRIEF.md).

- **The wheel ships the app.** The production frontend build is embedded in the Python package as static assets and served by FastAPI at `/` from the same origin as `/api` — the packaged realisation of D-030's same-origin decision, still with no CORS middleware. A `nature-cooling serve` console script (wrapping uvicorn behind the existing `serve` extra) makes the local-first story one `pip install` and one command. CI builds the frontend and the wheel together so the embedded assets can never go stale.
- **The container is packaging, not architecture.** One image built from the wheel (python-slim, non-root), plus a minimal `compose.yaml` mounting a named volume at the `platformdirs` data path so projects survive container replacement. No reverse proxy, TLS, or multi-user machinery in v1 — that remains the host's concern and v2's scope (OQ-31).
- **The documentation site renders the existing corpus; it is not a second corpus.** MkDocs + Material sourcing the current Markdown under `docs/` with the README as the landing page — no page authored twice, so the site cannot drift from the repository (D-030's one-source-of-truth rule applied to prose). Brand styling via the criterra.eu tokens and the three self-hosted families; no third-party requests from the published site. Published to GitHub Pages by CI on pushes to `main`.
- **Releases are automated from tags.** A `vX.Y.Z` tag triggers: full gates, wheel build, container image to GHCR, docs deploy, GitHub release with the wheel attached. The paper PDF and the Methodology Report remain versioned in-repo (D-012).
- **Gates unchanged**, plus a packaged-wheel smoke check (install the built wheel, start the server, assert `/` serves the app shell and `/api/meta` answers) rather than any new test framework. The engine and methodology are untouched; no methodology version bump.

## D-036 — Phase 6 implementation rulings (2026-07-31)

Recorded during the Phase 6 implementation of D-035; none alters a methodology value, an engine formula, or an API contract.

- **The wheel embeds the methodology configuration and the bibliography, not only the frontend build.** Implementation surfaced that the configuration loader resolves `config/` and `docs/methodology/BIBLIOGRAPHY.md` from the repository root, which an installed wheel does not have — so "the wheel ships the app" (D-035) necessarily includes the methodology data the engine refuses to start without. All three are staged into `nature_cooling/_bundled` by `tools/build_wheel.sh` (gitignored, admitted by the hatchling `artifacts` setting, removed after the build). Resolution is **repository-first**: a checkout always runs against the live files, the embedded copies serve only installed wheels, so development behaviour is unchanged and a stale staging directory can never shadow the repository.
- **The embedded app serves with a single-page fallback, `/api` exempt.** Client-side routes name no file in the build, so unmatched paths serve `index.html` and let the frontend router resolve them — except paths under `/api`, where a typo stays an API 404 rather than an HTML 200. The API's routes are registered before the static mount and are unaffected.
- **`nature-cooling serve` is deliberately minimal:** one subcommand with `--host` (default 127.0.0.1) and `--port` (default 8000), wrapping `uvicorn.run` imported lazily; without the `serve` extra it exits 1 naming the exact `pip install` command. No other subcommands in v1 — the engine's Python API and the service remain the programmatic surfaces.
- **The docs site adapts the corpus at build time; it never edits it.** `index.md` is generated from the README by a build hook (never committed), with two transforms: the CI/license badge images are dropped — they are third-party requests, which the published site must not make (D-035) — and repository-relative links are rebased (corpus links lose their `docs/` prefix; `LICENSE`, `paper/` point at GitHub). Corpus pages get one transform: relative links that climb out of `docs/` (`../../config/…`) are rewritten to the GitHub repository. The three font families are injected into the site from `frontend/public/fonts` — the same self-hosted files the application serves, with their OFL notice.
- **Docs tooling lives in `docs/requirements.txt`** (MkDocs + Material only, no further plugins), installed by the CI docs jobs and by contributors previewing the site — the backend package's dependencies are untouched, keeping the D-035 "packaging tooling only, dev-only" rule literal. The `build` package joins the backend `dev` extra for the wheel build.
- **The container image name is the lowercased repository path on GHCR** (`ghcr.io/dimitrios-kafetzis/criterranaturecoolingtool`), tagged with the release tag and `latest`. CI builds the image on every push — not only at release — so a broken `Dockerfile` cannot reach a tag.

## D-037 — Phase 7 is v1.0 stabilisation: external review and hardening (2026-07-31)

The original roadmap ends at Phase 6, so the path onward was decided rather than inherited. Approved scope for Phase 7, recorded in [PHASE-7-BRIEF.md](PHASE-7-BRIEF.md):

- **In: an external methodology review round.** The review package is the existing paper and Methodology Report (D-012) plus the published site — no new document. The phase's repository work is structured critique intake (an issue template asking for the report section, the claim challenged, and supporting literature) and a triage rule: methodology-blocking findings change configuration/report through the D-017 evidence gates with a version bump; clarifications change wording without one; declined findings are recorded with rationale. Outreach itself is the author's action, outside the codebase.
- **In: a bounded hardening set.** A WCAG AA accessibility pass (verifying the promise ARCHITECTURE §3 already makes), packaged-app UX polish limited to defects found by use, and the D-034 frontend catalog defect corrected the way the report catalog already corrected it.
- **Out: PyPI publication — deferred, not rejected.** Distribution remains the GitHub release wheel and the GHCR image; PyPI is revisited after v1.0 alongside the V2 decision.
- **Out: a strict review-gated exit.** `v1.0.0` is **time-boxed**: it ships when the hardening set lands, and review findings are handled as they arrive — a methodology change accepted afterwards is an ordinary versioned release (OQ-15). Package semver and the date-stamped methodology version stay independent: `v1.0.0` asserts product stability, not methodological finality.

## D-038 — Post-v1 review programme: three releases (2026-07-31)

The v1 tool was reviewed in the browser by the author and produced eight comments. They are scheduled as three releases rather than one, because their risk profiles differ sharply and the largest of them should target the questionnaire's *final* shape rather than its current one. Approved 2026-07-31.

| Release | Comments addressed | Character |
|---|---|---|
| **v1.1** | Favicon; Criterra brand and copyright presence; `land_use` gains *memorial* and *campus*; cooling-refuge access clarified and split; per-parameter explanations | Interface and identity, plus one bounded methodology change |
| **v1.2** | The NbS library replaced by the curated UNEP catalogue with scale- and condition-based availability gating, driven by four new site questions; multi-intervention selection | Methodology, engine, configuration, report and interface together |
| **v1.3** | Map-based site selection with parameter autofill | Interface plus one bundled dataset |

The map is deliberately **last**: autofill must target the questionnaire that v1.2 leaves behind, not the one v1.1 ships. Package semver moves independently of the date-stamped methodology version, as D-037 established.

**On the absent `v1.0.0` tag.** The repository's last tag is `v0.6.0`, and D-037 reserved `v1.0.0` for a time-boxed Phase 7 stabilisation release. The review that produced these eight comments arrived before that time box closed, so the Phase 7 hardening set is not skipped — it ships *inside* v1.1.0, which carries the packaged-app UX polish the review itself identified and confirms the D-034 catalog defect fixed. The version numbering follows the review conversation rather than the roadmap, and the roadmap is corrected to match rather than the other way round: renumbering the approved releases to preserve a tag that was never cut would serve the document, not the reader. Tagging the currently published state retroactively as `v1.0.0` remains available and costs nothing if wanted.

## D-039 — Cooling-refuge access is one dimension measured by two indicators (2026-07-31, v1.1)

Review comment 5 asked whether `access_to_cooled_indoor_space` should be split into indoor and outdoor, and noted that the field's meaning was not clear to users. Both parts are accepted, at version `2026.08.03`.

**The split is literature-supported.** `reid2009` already grounds air-conditioning prevalence as an independent vulnerability dimension (D-007, §5.2). Two further sources ground the outdoor half: `burkart2016` quantifies it directly in Lisbon — above the 99th temperature percentile, elderly mortality rose 14.7% per °C in the least-vegetated areas against 3.0% in the most vegetated, and 7.1% per °C beyond 4 km from water against 2.1% within it — and `sera2019` confirms across 340 cities in 22 countries that higher green-space levels attenuate the heat–mortality relationship. Access to a cool *outdoor* refuge is therefore an evidenced protective factor, not an inferred one, and the tool asks about it as `access_to_cool_outdoor_refuge` (inverted scale, like its indoor counterpart).

**It is one dimension, not two.** The Vulnerability Score's third term keeps its name (`cooling_access_deficit`) and its **0.20 weight, unchanged**; what changes is that the term is now measured by up to two indicators instead of one. `weights.yaml` is untouched, so the published sensitivity analysis remains valid.

**The dimension is the mean of the indicators actually supplied.** If both are answered, the dimension is their mean; if one is answered, it equals that one; if neither is (absent or explicit `unknown`), it takes the neutral 50 exactly as today. Averaging against a neutral 50 for the *unsupplied* indicator was considered and rejected: it would drag a supplied signal toward the middle purely because a second question was skipped, letting an unknown change the meaning of an answer the user did give — the defect D-026 fixed for the soil–water pair, in a new place. Under the adopted rule, answering the new question can move the score in either direction according to what the answer says, and skipping it costs nothing, which is the §3.2 unknown-neutral principle stated for a two-indicator dimension.

**Confidence treats the two as alternatives for one slot.** The equity block's field list pairs them (`[access_to_cooled_indoor_space, access_to_cool_outdoor_refuge]`), following the established `lst_anomaly_c` / `heat_exposure_level` pattern: the completeness question is whether the user described cooling-refuge access at all, and either indicator answers it. The block's denominator stays at six slots.

**Consequence: no golden scenario output changes.** No scenario supplies the new field, so every stored expectation holds unchanged — the new indicator is strictly additive. This is a property of the design, not a constraint imposed on it.

**Disclosed overlap.** The outdoor indicator describes cool refuges in the *surroundings* reachable by the site's users, while the Heat Exposure Score's vegetation-deficit component describes greenness *of the site itself*. They are distinct but adjacent, and the partial conceptual overlap is declared in Methodology Report §5.2 rather than left for a reviewer to discover, in the manner of D-007.

## D-040 — `land_use` gains *memorial* and *campus* (2026-07-31, v1.1)

Review comment 3. Both are common project settings absent from the enumeration, and both are named typologies in the UNEP catalogue that v1.2 adopts (Memorial Landscape, Campus Landscape, Green Campus), so adding them now also prepares the gating rules that release needs.

The land-use enumeration feeds exactly one scoring rule — the suitability urban-context sub-indicator (D-022), which compares the site's land use against each typology's `typical_use_context` list. Adding a value without extending those lists would silently score both new uses as *out of context* (25, a penalty of up to 7.5 points) for every typology, so the lists are extended on a documented reading of what each new setting is:

- **Campus** — educational, healthcare, or corporate institutional grounds — is a mixed environment of buildings, internal circulation, and open space. It is therefore added wherever a school, public-space, or mixed-use context already applies: twelve of the fourteen typologies.
- **Memorial** — cemeteries, memorial parks, remembrance gardens — is low-intensity public green space. It is added wherever a park or public-space context already applies: seven typologies. It is not added to the building-envelope typologies (green roof, green façade), to schoolyard greening, or to street tree planting, none of which describes a memorial setting; avenue-style planting in a memorial landscape is covered by the shaded pedestrian corridor.

Neither value is added to `blue_green_corridor` or `riparian_restoration`, whose context is an existing water feature rather than a land use. No existing land use changes meaning, and no golden scenario is affected.

## D-041 — Every questionnaire parameter carries an on-demand explanation (2026-07-31, v1.1)

Review comment 6: users could not tell what several parameters meant — "land surface temperature anomaly" was named specifically — and long explanatory text under every field was explicitly unwanted.

Each field gains an **info control beside its label** opening a small popover with three parts: what the parameter means in plain language, what it affects in the scoring, and where to read more. The one-line help text under the field is kept where it is genuinely short and drops out where the popover replaces it, so the default view of the form gets *shorter*, not longer. The popover is a native disclosure pattern — keyboard reachable, dismissible with Escape, associated with its field for screen readers — consistent with the WCAG AA commitment (ARCHITECTURE §3) rather than a hover-only tooltip, which fails touch and keyboard users alike.

All explanation strings live in the existing message catalog (D-030's externalisation rule), stated in the same language the Methodology Report uses so that the two cannot drift into describing different quantities. The catalog defect D-034 recorded — the frontend rendering the cooling block's `not_estimated` statuses with the economic wording "requires cost data" — is corrected in the same change set, as D-037 scheduled.

## D-042 — Criterra identity and copyright are present in the product (2026-07-31, v1.1)

Review comments 1 and 2: the application shipped no favicon and carried the Criterra name only as a four-word subtitle. The tool is Criterra's first product and must say so.

The **horizontal serif lockup** (the decided brand logo) appears in the application header, on the PDF report's first page, and on the documentation site; the **leaf mark alone** becomes the favicon at small sizes, where the wordmark would be illegible. A footer states the copyright and the product relationship, and links to criterra.eu. All assets are self-hosted alongside the three brand font families — the no-third-party-request rule (D-030, D-035) covers images exactly as it covers fonts.

Copyright and licensing are distinct and both are stated: the **code** remains Apache-2.0 (D-004), while the Criterra name and logo are marks that the licence does not convey. A `NOTICE` file records this in the form Apache-2.0 anticipates, so the permissive licence and the brand assertion coexist without ambiguity.

## D-043 — The catalogue's three-level structure, and six rulings that follow (2026-08-01, v1.2)

The v1.2 review pack ([V1.2-REVIEW-PACK.md](V1.2-REVIEW-PACK.md)) curated all 243 entries of the UNEP catalogue to **110 typologies** — 88 merged, 45 dropped — and raised six structural decisions, three of which contradicted rules approved when the release was scoped. All six are approved as proposed.

**The finding underneath all six.** The catalogue mixes three kinds of thing, and the tool's single `nbs_type` concept can represent only one of them:

| Kind | Count | What it is |
|---|---:|---|
| **Element** | 105 | A discrete thing you build — a stormwater tree pit, an extensive green roof, a modular living wall. A leaf typology with its own form and cooling behaviour. |
| **Composite** | 101 | A coherent spatial system *made of* elements — a green street, a cooling plaza, a constructed wetland, a neighbourhood park. |
| **Strategy / context / model** | 37 | Not an intervention: a land-use context, a management objective, an umbrella category, a planning model. |

The document states this about itself throughout — the park list "mixes three different bases of classification", the ecological network list "mixes several levels of organisation", an eco-district "is not itself an NbS", urban agriculture is "not one specific NbS typology". Nearly every drop is a kind-3 entry, and no capability is lost by dropping them: a land-use context is already carried by the `land_use` input, and a strategy is a *package* of kept entries.

**D-043.1 — The four land-use contexts become contexts, not typologies.** Hospital landscape, campus landscape, memorial landscape, and schoolyard greening are dropped as selectable solutions. The approved building-scale gating rule ("if it is school then schoolyard greening") is realised instead by mapping the land use to the real typologies that suit it, which offers the user more rather than fewer options and puts the mapping where it belongs — in the availability matrix. Consequence, accepted knowingly: **`schoolyard_greening` is retired as a typology**, becoming a land-use-driven bundle. It carries cited values and appears in golden scenario s06, so this is a methodology change with a version bump, not a rename. The alternative — keeping a card named after the site the user has just described — was considered and rejected as asking the same question twice.

**D-043.2 — City and district scales offer packages, not single interventions.** This supersedes the approved rule "for the district must be only the district scale". A strict reading of that rule left district-scale users three usable options and city-scale users six, because almost everything at those scales is a strategy the document disqualifies. The correction is not to lower the bar but to recognise that a district is not a place where one thing is installed: at these scales the assessment composes several kept typologies and scores them as a package (D-043.6). The surviving district "networks" become **named preset packages**.

**D-043.3 — Productive-landscape gating asks who can deliver, not who is interested.** The approved yes/no ("is there interest to create productive landscape from individuals or communities") would have suppressed the urban farm and the agroforestry system — commercially delivered, and the highest-canopy, highest-cooling entries in the group — on a "no". Replaced by a multi-select over {community, individual, institutional, commercial}, which gates correctly at no extra cost in user effort.

**D-043.4 — "Urban forest" is fixed to the site reading and renamed.** The document warns the term means either a whole-city tree system or a specific tree-dominated site, and that the two must not be mixed. The tool's existing typology is already the site reading (2 000 m² minimum), so the reading is kept and the display name disambiguated. The city-wide reading is what a city-scale package expresses (D-043.2). Display-name change only; envelope and minimum area unmoved.

**D-043.5 — Street typologies are preset packages over elements.** The document requires that street-scale typologies be integrated linear systems whose composing elements are "referenced rather than redefined", and explicitly that "Street Trees" be removed as a street typology. `street_tree_planting` is therefore retained as the **element** it has always been, and the seven kept street typologies compose elements.

**D-043.6 — The existing fourteen keep their identity and their cited values.** Four catalogue entries merge onto them (cooling park → `park_upgrade`, riparian forest → `riparian_restoration`, productive courtyard → `courtyard_greening`, edible streetscape → `street_tree_planting`). They are the only entries in the library with individually retrieved literature behind them; trading that for a catalogue name would exchange evidence for tidiness. A catalogue entry stays separate only where it adds a distinct behaviour rather than a distinct name.

**Why packages are the structural answer, not merely a requested feature.** D-043.1, D-043.2 and D-043.5 are independent findings — a land-use context, a planning scale, and a linear spatial system — and all three resolve through the same mechanism: composing kept typologies and scoring them together under the D-038 capped-never-summed rule. Review comment 8 asked for multi-selection as a convenience; the catalogue shows it is what the domain actually requires.

## D-044 — The archetype model, and the four remaining v1.2 decisions (2026-08-01)

Parts 3 and 4 of the review pack ([V1.2-REVIEW-PACK-2.md](V1.2-REVIEW-PACK-2.md)) are approved: **18 cooling archetypes**, all 110 kept typologies mapped to exactly one, and the full availability matrix. Twelve archetypes are the existing v1.1 typologies unchanged, four are newly retrieved, two are derived with their bounding argument stated. An entry inherits a *cited* envelope and the report names the evidence class it inherited from — this is how the catalogue is adopted without weakening D-017.

**Four retrieval findings are load-bearing and must survive implementation.**

1. **Small constructed water features take their own archetype at 0.0–1.0 °C**, separate from large water bodies at 0.5–3.0 °C (`jacobs2020`, `yao2023b`, `ampatzidis2020` against `volker2013`, `yao2023a`). The two clusters exist as separate bodies of study, **not as a dose–response curve** — the size-threshold literature is land-surface-temperature only — so the engine must never interpolate between them by area. Without this split, constructed wetlands and water squares would have inherited `blue_green_corridor` (1.0–3.0 °C) on family resemblance and been overstated roughly threefold.
2. **Non-canopy vegetation is 0.0–1.5 °C** (`armson2012`, `gill2013`), with a genuine zero floor for dry or dormant planting. `armson2012` is decisive because it measures grass cutting *surface* temperature by up to 24 °C while having little effect on globe temperature — the surface/air conflation that inflates most published grass figures.
3. **Vegetated shade structures are 0.0–2.5 °C, low confidence** (`chafer2020`, `ouyang2024`, `colter2019`). The `keravec2026` "shading devices 2.0 °C" figure **does not transfer to pergola scale** and is not used: that category aggregates area-scale shading, and applying it would rate a pergola above measured tree canopy.
4. **Both productive classes inherit, and the gap is citable.** `kumar2024` reviews 51 green–blue infrastructure types across 202 publications and places allotments and city farms among the least-studied with insufficient data to quantify. Irrigation is documented as *sustaining* an entry's position in its envelope through drought, never as raising it (`cheung2022`: measured agricultural cooling 0.09–0.43 °C against modelled potentials of 2.1–2.5 °C, and irrigation warms nights).

**A validation, and a deliberate non-adoption.** `kumar2024` post-dates the v1.1 calibration and reports street trees at up to 2.8 °C in situ — inside the tool's 0.5–3.0 °C envelope, so D-014's conservative calibration holds against newer evidence. The same review reports figures well above the tool's envelopes for other types (green walls 4.1 ± 4.2 °C, vegetated balconies 3.8 ± 2.7 °C, botanical gardens 5.0 ± 3.5 °C). These are **not** adopted: selective adoption would break internal consistency (balconies outscoring street trees), and wholesale adoption is a full library recalibration requiring its own sensitivity analysis. Recorded as a candidate for a future methodology review.

**The four remaining decisions, approved as recommended.**

- **D-044.1 — The four new site questions gate availability and feed no score.** Gating is not scoring. Making them scoring inputs would need its own justification and would move every existing result. They are recorded in the input schema and disclosed in the field reference as availability-only, in the manner D-031 used for `heat_index_concern`.
- **D-044.2 — The release is `v2.0.0`.** `nbs_type` becomes a list and the schema gains four fields, which breaks stored drafts. D-029 forbids silent migration, so drafts are migrated **explicitly**: `nbs_type` is wrapped into a single-element list, the four new fields are absent (not defaulted), and the migration is itemised. Stored *results* are never touched — they keep the methodology version that produced them (OQ-15). Package semver moves to 2.0.0 while the methodology version stays date-stamped and independent (D-037).
- **D-044.3 — Suitability is inherited from the archetype, with per-entry overrides only where the source text states a constraint.** Inventing a minimum area or a soil requirement for each of 110 entries would manufacture precision the catalogue does not contain; inheriting and overriding on evidence keeps every value traceable to either a cited archetype or a quoted line of the source.
- **D-044.4 — Package size is unbounded but warned above five components.** Under the capped-never-summed rule (D-038) a large package's headline number is carried by its strongest member while the remainder add co-benefit breadth, so a hard cap would forbid something harmless; the warning states plainly that adding a sixth component will not raise the temperature estimate.

Implementation may now proceed against [V1.2-BRIEF.md](V1.2-BRIEF.md) and both halves of the review pack. The sensitivity analysis is **regenerated, not carried forward** — unlike `2026.08.03`, this release genuinely changes the typology library.

## D-045 — v2.0.0 implementation rulings, and one envelope corrected against its source (2026-08-01)

Recorded during the implementation of D-043 and D-044. One is a methodology change; the rest fix implementation shape without moving a value.

**D-045.1 — `large_water_body` ships at 0.1–3.0 °C, not the proposed 0.5–3.0 °C.** This is the only approved value this release moved, and it moved because the evidence underneath it was not what the review pack said.

The pack attributed to `yao2023a` a cooling magnitude "near 2 °C". Source verification before the value entered configuration established that the paper reports no such figure: *Are water bodies effective for urban heat mitigation?* measures urban lakes in two humid subtropical cities at a **0.1–0.6 °C** daytime cool island — an order of magnitude below the attributed value — alongside a 1.2–1.3 °C nocturnal heat island. Holding the floor at 0.5 °C would have made the tool claim more than its most direct field evidence supports, which is precisely the inflation D-008 exists to prevent, and would have shipped a citation that does not say what the configuration claims it says.

The ceiling is unchanged at 3.0 °C, on `keravec2026` (2.1 °C) and the upper bound of `volker2013`'s confidence interval (3.2 K). The resulting envelope is wide, and **the width is the finding**: a remote-sensing-inclusive meta-analysis and direct field measurement of lakes disagree by an order of magnitude, and `ampatzidis2020` identifies remote sensing as the overestimating mode. A narrower envelope would have to pick a side the evidence does not support picking, so the archetype carries an output caveat stating the disagreement rather than leaving a reviewer to wonder why the range is so wide.

Four further corrections were made to the pack's citations before they shipped, none of which moved a value: `chafer2020`'s author list was wrong (Pisello and Piselli, not Pérez and Coma); `yao2023b`'s nocturnal warming is 1.8 °C, not a 1.2–1.8 °C range conflated with the other Yao paper; `kraemer2022` is a study of two Leipzig **parks** under drought, not of allotment gardens, and is cited as such; and `ouyang2024`'s mean-radiant-temperature reduction is 13.7–15.9 °C, not 14–16. The verification policy of the bibliography did its job here, and the discipline is worth naming: **a design may be approved, but a citation is only settled once it has been read.**

**D-045.2 — Availability gates on positive confirmation for physical facts, and never subtracts on an unanswered governance question.** Three of the four new questions describe a physical fact about the site and withhold their entries until confirmed; the productive-governance multi-select filters only what it names and suppresses nothing while empty. This is D-043.3's reasoning applied consistently — the ruling exists because a "no" would have suppressed the commercially delivered entries — and it is the reason the review pack's published situation counts are governance-agnostic. All nine of those counts, and all four land-use totals, are asserted directly by the test suite; the governance filter is tested separately, since answering it necessarily reduces them (a school site offers 67 entries unanswered and 63 with only *institutional* selected).

**D-045.3 — The urban-context sub-indicator reads the availability matrix's own land-use list.** D-022 compares the site's land use against a typology's `typical_use_context`; rather than maintain a second per-entry list that could drift, the resolved entry's context list *is* its availability list. An entry is therefore "in context" exactly where it is offered, and out of context only where the user has deliberately selected something the matrix did not offer — which D-019 permits and the engine warns about.

**D-045.4 — Migration distinguishes a retired slug from a slug whose evidence class moved.** Nine v1.1 slugs no longer name a selectable entry and their drafts must be re-chosen; three (`pocket_park`, `blue_green_corridor`, `courtyard_greening`) still name a catalogue entry and only their inherited evidence class changed. Telling a user to re-select an intervention that is still there would be a false alarm about their own saved work, so the two cases carry different notes and a test compares both tables against the library rather than trusting them to be maintained by hand. Stored *results* remain untouched in every case (OQ-15).

**D-045.5 — The two-page report contract is held by bounding what grows, and counting what is left out.** Package size is deliberately unbounded (D-044.4), so the package itemisation and the assumptions list can both outgrow a page. Each is rendered against a measured space budget and states how many lines did not fit; warnings are never truncated, being safety information, and the method note always renders. The workbook has no page limit and always carries every line. A report that silently showed part of a package would imply it had shown all of it.

**D-045.6 — Per-component co-benefit defaults are itemised once per component in a package.** The same handful of library defaults is applied per component, and repeating five near-identical sentences for each of six components buries the disclosure it exists to make. A package itemises one line per component naming the dimensions that took a default; single-intervention assessments are unchanged. The defaults applied are identical either way — only their presentation differs.

---

## D-046 — The catalogue release shipped; the map release is scoped as v2.1 (2026-08-01)

**The catalogue release shipped** as package `2.0.0` at methodology `2026.08.04`: 110 typologies over 18 cited archetypes, packages, availability gating, four availability-only questions, and explicit draft migration. Every gate passed, including a packaged-wheel smoke check that served the published 67 school-site options from an installed wheel. Implementation rulings are in D-045.

**The third release of the D-038 programme is renumbered from `v1.3` to `v2.1`**, because package semver moved to 2.0.0 for the catalogue release and a `v1.3` tag after `v2.0.0` would be nonsense. Scope is unchanged: map-based site selection with parameter autofill, deliberately last so that autofill targets the questionnaire v2.0 leaves behind. Recorded in [V2.1-BRIEF.md](V2.1-BRIEF.md).

**A label collision is corrected in the same change set.** [V2-VISION.md](V2-VISION.md) used `v2.0`–`v2.3` as *thematic wave* labels for the deferred vision, written when the product was v1 and "v2" meant "the future". The product now genuinely occupies that version namespace, so the same string denoted two different things — the shipped catalogue release and an unbuilt portfolio-mode wave. The vision's waves are relabelled **Horizon 1–4**, which is what they always were. No vision scope changes; only labels that had become ambiguous. Renaming the vision rather than the product is the right way round: package versions are stamped into released artefacts, results, and tags, and cannot be renamed after the fact.

**Three decisions are open for v2.1 and are stated in the brief rather than pre-empted here.** The first is load-bearing: a usable basemap and the no-third-party-request rule (D-030, D-035) cannot both be had in full, and the brief sets out four options with a recommendation. It is flagged as the first deliberate exception to a rule that has held absolute for four releases, and it is the author's call, not the implementer's. The other two concern whether an autofilled value counts as *supplied* for confidence, and the Köppen–Geiger to climate-zone mapping, which is a methodology value needing a citation and a version bump.

---

## D-047 — The three v2.1 decisions, ruled (2026-08-01)

All three questions [V2.1-BRIEF.md](V2.1-BRIEF.md) left open are approved as recommended. The design gate for v2.1 is closed; implementation may proceed against the brief.

**D-047.1 — The basemap ships bundled, and external tiles are opt-in.** Natural Earth vectors (public domain) are bundled so the map works entirely offline and delivers the country and climate-zone autofills with no network at all; external tiles exist only if a user explicitly names a source and switches it on.

This is **the first deliberate exception to the no-third-party-request rule** since D-030 established it, and it is worth being precise about what is and is not being conceded. The rule is not relaxed: the **default build still makes no third-party request**, CI still enforces that, and a deployment inside a restricted network keeps working exactly as it does today. What is conceded is that a world-scale basemap at street zoom cannot be bundled — a fact about the size of the earth, not a preference — so a user who needs to draw a site boundary accurately is offered an informed choice rather than a silent limitation. The alternative considered and rejected was defaulting tiles on, which would have made the packaged tool phone out of the box and quietly broken the institutional deployments the rule exists to protect.

Verifying the option before ruling on it moved one number materially: the bundled basemap was estimated at 5–15 MB in the first draft of the brief and is a few hundred kilobytes in fact (Natural Earth 1:110m admin-0 countries is ~175 KB). Size is therefore not an argument against bundling, and the decision reduced to the tile question alone.

**D-047.2 — An autofilled value counts as supplied, and is marked as autofilled.** The user chose the location and the classification is cited, so it is not a guess and should not be treated as one. It is marked as autofilled in the interface, in the stored input, and in the report's Inputs sheet — the provenance treatment defaults have carried since D-034 — and it **never overwrites an answer the user has already given**.

The alternative — not counting it — was rejected for a specific perversity: it would mean that clicking the map and typing the same climate zone by hand produce *different confidence readings for identical inputs*, which teaches users that the tool's confidence meter measures effort rather than information. The disclosure requirement does the work that not-counting was meant to do, without that defect.

**D-047.3 — Köppen–Geiger classes with no urban-heat counterpart map to `other`.** Polar and boreal classes (ET, EF, Dfc and neighbours) map to `other`, which is already the tool's neutral climate condition at factor 1.0, so an unclassifiable location receives neither boost nor penalty. Forcing them into `temperate` was rejected because it would assert that a tundra site cools like a temperate one, which no source in the bibliography supports — an uncited claim introduced through a lookup table is still an uncited claim.

**Source and licence settled before the ruling, not after.** Beck, H.E., et al. (2023), *High-resolution (1 km) Köppen-Geiger maps for 1901–2099 based on constrained CMIP6 projections*, Scientific Data 10, 724, doi:10.1038/s41597-023-02549-6, CC BY 4.0 — the same licence basis on which the `ember` emission factors already ship inside the wheel (D-036), so the redistribution precedent exists. The present-day map covers 1991–2020. The mapping table itself is a methodology value and requires an evidence-table entry, a `config/` table, and a **methodology version bump**; the release should ship the coarsest layer that classifies correctly rather than the finest available.

---

## D-013 — Weights are expert-calibrated and defended by sensitivity analysis (2026-07-30)

Aggregation weights cannot be "derived" from literature and we do not pretend otherwise. They are declared as expert judgment following composite-indicator practice (OECD/JRC Handbook), and defended empirically via the published sensitivity analysis (see D-011/OQ-29).
