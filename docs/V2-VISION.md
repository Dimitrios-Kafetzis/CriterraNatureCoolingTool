# Version 2 Vision

**Purpose of this document.** Version 1 of the Nature for Cooling Rapid Assessment Tool is deliberately lean: a credible, transparent, literature-grounded screening instrument for single-site assessment and same-site intervention comparison. Everything below was consciously deferred — not dropped. This document keeps the v2 vision presentation-ready for partners, investors, and funders.

## The v1 → v2 arc

v1 proves the core claim: *nature-based cooling decisions can be made comparable, transparent, and fast.* v2 scales that claim along three axes — **from one site to a whole city**, **from assessment to design guidance**, and **from a single user to an institution**.

## Deferred capabilities

### 1. City-scale GIS hotspot workflow
Reproducible pipeline (open satellite + census data: Landsat/MODIS LST, Sentinel-2 NDVI, WorldPop, OSM) producing three maps per city — heat exposure, social vulnerability, combined heat priority — that tell a city *where to point the site-level tool*. v1 already accepts GIS-derived inputs (`lst_anomaly_c`); v2 automates their production, including a "click the map to pre-fill an assessment" mode.
**Why deferred:** it is a data-delivery workflow, not core methodology; shipping it first-class requires per-country data partnerships.

### 2. Portfolio mode — many sites, one investment ranking
Assess dozens of sites, rank them on the shared Opportunity Score axis, and export an investment pipeline table (with batch CSV ingestion for power users). This is the feature that turns the tool from a project instrument into a **city programming instrument**.
**Why deferred:** needs the comparison UX and storage model of v1 as its foundation.

### 3. Climate-responsive planting guidance
From typology selection to ecological design direction: planting strategy (canopy-focused, multi-layer, water-sensitive), climate-responsive criteria (drought tolerance, heat resistance, soil compatibility), and region-specific example species with design considerations (spacing, establishment, irrigation).
**Why deferred:** to meet the project's evidence standard, species guidance needs its own regional evidence base; v1's credibility should not wait for it.

### 4. Funder / investor view
A stripped-down report rendering for audiences who consume results but never enter inputs: headline scores, cost envelope, payback, equity narrative, confidence — one page.

### 5. Institutional deployment
Multi-user workspaces with shared project libraries (a city planning team seeing one portfolio), authentication, hosted instances with per-country configuration packs (Brazil, Cambodia, Côte d'Ivoire first), and full UI localisation (Portuguese, Khmer, French) beyond v1's English-plus-translated-guides.

### 6. Methodology evolution
Per-country weight calibration with local expert panels; maturity/time-discounted benefit profiles; carbon sequestration accounting; Excel workbook companion generated from the same configuration (guaranteed result parity with the web tool).

## Sequencing logic

| Wave | Theme | Builds on |
|---|---|---|
| v2.0 | Portfolio mode + funder view | v1 comparison UX + storage |
| v2.1 | GIS workflow + map-driven prefill | v1 GIS-ready inputs |
| v2.2 | Institutional deployment + localisation | hosted v1 |
| v2.3 | Planting guidance + methodology evolution | v1 evidence-base process |

## Why this is investable

- **A validated wedge:** v1 establishes the methodology, the evidence base, and the user base; every v2 capability multiplies an asset that already exists rather than betting on a new one.
- **Open core, expert edge:** the tool is Apache-2.0 open source; Criterra's commercial layer is calibration, delivery, and institutional deployment — the parts that require judgment, not licenses.
- **Alignment with funded agendas:** urban heat adaptation, NbS mainstreaming, and equity-first climate investment (UNEP Nature for Cooling Challenge and successors) are precisely the axes v2 scales along.
