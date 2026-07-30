# Evidence Tables — NbS Typology Library

For each of the 14 typologies: the evidence consulted, the value adopted by the tool, and the reasoning that connects them. Source keys refer to [BIBLIOGRAPHY.md](BIBLIOGRAPHY.md). These tables are the direct source for the `sources:` arrays in [`config/nbs_typologies.yaml`](../../config/nbs_typologies.yaml).

## How to read these tables

**All adopted °C values are daytime, pedestrian-level AIR temperature reductions**, relative to an equivalent unimproved site. This is the metric decision-makers assume when they read "cooling", and mixing it with surface temperature or comfort indices is the most common way screening tools mislead. Where a source reports surface temperature or a comfort index (PET/UTCI), that is stated and the value is used only for ranking or caveats — never converted into a °C air-temperature claim.

**Adopted ranges are envelopes, not predictions.** The lower bound represents a poorly performing instance of the typology; the upper bound represents a well-executed instance under favourable conditions. Site adjustment moves an assessment *within* this envelope and can never exceed it (decision D-008).

**Calibration bias is corrected downward.** `keravec2026` synthesises many modelling studies, which systematically report larger effects than field measurement; `bowler2010`, restricted to empirical studies, reports roughly half the park cooling that the modelling-inclusive synthesis does (0.94 °C vs 1.3 °C). Where the two disagree, adopted upper bounds sit at or below the modelling-derived central estimate rather than above it.

**Confidence** is recorded per typology and propagates into the tool's output: `high` (multiple converging sources including a synthesis), `medium` (a synthesis estimate with limited typology-specific corroboration), `low` (sparse or indirect evidence — the tool flags these results explicitly).

---

## Category: Green

### 01 — Street tree planting

| Source | Metric | Finding |
|---|---|---|
| `keravec2026` | Air (pedestrian, daytime) | Street trees **1.5 °C** central estimate; tropical (A) **4.0 ± 1.6 °C**; arid (B) **1.7 ± 1.4 °C**; hot-summer subzones **3.0 ± 0.8 °C** |
| `bowler2010` | Air | Empirical studies broadly support cooler air beneath tree canopy |
| `ziter2019` | Air | Cooling nonlinear in canopy cover, strongest above **40%** cover; peak effect at 60–90 m scale |
| `zolch2016` | PET (comfort) | Trees best-performing measure, **−13% PET** at pedestrian level |
| `rahman2020` | Air / surface | Species and leaf area index materially change cooling delivered |

**Adopted: 0.5 – 3.0 °C · base cooling score 75 · confidence high.**
The upper bound is set at 3.0 °C rather than the tropical central estimate of 4.0 °C: that figure carries a ±1.6 °C interval and reflects favourable tropical conditions, so adopting it as a general ceiling would overstate typical performance. `ziter2019` supplies the canopy-condition dependence that the tool's canopy adjustment factor encodes.

### 02 — Shaded pedestrian corridor

| Source | Metric | Finding |
|---|---|---|
| `keravec2026` | Air (pedestrian, daytime) | Street trees **1.5 °C**; shading devices **2.0 °C**; narrow streets **4.2 °C** (geometry effect) |
| `zolch2016` | PET | Shade placement in heat-exposed locations outperforms maximising total green cover |

**Adopted: 0.5 – 3.0 °C · base cooling score 80 · confidence medium.**
Treated as street trees plus deliberate shade continuity along a movement corridor. Scored slightly above street trees because shade is placed where exposure occurs, which `zolch2016` identifies as the decisive factor. The narrow-street figure is *not* inherited — it is an urban-form effect, not an NbS intervention.

### 03 — Pocket park

| Source | Metric | Finding |
|---|---|---|
| `keravec2026` | Air (pedestrian, daytime) | Parks **1.3 °C**; green areas **2.0 °C** |
| `bowler2010` | Air | Park on average **0.94 °C** cooler by day; **larger** parks and those **with trees** cooler |

**Adopted: 0.3 – 1.5 °C · base cooling score 65 · confidence high.**
Explicitly the small end of the park distribution. `bowler2010`'s size relationship is the reason a pocket park is bounded below the general park estimate.

### 04 — Urban forest / dense canopy planting

| Source | Metric | Finding |
|---|---|---|
| `keravec2026` | Air (pedestrian, daytime) | Urban forests **2.1 °C** — among the highest-performing green measures |
| `ziter2019` | Air | Greatest cooling where canopy cover exceeds **40%**; effect grows with patch scale to 60–90 m |
| `bowler2010` | Air | Larger, tree-rich green sites cooler |

