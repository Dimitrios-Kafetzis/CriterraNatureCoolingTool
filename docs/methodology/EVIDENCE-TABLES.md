# Evidence Tables — NbS Typology Library

For each of the **18 cooling archetypes**: the evidence consulted, the value adopted by the tool, and the reasoning that connects them. Source keys refer to [BIBLIOGRAPHY.md](BIBLIOGRAPHY.md). These tables are the direct source for the `sources:` arrays in [`config/nbs_typologies.yaml`](../../config/nbs_typologies.yaml).

## The two-level library, and why it exists

From version `2026.08.04` the library has two levels (D-044). An **archetype** is a cited evidence class carrying every performance value; a **typology** is one of the **110 curated catalogue entries**, each inheriting exactly one archetype and carrying no performance value of its own.

The reason is simple and worth stating plainly: **solution-specific cooling literature does not exist for 110 typologies.** Retrieving a distinct envelope for a felt-pocket living wall, a suspended-pavement tree pit and a green parking lane is not possible, because nobody has measured them. The alternative to archetypes was inventing 110 envelopes, which would have manufactured precision the catalogue does not contain and broken the evidence rules the tool exists to honour.

So an entry inherits a *cited* envelope, and **every result names the evidence class it inherited from**. A Miyawaki forest reports its cooling on the dense-canopy evidence, and says so. That sentence is the whole design.

Twelve archetypes are the v1.1 typologies unchanged — same envelopes, same base scores, same evidence ratings, same citations (D-043.6). They are the only entries in the library with individually retrieved literature behind them, and this release keeps that evidence rather than trading it for catalogue names. Four are newly retrieved. Two are derived, with the bounding argument stated.

## How to read these tables

**All adopted °C values are daytime, pedestrian-level AIR temperature reductions**, relative to an equivalent unimproved site. This is the metric decision-makers assume when they read "cooling", and mixing it with surface temperature or comfort indices is the most common way screening tools mislead. Where a source reports surface temperature or a comfort index (PET/UTCI/globe temperature), that is stated and the value is used only for ranking or caveats — never converted into a °C air-temperature claim. Two of the four new archetypes exist precisely because a source measured both on the same plots and the two diverged by an order of magnitude.

**Adopted ranges are envelopes, not predictions.** The lower bound represents a poorly performing instance of the typology; the upper bound represents a well-executed instance under favourable conditions. Site adjustment moves an assessment *within* this envelope and can never exceed it (decision D-008).

**Calibration bias is corrected downward.** `keravec2026` synthesises many modelling studies, which systematically report larger effects than field measurement; `bowler2010`, restricted to empirical studies, reports roughly half the park cooling that the modelling-inclusive synthesis does (0.94 °C vs 1.3 °C). Where the two disagree, adopted upper bounds sit at or below the modelling-derived central estimate rather than above it. The same principle decided the `large_water_body` floor at implementation (D-045).

**Confidence** is recorded per archetype and propagates into the tool's output: `high` (multiple converging sources including a synthesis), `medium` (a synthesis estimate with limited class-specific corroboration), `low` (sparse, indirect, or inherited evidence — the tool flags these results explicitly).

## The archetype set

| Archetype | °C envelope | Base score | Evidence | Provenance | Entries |
|---|---|---:|---|---|---:|
| `street_tree_canopy` | 0.5 – 3.0 | 75 | high | existing | 15 |
| `continuous_shaded_corridor` | 0.5 – 3.0 | 80 | medium | existing | 2 |
| `small_green_area_with_trees` | 0.3 – 1.5 | 65 | high | existing | 6 |
| `dense_tree_canopy` | 1.0 – 3.0 | 90 | high | existing | 10 |
| `established_park` | 0.5 – 2.0 | 70 | high | existing | 10 |
| `extensive_green_roof` | 0.1 – 1.0 | 45 | medium | existing | 7 |
| `green_facade_living_wall` | 0.3 – 2.0 | 50 | low | existing | 11 |
| `bioretention` | 0.1 – 0.8 | 55 | low | existing | 8 |
| `blue_green_corridor` | 1.0 – 3.0 | 85 | medium | existing | 5 |
| `riparian_restoration` | 1.0 – 3.0 | 85 | medium | existing | 6 |
| `permeable_shaded_hardscape` | 0.5 – 2.5 | 70 | medium | existing | 2 |
| `enclosed_courtyard` | 0.3 – 1.5 | 60 | low | existing | 1 |
| `large_water_body` | **0.1 – 3.0** | 75 | medium | new | 3 |
| `small_constructed_water` | 0.0 – 1.0 | 40 | medium | new | 6 |
| `non_canopy_vegetation` | 0.0 – 1.5 | 50 | medium | new | 7 |
| `vegetated_shade_structure` | 0.0 – 2.5 | 55 | low | new | 2 |
| `productive_canopy` | 0.5 – 2.0 | 60 | low | derived | 3 |
| `productive_non_canopy` | 0.0 – 1.5 | 45 | low | derived | 6 |

