# Nature for Cooling — Rapid Assessment Tool

**An open-source, screening-level decision-support tool that helps planners, developers, and researchers evaluate and prioritise nature-based solutions (NbS) for urban cooling** — turning a structured site description into transparent, literature-grounded, comparable scores in minutes, so that early planning and investment decisions no longer rely on intuition or unaffordable simulation.

Developed by [Criterra](https://criterra.eu).

[![CI](https://github.com/Dimitrios-Kafetzis/CriterraNatureCoolingTool/actions/workflows/ci.yml/badge.svg)](https://github.com/Dimitrios-Kafetzis/CriterraNatureCoolingTool/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

> **Status: Phase 0 — repository scaffold.** The methodology evidence base and calculation engine are under active development. See [Roadmap](#roadmap).

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

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — system design
- [docs/DECISIONS.md](docs/DECISIONS.md) — decision log with rationale
- [docs/methodology/](docs/methodology/) — the methodology report and evidence tables (expert/UNEP-facing)
- [docs/V2-VISION.md](docs/V2-VISION.md) — deferred features and product vision

## Roadmap

| Phase | Deliverable | Status |
|---|---|---|
| 0 | Repository scaffold, governance docs, CI | ✅ |
| 1 | Methodology evidence base + expert Methodology Report + cited configuration | 🔄 next |
| 2 | Calculation engine (pure Python, 100% test coverage, golden scenarios) | ⏳ |
| 3 | FastAPI service | ⏳ |
| 4 | React/TypeScript web app (questionnaire wizard, dashboard, A/B/C comparison) | ⏳ |
| 5 | Report export (PDF / XLSX) | ⏳ |
| 6 | Documentation site, packaging, hosting | ⏳ |

## Running locally

> Coming with Phase 3/4. The target is a single command for the full stack; the engine will also be usable standalone (`pip install`, Python API + CLI).

## License

[Apache-2.0](LICENSE) © Criterra
