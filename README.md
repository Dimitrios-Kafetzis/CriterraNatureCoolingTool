# Nature for Cooling — Rapid Assessment Tool

**An open-source, screening-level decision-support tool that helps planners, developers, and researchers evaluate and prioritise nature-based solutions (NbS) for urban cooling** — turning a structured site description into transparent, literature-grounded, comparable scores in minutes, so that early planning and investment decisions no longer rely on intuition or unaffordable simulation.

Developed by [Criterra](https://criterra.eu).

[![CI](https://github.com/Dimitrios-Kafetzis/CriterraNatureCoolingTool/actions/workflows/ci.yml/badge.svg)](https://github.com/Dimitrios-Kafetzis/CriterraNatureCoolingTool/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

> **Status: Phase 1 complete — methodology evidence base published.** The [Methodology Report](docs/methodology/METHODOLOGY.md) is open for expert review; the calculation engine is next. See [Roadmap](#roadmap).

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
├── frontend/      React + TypeScript web application (Phase 4)
├── docs/          Architecture, decision log, methodology & evidence base, v2 vision
└── .github/       CI/CD workflows
```

Key documents:

- **[docs/methodology/METHODOLOGY.md](docs/methodology/METHODOLOGY.md)** — the Methodology Report: the complete scientific basis, written for expert review
- [docs/methodology/EVIDENCE-TABLES.md](docs/methodology/EVIDENCE-TABLES.md) — per-typology derivations from the literature
- [docs/methodology/BIBLIOGRAPHY.md](docs/methodology/BIBLIOGRAPHY.md) — sources with verification status
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — system design
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
| 2 | Calculation engine (pure Python, 100% test coverage, golden scenarios, sensitivity analysis) | 🔄 next |
| 3 | FastAPI service | ⏳ |
| 4 | React/TypeScript web app (questionnaire wizard, dashboard, A/B/C comparison) | ⏳ |
| 5 | Report export (PDF / XLSX) | ⏳ |
| 6 | Documentation site, packaging, hosting | ⏳ |

## Running locally

> Coming with Phase 3/4. The target is a single command for the full stack; the engine will also be usable standalone (`pip install`, Python API + CLI).

## License

[Apache-2.0](LICENSE) © Criterra