**How the base cooling score of a new archetype was placed.** The base score is a relative 0–100 strength score, not a physical quantity, and the v1.1 set is not a function of the envelope midpoint — bioretention sits at 55 with a 0.45 °C midpoint while the green roof sits at 45 with a 0.55 °C midpoint. There is therefore no formula to apply, and inventing one would have moved twelve calibrated values to make six new ones look derived. Each new score is instead placed against a **named comparator already in the library**, with the argument stated in its section below.

---

## Category: Green

### `street_tree_canopy` — street trees, tree pits, trenches, avenues, green streets

| Source | Metric | Finding |
|---|---|---|
| `keravec2026` | Air (pedestrian, daytime) | Street trees **1.5 °C** central estimate; tropical (A) **4.0 ± 1.6 °C**; arid (B) **1.7 ± 1.4 °C**; hot-summer subzones **3.0 ± 0.8 °C** |
| `bowler2010` | Air | Empirical studies broadly support cooler air beneath tree canopy |
| `ziter2019` | Air | Cooling nonlinear in canopy cover, strongest above **40%** cover; peak effect at 60–90 m scale |
| `zolch2016` | PET (comfort) | Trees best-performing measure, **−13% PET** at pedestrian level |
| `rahman2020` | Air / surface | Species and leaf area index materially change cooling delivered |

**Adopted: 0.5 – 3.0 °C · base cooling score 75 · confidence high.**
The upper bound is set at 3.0 °C rather than the tropical central estimate of 4.0 °C: that figure carries a ±1.6 °C interval and reflects favourable tropical conditions, so adopting it as a general ceiling would overstate typical performance. `ziter2019` supplies the canopy-condition dependence that the tool's canopy adjustment factor encodes.

### `continuous_shaded_corridor` — vegetated arcades, green pedestrian streets

| Source | Metric | Finding |
|---|---|---|
| `keravec2026` | Air (pedestrian, daytime) | Street trees **1.5 °C**; shading devices **2.0 °C**; narrow streets **4.2 °C** (geometry effect) |
| `zolch2016` | PET | Shade placement in heat-exposed locations outperforms maximising total green cover |

**Adopted: 0.5 – 3.0 °C · base cooling score 80 · confidence medium.**
Treated as street trees plus deliberate shade continuity along a movement corridor. Scored slightly above street trees because shade is placed where exposure occurs, which `zolch2016` identifies as the decisive factor. The narrow-street figure is *not* inherited — it is an urban-form effect, not an NbS intervention.

### `small_green_area_with_trees` — tree clusters, tree islands, tree plazas, green playgrounds, intensive roofs, podiums

| Source | Metric | Finding |
|---|---|---|
| `keravec2026` | Air (pedestrian, daytime) | Parks **1.3 °C**; green areas **2.0 °C** |
| `bowler2010` | Air | Park on average **0.94 °C** cooler by day; **larger** parks and those **with trees** cooler |

**Adopted: 0.3 – 1.5 °C · base cooling score 65 · confidence high.**
Explicitly the small end of the park distribution. `bowler2010`'s size relationship is the reason a pocket park is bounded below the general park estimate.

### `dense_tree_canopy` — groves, microforests, urban woodland, afforestation, forest districts

| Source | Metric | Finding |
|---|---|---|
| `keravec2026` | Air (pedestrian, daytime) | Urban forests **2.1 °C** — among the highest-performing green measures |
| `ziter2019` | Air | Greatest cooling where canopy cover exceeds **40%**; effect grows with patch scale to 60–90 m |
| `bowler2010` | Air | Larger, tree-rich green sites cooler |

**Adopted: 1.0 – 3.0 °C · base cooling score 90 · confidence high.**
The best-evidenced high performer: three independent sources converge on dense canopy at scale as the strongest vegetation-based cooling intervention.

### `established_park` — the nine park tiers and the civic green

| Source | Metric | Finding |
|---|---|---|
| `keravec2026` | Air (pedestrian, daytime) | Parks **1.3 °C**; green areas **2.0 °C** |
| `bowler2010` | Air | **0.94 °C** mean; parks with trees cooler than open turf |

**Adopted: 0.5 – 2.0 °C · base cooling score 70 · confidence high.**
Represents *added* cooling from increasing canopy and vegetation complexity in an existing park — the baseline is already partly green, so the achievable increment is bounded below new-forest values.

### Retired at 2026.08.04 — schoolyard greening

`schoolyard_greening` carried its own cited values in v1.1. It is **retired as a typology** by D-043.1: the source document is explicit that a schoolyard is a *land-use context*, not an intervention, and the tool would otherwise ask "what is the land use here?" and then offer, as an intervention, the land use it had just been told. A school site is now offered the real interventions that suit it — 72 of them — through the availability matrix. The evidence that supported the retired typology (green areas 2.0 °C, street trees 1.5 °C, the `ziter2019` city-block scale finding) is the same evidence supporting `small_green_area_with_trees`, which the canonical green playground entry inherits.

