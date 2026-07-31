# Nature for Cooling Rapid Assessment Tool — Methodology Report

**Version:** 2026.08.03 (methodology configuration version `2026.08.03`)
**Status:** Version 1 methodology, released for expert review; calculation engine implemented (Phase 2)

Version `2026.08.01` discharged the specification gaps disclosed at `2026.07.30`: the sub-indicator derivation rules (§5.10), the cost-feasibility brackets and combination rule (§5.8), the confidence field-to-block mapping (§6.2), and the published sensitivity analysis (§7). Version `2026.08.02` corrects an incentive defect in the soil–water condition found during engine implementation (§5.4, D-026): reliable irrigation now maps to *excellent*, and a condition pair containing an unknown is capped at the neutral factor — so complete favourable data strictly dominates leaving the question blank. Version `2026.08.03` makes two additive changes arising from the v1 review (D-039, D-040): the cooling access deficit becomes one dimension measured by two indicators, indoor and outdoor, at its existing 0.20 weight (§5.2); and the land-use enumeration gains *campus* and *memorial*, with the affected typology context lists extended (§4.4, §5.10). **No typology value, cooling envelope, or aggregation weight has changed since `2026.07.30`**, and every golden-scenario output is unchanged at `2026.08.03` — the new indicator is strictly additive, so the sensitivity analysis of §7 remains valid as published.
**Prepared by:** Criterra
**Licence:** Apache-2.0. Source code, configuration, and this document are public.

This document specifies the complete methodology of the Nature for Cooling Rapid Assessment Tool and describes how the calculation engine implements it. It is written to be read independently of the software, by reviewers who wish to evaluate the scientific basis of the tool's outputs. Every quantitative value the tool applies is derived here and traced to a source in [BIBLIOGRAPHY.md](BIBLIOGRAPHY.md); the per-typology derivations are in [EVIDENCE-TABLES.md](EVIDENCE-TABLES.md).

Reviewers are specifically invited to challenge: the adopted cooling envelopes (§4), the aggregation weights (§5.9), the energy derivation (§5.6), and the treatment of uncertainty (§6).

---

## Table of contents

