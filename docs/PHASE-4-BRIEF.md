# Phase 4 Brief — Web Application

The implementation brief for Phase 4, fixed at the close of Phase 3 so that the
web app is implemented against settled decisions rather than re-designed.
Companion to [UX-SPECIFICATION.md](UX-SPECIFICATION.md) (the interaction
design this phase realises), [ARCHITECTURE.md](ARCHITECTURE.md) §3 and §5
(structure and gates), and [DECISIONS.md](DECISIONS.md) (D-030 records the
implementation-shape decisions; D-031 closes the D-027 questionnaire
deferrals).

## Starting state

Phases 0–3 are complete at `v0.3.0`, methodology `2026.08.02`:

- The FastAPI service exposes everything the frontend needs (ARCHITECTURE
  §2.3): stateless `/api/assessments/evaluate` and `/api/assessments/validate`
  (errors, never-blocking warnings, per-block confidence preview, and the
  highest-value missing field hint), the typology library and methodology as
  cited data, service metadata, and full project/assessment CRUD with explicit
  evaluation and the D-021 duplicate operation over local-first storage.
- The frontend computes nothing. Even previews come from `/validate`
  (ARCHITECTURE boundary 3); the wizard, dashboard, comparison view, and
  methodology browser are renderers of API responses.

## Scope

Everything under `frontend/` per ARCHITECTURE §3, realising the UX
specification in full:

| Screen | Source of truth |
|---|---|
| Entry: start new / open saved project | UX §2; `GET /api/projects` |
| Six-step questionnaire wizard with inline validation, warnings, auto-save, and the live confidence panel | UX §3–4; `/validate`, assessment `PATCH` (D-020) |
| Guided typology picker: 14 cards sorted and annotated by fit, unsuitable options selectable (D-019) | UX §5; `GET /api/typologies` + site data already entered |
| Results dashboard: score cards, flags, recommendation, six blocks with ranges and per-block confidence, assumptions, method note | UX §6; explicit evaluate endpoint |
| Same-site A/B/C comparison via duplicate (D-021) | UX §7; duplicate endpoint |
| Methodology browser rendering the live configuration with citations | UX §8; `GET /api/methodology`, `GET /api/typologies` |

Visual identity: criterra.eu design tokens (paper `#eaebe2`, ink `#16231c`,
brand green `#2e6a4e`; Newsreader / Hanken Grotesk / IBM Plex Mono,
self-hosted). *"A scientific instrument, not a lifestyle app."* WCAG AA;
`prefers-reduced-motion` respected; strings externalised (UX §9).

## Decided contracts (D-030, D-031 — implement, do not re-litigate)

1. **Toolchain:** Vite + React + TypeScript strict; `vitest` + Testing
   Library; ESLint (typescript-eslint) + Prettier. CI gains a frontend job
   (lint, format check, `tsc --noEmit`, tests); the backend job is unchanged.
2. **Same-origin integration:** the Vite dev server proxies `/api` to the
   FastAPI service. The API gains **no CORS middleware**.
3. **Generated API types:** TypeScript types come from the service's OpenAPI
   schema, are committed, and CI fails on drift. No hand-written duplicates
   of engine schemas.
4. **State:** thin typed `fetch` client + React state/context; `react-router`
   for navigation; no data-fetching or global-state library. Auto-save =
   debounced draft `PATCH`; validation and the confidence panel = debounced
   `/validate` with the full draft payload, errors filtered to the active
   step's fields. Evaluated results render from the stored result only.
5. **Questionnaire field rulings (D-031):** `heat_index_concern` is not
   asked; `current_shade_level` is asked in step 2; "planted area" does not
   exist. The confidence panel renders the evidence-cap explanation when
   `cooling_capped_by_evidence` is true (UX §4).

## Non-negotiable rules

1. **The engine and API are not touched** unless a genuine defect is found —
   stop and raise it, as in Phases 2–3. No methodology value moves without a
   version bump across `config/`, the Methodology Report, and the paper.
2. **No number originates in the frontend.** No score, threshold, band,
   default, confidence level, or recommendation text is computed or hard-coded
   client-side; every figure and level renders from an API response. Score
   bands, weights, and typology values shown in the methodology browser come
   from `GET /api/methodology` / `GET /api/typologies`, never from constants.
3. **Validation severities are exactly two** (OQ-08): errors block progression
   within their step; warnings never block anything.
4. **No AI attribution anywhere** — code, docs, commits. Sole author:
   Dimitris Kafetzis. Run the attribution grep before pushing.
5. **Quality gates:** backend gates unchanged (`ruff check`, `ruff format
   --check`, strict `mypy`, `pytest` at 100% coverage); frontend adds ESLint,
   Prettier check, `tsc --noEmit`, and `vitest` component/unit tests covering
   each screen's contract with the API (mock at the `fetch` boundary using
   recorded response shapes, not invented ones).
6. **Runtime dependencies limited to:** `react`, `react-dom`, `react-router`.
   Dev tooling limited to the D-030 list (Vite, TypeScript, vitest, Testing
   Library, ESLint stack, Prettier, an OpenAPI type generator). Nothing
   heavier — no component libraries, no CSS frameworks, no chart libraries
   (the design uses score cards and simple meters) — without a recorded
   decision.

## Delivery

Conventional Commits, one coherent Phase 4 change set to `main`, CI green
(both jobs). Update: README roadmap (Phase 4 ✅, Phase 5 next) and the
running-locally section (dev proxy workflow), decision-log entries for any new
decisions taken during implementation, backend package and frontend
`package.json` to 0.4.0, and a `v0.4.0` tag with a GitHub release on
completion.