## Category: Building

### `extensive_green_roof` — the roof systems and the green terrace

| Source | Metric | Finding |
|---|---|---|
| `keravec2026` | Air (pedestrian, daytime) | Green roofs **1.1 °C** — the lowest-performing green measure in the synthesis |
| `zolch2016` | PET (pedestrian) | Green roof effects at pedestrian level **negligible** |
| `santamouris2014` | Air (city scale) | **0.3–3 K** average urban ambient reduction — but only for **city-scale deployment in simulation studies** |

**Adopted: 0.1 – 1.0 °C · base cooling score 45 · confidence medium.**
This typology carries the largest interpretive gap in the library, and the tool resolves it conservatively. A green roof's thermal benefit is concentrated at roof level and inside the building beneath; `zolch2016` finds essentially nothing at street level, while `santamouris2014`'s larger figures describe *many* roofs across a whole city, which is not what a site-level assessment evaluates. The adopted range therefore sits near the bottom of the published spread, and the tool states in its output that green-roof benefits are principally building-level rather than street-level.

### `green_facade_living_wall` — facades, living walls, screens, noise barriers, retaining walls, balconies

| Source | Metric | Finding |
|---|---|---|
| `keravec2026` | Air (pedestrian, daytime) | Green walls **3.0 °C** central; strongly climate-dependent — Cwa **5.7 ± 1.0**, BWh **5.5 ± 1.0**, Csa **2.9 ± 0.8**, Cfa/Cfb **1.3**, Af **1.0 ± 0.8 °C** |
| `zolch2016` | PET (pedestrian) | Green façades **−5% to −10% PET**, below trees (−13%) |

**Adopted: 0.3 – 2.0 °C · base cooling score 50 · confidence low.**
The evidence is genuinely contradictory: the synthesis ranks green walls near the top on air temperature, while the micro-scale comparison ranks them below trees on comfort. The likely explanation is measurement position — near-wall measurements capture a strong local effect that does not extend across the street canyon. Given a fivefold spread across climate subzones and an unresolved conflict between sources, this typology is assigned **low confidence**, a conservative envelope, and an explicit caveat in the tool's output.

---

## Category: Blue-Green

### `bioretention` — rain gardens, bioswales, stormwater tree pits, planters

| Source | Metric | Finding |
|---|---|---|
| `keravec2026` | Air (pedestrian, daytime) | No bioswale-specific estimate; green areas **2.0 °C**, water bodies **2.1 °C** — neither transferable to a small drainage feature |
| `gunawardena2017` | Air | Tree-dominated greenspace delivers heat-stress relief; small blue features are not identified as significant coolers |

**Adopted: 0.1 – 0.8 °C · base cooling score 55 · confidence low.**
No source was found that quantifies air-temperature cooling for rain gardens or bioswales specifically. This is stated rather than papered over: the value is a reasoned lower bound from adjacent evidence, flagged low confidence, and the tool reports this typology's primary benefits as **stormwater and biodiversity**, not cooling.

### `blue_green_corridor` — the terrestrial and blue-green network corridors

| Source | Metric | Finding |
|---|---|---|
| `keravec2026` | Air (pedestrian, daytime) | Water bodies **2.1 °C**; urban forests **2.1 °C**; water bodies and parks reported as delivering consistent cooling largely independent of climate |
| `gunawardena2017` | Air | Green and blue features together offer synergistic benefits; **poorly designed bluespace can worsen heat stress in humid conditions** |

**Adopted: 1.0 – 3.0 °C · base cooling score 85 · confidence medium.**
Combines two of the strongest individual measures along a linear corridor. The humidity caveat from `gunawardena2017` is encoded as a climate-suitability penalty in tropical-wet zones rather than left as prose.

### `riparian_restoration` — river, canal and floodplain restoration, daylighted streams, riparian buffers

| Source | Metric | Finding |
|---|---|---|
| `keravec2026` | Air (pedestrian, daytime) | Water bodies **2.1 °C**, climate-robust; urban forests **2.1 °C** |
| `gunawardena2017` | Air | Bluespace cooling mechanisms and the humid-condition heat-stress caveat |

**Adopted: 1.0 – 3.0 °C · base cooling score 85 · confidence medium.**
Same evidential basis as the blue-green corridor — restored riparian corridors combine a water body with dense riparian canopy. Same humidity caveat applies.

---

## Category: Hybrid

### `permeable_shaded_hardscape` — cooling plazas and permeable plazas

| Source | Metric | Finding |
|---|---|---|
| `keravec2026` | Air (pedestrian, daytime) | Permeable pavements **2.9 °C**; cool pavements **2.0 °C**; shading devices **2.0 °C** |
| `zolch2016` | PET | Shade positioned in heat-exposed locations is the decisive design factor |

