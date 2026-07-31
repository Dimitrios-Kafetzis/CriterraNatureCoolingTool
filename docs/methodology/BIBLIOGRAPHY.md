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
