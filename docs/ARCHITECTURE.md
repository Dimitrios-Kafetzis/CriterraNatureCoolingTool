# System Architecture

Architecture of the Nature for Cooling Rapid Assessment Tool. Companion to [DECISIONS.md](DECISIONS.md) (why) and [methodology/](methodology/) (what the numbers mean). This document describes v1; deferred capabilities live in [V2-VISION.md](V2-VISION.md).

## 1. Overview

```mermaid
flowchart LR
    subgraph data["Methodology as data"]
      Config["config/*.yaml<br/>typologies · weights · factors<br/>country defaults · citations"]
    end
    subgraph backend["backend/ (Python)"]
      Engine["nature_cooling.engine<br/>pure, deterministic scoring"]
      API["nature_cooling.api<br/>FastAPI (stateless)"]
      Report["report builder<br/>PDF / XLSX (Phase 5)"]
    end
    subgraph frontend["frontend/ (React + TS)"]
      Wizard["6-step questionnaire wizard"]
      Dash["results dashboard + A/B/C comparison"]
      Method["methodology browser"]
    end
    Config --> Engine
    Engine --> API
    API --> Wizard
    API --> Dash
    API --> Method
    Engine --> Report
```

Three hard boundaries:

1. **Config → Engine.** All methodology values (typology performance, weights, factors, defaults, citations) are YAML under `config/`, schema-validated at load. Changing the methodology never requires changing code.
2. **Engine → API.** The engine is a pure function `run_assessment(AssessmentInput, MethodologyConfig) → AssessmentResult` — no I/O, no network, no randomness, no global state. The API is a thin stateless wrapper.
3. **API → Frontend.** The frontend owns UX only. It never computes scores; even previews come from the API. One source of truth for every number.

## 2. Backend

### 2.1 Package layout

```
backend/
├── pyproject.toml                  # distribution: criterra-nature-cooling
├── src/nature_cooling/
│   ├── __init__.py                 # __version__ (engine semver)
│   ├── engine/
│   │   ├── models.py               # Pydantic v2: AssessmentInput / AssessmentResult
│   │   ├── config.py               # YAML loader + schema validation + version stamp
│   │   ├── scoring/                # one module per formula family
│   │   │   ├── heat_exposure.py    #   heat exposure (data-rich / data-poor paths)
│   │   │   ├── vulnerability.py
│   │   │   ├── heat_priority.py
│   │   │   ├── suitability.py      #   suitability score + hard suitability flags (D-009)
│   │   │   ├── adjustment.py       #   derived site factors (OQ-16/17 rules)
│   │   │   ├── cooling.py          #   score + °C range clipped to envelope (D-008)
│   │   │   ├── energy_ghg.py
│   │   │   ├── costs.py            #   capex, savings, payback, derived feasibility (D-010)
│   │   │   ├── co_benefits.py
│   │   │   ├── equity.py
│   │   │   └── final_score.py
│   │   ├── confidence.py           # branched per-block confidence (OQ-09)
│   │   ├── recommendation.py       # deterministic template composer
│   │   └── runner.py               # orchestration: run_assessment()
│   └── api/
│       ├── main.py                 # FastAPI app factory
│       ├── schemas.py              # API-layer models + storage document schema (D-028)
│       ├── storage.py              # local-first project store (platformdirs, atomic JSON)
│       ├── validation.py           # /validate: errors, warnings, confidence preview + hint
│       └── routes/                 # assessments, methodology, meta, projects
└── tests/
    ├── scoring/                    # unit tests per module (100% engine coverage target)
    ├── scenarios/                  # golden cases: input JSON → hand-verified expected output
    └── api/                        # contract tests per endpoint (100% api coverage target)
```

### 2.2 Engine contract

- **Deterministic:** same `AssessmentInput` + same config version → byte-identical `AssessmentResult`.
- **Versioned:** every result records `engine_version` (semver) and `methodology_version` (date-stamped config version). Comparisons across differing methodology versions warn.
- **Missing data:** required fields fail validation before scoring; optional fields fall back (qualitative → `unknown` = 50; quantitative → `None` propagates to `not_applicable`, never a silent zero). Every applied default is itemised in `assumptions_applied`.
- **Suitability gates:** disqualifying site conditions produce `suitability_flags` in the result; the UI and report must render them prominently (D-009).

### 2.3 API surface (v1)

