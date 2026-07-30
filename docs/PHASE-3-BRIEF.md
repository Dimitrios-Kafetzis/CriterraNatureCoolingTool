# Phase 3 Brief — FastAPI Service

The implementation brief for Phase 3, fixed at the close of Phase 2 so that the
API is implemented against settled decisions rather than re-designed. Companion
to [ARCHITECTURE.md](ARCHITECTURE.md) (structure) and
[DECISIONS.md](DECISIONS.md) (rationale; D-028 records the design decisions
below).

## Starting state

Phases 0–2 are complete at engine `v0.2.0`, methodology `2026.08.02`:

- The engine is a pure, deterministic function
  `run_assessment(AssessmentInput, MethodologyConfig) → AssessmentResult`
  (`backend/src/nature_cooling/engine/`), with 100% line coverage enforced in
  CI, 20 hand-verified golden scenarios, and a published sensitivity analysis.
- The public engine surface is `nature_cooling.engine`:
  `AssessmentInput`, `AssessmentResult`, `MethodologyConfig`, `load_config`,
  `get_config`, `run_assessment`. Phase 3 consumes this surface and does not
  reach around it.

## Scope

Everything under `backend/src/nature_cooling/api/` per ARCHITECTURE §2:
`main.py` (app factory) plus `routes/`, and a thin local-first storage layer.

**Stateless assessment endpoints (ARCHITECTURE §2.3):**

| Endpoint | Purpose |
|---|---|
| `POST /api/assessments/evaluate` | Validate input, run the engine, return the full result |
| `POST /api/assessments/validate` | Dry-run validation for inline form feedback (see contract below) |
| `GET  /api/typologies` | Typology library incl. suitability conditions and citations |
| `GET  /api/methodology` | Formulas, weights, factors, version — powers the methodology browser |
| `GET  /api/meta` | Engine version, methodology version, licence |

**Local-first persistence (D-020, D-021, D-028):** project/assessment CRUD and
a duplicate-assessment operation, exact endpoint shapes to be designed in
Phase 3 and recorded by updating the ARCHITECTURE §2.3 table in the same
change set.

## Decided contracts (D-028 — implement, do not re-litigate)

1. **`/validate` returns:** field errors (block progression within a step);
   warnings (never blocking; OQ-04/08: cover sum > 105%, intervention area >
   site area — exactly the engine's `_warnings` rules); a per-block confidence
   preview (levels and completeness percentages from
   `nature_cooling.engine.confidence`); and the **highest-value missing field
   hint** per block: the first unsupplied field group in the configured
   `derived_scores.yaml` order whose single completion would raise the block's
   confidence level — falling back to the first unsupplied group when no
   single completion raises the level. Deterministic, config-driven, no new
   methodology values. Validation has exactly two severities (OQ-08).
2. **Storage:** JSON under the platform user-data directory (`platformdirs`),
   one file per project: `schema_version`, `project_id` (UUID4), `name`,
   `created_at` / `updated_at` (ISO-8601 UTC), the site description, and
   `assessments[]`, each holding its full input, its full `AssessmentResult`
   (including `methodology_version` and `engine_version`), an `assessment_id`,
   a `label`, and `created_at`. **Stored results are never recomputed**
   (OQ-15): a newer methodology version is surfaced as *available*; re-running
   is an explicit user action that creates a new assessment. UUIDs and clocks
   live only in the API/storage layer — the engine remains pure.
3. **Comparison (D-021):** duplicating an assessment copies the site and
   vulnerability description into a new draft and blanks only the intervention
   and cost/energy groups.

## Non-negotiable rules

1. **The engine is not touched.** No file under `engine/` changes unless a
   genuine defect is found — in which case stop and raise it, as in Phase 2.
   No methodology value moves without a version bump across `config/`, the
   Methodology Report, and the paper.
2. **The API is a thin, stateless wrapper for scoring.** No score, default,
   threshold, or recommendation text originates in the API layer. One source
   of truth for every number.
3. **Determinism end-to-end for scoring responses**: identical request body +
   identical methodology version → byte-identical `evaluate` response body
   (timestamps and IDs appear only in storage endpoints).
4. **No AI attribution anywhere** — code, docs, commits. Sole author:
   Dimitris Kafetzis. Run the attribution grep before pushing.
5. **Quality gates unchanged:** `ruff check`, `ruff format --check`,
   `mypy` (strict), `pytest` with the 100% coverage gate now covering the
   `api` package as well as the engine (the API is thin; keep it fully
   covered). API contract tests use FastAPI's test client; storage tests use
   `tmp_path`, never the real user-data directory.
6. **New dependencies:** `fastapi`, `uvicorn` (serve extra), `httpx` (dev),
   `platformdirs`. Nothing heavier without a recorded decision.

## Delivery

Conventional Commits, one coherent Phase 3 change set to `main`, CI green.
Update: README roadmap (Phase 3 ✅, Phase 4 next), ARCHITECTURE §2.3 endpoint
table, decision-log entries for any new decisions taken during implementation,
and a `v0.3.0` tag on completion.