**Adopted: 0.5 – 2.5 °C · base cooling score 70 · confidence medium.**
The permeable-pavement estimate is high relative to other measures and rests on a narrower evidence base than the vegetation figures, so the adopted upper bound is set below it. Performance depends heavily on whether shade is actually delivered — captured by the tool's canopy adjustment.

### `enclosed_courtyard` — courtyard greening

| Source | Metric | Finding |
|---|---|---|
| `keravec2026` | Air (pedestrian, daytime) | Green areas **2.0 °C**; green walls **3.0 °C**; enclosed-courtyard geometry not separately resolved |
| `zolch2016` | PET | Micro-scale greening in dense residential fabric reduces PET; placement dominates quantity |
| `ziter2019` | Air | Cooling effect scales with patch size — courtyards are below the 60–90 m optimum |

**Adopted: 0.3 – 1.5 °C · base cooling score 60 · confidence low.**
Small, enclosed, and often sheltered from ventilation. Bounded by scale limitation; no courtyard-specific synthesis exists, hence low confidence.

### Retired at 2026.08.04 — the mixed NbS package

`mixed_nbs_package` was a single averaged card standing in for "several things at once". It is replaced by real, itemised packages (D-038): the user selects the actual components, each is scored individually and shown individually, and the package's temperature is **capped at the best-evidenced component and never summed**.

The finding underneath has not changed and is not re-argued here — no retrieved source quantifies super-additive cooling from combining measures, which is why the v1.1 typology was capped at 3.0 °C rather than the draft's 3.5 °C. What changed is that the tool no longer needs an opaque typology to express it. A package's advantage appears where the evidence supports it: co-benefit breadth (unioned across components), not extra degrees. Costs sum; suitability takes the weakest component, because a package is no more deliverable on a site than its least suitable member.

---

---

## The four archetypes retrieved for this release

Each exists because the catalogue contains entries that would otherwise have inherited an envelope belonging to a different body of study. In two cases that inheritance would have overstated the entry roughly threefold.

### `large_water_body` — urban lake restoration, living shorelines, coastal ecological corridors

| Source | Metric | Finding |
|---|---|---|
| `keravec2026` | Air (pedestrian, daytime) | Water bodies **2.1 °C**, reported as largely climate-independent |
| `volker2013` | Air / mixed | Meta-analysis of **27 studies**: pooled **2.5 K (95% CI 1.9–3.2 K)** in the warmest months, **when remote-sensing data are included**; a single pooled estimate across ponds, lakes and rivers together, *not* differentiated by size |
| `yao2023a` | Air (screen height, field) | Year-long measurement of urban lakes in two humid subtropical cities: **0.1–0.6 °C** daytime cool island, **1.2–1.3 °C** heat island at night |
| `ampatzidis2020` | Method | A clear disparity between cooling potentials from **remote sensing** and those from field measurement or simulation; at night blue space may **exacerbate** the heat island |

**Adopted: 0.1 – 3.0 °C · base cooling score 75 · confidence medium.**

**The floor is 0.1 °C, not the 0.5 °C the review pack proposed.** The pack attributed a cooling magnitude "near 2 °C" to `yao2023a`; source verification at implementation established that the paper reports no such figure and in fact measures an order of magnitude less by day. Holding the floor at 0.5 °C would have made the tool claim more than its most direct field evidence supports — precisely the inflation D-008 exists to prevent — so the floor was lowered to the measured minimum. This is recorded as D-045.

**The width of the envelope is the finding, not a defect.** A remote-sensing-inclusive meta-analysis and direct field measurement of actual urban lakes disagree by an order of magnitude, and `ampatzidis2020` names remote sensing as the overestimating mode. A narrower envelope would have to pick a side, and the evidence does not justify picking one. The tool therefore reports the disagreement, and the output caveat says so in as many words rather than leaving the user to wonder why the range is so wide.

**Base score 75**, placed below `blue_green_corridor` (85) and equal to `street_tree_canopy`. A water body alone lacks the corridor's canopy component — the corridor's envelope rests on the canopy evidence as much as on the water evidence — and its field-measured daytime performance is weak.

### `small_constructed_water` — constructed wetlands, retention ponds, detention basins, water squares, floating wetlands, roof wetlands

| Source | Metric | Finding |
|---|---|---|
| `jacobs2020` | Air (pedestrian, simulated + synthesis) | 16 configurations: afternoon air temperature reduced **typically 0.2 °C, maximum 0.6 °C**. Of 20 papers synthesised, **14 (70%) report ≤1 °C**. Concludes the effect "can be considered **negligible in design practice**" |
| `yao2023b` | Air (field) | Urban pond: **0.6 °C** daytime cooling against a reference site, **1.8 °C** nocturnal *warming* |
| `ampatzidis2020` | Method / nocturnal | Cooling varies with time of day, season and location; sensible cooling can be offset by increased water-vapour content |

**Adopted: 0.0 – 1.0 °C · base cooling score 40 · confidence medium.**