| Endpoint | Purpose |
|---|---|
| `POST /api/assessments/evaluate` | Validate input, run engine, return full result (stateless) |
| `POST /api/assessments/validate` | Dry-run validation for inline form feedback: errors + warnings, per-block confidence preview, highest-value missing field hint (D-028) |
| `GET  /api/typologies` | Typology library incl. suitability conditions and citations |
| `GET  /api/methodology` | Formulas, weights, factors, version — powers the methodology browser |
| `GET  /api/meta` | Engine version, methodology version, license |
| `GET  /api/projects` | Project summaries, most recently updated first |
| `POST /api/projects` | Create a project (name + site description) |
| `GET  /api/projects/{id}` | Full project incl. assessments and `methodology_update_available` flags (OQ-15) |
| `PATCH /api/projects/{id}` | Update name / site description |
| `DELETE /api/projects/{id}` | Delete a project |
| `POST /api/projects/{id}/assessments` | Create a draft assessment (auto-save target, D-020) |
| `GET  /api/projects/{id}/assessments/{aid}` | One stored assessment |
| `PATCH /api/projects/{id}/assessments/{aid}` | Update label / draft input (input frozen once evaluated) |
| `DELETE /api/projects/{id}/assessments/{aid}` | Delete an assessment |
| `POST /api/projects/{id}/assessments/{aid}/evaluate` | Explicitly run the engine and persist the result; refuses to recompute a stored result (OQ-15) |
| `POST /api/projects/{id}/assessments/{aid}/duplicate` | Comparison draft: carries the site description, blanks intervention + cost/energy groups (D-021) |
| `POST /api/reports/pdf` (Phase 5) | Render a result to the 2-page PDF |

Persistence in v1 is **local-first**: one JSON document per project (`schema_version`, identity, timestamps, site description, `assessments[]` each holding its full input and full versioned result) under the `platformdirs` user-data directory, owned by a thin storage layer behind the API (D-028); multi-user storage is v2. Stored results are never recomputed — a newer methodology version is surfaced as available, and re-running is an explicit user action creating a new assessment (OQ-15).

## 3. Frontend

React + TypeScript (Vite). Structure mirrors the user journey:

- **Questionnaire wizard** — the 6 input groups as steps (project → site → climate → vulnerability → intervention → cost/energy); inline validation via `/validate`; every field with the qualitative fallback and "unknown" affordances the methodology requires.
- **Results dashboard** — score cards (Heat Priority Index, NbS Cooling Opportunity Score), the six output blocks, branched confidence badges, suitability flags, assumptions list, recommendation.
- **Comparison view** — same site, interventions A/B/C side by side (D-005).
- **Methodology browser** — renders `/api/methodology` + citations; every score in the UI links to its formula and sources.

Visual identity: the criterra.eu design tokens (paper `#eaebe2`, ink `#16231c`, brand green `#2e6a4e`; Newsreader / Hanken Grotesk / IBM Plex Mono, self-hosted). Design north star: *"a scientific instrument, not a lifestyle app"* — whitespace, one accent colour, score cards, no rainbow dashboards. WCAG AA.

## 4. Configuration (`config/`)

| File | Content |
|---|---|
| `nbs_typologies.yaml` | 14 typologies: performance values, suitability conditions, cost defaults — **every value carries a `sources:` array (DOI + finding)** |
| `weights.yaml` | All aggregation weights (single global set, D-011/OQ-29) |
| `adjustment_factors.yaml` | Condition → factor tables + derivation rules |
| `input_mapping.yaml` | Qualitative → numeric mappings |
| `country_defaults.yaml` | Emission factors, energy prices, currency (each cited: IEA/Ember, national sources) |
| `recommendation_templates.yaml` | Deterministic recommendation fragments |

Each file has a top-level `version:` (date-stamped). CI validates schemas and refuses uncited performance values.

## 5. Quality and CI/CD

- **Tooling:** `ruff` (lint + format), `mypy --strict` on the engine, `pytest` + coverage; frontend: `eslint`, `tsc`, `vitest` (from Phase 4).
- **Tests:** unit tests per scoring module; ~20 golden scenarios with hand-verified outputs as regression armor; config schema tests; API contract tests; determinism test (repeat runs byte-identical).
- **CI (GitHub Actions):** every push/PR → lint, type-check, tests, coverage gate. Releases tagged `vX.Y.Z`; methodology version changes require a matching Methodology Report update (checked in review).
- **Conventional Commits**; one development phase per PR/merge to `main`.

## 6. Deployment model

- **v1 local-first:** one command starts API + frontend on the developer/user machine.
- **Later hosting:** the same containers deploy to a small VPS or PaaS; the engine's statelessness makes this a packaging exercise, not a rewrite.