**Adopted: 1.0 – 3.0 °C · base cooling score 90 · confidence high.**
The best-evidenced high performer: three independent sources converge on dense canopy at scale as the strongest vegetation-based cooling intervention.

### 05 — Park upgrade

| Source | Metric | Finding |
|---|---|---|
| `keravec2026` | Air (pedestrian, daytime) | Parks **1.3 °C**; green areas **2.0 °C** |
| `bowler2010` | Air | **0.94 °C** mean; parks with trees cooler than open turf |

**Adopted: 0.5 – 2.0 °C · base cooling score 70 · confidence high.**
Represents *added* cooling from increasing canopy and vegetation complexity in an existing park — the baseline is already partly green, so the achievable increment is bounded below new-forest values.

### 06 — Schoolyard greening

| Source | Metric | Finding |
|---|---|---|
| `keravec2026` | Air (pedestrian, daytime) | Green areas **2.0 °C**; street trees **1.5 °C** |
| `ziter2019` | Air | Cooling maximised at city-block scale (60–90 m) — comparable to a schoolyard footprint |
| `bowler2010` | Air | Tree-containing green sites outperform open green |

**Adopted: 0.5 – 2.0 °C · base cooling score 75 · confidence medium.**
No schoolyard-specific synthesis was found; values are inherited from small green areas with trees at a matching spatial scale. The typology's distinct value lies in exposure (children are a heat-vulnerable group) rather than in different physics — which the tool expresses through vulnerability and equity, not through inflated cooling.

---

## Category: Building

### 07 — Green roof

| Source | Metric | Finding |
|---|---|---|
| `keravec2026` | Air (pedestrian, daytime) | Green roofs **1.1 °C** — the lowest-performing green measure in the synthesis |
| `zolch2016` | PET (pedestrian) | Green roof effects at pedestrian level **negligible** |
| `santamouris2014` | Air (city scale) | **0.3–3 K** average urban ambient reduction — but only for **city-scale deployment in simulation studies** |

**Adopted: 0.1 – 1.0 °C · base cooling score 45 · confidence medium.**
This typology carries the largest interpretive gap in the library, and the tool resolves it conservatively. A green roof's thermal benefit is concentrated at roof level and inside the building beneath; `zolch2016` finds essentially nothing at street level, while `santamouris2014`'s larger figures describe *many* roofs across a whole city, which is not what a site-level assessment evaluates. The adopted range therefore sits near the bottom of the published spread, and the tool states in its output that green-roof benefits are principally building-level rather than street-level.

### 08 — Green façade

| Source | Metric | Finding |
|---|---|---|
| `keravec2026` | Air (pedestrian, daytime) | Green walls **3.0 °C** central; strongly climate-dependent — Cwa **5.7 ± 1.0**, BWh **5.5 ± 1.0**, Csa **2.9 ± 0.8**, Cfa/Cfb **1.3**, Af **1.0 ± 0.8 °C** |
| `zolch2016` | PET (pedestrian) | Green façades **−5% to −10% PET**, below trees (−13%) |

**Adopted: 0.3 – 2.0 °C · base cooling score 50 · confidence low.**
The evidence is genuinely contradictory: the synthesis ranks green walls near the top on air temperature, while the micro-scale comparison ranks them below trees on comfort. The likely explanation is measurement position — near-wall measurements capture a strong local effect that does not extend across the street canyon. Given a fivefold spread across climate subzones and an unresolved conflict between sources, this typology is assigned **low confidence**, a conservative envelope, and an explicit caveat in the tool's output.

---

## Category: Blue-Green

### 09 — Rain garden / bioswale

| Source | Metric | Finding |
|---|---|---|
| `keravec2026` | Air (pedestrian, daytime) | No bioswale-specific estimate; green areas **2.0 °C**, water bodies **2.1 °C** — neither transferable to a small drainage feature |
| `gunawardena2017` | Air | Tree-dominated greenspace delivers heat-stress relief; small blue features are not identified as significant coolers |

**Adopted: 0.1 – 0.8 °C · base cooling score 55 · confidence low.**
No source was found that quantifies air-temperature cooling for rain gardens or bioswales specifically. This is stated rather than papered over: the value is a reasoned lower bound from adjacent evidence, flagged low confidence, and the tool reports this typology's primary benefits as **stormwater and biodiversity**, not cooling.

### 10 — Blue-green corridor