**This archetype exists to prevent a threefold overstatement.** Constructed wetlands, retention ponds, detention basins and water squares would naturally have been mapped to `blue_green_corridor` (1.0–3.0 °C) on family resemblance — they are water, and water cools. Three independent lines say otherwise for *small constructed* water, and the tool follows them.

**The engine must never interpolate between this archetype and `large_water_body` by area.** The two clusters exist as separate bodies of study, not as a published dose–response curve: the size-threshold literature is land-surface-temperature only, and no published curve connects them on air temperature. An area-based interpolation would look eminently reasonable and would be unsourced. This is asserted directly by the test suite, on a site 2 500 times the minimum, so that a future edit cannot introduce it quietly.

**The floor is a genuine zero**, on `jacobs2020`'s own conclusion. **Base score 40**, below `extensive_green_roof` (45): the two share a ceiling near 1.0 °C, but this class has a true zero floor and the roof does not.

### `non_canopy_vegetation` — planting beds, groundcover, pocket meadows, roof meadows, green medians

| Source | Metric | Finding |
|---|---|---|
| `armson2012` | **Surface AND globe, same plots** | Grass cut maximum **surface** temperature by up to **24 °C** but had **little effect upon globe temperature**; shading cut globe temperature by **5–7 °C**. "Grass has little effect upon local air or globe temperatures … whereas tree shade can provide effective local cooling" |
| `gill2013` | Air (modelled) | Grass cooling "can be **reduced or lost in summer droughts**", projected to worsen under climate change |
| `kraemer2022` | Air (field, drought) | The grass-dominated park was the **hottest area during the daytime**; the tree-dominated park consistently cooler |
| `bowler2010` | Air | Parks containing trees reported cooler than open turf (qualitative) |
| `kumar2024` | Air | Grass and herbaceous systems sit well below canopy systems |

**Adopted: 0.0 – 1.5 °C · base cooling score 50 · confidence medium.**

`armson2012` is decisive **because it measures both metrics on the same plots**, and so isolates the surface/air conflation that inflates most published grass figures. A 24 °C surface reduction alongside almost no globe-temperature change is not a small effect measured badly; it is a large effect on the wrong quantity. Any figure for grass cooling that sounds impressive should be checked for which temperature it describes, and the tool's output caveat tells the user exactly that.

**The floor is a genuine zero** for dry or dormant planting, on `gill2013` and `kraemer2022`. **Base score 50**, below `small_green_area_with_trees` (65), which shares the 1.5 °C ceiling but adds canopy shade — the component `armson2012` shows is doing the work.

### `vegetated_shade_structure` — green pergolas and green waiting shelters

| Source | Metric | Finding |
|---|---|---|
| `chafer2020` | Air (field, like-for-like) | Vine-covered pergola against an **identical bare support**: maximum daytime difference **2.5 °C** (45.3 °C over the ropes, 42.9 °C under the greenery), west-oriented, Mediterranean |
| `ouyang2024` | Air **and** MRT | Shading structures: air temperature **−1.42 °C** (natural) / **−1.31 °C** (artificial); mean radiant temperature **−15.93 °C** / **−13.71 °C** |
| `colter2019` | PET | Sparse and open canopies group **with constructed shade structures**, 2.9–4.3 °C worse in PET than dense-canopy species |

**Adopted: 0.0 – 2.5 °C · base cooling score 55 · confidence low.**

**The `keravec2026` "shading devices 2.0 °C" figure is deliberately not used here.** That category aggregates area-scale shading, where the cooled air volume persists against advection; a pergola shades roughly 10 m². Applying it would rate a pergola above tree canopy, which `ouyang2024` measures at 1.42 °C. The same figure **is** used by `permeable_shaded_hardscape`, where the scale matches — the distinction is scale, not scepticism, and the test suite asserts both halves of it.

**A large comfort benefit and a small air-temperature one.** `ouyang2024` measures the two axes an order of magnitude apart. Users will feel substantially cooler under a pergola than the air-temperature figure suggests, and the output caveat says so — under-selling the intervention would be as misleading as over-selling it, just in the other direction.

Confidence is **low**, with n=1 for the actual intervention. The 2.5 °C ceiling is `chafer2020`'s measured peak; note that paper's abstract headlines "up to 5 °C", which is greenery against **unshaded** conditions rather than against the bare pergola. The like-for-like contrast is the one adopted, and the discrepancy is recorded in the bibliography so a reviewer checking the abstract does not read an error into it. **Base score 55**, well below `permeable_shaded_hardscape` (70), which shares the 2.5 °C ceiling on a broader evidence base.

---

## The two derived archetypes

Retrieval established that no class-specific evidence exists. Each is therefore bounded from an adjacent class with the bounding argument stated — and, unusually, **the absence itself is citable**, which is a stronger position than the rain-garden precedent where no source was found at all.

### `productive_canopy` — urban orchards, food forests, agroforestry systems

