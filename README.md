# Nature for Cooling — Rapid Assessment Tool

**An open-source, screening-level decision-support tool that helps planners, developers, and researchers evaluate and prioritise nature-based solutions (NbS) for urban cooling** — turning a structured site description into transparent, literature-grounded, comparable scores in minutes, so that early planning and investment decisions no longer rely on intuition or unaffordable simulation.

Developed by [Criterra](https://criterra.eu).

[![CI](https://github.com/Dimitrios-Kafetzis/CriterraNatureCoolingTool/actions/workflows/ci.yml/badge.svg)](https://github.com/Dimitrios-Kafetzis/CriterraNatureCoolingTool/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

> **Status: Phase 6 complete — the tool is packaged and published.** One `pip install` and one command (`nature-cooling serve`) now start the whole application — API and web app on a single origin — from a wheel that embeds the production frontend build and the cited methodology configuration. A container image ships to GHCR with a minimal compose file, the full documentation corpus is published at **[dimitrios-kafetzis.github.io/CriterraNatureCoolingTool](https://dimitrios-kafetzis.github.io/CriterraNatureCoolingTool/)**, and `vX.Y.Z` tags build and publish every artefact automatically. See [Roadmap](#roadmap).

---

## What it does

The tool answers five questions cities keep asking:

1. **Where** is urban heat most critical?
2. **Who** is most vulnerable?
3. **Which** nature-based solutions suit a given site?
4. **What** cooling, climate, cost, and social benefits will they deliver?
5. **Which** projects deserve priority for design and investment?

A user describes a site through a six-step questionnaire, selects one of 14 NbS typologies (street trees, urban forest, green roof, blue-green corridor, …), and receives:

- a **Heat Priority Index** (0–100) — how much the site deserves attention,
- a **Cooling Potential Score** (0–100) with an indicative **temperature-reduction range (°C)**,
- energy savings, avoided GHG emissions, cost and payback estimates,
- equity and co-benefit scores,
- a single **NbS Cooling Opportunity Score** (0–100) for comparing options and sites,
- a **confidence level** reflecting data completeness,
- an exportable report.

Interventions for the **same site can be compared side by side** (option A / B / C).

## What it is not

The tool is explicitly **not** a microclimate simulation (ENVI-met-class), a building energy model, a species-level planting design tool, or a regulatory/engineering approval instrument. It is a screening instrument for early-stage prioritisation: all quantitative outputs are **ranges, never point estimates**, and every result carries a confidence level.

## Design principles

| Principle | Meaning |
|---|---|
| **Methodology is the product** | All scoring rules, weights, and typology data live in inspectable configuration files (`config/`), not in code. |
| **Literature-grounded** | Every performance value cites peer-reviewed sources; the evidence base ships with the tool. See [docs/methodology/](docs/methodology/). |
| **Transparent & traceable** | Every score has a single documented formula. No black boxes, no ML in scoring. |
| **Deterministic** | Same inputs + same config version → same outputs, always. |
| **Tolerant of missing data** | Every optional input has a fallback; missing data lowers confidence but never blocks an assessment. Applied defaults are itemised in the result. |
| **Open** | Apache-2.0 licensed; code, methodology, and data are public. |

## Repository structure

```
├── config/        Methodology as data — typologies, weights, factors (YAML, cited)
├── backend/       Python: calculation engine (pure) + FastAPI API
├── frontend/      React + TypeScript web application
├── docs/          Architecture, decision log, methodology & evidence base, v2 vision
├── paper/         The methodology as a LaTeX scientific paper (for external review)
└── .github/       CI/CD workflows
```

Key documents:

- **[docs/methodology/METHODOLOGY.md](docs/methodology/METHODOLOGY.md)** — the Methodology Report: the complete scientific basis, written for expert review
- **[paper/](paper/)** — the same methodology as a full scientific paper ([main.pdf](paper/main.pdf), 72 pages): the document to send to UNEP, scientific reviewers, and public authorities
- [docs/methodology/EVIDENCE-TABLES.md](docs/methodology/EVIDENCE-TABLES.md) — per-typology derivations from the literature
- [docs/methodology/BIBLIOGRAPHY.md](docs/methodology/BIBLIOGRAPHY.md) — sources with verification status
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — system design
- [docs/UX-SPECIFICATION.md](docs/UX-SPECIFICATION.md) — questionnaire and results interaction design
- [docs/DECISIONS.md](docs/DECISIONS.md) — decision log with rationale
- [docs/V2-VISION.md](docs/V2-VISION.md) — deferred features and product vision

## Methodology at a glance

Cooling values are **daytime, pedestrian-level air temperature reductions**, each traced to published evidence — never mixed with surface temperature or comfort indices. Three calibration choices are worth knowing before reading any output:

- **Site conditions can lower an estimate below the literature envelope, never raise it above.** A well-suited site scores higher, but the tool will not claim more cooling than published evidence supports.
- **Energy savings are derived, not asserted** — from the estimated temperature reduction via a published temperature–electricity-demand sensitivity, rather than from unsourced per-typology factors.
- **No default costs ship with the tool.** NbS unit costs vary by an order of magnitude between contexts, so cost outputs are reported as *not estimated* unless the user supplies figures.

The methodology also states plainly where it is weak: green façade and bioswale evidence is thin or conflicting, all values are daytime-only, and the aggregation weights are expert judgment. Critique is welcome — see [how to challenge the methodology](docs/methodology/METHODOLOGY.md#9-methodology-governance).

## Roadmap

| Phase | Deliverable | Status |
|---|---|---|
| 0 | Repository scaffold, governance docs, CI | ✅ |
| 1 | Methodology evidence base + expert Methodology Report + cited configuration | ✅ |
| 2 | Calculation engine (pure Python, 100% test coverage, golden scenarios, sensitivity analysis) | ✅ |
| 3 | FastAPI service (scoring, validation + confidence preview, local-first project storage) | ✅ |
| 4 | React/TypeScript web app (questionnaire wizard, dashboard, A/B/C comparison) | ✅ |
| 5 | Report export (PDF / XLSX) | ✅ |
| 6 | Documentation site, packaging, hosting | ✅ |

## Running the tool

### Packaged (one command)

Install the wheel from the [latest release](https://github.com/Dimitrios-Kafetzis/CriterraNatureCoolingTool/releases/latest) — it embeds the web application and the cited methodology configuration, so nothing else is needed:

```bash
pip install "criterra_nature_cooling-<version>-py3-none-any.whl[serve]"
nature-cooling serve                  # http://127.0.0.1:8000 — app + API, one origin
```

Or run the container image (projects persist in a named volume at the platform data path):

```bash
docker run -p 8000:8000 ghcr.io/dimitrios-kafetzis/criterranaturecoolingtool:latest
# or, with the durable volume from the repository's compose.yaml:
docker compose up -d
```

Both serve the web app at `/` and the API at `/api` from one origin (D-030 — no CORS middleware, by design). Projects are stored as JSON under your platform user-data directory; stored results are never silently recomputed when the methodology moves.

To build the wheel yourself: `tools/build_wheel.sh` (Node 18+ and the backend `dev` extra) — it builds the frontend, embeds it with the configuration into the package, and produces `backend/dist/*.whl`.

### Development (two processes)

The FastAPI service and the Vite dev server, which proxies `/api` to it (same-origin integration, D-030).

```bash
# Terminal 1 — the API
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,serve]"
pytest   # 100% coverage gate (engine + API)

uvicorn nature_cooling.api.main:app   # http://127.0.0.1:8000/docs

# Terminal 2 — the web app (Node 18+)
cd frontend
npm install
npm run dev                           # http://127.0.0.1:5173
```

The API serves scoring (`POST /api/assessments/evaluate`), inline validation with a live confidence preview (`POST /api/assessments/validate`), the typology library and methodology as data, local-first project storage, and report export — `GET /api/projects/{id}/assessments/{aid}/report.pdf` and `…/report.xlsx` render a stored, evaluated assessment as the 2-page PDF report or the XLSX workbook (the results page's **Export** actions download exactly these). See the endpoint table in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#23-api-surface-v1). Projects are stored as JSON under your platform user-data directory; stored results are never silently recomputed when the methodology moves.

The frontend's API types are generated from the service's OpenAPI schema and committed (`frontend/openapi.json`, `frontend/src/api/schema.ts`); after changing the API, regenerate with `npm run generate` — CI fails on drift.

The engine also remains usable standalone:

```python
from nature_cooling.engine import AssessmentInput, load_config, run_assessment

result = run_assessment(
    AssessmentInput(
        assessment_scale="neighbourhood",
        site_area_m2=6000,
        climate_zone="temperate",
        nbs_type="street_tree_planting",
    ),
    load_config(),
)
print(result.opportunity.score, result.opportunity.category)
```

## Documentation site

The full documentation corpus — Methodology Report, evidence tables, bibliography, sensitivity analysis, architecture, decision log, UX specification — is published at [dimitrios-kafetzis.github.io/CriterraNatureCoolingTool](https://dimitrios-kafetzis.github.io/CriterraNatureCoolingTool/), rendered directly from the Markdown in this repository (no page is authored twice) and redeployed by CI on every push to `main`. Preview locally with `pip install -r docs/requirements.txt && mkdocs serve`.

## License

[Apache-2.0](LICENSE) © Criterra