| Source | Metric | Finding |
|---|---|---|
| `keravec2026` | Air (pedestrian, daytime) | Water bodies **2.1 °C**; urban forests **2.1 °C**; water bodies and parks reported as delivering consistent cooling largely independent of climate |
| `gunawardena2017` | Air | Green and blue features together offer synergistic benefits; **poorly designed bluespace can worsen heat stress in humid conditions** |

**Adopted: 1.0 – 3.0 °C · base cooling score 85 · confidence medium.**
Combines two of the strongest individual measures along a linear corridor. The humidity caveat from `gunawardena2017` is encoded as a climate-suitability penalty in tropical-wet zones rather than left as prose.

### 11 — Riparian restoration

| Source | Metric | Finding |
|---|---|---|
| `keravec2026` | Air (pedestrian, daytime) | Water bodies **2.1 °C**, climate-robust; urban forests **2.1 °C** |
| `gunawardena2017` | Air | Bluespace cooling mechanisms and the humid-condition heat-stress caveat |

**Adopted: 1.0 – 3.0 °C · base cooling score 85 · confidence medium.**
Same evidential basis as the blue-green corridor — restored riparian corridors combine a water body with dense riparian canopy. Same humidity caveat applies.

---

## Category: Hybrid

### 12 — Permeable shaded plaza

| Source | Metric | Finding |
|---|---|---|
| `keravec2026` | Air (pedestrian, daytime) | Permeable pavements **2.9 °C**; cool pavements **2.0 °C**; shading devices **2.0 °C** |
| `zolch2016` | PET | Shade positioned in heat-exposed locations is the decisive design factor |

**Adopted: 0.5 – 2.5 °C · base cooling score 70 · confidence medium.**
The permeable-pavement estimate is high relative to other measures and rests on a narrower evidence base than the vegetation figures, so the adopted upper bound is set below it. Performance depends heavily on whether shade is actually delivered — captured by the tool's canopy adjustment.

### 13 — Courtyard greening

| Source | Metric | Finding |
|---|---|---|
| `keravec2026` | Air (pedestrian, daytime) | Green areas **2.0 °C**; green walls **3.0 °C**; enclosed-courtyard geometry not separately resolved |
| `zolch2016` | PET | Micro-scale greening in dense residential fabric reduces PET; placement dominates quantity |
| `ziter2019` | Air | Cooling effect scales with patch size — courtyards are below the 60–90 m optimum |

**Adopted: 0.3 – 1.5 °C · base cooling score 60 · confidence low.**
Small, enclosed, and often sheltered from ventilation. Bounded by scale limitation; no courtyard-specific synthesis exists, hence low confidence.

### 14 — Mixed NbS package

| Source | Metric | Finding |
|---|---|---|
| `keravec2026` | Air (pedestrian, daytime) | Best-performing individual NbS measures cluster at **2.0–3.0 °C**; no synthesis estimate exists for combined packages |
| `gunawardena2017` | Air | Combined green and blue features offer synergistic ecosystem benefits (stated qualitatively, not quantified) |

**Adopted: 1.0 – 3.0 °C · base cooling score 80 · confidence medium.**
**The draft methodology's 3.5 °C upper bound was rejected.** No retrieved source quantifies super-additive cooling from combining measures. Claiming that a package outperforms its strongest component would be an unsourced assumption, so the envelope is capped at the best-evidenced single-measure ceiling. The package's advantage is expressed where evidence supports it — breadth of co-benefits and robustness across site conditions — not as extra degrees.

---

## Cross-cutting notes

**Nighttime.** All adopted values are daytime. `keravec2026` reports substantially smaller nighttime effects (parks 1.2 °C, green walls 1.4 °C), and `ziter2019` finds canopy cooling minimal at night while impervious-surface warming persists. The tool does not report a nighttime estimate; the Methodology Report states this limitation, which matters because heat-health risk is strongly associated with nighttime heat.

**Climate dependence is first-order, not a refinement.** `keravec2026` finds solution type alone explains 12% of variance in effectiveness, rising to 78% once Köppen–Geiger subzone is included. This is the empirical justification for the climate suitability factor, and the reason the tool refuses to present a single global cooling number per typology.

**Energy factors are derived, not stored.** No per-typology energy-reduction factors appear in these tables. Cooling-energy savings are derived from estimated air-temperature reduction using the temperature–electricity-demand sensitivity of `akbari2001` (2–4% per °C); see the Methodology Report.

**Costs are not defaulted.** No source retrieved provides defensible global unit costs, and `worldbank2021` documents order-of-magnitude variation between contexts. The tool therefore ships **no default cost values** and reports cost outputs as not estimated unless the user supplies them.