| Source | Metric | Finding |
|---|---|---|
| `kumar2024` | Coverage | Review of 51 green–blue infrastructure types across 202 publications: allotments and city farms are **among the least-studied categories, with insufficient data to quantify** |
| `ziter2019` | Air | Cooling strengthens above approximately **40% canopy cover** |
| `colter2019` | PET | Sparse canopies perform no better than solid artificial shade |
| `cheung2022` | Air | Measured agricultural cooling **0.09–0.43 °C** against modelled potentials of **2.1–2.5 °C**; irrigation raises the daily *minimum* temperature |

**Adopted: 0.5 – 2.0 °C · base cooling score 60 · confidence low.**

Derived, not retrieved. Bounded **below** `dense_tree_canopy` on two grounds: orchard and agroforestry canopies are deliberately kept open for access and yield, so they sit below the `ziter2019` inflection, and `colter2019` establishes that sparse canopies do not perform like closed ones. The envelope matches `established_park` at a lower evidence rating — the same range, honestly labelled as inherited rather than measured. **Base score 60**, below `established_park` (70) for the same reason.

**Irrigation is not credited as extra degrees.** `cheung2022` documents it as *sustaining* performance through drought, not raising it. One nuance is carried forward carefully: the measured-versus-modelled gap above is specific to **agricultural fields**, and the same paper measures −2 to −1 °C in irrigated urban parks, much closer to the modelled values. The methodology therefore does **not** claim that models overstate irrigation cooling in general.

### `productive_non_canopy` — community gardens, allotments, school gardens, urban farms, productive roofs, rooftop farms

| Source | Metric | Finding |
|---|---|---|
| `kumar2024` | Coverage | Allotments and city farms among the least-studied of 51 types, insufficient data to quantify |
| `rost2020` | Air (**nocturnal only**) | 13 Berlin allotment complexes averaged **2.7 K cooler at night** than built-up areas |
| `armson2012` | Surface / globe | Ground-level vegetation cuts surface temperature substantially while barely affecting globe temperature |
| `cheung2022` | Air | Measured 0.09–0.43 °C against modelled 2.1–2.5 °C; irrigation warms nights |

**Adopted: 0.0 – 1.5 °C · base cooling score 45 · confidence low.**

Inherits the `non_canopy_vegetation` envelope, because cultivated ground-level planting *is* ground-level vegetation whose cover is periodically broken between crops. Rated **low** rather than medium because the inheritance is an argument rather than a measurement of this class.

**`rost2020` is the best allotment measurement available, and it cannot be used for a value.** It is nocturnal only — the restriction is in its title, abstract and design — and this tool reports daytime air temperature. It is cited as evidence of what the productive-landscape literature does and does not measure, which is exactly the point `kumar2024` makes at review scale. **Base score 45**, below `non_canopy_vegetation` (50), for the periodic bare-ground reason.

---

## Suitability: inheritance, and the 21 overrides

Suitability conditions — minimum viable area, soil requirement, irrigation requirement — are inherited from the archetype, with **per-entry overrides only where the catalogue's own description of the entry makes an inherited value plainly wrong** (D-044.3). Inventing a minimum area and a soil requirement for each of 110 entries would manufacture precision the catalogue does not contain.

**No new number enters the methodology through an override.** Every replacement value is one already present in the cited v1.1 library — 20, 50, 200, 500, 1 000, 2 000 m² — borrowed from the typology that established it. The override list is deliberately short, and a test fails if it grows past 25 entries, because a long list would mean the inheritance ruling had quietly been abandoned.

| Entries | Override | Why the inherited value is wrong |
|---|---|---|
| Tree grove, microforest, rooftop woodland | area → 200 m² | `dense_tree_canopy`'s 2 000 m² describes the woodland its *cooling evidence* comes from, not the footprint of a site element. The document defines a microforest as a small dense patch on a constrained site. |
| Intensive green roof, productive green roof, roof meadow, roof wetland (50 m²); rooftop farm, rooftop woodland (200 m²) | soil → none | A roof's growing medium is **built, not ground**. Requiring ground soil on a roof would flag every roof entry whose archetype happens to be a ground-level class. |
| Green podium, water square, floating wetland | soil → none | Built structure or open water, likewise. Water square also → 200 m² (plaza scale). |
| Direct and indirect ground-rooted façades, green noise barrier, vegetated retaining wall | soil → limited | The document defines these as rooted in **natural ground**, which the containerised living-wall archetype does not require. This override makes the tool *stricter*, not more permissive. |
| Pocket park | area → 200 m² | This entry **is** the tool's own cited pocket park; its minimum area is the one v1.1 established. |
| Riparian buffer | area → 200 m² | The document distinguishes a discrete vegetated strip from the restored corridor the archetype describes. |
| Railway green corridor, green mobility network | area → 1 000 m² | Corridor- and district-scale systems inheriting an element archetype. |
| Urban farm (500 m²), agroforestry system (1 000 m²) | area | The document distinguishes field-scale production from garden scale. |