1. [Purpose, scope, and intended use](#1-purpose-scope-and-intended-use)
2. [Conceptual framework](#2-conceptual-framework)
3. [Inputs and normalisation](#3-inputs-and-normalisation)
4. [The NbS typology library](#4-the-nbs-typology-library)
5. [Scoring formulas](#5-scoring-formulas)
6. [Uncertainty, confidence, and missing data](#6-uncertainty-confidence-and-missing-data)
7. [Sensitivity analysis](#7-sensitivity-analysis)
8. [Limitations and responsible use](#8-limitations-and-responsible-use)
9. [Methodology governance](#9-methodology-governance)

---

## 1. Purpose, scope, and intended use

### 1.1 Purpose

The tool is a **screening-level, multi-criteria decision-support instrument**. It converts a structured description of an urban site and a proposed nature-based intervention into comparable scores and indicative quantitative estimates, so that early planning and investment decisions can be made on a transparent, evidence-referenced basis rather than on intuition.

It occupies a deliberate position between two existing options: unstructured judgment and spreadsheets on one side, and detailed microclimate simulation (ENVI-met-class models, CFD, building energy simulation) on the other. The former is fast but not comparable or defensible; the latter is rigorous but too slow and too expensive to apply across the many candidate sites a city must triage. The tool is designed for the triage step.

### 1.2 What the tool does not do

It is **not** a microclimate simulation, a building energy model, a species-level planting design tool, or a regulatory or engineering approval instrument. It does not predict the temperature at a specific location and time. It does not replace site investigation, detailed design, or local expert judgment. Outputs are indicative ranges intended for comparison and prioritisation, not for design specification or for contractual performance guarantees.

### 1.3 Intended users and decisions

Three user groups are supported: municipal planners and public agencies; developers and consultants; and researchers and NGOs. The decisions the tool is designed to inform are: whether a site merits attention at all; which of several candidate interventions best suits a given site; and how a proposed intervention performs across cooling, energy, climate, cost, equity, and co-benefit dimensions simultaneously.

### 1.4 Design commitments

| Commitment | Consequence for the methodology |
|---|---|
| **Transparency** | Every score has one documented formula. No machine learning, no opaque calibration, no undisclosed adjustment. |
| **Determinism** | Identical inputs and identical methodology version always yield identical outputs. No stochastic components. |
| **Evidence traceability** | Every performance value cites a source. Values that could not be grounded are either omitted or explicitly flagged as low-confidence. |
| **Honest uncertainty** | All quantitative outputs are ranges. Every result carries a confidence rating. Missing data reduces confidence rather than being silently imputed. |
| **Auditability** | Methodology lives in versioned configuration files, not in code; every result records the methodology version that produced it. |

---

## 2. Conceptual framework

### 2.1 Risk framing

The tool follows the standard climate-risk decomposition — risk arises from the interaction of a **hazard** with **exposure** and **vulnerability** — which is why a physically hot site with no exposed population scores differently from an equally hot site surrounded by vulnerable residents. This framing is applied in the Baseline layer (§5.1–5.3).

### 2.2 Three-layer structure

```
Layer 1 — Baseline Assessment          Does this site deserve attention?
  Heat Exposure Score  ─┐
                        ├─►  Heat Priority Index (0–100)
  Vulnerability Score  ─┘

Layer 2 — NbS Performance              What can this intervention deliver here?
  Typology library value  ─┐
                           ├─►  Cooling Potential Score (0–100)
  Site adjustment factor  ─┘         + temperature reduction range (°C)

Layer 3 — Impact and Feasibility       What does it cost and what else does it do?
  Energy savings → GHG avoided
  Capital cost → payback → cost feasibility
  Co-benefits · Equity

Aggregation
  NbS Cooling Opportunity Score (0–100) + confidence + recommendation
```

### 2.3 Relationship to published frameworks

The layered structure follows the logic of `norton2015`, the closest published antecedent: a framework for prioritising urban green infrastructure for cooling that combines site thermal conditions, vulnerability, and intervention suitability. The composite-indicator construction — variable selection, normalisation, weighting, aggregation, and mandatory sensitivity analysis — follows `nardo2008`.

The tool's distinguishing choice is its treatment of climate: `keravec2026` finds that intervention type alone explains only 12% of the variance in observed cooling effectiveness, rising to 78% once Köppen–Geiger climate subzone is included. A tool that reported one global cooling number per intervention would therefore be discarding most of the explanatory signal. Climate suitability is consequently a first-order adjustment in Layer 2, not a refinement.

---

## 3. Inputs and normalisation

### 3.1 Input structure

Inputs are collected in six groups: project information; site characteristics; climate and heat exposure; vulnerability and equity; the proposed NbS intervention; and cost and energy parameters. Every input is either required (the assessment cannot proceed without it) or optional (absence reduces confidence but never blocks the assessment).

### 3.2 Qualitative normalisation

Most inputs accept a qualitative level, because most users do not have measured data. Levels map to a 0–100 scale:

| Level | Score |
|---|---|
| Low | 25 |
| Medium | 50 |
| High | 75 |
| Very high | 100 |
| Unknown | 50 (neutral) |

An inverted mapping applies where a high level indicates *lower* risk. The two cooling-refuge access indicators are the principal case: high access → 25, medium → 50, low → 100. `reid2009` supports treating air-conditioning access as an independent protective dimension — in that study air-conditioning prevalence emerged as one of four factors explaining more than 75% of variance across ten heat-vulnerability variables — and `burkart2016` and `sera2019` support the same treatment for reachable shaded green and blue space (§5.2).

Assigning `unknown` a neutral 50 is a deliberate, disclosed choice: it avoids both optimistic and pessimistic bias in the score while the confidence mechanism (§6) records that the information was absent.

### 3.3 Land surface temperature as an optional proxy

Where a user supplies a land-surface-temperature anomaly (°C above the city mean, typically from satellite imagery), the tool converts it linearly to a 0–100 score: 0 °C → 0, +10 °C → 100, clamped at both ends.

This proxy is used with a stated caution. `venter2021` reports that satellite-derived surface urban heat island magnitudes substantially exceed air-temperature (canopy-layer) values — a mean surface UHI of 1.45 °C against a canopy-layer UHI of 0.26 °C, an approximately sixfold difference — reflecting the distinction between surface, canopy-layer, and boundary-layer heat islands established by `oke1976`. The tool therefore treats LST **only as a relative indicator of which parts of a city are hotter**, never as an air-temperature prediction, and never converts it into a °C outcome. The 10 °C ceiling is consistent with observed intra-urban surface anomaly ranges while keeping the normalisation interpretable.

---

## 4. The NbS typology library

### 4.1 Structure

Fourteen typologies are supported, in four families: green (street tree planting, shaded pedestrian corridor, pocket park, urban forest, park upgrade, schoolyard greening), building (green roof, green façade), blue-green (rain garden/bioswale, blue-green corridor, riparian restoration), and hybrid (permeable shaded plaza, courtyard greening, mixed NbS package).

Each typology carries: a base cooling score (0–100), a temperature reduction envelope (min–max °C), its primary cooling mechanism, suitability conditions, an evidence confidence rating, and its source citations.

### 4.2 Adopted values

All values are **daytime, pedestrian-level air temperature reductions**. Derivations are in [EVIDENCE-TABLES.md](EVIDENCE-TABLES.md).

| ID | Typology | Family | Base score | Envelope (°C) | Confidence |
|---|---|---|---:|---|---|
| 01 | Street tree planting | Green | 75 | 0.5 – 3.0 | High |
| 02 | Shaded pedestrian corridor | Green | 80 | 0.5 – 3.0 | Medium |
| 03 | Pocket park | Green | 65 | 0.3 – 1.5 | High |
| 04 | Urban forest / dense canopy | Green | 90 | 1.0 – 3.0 | High |
| 05 | Park upgrade | Green | 70 | 0.5 – 2.0 | High |
| 06 | Schoolyard greening | Green | 75 | 0.5 – 2.0 | Medium |
| 07 | Green roof | Building | 45 | 0.1 – 1.0 | Medium |
| 08 | Green façade | Building | 50 | 0.3 – 2.0 | Low |
| 09 | Rain garden / bioswale | Blue-Green | 55 | 0.1 – 0.8 | Low |
| 10 | Blue-green corridor | Blue-Green | 85 | 1.0 – 3.0 | Medium |
| 11 | Riparian restoration | Blue-Green | 85 | 1.0 – 3.0 | Medium |
| 12 | Permeable shaded plaza | Hybrid | 70 | 0.5 – 2.5 | Medium |
| 13 | Courtyard greening | Hybrid | 60 | 0.3 – 1.5 | Low |
| 14 | Mixed NbS package | Hybrid | 80 | 1.0 – 3.0 | Medium |

### 4.3 Three calibration decisions worth reviewer attention

**Modelling bias is corrected downward.** `keravec2026` synthesises 64 systematic reviews, many dominated by simulation studies, which systematically report larger effects than field measurement. The comparison is visible within our own sources: for parks, the modelling-inclusive synthesis gives 1.3 °C while `bowler2010`, restricted to empirical studies, gives 0.94 °C. Adopted upper bounds therefore sit at or below synthesis central estimates rather than above them.

**The mixed package does not claim super-additivity.** The draft methodology proposed a 3.5 °C ceiling for combined interventions. No retrieved source quantifies super-additive cooling from combining measures; `gunawardena2017` describes synergy qualitatively but does not quantify it. The envelope is therefore capped at 3.0 °C, the best-evidenced single-measure ceiling. The package's advantage is represented in co-benefit breadth and robustness, not in additional degrees.

**Green roofs and green façades are the weakest points in the library, and are labelled as such.** For green roofs, `santamouris2014` reports 0.3–3 K ambient reduction, but explicitly for *city-scale deployment in simulation studies* — not for one roof on one building, which is what a site-level assessment evaluates; `zolch2016` finds pedestrian-level effects negligible. For green façades, sources conflict outright: `keravec2026` ranks green walls near the top on air temperature (3.0 °C, with a fivefold spread across climate subzones) while `zolch2016` ranks them below trees on thermal comfort, a discrepancy plausibly explained by near-wall measurement position. Both typologies receive conservative envelopes, reduced confidence, and explicit caveats in the tool's output.

### 4.4 Suitability conditions

Each typology declares conditions under which it is unsuitable — minimum viable site area, soil requirement, irrigation requirement, and unsuitable climate zones. When a disqualifying condition is met, the tool computes the assessment transparently but attaches a prominent **"not suitable for this site"** flag naming the reason, and the recommendation text states it. Silently returning a merely lower score for a physically implausible intervention would misrepresent the finding.

The humidity caveat from `gunawardena2017` — poorly designed blue space may exacerbate heat stress under humid conditions — is encoded as a climate-suitability penalty for blue typologies in tropical-wet zones rather than left as prose.

---

## 5. Scoring formulas

Notation: all scores are 0–100 unless stated. `clamp(x)` bounds a value to [0, 100].

### 5.1 Heat Exposure Score

Two paths, depending on data availability.

**Data-rich** (a land-surface-temperature anomaly is supplied):

```
Heat Exposure = clamp( 0.40 × LST_score
                     + 0.25 × Imperviousness_score
                     + 0.20 × Solar_exposure_score
                     + 0.15 × Vegetation_deficit_score )
```
where `Vegetation_deficit_score = clamp(100 − existing_green_cover_percent)`.

**Data-poor** (no LST supplied): `Heat Exposure = qualitative heat exposure level score`.

On the data-rich path, a missing imperviousness or green-cover value enters as the neutral 50 with an itemised assumption — these are score components, not physical claims, and propagating *not calculated* into a composite score would block the score that a missing sub-input was only meant to weaken. On the data-poor path a missing heat exposure level likewise defaults to the neutral 50, itemised.

The component selection reflects established surface-energy-balance drivers of urban heat: surface temperature, sealed surfaces, solar loading, and vegetation deficit. `ziter2019` provides direct empirical support for two of them — impervious cover raises air temperature approximately linearly, and canopy cover reduces it nonlinearly. The weights are expert judgment (§5.9).

### 5.2 Vulnerability Score

```
Vulnerability = clamp( 0.40 × Population_density_score
                     + 0.40 × Vulnerable_group_score
                     + 0.20 × Cooling_access_deficit_score )
```

Indicator selection follows `reid2009`, whose factor analysis of ten heat-vulnerability variables identified social/environmental vulnerability, social isolation, air-conditioning prevalence, and elderly/diabetes proportion as four factors explaining more than 75% of total variance. Population density and vulnerable-group presence are weighted equally because that analysis gives no basis for ranking demographic vulnerability above exposure density; cooling access carries the smaller weight because it is the most frequently unknown at screening stage. `sera2019` independently supports population density as a heat-vulnerability modifier across 340 cities in 22 countries.

**The cooling access deficit is one dimension measured by two indicators** (from version `2026.08.03`, D-039). Refuge from heat is reached either indoors or outdoors, and the evidence for the two is separate:

| Indicator | Question | Grounding |
|---|---|---|
| `access_to_cooled_indoor_space` | How easily local users can reach air-conditioned or otherwise actively cooled indoor space | `reid2009` — air-conditioning prevalence is one of the four factors, an independent dimension |
| `access_to_cool_outdoor_refuge` | How easily local users can reach shaded green or blue space | `burkart2016` — above the 99th temperature percentile, elderly mortality rose 14.7% per °C in the least-vegetated areas against 3.0% in the most vegetated, and 7.1% per °C beyond 4 km from water against 2.1% within it; `sera2019` corroborates at multi-country scale |

Both normalise through the inverted scale, so *low* access scores a *high* deficit. The dimension keeps its **0.20 weight, unchanged**; only its measurement changed, so the aggregation weights and the published sensitivity analysis are untouched.

```
Cooling_access_deficit = mean( indicators actually supplied )
                       = 50   if neither indicator was supplied
```

Averaging an *unsupplied* indicator in at the neutral 50 was considered and rejected. It would pull a signal the user did give toward the middle purely because a second question was skipped — an unknown changing the meaning of an answer, which is the defect §5.4 and D-026 removed from the soil–water pair. Under the adopted rule a single answer speaks for the dimension, answering the second moves it in whichever direction that answer warrants, and skipping costs nothing. The two indicators correspondingly share one confidence slot (§6.2): the completeness question is whether cooling-refuge access was described at all, and either indicator answers it.

**Disclosed overlap.** The outdoor indicator describes cool refuges in the *surroundings* that the site's users can reach; the Heat Exposure Score's vegetation-deficit component (§5.1) describes greenness *of the site itself*. The two are distinct quantities but conceptually adjacent, and a site in a green district with a bare site will register both a low outdoor-refuge deficit and a high vegetation deficit. This is stated here rather than left for a reviewer to find, in the manner of the vulnerability double-contribution declared in §5.9.

### 5.3 Heat Priority Index

```
Heat Priority Index = clamp( 0.60 × Heat Exposure + 0.40 × Vulnerability )
```

Interpretation: 0–30 Low · 31–60 Medium · 61–80 High · 81–100 Critical.

### 5.4 Site adjustment factor

Four site conditions modulate typology performance. Each maps to a factor: poor 0.5, moderate 0.8, good 1.0, excellent 1.2, unknown 1.0.

```
Adjustment = 0.40 × Canopy_factor
           + 0.25 × Soil_water_factor
           + 0.20 × Scale_factor
           + 0.15 × Climate_factor
```

All four conditions are **derived from inputs the user has already given** — no additional questions are asked:

| Condition | Derivation |
|---|---|
| Canopy | (existing canopy + new canopy at maturity) ÷ site area → poor <10%, moderate 10–25%, good 25–40%, excellent >40% |
| Soil–water | the lower of soil availability and irrigation availability, on the mapping none → poor; limited, occasional → moderate; moderate → good; reliable, high → excellent. When exactly one of the two is known, the condition is capped at good (D-026): a pair containing an unknown may never exceed the neutral factor, so declaring reliable irrigation is never worse — and with high soil strictly better — than skipping the question |
| Scale | assessment scale: city/district → large, neighbourhood → medium, site/building → small |
| Climate | typology × climate-zone suitability lookup |

The canopy thresholds are taken from `ziter2019`, which found cooling increases nonlinearly with canopy cover and is greatest above 40% — the tool's "excellent" boundary is placed at that empirically identified inflection rather than chosen arbitrarily. Canopy carries the largest weight because it is the condition with the strongest direct empirical support. The climate factor is separately justified by `keravec2026`'s finding that climate subzone raises explained variance in effectiveness from 12% to 78%.

### 5.5 Cooling Potential Score and temperature reduction

```
Cooling Potential Score = clamp( Base_cooling_score × Adjustment )

ΔT_min = clip( typology_min × Adjustment, typology_min_envelope, typology_max_envelope )
ΔT_max = clip( typology_max × Adjustment, typology_min_envelope, typology_max_envelope )
```

**The clipping rule is a deliberate correction to the draft methodology.** Without it, an adjustment factor above 1.0 applied to a typology's upper bound produces temperature claims exceeding anything in the literature — an urban forest on an excellent site would report up to 3.6 °C, which no retrieved source supports. Because the published envelopes already represent well-executed interventions under favourable conditions, site quality is allowed to *degrade* estimated performance below the envelope but never to exceed it. The 0–100 Cooling Potential Score remains free to rise, so the tool can still express that a site is exceptionally well suited without inflating its physical claim.

Shade potential is reported separately and directly: `shade_potential_percent = clamp(new_canopy_area_at_maturity ÷ site_area × 100)`.

**Time-to-benefit (OQ-06).** No maturity discount is applied to cooling values. Instead, the expected maturity period is reported as a time-to-benefit class so that a slow-maturing intervention is never presented as delivering its cooling immediately: under 1 year *immediate*, 1–3 years *short-term*, 3–10 years *medium-term*, beyond 10 years *long-term* (half-open brackets: a value falls in a bracket when ≥ its minimum and < its maximum; buckets in `derived_scores.yaml`). Absent a maturity period, the output is *not estimated*.

### 5.6 Energy savings — derived, not assumed

The draft methodology stored per-typology "energy reduction factors" (2–15%) for which no source could be found. These have been **removed and replaced by a derivation** from the estimated cooling effect:

```
Energy_savings = Annual_cooling_energy_demand × ΔT × sensitivity
    where sensitivity ∈ [0.02, 0.04] per °C
```

`akbari2001` reports that urban electricity demand increases by **2–4% for each 1 °C** of temperature increase, and estimates that 5–10% of urban electricity demand serves to compensate for the 0.5–3.0 °C urban temperature elevation. Applying that sensitivity in reverse to an estimated temperature reduction yields an energy saving that is (a) sourced, (b) internally consistent with the tool's own cooling estimate, and (c) automatically responsive to site conditions.

Two constraints apply. Energy savings are calculated **only** where the user confirms that nearby building cooling demand is relevant *and* supplies an annual cooling energy demand; otherwise the result is reported as `not_applicable` or `missing_energy_demand`, never as zero. And the derivation applies to typologies capable of affecting adjacent building loads; for typologies whose benefit is principally amenity-level, the tool reports the limitation rather than a number.

The engine checks the preconditions in a fixed order and reports the first that fails: `typology_not_applicable` (the intervention cannot affect building loads, whatever the user supplied), then `not_applicable` (the user states demand is not relevant), then `relevance_not_confirmed` (the relevance question was skipped or answered *unknown* — a supplied demand figure cannot substitute for the unanswered confirmation), then `missing_energy_demand`. The range combines the clipped ΔT interval with the sensitivity interval: `E_min = demand × ΔT_min × 0.02`, `E_max = demand × ΔT_max × 0.04`.

This derivation is an area where reviewer input is particularly welcome: the sensitivity is drawn from predominantly North American evidence and its transferability to other building stocks and climates is untested.

### 5.7 GHG emissions avoided

```
GHG_avoided = Energy_savings × grid_emission_factor
```

Grid emission factors are sourced per country from `ember`, which publishes electricity carbon intensity (gCO₂/kWh) for 215 countries under a CC-BY-4.0 licence permitting redistribution with attribution. Where no factor is available for a country, the tool reports GHG as not calculated rather than substituting a global average.

### 5.8 Costs — why the tool ships no default values

`worldbank2021` states that NbS project costs vary significantly and are highly site- and project-specific, that unit costs differ sharply between developed and developing contexts — illustrated by dredging at US$2/m³ in Bangladesh against US$59/m³ in the United Kingdom — and that urban implementation costs typically exceed rural ones. No source was found offering globally applicable unit costs for the typologies in this library.

The tool therefore **ships no default cost values in v1**. Where the user supplies a capital cost, the tool computes cost outputs; where they do not, capital cost, payback, and cost feasibility are reported as *not estimated*. Fabricating a default per-square-metre cost would produce the most decision-relevant number in the assessment — payback — from an invented input, which no confidence rating could adequately qualify. Locally calibrated cost tables are a defined extension point: a deployment may supply its own cost configuration, which the tool records as a documented assumption.

Where costs are supplied:

```
Annual_cost_savings = Energy_savings × energy_price
Simple_payback      = Capital_cost ÷ Annual_cost_savings      (null if savings ≤ 0)
Cost_feasibility    = f(payback bracket, implementation complexity, maintenance intensity)
```

`Cost_feasibility` is derived rather than user-asserted: short payback, low complexity, and low maintenance yield high feasibility. When payback cannot be computed, cost feasibility is reported as unavailable and is excluded from aggregation with the weight redistributed proportionally — the alternative, substituting a neutral 50, would silently reward projects with no economic evidence.

**The derivation, fixed at version 2026.08.01 (D-023).** Because the energy saving is an interval spanning an order of magnitude, the payback bracket is applied to the payback computed from the **central** energy estimate (the midpoint of the savings range); the reported payback interval still carries both ends. Brackets (half-open, in `derived_scores.yaml`): under 5 years → 100 (*short*), 5–10 → 75 (*medium*), 10–20 → 50 (*long*), 20 and beyond → 25 (*very long*). The boundaries follow common public-investment screening horizons: a single budget mandate, a municipal capital plan, dedicated adaptation finance, and beyond-energy-case territory respectively.

```
Cost_feasibility = 0.50 × payback_bracket_score
                 + 0.25 × complexity_score      (inverted: low complexity → 100)
                 + 0.25 × maintenance_score     (inverted: low maintenance → 100)
```

Payback dominates as the only quantitative economic signal; complexity and maintenance are qualitative delivery-risk modifiers weighted equally because no evidence ranks one above the other. Unknown complexity or maintenance takes the neutral 50, itemised.

**Investment readiness (OQ-11).** Reported qualitatively alongside feasibility: the payback bracket sets the base level (*short* → high, *medium* → medium, *long* and *very long* → low), downgraded one level if implementation complexity is high and one level if the energy-block confidence is low, with a floor at low. Whenever cost feasibility is *not estimated*, so is investment readiness. (With the shipped confidence field mapping, a calculated energy saving implies at least medium energy confidence, so the energy-confidence downgrade binds only in deployments that alter the confidence field lists.)

### 5.9 Aggregation and the weighting question

```
NbS Cooling Opportunity Score =
    0.25 × Heat Priority Index
  + 0.25 × Cooling Potential Score
  + 0.15 × NbS Suitability Score
  + 0.15 × Vulnerability Score
  + 0.10 × Co-benefit Score
  + 0.10 × Cost Feasibility Score
```

Interpretation: 0–30 Low priority · 31–60 Moderate opportunity · 61–80 Strong opportunity · 81–100 High-priority project.

**These weights are expert judgment, and the tool says so.** `nardo2008` is explicit that weighting in composite indicators is a value choice rather than a technical derivation; no literature can supply the relative importance of cooling performance versus equity versus cost. The weights are declared, versioned, adjustable in configuration, and defended empirically through sensitivity analysis (§7) rather than by appeal to authority.

**Vulnerability enters the final score twice, and this is intentional.** It contributes 0.40 of the Heat Priority Index, which itself carries 0.25, and it appears directly at 0.15. Effective weights are therefore:

| Component | Effective weight in final score |
|---|---:|
| Vulnerability | 0.25 |
| Cooling Potential | 0.25 |
| Heat Exposure | 0.15 |
| NbS Suitability | 0.15 |
| Co-benefits | 0.10 |
| Cost Feasibility | 0.10 |

The tool therefore weights *who is affected* (0.25) above *how hot the site is physically* (0.15). This is a deliberate equity-forward stance: among two equally hot sites, the one serving a more vulnerable population ranks higher. It is disclosed here because an undisclosed double contribution would be a defect; disclosed and quantified, it is a defensible position that reviewers may legitimately dispute. Any deployment may rebalance it in configuration.

### 5.10 Composite sub-score derivation rules (fixed at 2026.08.01, D-022)

Version 2026.07.30 declared the weights of the NbS Suitability, Co-benefit, and Equity scores but not the rules mapping inputs to their sub-indicators. Those rules are now fixed, live in `derived_scores.yaml`, and — like the aggregation weights — are expert judgment, declared and versioned rather than derived from literature.

**NbS Suitability** (`0.30 space + 0.25 soil + 0.20 water + 0.15 maintenance + 0.10 urban context`). All sub-indicators derive from inputs already supplied (OQ-16/17); no new questions are asked:

| Sub-indicator | Rule |
|---|---|
| Space | ratio = site area ÷ typology minimum viable area: <1× → 25 **and the D-009 flag**; 1–2× → 50; 2–5× → 75; ≥5× → 100 |
| Soil | availability vs. the typology requirement on the ordinal scale none < limited < moderate < high: requirement *none* → 100; availability unknown → 50 (no flag — a disqualification is never asserted from absent information); below requirement → 25 **and the D-009 flag**; meets exactly → 75; exceeds → 100 |
| Water | same rule on none < occasional < reliable against the irrigation requirement |
| Maintenance | declared maintenance intensity through the inverted scale: low → 100, medium → 50, high → 25, unknown → 50 |
| Urban context | site land use in the typology's `typical_use_context` → 100; outside it → 25 (a caution, not a disqualification); unknown → 50 |

The land-use enumeration gained **campus** and **memorial** at `2026.08.03` (D-040). Because the enumeration feeds this sub-indicator alone, adding values without extending the typology context lists would have scored both new settings *out of context* for every typology. The lists were therefore extended on a reading of what each setting is: campus — institutional grounds combining buildings, circulation, and open space — was added wherever a school, public-space, or mixed-use context already applied (twelve typologies); memorial — cemeteries and remembrance landscapes, low-intensity public green space — wherever a park or public-space context already applied (seven typologies). Neither was added to the blue-green corridor or riparian restoration, whose context is an existing water feature rather than a land use. No existing land use changed meaning.

**Equity** (`0.35 vulnerable-user benefit + 0.25 public accessibility + 0.20 safety & comfort + 0.20 participation relevance`). Each sub-indicator reads how much equity benefit the intervention can deliver here, so a *deficit* raises the score, paralleling the risk framing of the Vulnerability Score. Vulnerable-user benefit reuses the vulnerable-population input (no duplicate question); public accessibility and community participation are the two new optional inputs introduced at this version; safety concern deliberately uses the standard (non-inverted) scale — a site with greater safety and comfort problems stands to gain more from a well-designed intervention. The Equity Score is reported as its own block with its own confidence and **does not enter the final aggregation**; equity reaches the headline score through the Vulnerability Score, as §5.9 discloses.

**Co-benefits** take the cited per-typology default levels with user override (OQ-18). The library ships no default for *social inclusion*; absent an override it falls to the neutral 50 and is itemised. Every applied library default is likewise itemised, so a reader can see which co-benefit levels came from the user and which from the configuration.

---

## 6. Uncertainty, confidence, and missing data

### 6.1 Ranges, not point estimates

All quantitative outputs — temperature reduction, energy savings, GHG avoided, cost savings — are reported as ranges. Point estimates would imply a precision the underlying evidence does not support: adopted cooling envelopes span factors of two to six, and `keravec2026`'s climate-subzone estimates carry uncertainty intervals of ±0.6 to ±2.0 °C.

### 6.2 Branched confidence

A single confidence rating would obscure the common case where a site has good physical data but no economic data. Confidence is therefore computed separately for each output block — cooling, energy, economic, equity — from the completeness of the inputs feeding that block:

| Completeness of relevant fields | Confidence |
|---|---|
| < 40% | Low |
| 40–70% | Medium |
| > 70% | High |

Two additional constraints apply. Evidence confidence propagates: a typology rated low-confidence in the library (green façade, rain garden/bioswale, courtyard greening) caps the cooling-block confidence at medium regardless of input completeness, because complete inputs cannot compensate for thin underlying evidence. And a high score with low confidence is presented as a flag for further investigation, never as a verdict.

**The field-to-block mapping, fixed at 2026.08.01 (D-024), extended at 2026.08.03 (D-039).** The fields counted for each block are enumerated in `derived_scores.yaml`: ten slots for cooling (canopy, green cover, imperviousness, soil, irrigation, shade level, one heat-signal slot filled by *either* the LST anomaly *or* the qualitative heat exposure level, solar exposure, new canopy at maturity, maturity period); three for energy (relevance confirmation, demand, energy price); four for economic (capital cost, energy price, implementation complexity, maintenance intensity); six for equity (population density, vulnerable presence, one cooling-refuge access slot filled by *either* the indoor *or* the outdoor indicator, safety concern, public accessibility, community participation). A field answered *unknown* counts as **not supplied** — an explicit unknown carries no more information than a skipped question. Completeness is the share of supplied slots; the thresholds of the table above apply with exact boundaries: below 40% low, 40–70% (inclusive) medium, above 70% high.

**Overall confidence** is the lower median of the four block ratings (rank the four, take the second-lowest). A mean would need a rounding rule at half-steps; the lower median is exact, slightly conservative, and never reports an overall rating higher than three of the four blocks.

### 6.3 Missing data

Required inputs must be present; the assessment does not proceed without them. Optional inputs, when absent, follow explicit rules: qualitative inputs default to `unknown` (neutral 50) and quantitative inputs propagate as *not calculated* — never as zero, which would understate results while appearing to be a finding. Every default the engine applies is itemised in the result and reproduced in the report, so a reader can see exactly which numbers came from the user and which from the tool.

---

## 7. Sensitivity analysis

`nardo2008` treats uncertainty and sensitivity analysis as integral to credible composite indicators, not optional. Because the aggregation weights (§5.9) are the tool's most consequential unsourced choice, their influence must be quantified and published rather than asserted to be small.

The tool's published sensitivity analysis varies each aggregation weight by **±25%** (renormalising the remainder) across the golden-scenario set and reports rank stability, score displacement, category migration, and an influence ranking. It is implemented in [`tools/sensitivity_analysis.py`](../../tools/sensitivity_analysis.py), its full output is committed at [SENSITIVITY-ANALYSIS.md](SENSITIVITY-ANALYSIS.md), and it must be regenerated whenever any aggregation weight changes.

### 7.1 Results at version 2026.08.03

The analysis was executed against the 20 hand-verified golden scenarios (190 scenario pairs), re-scoring the full set under each of the 12 perturbations (6 weights × ±25%). The figures below were produced at `2026.08.01` and re-confirmed unchanged at `2026.08.03`: no aggregation weight has moved, and no golden-scenario output changed under D-039 or D-040.

1. **Rank stability.** Worst case **0.9737** (under the −25% Heat Priority Index perturbation: 5 of 190 pairs reorder); 9 of 12 perturbations preserve at least 98.4% of pair orderings. Reordering occurs only between scenarios whose baseline scores differ by less than about 2 points — pairs that the methodology itself would describe as materially equivalent.
2. **Score displacement.** Pooled across all 240 scenario-perturbation combinations: mean **0.42** points, median 0.32, 75th percentile 0.59, maximum **2.01** points (on a 0–100 scale).
3. **Category migration.** **3 of 240** combinations cross a band boundary, and each involves a baseline score within ~1.3 points of the boundary (59.58 → 60.3/60.39 across the Moderate–Strong line; 80.92 → 79.63 across the Strong–High-priority line). No scenario moves by more than one band, and no scenario far from a boundary migrates.
4. **Influence ranking.** Cooling Potential (mean displacement 0.58) and the Heat Priority Index (0.53) are the most influential weights, followed by Vulnerability (0.49), Suitability (0.45), Co-benefits (0.31), and Cost Feasibility (0.17). Cost feasibility ranks last partly by construction: it is excluded and redistributed in the 15 of 20 scenarios that supply no cost data, so its weight only binds where economic evidence exists.

### 7.2 Interpretation

Under ±25% perturbation of any single aggregation weight, the tool's priority ordering is substantially stable: at least 97.4% of pairwise orderings survive every perturbation, absolute scores move by well under half a point on average, and category changes occur only for sites already sitting on a band boundary. The disclosed equity-forward stance (§5.9) therefore changes fewer decisions than its prominence might suggest — a deployment that disagrees with the weights can expect a materially similar priority list unless two options were near-tied to begin with.

Two honest qualifications. First, the analysis perturbs one weight at a time; simultaneous perturbation of several weights would produce larger displacements, and the published figures should not be quoted as bounds for arbitrary re-weightings. Second, the golden-scenario set is designed to span the methodology's behaviour (climates, typologies, data completeness, cost availability), not to be a probability sample of real assessments; stability figures are properties of this set. Both caveats argue for the standing rule that near-boundary results be read as ranges, not verdicts — which the confidence mechanism already enforces at the point of use.

---

## 8. Limitations and responsible use

**Screening level.** Outputs are indicative estimates from simplified typology factors and user-supplied or default assumptions. They are not microclimate simulation outputs and must not be presented as predicted temperatures at a location.

**Daytime only.** All cooling values are daytime. `keravec2026` reports substantially smaller nighttime effects, and `ziter2019` finds canopy cooling minimal at night while impervious-surface warming persists. Nighttime heat is strongly associated with heat-health outcomes, so a favourable daytime result should not be read as overnight heat relief.

**Air temperature only.** The tool estimates air temperature reduction. Thermal comfort — which shade improves substantially through radiant load reduction even where air temperature changes little — is not quantified. This systematically understates the benefit of shade-dominant interventions; `zolch2016`'s 13% PET reduction from trees illustrates the magnitude of what is omitted.

**Evidence is geographically uneven.** The underlying literature is dominated by temperate and subtropical Northern Hemisphere cities. Tropical and arid-climate estimates rest on fewer studies with wider intervals, and the energy sensitivity derives largely from North American evidence. Applications in under-represented contexts should treat outputs as more uncertain than the confidence rating alone suggests.

**Modelling bias.** Much of the synthesised evidence derives from simulation rather than field measurement, and simulation tends to report larger effects. This is mitigated by conservative bound-setting (§4.3), not eliminated.

**No default costs.** Economic outputs require user-supplied costs (§5.8). Absent them, the tool reports no capital cost, payback, or cost feasibility.

**Weights are contestable.** The aggregation weights, including the equity-forward emphasis (§5.9), are value choices. Users who disagree should adjust them in configuration and re-run rather than reinterpreting outputs.

**Responsible use.** Use the tool to compare options and set priorities, not to justify a decision already taken. Combine results with local knowledge and stakeholder input. Validate assumptions through site visits. Re-run assessments as better data becomes available. Report the confidence rating and methodology version alongside any score that is quoted.

---

## 9. Methodology governance

**Versioning.** The methodology version (`2026.08.03`) stamps both this document and the configuration files, and is recorded in every assessment result. A change to any methodology value requires a version bump and a corresponding update to this document in the same change set; continuous integration enforces that performance values carry citations.

**Change process.** Methodology changes are proposed as public pull requests with their evidence. Existing assessments are never silently recomputed: results retain the version that produced them, and the interface indicates when a newer methodology version is available.

**How to challenge this methodology.** Open an issue in the repository referencing the section number and, where possible, the literature supporting your position. The values most in need of external scrutiny are the green façade and bioswale envelopes (thin or conflicting evidence), the energy sensitivity transferability (§5.6), and the aggregation weights (§5.9). Methodology critique is a first-class contribution to this project.
