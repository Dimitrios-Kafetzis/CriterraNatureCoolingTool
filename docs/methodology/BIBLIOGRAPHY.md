# Bibliography

Every source cited by the methodology, with its verification status. Sources are referenced elsewhere by their key (e.g. `bowler2010`).

**Verification policy.** A source enters this bibliography only after its bibliographic details have been checked against the publisher record, an institutional repository, or an indexing service. The *Verified* column records what was confirmed:

- **Full** — bibliographic details and the specific quantitative finding used by the methodology were both confirmed from a retrieved source.
- **Metadata + finding (secondary)** — bibliographic details confirmed from the publisher/repository; the quantitative finding confirmed from an authoritative secondary description (e.g. publisher abstract page or indexing service) rather than the full text.
- **Metadata only** — bibliographic details confirmed; the finding is referenced qualitatively only.

Where a value in the tool depends on a finding that is not *Full*, the configuration marks its confidence accordingly. Several publisher sites (Elsevier, PNAS, Science) block automated retrieval; findings from those were confirmed via open repositories, PubMed, or publisher abstract pages, and this is noted per entry.

---

## Cooling performance of urban vegetation

**`bowler2010`** — Bowler, D.E., Buyung-Ali, L., Knight, T.M., Pullin, A.S. (2010). Urban greening to cool towns and cities: A systematic review of the empirical evidence. *Landscape and Urban Planning*, 97(3), 147–155. DOI: [10.1016/j.landurbplan.2010.05.006](https://doi.org/10.1016/j.landurbplan.2010.05.006)
*Finding used:* meta-analysis of empirical park studies — a park was on average **0.94 °C cooler during the day** than its non-green surroundings; larger parks and parks with trees tended to be cooler.
*Verified:* Metadata (Bangor University repository) + finding (secondary: publisher abstract description). Elsevier full text blocked.

**`ziter2019`** — Ziter, C.D., Pedersen, E.J., Kucharik, C.J., Turner, M.G. (2019). Scale-dependent interactions between tree canopy cover and impervious surfaces reduce daytime urban heat during summer. *PNAS*, 116(15), 7575–7580. DOI: [10.1073/pnas.1817561116](https://doi.org/10.1073/pnas.1817561116)
*Findings used:* air temperature decreases **nonlinearly** with canopy cover, with greatest cooling **above ~40% canopy cover**; daytime intra-urban air temperature range averaged **3.5 °C** (1.1–5.7 °C), nighttime **2.1 °C** (1.2–3.0 °C); maximum daytime cooling at **60–90 m** radii (city-block scale); impervious cover raises temperature approximately linearly and its effect **persists at night**.
*Verified:* Full (PubMed record, PMID 30910972).

**`zolch2016`** — Zölch, T., Maderspacher, J., Wamsler, C., Pauleit, S. (2016). Using green infrastructure for urban climate-proofing: An evaluation of heat mitigation measures at the micro-scale. *Urban Forestry & Urban Greening*, 20, 305–316. DOI: [10.1016/j.ufug.2016.09.011](https://doi.org/10.1016/j.ufug.2016.09.011)
*Findings used:* micro-scale (ENVI-met) comparison at pedestrian level — trees achieved an average **PET reduction of 13%**; green façades **5–10%**; **green roof effects were negligible** at pedestrian level. Increasing green cover did not correspond linearly to PET reduction; placement matters more than quantity.
*Verified:* Full (Lund University research portal record).
*Note:* PET is a thermal-comfort index, not air temperature. Used in this methodology for the **relative ranking** of intervention families and for the green-roof street-level caveat, never as an air-temperature value.

**`rahman2020`** — Rahman, M.A., et al. (2020). Tree cooling effects and human thermal comfort under contrasting species and sites. *Agricultural and Forest Meteorology*, 287, 107947. DOI: [10.1016/j.agrformet.2020.107947](https://doi.org/10.1016/j.agrformet.2020.107947)
*Finding used:* species and site conditions materially change tree cooling performance; leaf area index correlates positively with surface cooling, transpirational air cooling, and comfort improvement.
*Verified:* Metadata only (publisher listing). Used qualitatively — to justify that canopy condition modulates performance — never for a numeric value.

---

## Synthesis across measures and climates

**`keravec2026`** — Keravec-Balbot, T., Schoetter, R., Masson, V. (2026). Adapting cities to heat: an umbrella review of the effectiveness of urban cooling measures across climates. *Environmental Research Letters*, 21(14), 143003. DOI: [10.1088/1748-9326/ae870e](https://doi.org/10.1088/1748-9326/ae870e)
*Findings used:* umbrella review of **64 systematic reviews**, multilevel meta-regression of **pedestrian-level daytime air temperature** reductions. Central estimates by measure: green walls 3.0 °C, permeable pavements 2.9 °C, water bodies 2.1 °C, urban forests 2.1 °C, green areas 2.0 °C, shading devices 2.0 °C, street trees 1.5 °C, parks 1.3 °C, green roofs 1.1 °C. Climate-zone estimates including street trees **4.0 ± 1.6 °C in tropical (A)** vs **1.7 ± 1.4 °C in arid (B)** climates. Variance explained: solution type alone **12%**, solution + climate zone **30%**, solution + Köppen–Geiger subzone **78%**. Nighttime effects are markedly smaller (parks 1.2 °C, green walls 1.4 °C).
*Verified:* Full (IOPscience, open access).
*Role in this methodology:* the primary cross-typology anchor, and the empirical basis for treating climate suitability as a first-order adjustment.

**`kumar2024`** — Kumar, P., Debele, S.E., Khalili, S., et al. (2024). Urban heat mitigation by green and blue infrastructure: Drivers, effectiveness, and future needs. *The Innovation*, 5(2), 100588. DOI: [10.1016/j.xinn.2024.100588](https://doi.org/10.1016/j.xinn.2024.100588)
*Findings used:* systematic review screening **27,486 papers** to **202** analysed, covering **51 green–blue infrastructure (GBGI) types** in 10 divisions. Reports street trees at up to **2.8 °C** by in-situ monitoring. Explicitly identifies **allotments and city farms among the least-studied categories**, with insufficient data to quantify their cooling (alongside private gardens, zoological gardens, golf courses, estuaries). Also reports means well above this tool's envelopes for other types — botanical gardens 5.0 ± 3.5 °C, wetlands 4.9 ± 3.2 °C, green walls 4.1 ± 4.2 °C, vegetated balconies 3.8 ± 2.7 °C.
*Verified:* Full (PMC open access record, PMC10909648).
*Role:* two distinct roles. (1) **A validation:** this 2024 typology-resolved review post-dates the v1.1 calibration, and its in-situ street-tree figure of 2.8 °C sits inside the tool's existing 0.5–3.0 °C envelope, so the conservative calibration of D-014 holds against newer and broader evidence. (2) **A citable evidence gap:** it is the source that lets the methodology state the absence of productive-landscape cooling evidence as a finding rather than as a search failure. Its higher figures are **deliberately not adopted** — see D-044 for why selective adoption would break internal consistency and wholesale adoption would be a separate recalibration with its own sensitivity analysis.

---

## Water bodies and constructed water features

The two water archetypes are separate bodies of study, not two points on one curve. The sources below are what establishes that, and the engine never interpolates between them by area (D-044).

**`jacobs2020`** — Jacobs, C., Klok, L., Bruse, M., Cortesão, J., Lenzholzer, S., Kluck, J. (2020). Are urban water bodies really cooling? *Urban Climate*, 32, 100607. DOI: [10.1016/j.uclim.2020.100607](https://doi.org/10.1016/j.uclim.2020.100607)
*Findings used:* **16** representative virtual urban water bodies simulated (ENVI-met 4.1.3, REALCOOL project). "Afternoon air temperatures in surrounding spaces were reduced by **typically 0.2 °C** and the **maximum cooling effect was 0.6 °C**." A synthesis of results reported in **20 papers** for water bodies without fountains gives a median air-temperature effect of about 0.5 °C, with **14 of the 20 (70%) reporting 1 °C or less**. The paper concludes that local thermal effects of small water bodies "can be considered **negligible in design practice**".
*Verified:* Full (open publisher PDF via the Wageningen repository, read directly).
*Role:* the primary source for the `small_constructed_water` archetype, and the reason constructed wetlands, ponds, basins and water squares are **not** allowed to inherit the corridor envelope on family resemblance.

**`volker2013`** — Völker, S., Baumeister, H., Claßen, T., Hornberg, C., Kistemann, T. (2013). Evidence for the temperature-mitigating capacity of urban blue space – a health geographic perspective. *ERDKUNDE*, 67(4), 355–371. DOI: [10.3112/erdkunde.2013.04.05](https://doi.org/10.3112/erdkunde.2013.04.05)
*Finding used:* systematic review and meta-analysis of **27 studies**; a cooling effect of **2.5 K (95% CI 1.9–3.2 K, p < 0.01)** during the warmest months of the northern hemisphere is attributed to urban blue sites **when remote-sensing data are included**.
*Verified:* Full (open-access publisher PDF, read directly).
*Caveats recorded:* this is a **single pooled estimate across ponds, lakes and rivers together — it does not differentiate cooling by water-body size**, so it cannot be used to justify a size-dependent gradient. Its magnitude also depends on the inclusion of remote-sensing data, which `ampatzidis2020` identifies as the overestimating measurement mode.

**`yao2023a`** — Yao, L., Sailor, D.J., Yang, X., Xu, G., Zhao, L. (2023). Are water bodies effective for urban heat mitigation? Evidence from field studies of urban lakes in two humid subtropical cities. *Building and Environment*, 245, 110860. DOI: [10.1016/j.buildenv.2023.110860](https://doi.org/10.1016/j.buildenv.2023.110860)
*Findings used:* year-long continuous screen-height measurements at lake, residential and rural sites in Nanjing and Guangzhou, China. Relative to rural sites the lakes showed a **weak urban cool island intensity of 0.1–0.6 °C during the day**, but a **heat island intensity of 1.2–1.3 °C at night** during the warm months (May–September).
*Verified:* Metadata + finding (secondary: Arizona State University Elsevier Pure institutional record, full abstract). Elsevier full text blocked.
*Role:* **the most direct field evidence for large water bodies, and the reason the `large_water_body` envelope floor was lowered from the 0.5 °C proposed in the review pack to 0.1 °C at implementation.** The pack attributed a cooling magnitude "near 2 °C" to this source; retrieval established that the paper reports no such figure and in fact measures an order of magnitude less by day. See D-045.

**`yao2023b`** — Yao, L., Sailor, D.J., Zhang, X., Wang, J., Zhao, L., Yang, X. (2023). Diurnal pattern and driving mechanisms of the thermal effects of an urban pond. *Sustainable Cities and Society*, 91, 104407. DOI: [10.1016/j.scs.2023.104407](https://doi.org/10.1016/j.scs.2023.104407)
*Finding used (verbatim):* "compared with a reference soil-site, the pond exerted a moderate daytime cooling effect (**0.6 °C**) but a pronounced nocturnal warming effect (**1.8 °C**)." Field measurement at an urban pond in Nanjing, China, with an energy-balance analysis.
*Verified:* Metadata + finding (secondary: Arizona State University Elsevier Pure record, full abstract). Elsevier full text blocked.
*Role:* independent field corroboration of `jacobs2020`'s simulated magnitudes for small water features, and one half of the nocturnal-warming caveat.

**`ampatzidis2020`** — Ampatzidis, P., Kershaw, T. (2020). A review of the impact of blue space on the urban microclimate. *Science of the Total Environment*, 730, 139068. DOI: [10.1016/j.scitotenv.2020.139068](https://doi.org/10.1016/j.scitotenv.2020.139068)
*Findings used:* the cooling effect of blue space **varies with time of day, season and location**; there is "a clear disparity between the cooling potentials reported by **remote sensing** as opposed to field measurements or numerical simulations"; and "during the night blue spaces may actually **exacerbate the UHI**, reducing urban thermal comfort", with sensible cooling partly offset by increased water-vapour content.
*Verified:* Full for the diurnal-variability and nocturnal findings (publisher abstract read in full via the University of Bath research portal); the remote-sensing statement is *Metadata + finding (secondary)* — the substance is in the abstract as quoted above, while the compact "remote sensing overestimates" phrasing appears in the article Highlights via an indexing service.
*Role:* the methodological warning that governs how the two water archetypes are read, and the second half of the nocturnal-warming caveat. The tool is daytime-only and already declares that limitation; these sources sharpen it.

---

## Non-canopy vegetation

**`armson2012`** — Armson, D., Stringer, P., Ennos, A.R. (2012). The effect of tree shade and grass on surface and globe temperatures in an urban area. *Urban Forestry & Urban Greening*, 11(3), 245–255. DOI: [10.1016/j.ufug.2012.05.002](https://doi.org/10.1016/j.ufug.2012.05.002)
*Findings used:* measured on the same plots — grass reduced **maximum surface temperatures by up to 24 °C** and tree shade by up to 19 °C, but **surface composition had little effect upon globe temperatures**, whereas **shading reduced globe temperature by 5–7 °C**. The authors conclude that "grass has little effect upon local air or globe temperatures … whereas tree shade can provide effective local cooling".
*Verified:* Full (University of Manchester Research Explorer record, complete abstract).
*Role:* the decisive source for the `non_canopy_vegetation` archetype, precisely because it measures both metrics on the same plots and so isolates the **surface/air conflation** that inflates most published grass cooling figures. This is why grass-dominated typologies do not inherit tree-canopy values.

**`gill2013`** — Gill, S.E., Rahman, M.A., Handley, J.F., Ennos, A.R. (2013). Modelling water stress to urban amenity grass in Manchester UK under climate change and its potential impacts in reducing urban cooling. *Urban Forestry & Urban Greening*, 12(3), 350–358. DOI: [10.1016/j.ufug.2013.03.005](https://doi.org/10.1016/j.ufug.2013.03.005)
*Finding used:* grass cooling "can be **reduced or lost in summer droughts**, when soils dry out, an effect that is likely to be more pronounced and occur for longer as climate change proceeds".
*Verified:* Metadata + finding (secondary: Crossref record for bibliographic details; abstract via indexing services). Elsevier full text blocked.
*Caveat recorded:* this is a **modelling** study (a bucket soil-moisture model for Greater Manchester, validated by weighing ryegrass turves), not a field measurement of cooling. It is cited for the *direction and mechanism* of drought sensitivity, never for a numeric cooling value.
*Role:* the justification for a genuine **zero floor** on the non-canopy envelope: dry or dormant planting delivers nothing.

**`kraemer2022`** — Kraemer, R., Kabisch, N. (2022). Parks Under Stress: Air Temperature Regulation of Urban Green Spaces Under Conditions of Drought and Summer Heat. *Frontiers in Environmental Science*, 10, 849965. DOI: [10.3389/fenvs.2022.849965](https://doi.org/10.3389/fenvs.2022.849965)
*Findings used:* two structurally distinct inner-city parks in Leipzig, Germany (one tree-dominated, one grass-dominated) measured through the 2018–2019 heat and drought periods. Maximum spatially averaged cooling between green space and built-up surroundings was **1.1 °C, in the morning**; in the afternoon, with peaks near 40 °C, cooling was confined to shaded areas and average differences fell **below 1 °C**. The tree-dominated park was consistently cooler (maximum differences 0.39–1.06 °C); the grass-dominated park was the hottest area during the day and cooled more effectively at night.
*Verified:* Full (open access, Frontiers, read directly).
*Role:* field corroboration under drought stress of the same ordering `armson2012` establishes experimentally — trees over grass by day — and independent support for the drought sensitivity `gill2013` models. **Note:** an earlier draft of the v1.2 review pack cited this source in connection with allotment gardens; it is a **parks** study and is cited as such.

---

## Vegetated shade structures

**`chafer2020`** — Chàfer, M., Pisello, A.L., Piselli, C., Cabeza, L.F. (2020). Greenery System for Cooling Down Outdoor Spaces: Results of an Experimental Study. *Sustainability*, 12(15), 5888. DOI: [10.3390/su12155888](https://doi.org/10.3390/su12155888)
*Finding used (verbatim):* "In clear conditions, for the west oriented pergolas the maximum air temperature difference between the rope system and the greenery was found at 4:00 p.m. on 29 June 2019 during daytime with a difference of **2.5 °C**" (45.3 °C under the bare rope support against 42.9 °C under the greenery). Summer 2019 field experiment in a continental Mediterranean climate (Lleida, Spain), comparing two **identical pergola structures**, one planted and one fitted with support ropes only.
*Verified:* Full (publisher PDF retrieved and read; author list independently confirmed against the Crossref record).
*Caveats recorded, all three material:* (1) the 2.5 °C applies to the **west-oriented** pergolas; the east-oriented sensors showed a markedly smaller difference. (2) A **larger 3.1 °C difference was measured at night**, which this daytime-only tool does not use. (3) The paper's **abstract headlines "up to 5 °C"**, but that figure is greenery against **unshaded** conditions, not against the bare pergola — the like-for-like contrast this methodology needs is the 2.5 °C above, and the distinction is stated here so that a reviewer comparing the abstract with the adopted ceiling does not read an error into it.
*Role:* the only measured study of a vine pergola against an identical bare frame, and therefore the source of the `vegetated_shade_structure` ceiling.

**`ouyang2024`** — Ouyang, W., Ren, G., Tan, Z., Li, Y., Ren, C. (2024). Natural shading vs. artificial shading: A comparative analysis of their cooling efficacy in extreme hot weather. *Urban Climate*, 55, 101870. DOI: [10.1016/j.uclim.2024.101870](https://doi.org/10.1016/j.uclim.2024.101870)
*Findings used:* field measurements on extremely hot days in Hong Kong, comparing covered walkways against tree canopies. **Air temperature reduction 1.42 °C (natural) against 1.31 °C (artificial)**; **mean radiant temperature reduction 15.93 °C (natural) against 13.71 °C (artificial)**; PET reduction 9.06 °C against 9.70 °C.
*Verified:* Metadata + finding (secondary: Crossref and NASA ADS for bibliographic details; the quantitative findings from two independent renderings of the publisher abstract). ScienceDirect blocked.
*Role:* the source that separates the two axes for shade structures — an **order-of-magnitude difference between the comfort benefit and the air-temperature benefit** — and therefore the reason a shade structure's *air temperature* envelope is modest even though its comfort effect is large.

**`colter2019`** — Colter, K.R., Middel, A.C., Martin, C.A. (2019). Effects of natural and artificial shade on human thermal comfort in residential neighborhood parks of Phoenix, Arizona, USA. *Urban Forestry & Urban Greening*, 44, 126429. DOI: [10.1016/j.ufug.2019.126429](https://doi.org/10.1016/j.ufug.2019.126429)
*Finding used (verbatim):* "The difference in PET between full sun and under shade canopies of *Fraxinus* and *Quercus* trees was greater than under shade canopies of *Parkinsonia*, *Prosopis*, trees **or constructed ramadas** by 2.9 to 4.3 °C." Trees and ramadas together attenuated 88–97% of full sunlight, yet the ramadas did not deliver correspondingly greater thermal relief.
*Verified:* Full (Arizona State University Elsevier Pure record, complete abstract).
*Caveats recorded:* PET is a comfort index, not air temperature, and is used here only for the **ordering** it establishes. Conditions are narrow — hot summer midday, desert climate, six tree taxa.
*Role:* establishes that **sparse or open canopies group with solid artificial shade** rather than with dense canopy, which is what bounds the productive-canopy archetype below dense canopy and keeps the shade-structure archetype's confidence low.

---

## Productive landscapes and irrigation

**`rost2020`** — Rost, A.T., Liste, V., Seidel, C., Matscheroth, L., Otto, M., Meier, F., Fenner, D. (2020). How Cool Are Allotment Gardens? A Case Study of Nocturnal Air Temperature Differences in Berlin, Germany. *Atmosphere*, 11(5), 500. DOI: [10.3390/atmos11050500](https://doi.org/10.3390/atmos11050500)
*Finding used:* 13 allotment garden complexes measured in summer 2018 against densely built-up areas, two large inner-city parks, and rural areas. The complexes were on average **2.7 K cooler at night** than the urban reference.
*Verified:* Full (publisher-deposited abstract retrieved verbatim).
*Critical caveat applied by this methodology:* the study is **nocturnal only** — the restriction is in its title, abstract and design. This tool reports **daytime** air temperature, so `rost2020` **cannot** support a daytime cooling value and is not used for one. It is cited as evidence of what the productive-landscape literature does and does not measure.
*Role:* the best available allotment-garden measurement, and the demonstration that even it does not answer the question this tool asks.

**`cheung2022`** — Cheung, P.K., Nice, K.A., Livesley, S.J. (2022). Irrigating urban green space for cooling benefits: the mechanisms and management considerations. *Environmental Research: Climate*, 1(1), 015001. DOI: [10.1088/2752-5295/ac6e7c](https://doi.org/10.1088/2752-5295/ac6e7c)
*Findings used:* measured cooling in agricultural fields was **−0.43 °C (maize) and −0.09 °C (soybean)**, against **modelled** reductions in daily maximum air temperature of **2.1–2.5 °C**. Irrigation increases daytime soil heat storage which "would release at night", and the paper predicts an **increase in the daily minimum air temperature** as a result.
*Verified:* Full (open access, IOPscience, read directly).
*Caveat recorded, and it matters:* the measured-against-modelled gap above is specific to the **agricultural field** studies. The same paper reports measured irrigation cooling of **−2 °C to −1 °C in two urban parks in Melbourne**, much closer to the modelled values. The methodology therefore does not claim that models overstate irrigation cooling in general.
*Role:* the basis for treating irrigation as **sustaining** an entry's position within its envelope through drought, never as raising the envelope — and the source of the night-warming caveat on irrigated productive landscapes.

---

## Buildings, roofs, and façades

**`santamouris2014`** — Santamouris, M. (2014). Cooling the cities – A review of reflective and green roof mitigation technologies to fight heat island and improve comfort in urban environments. *Solar Energy*, 103, 682–703. DOI: [10.1016/j.solener.2012.07.003](https://doi.org/10.1016/j.solener.2012.07.003)
*Finding used (abstract, verbatim source):* "As it concerns green roofs, existing simulation studies show that when applied on a **city scale**, they may reduce the average urban ambient temperature between **0.3 and 3 K**." Also: a 0.1 rise in urban albedo corresponds to roughly 0.3 K average ambient decrease.
*Verified:* Full (open PDF via EEA Climate-ADAPT; abstract read directly).
*Critical caveat applied by this methodology:* the 0.3–3 K figure describes **city-scale mass deployment in simulation studies**, not the effect of one green roof on one building. It is therefore **not** used as a site-level typology value.

---

## Energy and emissions

**`akbari2001`** — Akbari, H., Pomerantz, M., Taha, H. (2001). Cool surfaces and shade trees to reduce energy use and improve air quality in urban areas. *Solar Energy*, 70(3), 295–310. DOI: [10.1016/S0038-092X(00)00089-X](https://doi.org/10.1016/S0038-092X\(00\)00089-X)
*Findings used:* urban **electricity demand increases by 2–4% for each 1 °C** of temperature increase; an estimated 5–10% of urban electricity demand serves to compensate for the 0.5–3.0 °C urban temperature elevation.
*Verified:* Metadata + finding (secondary: multiple indexing records; LBNL institutional listing).
*Role:* the basis for **deriving** cooling-energy savings from estimated air-temperature reduction, replacing unsourced per-typology energy factors.

**`ember`** — Ember (2026). *Yearly Electricity Data* / *Electricity Data Explorer*. Ember Energy. <https://ember-energy.org/data/yearly-electricity-data/>
*Use:* country-level electricity carbon intensity (gCO₂/kWh) for GHG conversion. Coverage of 215 countries; released under **CC-BY-4.0**, which permits redistribution inside an Apache-2.0 tool with attribution.
*Verified:* Full (licence and coverage confirmed on Ember's data pages).

---

## Blue and blue-green infrastructure

**`gunawardena2017`** — Gunawardena, K.R., Wells, M.J., Kershaw, T. (2017). Utilising green and bluespace to mitigate urban heat island intensity. *Science of the Total Environment*, 584–585, 1040–1055. DOI: [10.1016/j.scitotenv.2017.01.158](https://doi.org/10.1016/j.scitotenv.2017.01.158)
*Findings used:* **tree-dominated greenspace offers greater heat-stress relief** when most required; **poorly designed bluespace may exacerbate heat stress** under oppressive (humid) conditions; combined green and blue features offer synergistic benefits.
*Verified:* Metadata (TU Delft / Bath research portals) + findings (secondary: publisher abstract description). Elsevier full text blocked.
*Role:* justifies the humidity caveat applied to blue typologies in tropical-wet climates.

---

## Vulnerability and heat-health risk

**`reid2009`** — Reid, C.E., O'Neill, M.S., Gronlund, C.J., Brines, S.J., Brown, D.G., Diez-Roux, A.V., Schwartz, J. (2009). Mapping community determinants of heat vulnerability. *Environmental Health Perspectives*, 117(11), 1730–1736. DOI: [10.1289/ehp.0900683](https://doi.org/10.1289/ehp.0900683)
*Findings used:* ten vulnerability variables (six demographic, two household air-conditioning, vegetation cover, diabetes prevalence) reduce to **four factors explaining >75% of variance**: social/environmental vulnerability (education/poverty/race/green space), social isolation, **air-conditioning prevalence**, and elderly/diabetes proportion. Inner-city areas showed highest vulnerability.
*Verified:* Full (PMC open access record, PMC2801183).
*Role:* grounds the vulnerability sub-indicators, and specifically the treatment of **low access to cooled space as elevated vulnerability** as an independent dimension. Within the cooling access deficit dimension it grounds the **indoor** indicator (D-039).

**`burkart2016`** — Burkart, K., Meier, F., Schneider, A., Breitner, S., Canário, P., Alcoforado, M.J., Scherer, D., Endlicher, W. (2016). Modification of heat-related mortality in an elderly urban population by vegetation (urban green) and proximity to water (urban blue): evidence from Lisbon, Portugal. *Environmental Health Perspectives*, 124(7), 927–934. DOI: [10.1289/ehp.1409529](https://doi.org/10.1289/ehp.1409529)
*Findings used:* above the 99th temperature percentile (24.8 °C), mortality in the over-65 population rose **14.7% per °C in the least-vegetated areas against 3.0% in the most vegetated**, and **7.1% per °C beyond 4 km from water against 2.1% within 4 km**. Lisbon, 1998–2008.
*Verified:* Metadata (PubMed record, PMID 26566198; EHP open access) + findings (publisher abstract).
*Role:* grounds the **outdoor** indicator of the cooling access deficit dimension (D-039) — access to reachable shaded green or blue space as an evidenced protective factor, quantified separately from air conditioning.

**`sera2019`** — Sera, F., Armstrong, B., Tobias, A., Vicedo-Cabrera, A.M., Åström, C., Bell, M.L., Chen, B.-Y., et al. (2019). How urban characteristics affect vulnerability to heat and cold: a multi-country analysis. *International Journal of Epidemiology*, 48(4), 1101–1112. DOI: [10.1093/ije/dyz008](https://doi.org/10.1093/ije/dyz008)
*Findings used:* across **340 cities in 22 countries**, higher levels of **green space were associated with a decreased effect of heat** on mortality, while higher population density, PM2.5, GDP, and income inequality were associated with an increased effect. Heat-related deaths amounted to 0.54% (95% CI 0.49–0.58) of total deaths.
*Verified:* Metadata (PubMed record, PMID 30815699) + findings (publisher abstract).
*Role:* corroborates `burkart2016` at multi-country scale for the outdoor cooling-refuge indicator, and independently supports population density as a vulnerability indicator.

---

## Remote sensing as a heat proxy

**`venter2021`** — Venter, Z.S., Chakraborty, T., Lee, X. (2021). Crowdsourced air temperatures contrast satellite measures of the urban heat island and its mechanisms. *Science Advances*, 7(22), eabb9569. DOI: [10.1126/sciadv.abb9569](https://doi.org/10.1126/sciadv.abb9569)
*Finding used:* satellite-derived **surface** UHI substantially exceeds air-temperature (canopy-layer) UHI — reported mean SUHI **1.45 °C** vs CUHI **0.26 °C**, an approximately **sixfold overestimate**.
*Verified:* Metadata (ADS record; author-hosted PDF) + finding (secondary: indexed description). Publisher full text blocked.
*Role:* the basis for treating land-surface-temperature anomaly as a **relative screening proxy only**, never as an air-temperature prediction.

**`oke1976`** — Oke, T.R. (1976). The distinction between canopy and boundary-layer urban heat islands. *Atmosphere*, 14(4), 268–277. DOI: [10.1080/00046973.1976.9648422](https://doi.org/10.1080/00046973.1976.9648422)
*Use:* the foundational distinction between canopy-layer, boundary-layer, and surface urban heat islands.
*Verified:* Metadata only (widely indexed; cited in this methodology for the conceptual distinction, not for a numeric value).

---

## Prioritisation frameworks and indicator methodology

**`norton2015`** — Norton, B.A., Coutts, A.M., Livesley, S.J., Harris, R.J., Hunter, A.M., Williams, N.S.G. (2015). Planning for cooler cities: A framework to prioritise green infrastructure to mitigate high temperatures in urban landscapes. *Landscape and Urban Planning*, 134, 127–138. DOI: [10.1016/j.landurbplan.2014.10.018](https://doi.org/10.1016/j.landurbplan.2014.10.018)
*Use:* the closest published antecedent to this tool — a framework for prioritising and selecting urban green infrastructure for cooling, based on a review of relationships between urban geometry, green infrastructure, and temperature.
*Verified:* Metadata (Monash University research portal) + framework description (secondary).

**`nardo2008`** — Nardo, M., Saisana, M., Saltelli, A., Tarantola, S., Hoffmann, A., Giovannini, E. (2008). *Handbook on Constructing Composite Indicators: Methodology and User Guide*. OECD Publishing / European Commission JRC. ISBN 978-92-64-04345-9. <https://publications.jrc.ec.europa.eu/repository/handle/JRC47008>
*Use:* the standard reference for composite-indicator construction — theoretical framework, variable selection, missing-data treatment, normalisation, weighting and aggregation, and presentation. This methodology follows its sequence and its expectation that composite indicators be accompanied by uncertainty/sensitivity analysis.
*Verified:* Full bibliographic record (JRC repository); step sequence confirmed from OECD/JRC descriptions.

---

## Costs

**`worldbank2021`** — World Bank (2021). *A Catalogue of Nature-based Solutions for Urban Resilience*. Washington, D.C.: World Bank Group (Global Program on Nature-based Solutions & City Resilience Program). <https://documents.worldbank.org/en/publication/documents-reports/documentdetail/502101636360985715/>
*Findings used:* defines **14 NbS families** for urban resilience; states that **NbS project costs vary significantly and are highly site- and project-specific**, that unit costs differ sharply between developed and developing contexts (illustrated by dredging at US$2/m³ in Bangladesh vs US$59/m³ in the UK), and that urban implementation costs typically exceed rural ones.
*Verified:* Full (World Bank plain-text document retrieved directly).
*Role:* the documented justification for **not shipping global default unit costs** in v1 — see the cost policy in [METHODOLOGY.md](METHODOLOGY.md).