**Land-use context is not a second list.** The suitability urban-context sub-indicator (D-022) compares the site's land use against the entry's own land-use list, which is the availability matrix's list. An entry is therefore "in context" exactly where it is offered — one list, one meaning, and no opportunity for the two to drift apart.

---

## Availability: what gates, and what an unanswered question means

Availability decides which entries are *offered*. It feeds no score and enters no formula (D-044.1) — a property the test suite asserts directly, by scoring one site twice, with every availability question answered and with none of them answered, and requiring byte-identical output.

Three of the four conditions describe a **physical fact** about the site, and gate on positive confirmation: an entry that acts on an existing river is not offered until the user says there is a river, because offering it would be offering an intervention that cannot be built. The fourth describes **who could deliver** the intervention, and subtracts nothing until it is answered.

That asymmetry is deliberate and is the substance of D-043.3. The originally approved question — "is there interest to create productive landscape from individuals or communities", yes or no — would have suppressed the urban farm and the agroforestry system on a "no": the highest-canopy, highest-cooling entries in the group, and the ones a municipality is most likely to deliver. A multi-select over {community, individual, institutional, commercial} gates correctly at no extra cost in user effort, and an *empty* selection is not evidence that no delivery model exists. The tool never asserts a negative from absent information, here as in D-022 and D-026.

| Condition | Gates | Unanswered |
|---|---|---|
| Waterfront type | 12 water-landscape and ecological-network entries, by category | withholds |
| Railway | exactly one entry, the railway green corridor | withholds |
| Existing woodland | **restoration** types only — degraded woodland restoration, reforestation | withholds |
| Productive governance | the 7 productive entries, by who delivers them | **offers everything** |

Woodland **creation** types — urban woodland, microforest, afforestation, woodland buffer — carry no woodland condition and are offered regardless. The four **constructed** water features — constructed wetland, retention pond, detention basin, water square — carry no waterfront condition, because a constructed feature needs no existing water body.

**A note on the published situation counts.** The nine counts in the v1.2 review pack's part 4 were computed with the governance question unanswered, which is why they are reproduced in the test suite that way. Answering it reduces them: a school site offers 67 entries with the question unanswered and 63 when only *institutional* delivery is selected. Both are correct; they answer different questions.

---

## Climate classification: mapping Köppen–Geiger onto the tool's six zones

Added at version `2026.08.05` (D-047.3, D-048), for the map-based site picker.
The table lives in [`config/climate_classification.yaml`](../../config/climate_classification.yaml).

**This is a methodology value, and the distinction matters.** The
classification itself is cited and is not ours: `beck2023` publishes the
thirty Köppen–Geiger classes at 1 km for 1991–2020 under CC BY 4.0, and the
tool bundles the 0.1° layer of it. What is *not* in that source, or in any
source, is which of the tool's six zones each class belongs to. Thirty classes
onto six zones is a judgement, it selects a row of the climate adjustment
matrix, and it therefore changes results — so it is declared, derived here, and
version-stamped like every other methodology value.

| Source | Metric | Finding |
|---|---|---|
| `beck2023` | Köppen–Geiger class, 1991–2020 | Thirty classes, published at 1 km and coarser, under CC BY 4.0. The tool bundles the **0.1° (≈11 km)** layer. |
| `keravec2026` | Variance in cooling effectiveness explained | Solution type alone **12%**; adding climate zone **30%**; adding Köppen–Geiger subzone **78%**. Street trees **4.0 ± 1.6 °C** in tropical (A) versus **1.7 ± 1.4 °C** in arid (B). |

**Adopted: a four-branch rule, not thirty separate assignments.** Every one of
the thirty rows follows from one of four principles, and the config table
records which branch produced each row so the mapping can be checked against
the principle rather than taken on trust. A thirty-row table of individual
opinions could not be reviewed; a reviewer disagreeing with this one disagrees
with a stated principle, which is the point.

| Branch | Classes | Zone | Why |
|---|---|---|---|
| Tropical | `Af`, `Am` | `tropical_wet` | Group A splits on its dry season, which is the same split the tool's two tropical zones name. No dry season, or a brief one. |
| Tropical | `Aw` | `tropical_dry` | Savannah: a pronounced dry season. Nothing is interpreted here — the zone names and Köppen's subdivisions describe the same distinction. |
| Arid | `BWh`, `BWk` | `arid` | Group B splits on desert (BW) versus steppe (BS); the tool splits on arid versus semi-arid. Same axis. |
| Arid | `BSh`, `BSk` | `semi_arid` | The hot/cold third letter is deliberately ignored: the tool's arid downgrade encodes **water limitation constraining evapotranspiration**, not temperature. A cold desert limits evapotranspiration as a hot one does. |
| Warm season | C and D ending `a` or `b` | `temperate` | A hot or warm summer. This is where the mid-latitude cooling literature was measured — the studies behind the temperate row are overwhelmingly from Cfa, Cfb, Dfa and Dfb cities. |
| No warm season | C and D ending `c` or `d`, and all of E | `other` | Fewer than four months above 10 °C, or none. There is no warm season for the cooling literature to describe. |

**Group D is not sent to `other` wholesale, and that is deliberate.** The
temptation is to read "cold" as "not this tool's problem", but Chicago is
`Dfa`, Seoul is `Dwa` and Moscow is `Dfb`; all three have serious urban heat
problems, and all three sit squarely inside the evidence base behind the
temperate row. Discarding them would lose real signal in exchange for a tidier
rule.

**The classes with no urban-heat counterpart map to `other` (D-047.3).**
`other` is already the tool's neutral climate condition — every family resolves
to condition `unknown`, which is factor **1.0** — so an unclassifiable location
receives neither a boost nor a penalty. Forcing `ET`, `EF`, `Dfc` and their
neighbours into `temperate` was rejected: it would assert that a tundra site
cools like a temperate one, which no source in the bibliography supports, and
**an uncited claim introduced through a lookup table is still an uncited
claim**. Refusing to answer is the honest output when the literature has
nothing to say.

**What this table does and does not affect.** It is consulted only when a user
opens the map and accepts the value it offers. It never overrides an answer the
user has given, it introduces no new number into any formula, and a
questionnaire filled in without the map is unaffected by it entirely. Its
resolution — 0.1°, roughly 11 km — is stated in the interface and in the report
alongside every value it produces: the classification is reliable for the city
a site sits in, not for the site, which is the resolution at which climate zone
enters this methodology in any case.

**Country identification is not a methodology value** and is recorded here only
so that both map-derived inputs are documented together. It is a
point-in-polygon test against public-domain `naturalearth` boundaries, feeding
the emission-factor and currency defaults and nothing else. Its two judgements
are documented in [`data/geo/ATTRIBUTION.md`](../../data/geo/ATTRIBUTION.md):
territories with no ISO 3166-1 code are not assigned to the state that claims
them, and a point falling just outside a generalised coastline is attributed to
the coast it sits on within a stated 25 km tolerance.

---

## Cross-cutting notes

**Nighttime.** All adopted values are daytime. `keravec2026` reports substantially smaller nighttime effects (parks 1.2 °C, green walls 1.4 °C), and `ziter2019` finds canopy cooling minimal at night while impervious-surface warming persists. The tool does not report a nighttime estimate; the Methodology Report states this limitation, which matters because heat-health risk is strongly associated with nighttime heat.

The 2026.08.04 retrieval **sharpened this limitation into something closer to a warning** for two classes. Water bodies do not merely cool less at night — they *warm*: `yao2023b` measures 1.8 °C of nocturnal warming at an urban pond, `yao2023a` measures a 1.2–1.3 °C nocturnal heat island at urban lakes, and `ampatzidis2020` states that blue space may exacerbate the night-time heat island outright. Irrigated productive landscapes carry the same sign: `cheung2022` predicts an increase in the daily *minimum* temperature as stored heat is released. In both cases the effect is **outside** the daytime estimate rather than netted off against it, and both archetypes carry an output caveat saying so. A daytime-only tool that quietly omitted this would be reporting only the favourable half of what its own sources found.

**A validation, and a deliberate non-adoption.** `kumar2024` is a 2024 typology-resolved review post-dating the v1.1 calibration. It reports street trees at up to **2.8 °C by in-situ monitoring** — inside the tool's 0.5–3.0 °C envelope — so the conservative calibration of D-014 holds against newer and broader evidence. The same review reports figures well *above* the tool's envelopes for other types: green walls 4.1 ± 4.2 °C, vegetated balconies 3.8 ± 2.7 °C, botanical gardens 5.0 ± 3.5 °C. **These are not adopted.** Taking them selectively would break internal consistency — vegetated balconies would outscore street trees — and adopting them wholesale is a full recalibration of the library with its own sensitivity analysis, which is a separate decision. Note also that the green-wall figure's standard deviation exceeds its mean. Recorded as a candidate for a future methodology review (D-044).

**Climate dependence is first-order, not a refinement.** `keravec2026` finds solution type alone explains 12% of variance in effectiveness, rising to 78% once Köppen–Geiger subzone is included. This is the empirical justification for the climate suitability factor, and the reason the tool refuses to present a single global cooling number per typology.

**Energy factors are derived, not stored.** No per-typology energy-reduction factors appear in these tables. Cooling-energy savings are derived from estimated air-temperature reduction using the temperature–electricity-demand sensitivity of `akbari2001` (2–4% per °C); see the Methodology Report.

**Costs are not defaulted.** No source retrieved provides defensible global unit costs, and `worldbank2021` documents order-of-magnitude variation between contexts. The tool therefore ships **no default cost values** and reports cost outputs as not estimated unless the user supplies them.
