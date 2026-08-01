/**
 * The externalised message catalog (UX specification §9, D-030).
 *
 * Every user-facing string in the application lives here so that translation
 * never requires a code change. Strings that *state a result* — scores,
 * categories, confidence levels, recommendation text, warning texts,
 * assumption texts — are NOT here: they arrive from the API and are rendered
 * verbatim (PHASE-4-BRIEF rule 2). This catalog holds interface language
 * only: labels, actions, explanations, and display names for enum values the
 * API returns.
 */

export const messages = {
  app: {
    title: 'Nature for Cooling',
    subtitle: 'Rapid Assessment Tool',
    byCriterra: 'by Criterra',
    homeLink: 'Nature for Cooling — Rapid Assessment Tool, by Criterra',
    criterraLogoAlt: 'Criterra',
    nav: {
      projects: 'Projects',
      methodology: 'Methodology',
    },
    footer: {
      license: 'Apache-2.0 · open methodology',
      engine: 'Engine',
      methodologyVersion: 'Methodology',
      copyright: (year: number) => `© ${year} Criterra`,
      product: 'Nature for Cooling is a Criterra product.',
      site: 'criterra.eu',
      siteUrl: 'https://criterra.eu',
    },
    loading: 'Loading…',
    apiError: 'The assessment service could not be reached. Is the API running?',
    notFound: 'This page does not exist.',
  },

  entry: {
    heading: 'Evaluate nature-based solutions for urban cooling',
    what: 'This tool turns a structured description of a site and one or more proposed nature-based interventions — chosen from 110 typologies, from a single tree pit to a district-wide cooling network — into transparent, literature-grounded scores: a Heat Priority Index, a cooling opportunity score with an indicative temperature-reduction range, and energy, cost, equity, and co-benefit estimates.',
    whatItAsks:
      'It asks about 45 questions across six short steps: the site, its climate and heat exposure, who uses it, the intervention, and (optionally) cost and energy figures. Around 20 are required; a complete pass takes 15–25 minutes.',
    partialAnswers:
      'Partial answers are fine. Every optional question can be skipped in one click, and a live confidence meter shows exactly what each skipped answer costs — the assessment never blocks on missing data, and the tool never pretends to know something you did not tell it.',
    startNew: 'Start a new assessment',
    openSaved: 'Open a saved project',
    methodologyLink: 'How the numbers are produced — the methodology',
    newProjectName: 'Project name',
    newProjectHelp:
      'A name for the site or study you are assessing, e.g. “Riverside school quarter”.',
    create: 'Create project',
    creating: 'Creating…',
  },

  projects: {
    heading: 'Saved projects',
    empty: 'No saved projects yet. Assessments save automatically as you answer.',
    open: 'Open',
    delete: 'Delete',
    deleteConfirm: 'Delete this project and all its assessments? This cannot be undone.',
    updated: 'Updated',
    assessmentCount: (n: number) => (n === 1 ? '1 assessment' : `${n} assessments`),
    backToEntry: 'Back to start',
  },

  project: {
    assessments: 'Assessments',
    newAssessment: 'New assessment',
    defaultFirstLabel: 'Option A',
    draft: 'Draft',
    evaluated: 'Evaluated',
    methodologyUpdate: 'Newer methodology available — re-running creates a new assessment',
    continueDraft: 'Continue',
    viewResults: 'Results',
    duplicate: 'Compare another option',
    deleteAssessment: 'Delete',
    deleteAssessmentConfirm: 'Delete this assessment? This cannot be undone.',
    compare: 'Compare options',
    compareHint: 'Evaluate at least two options of this project to compare them side by side.',
    renamePrompt: 'New label for this assessment:',
    empty: 'No assessments yet.',
    createdAt: 'Created',
    /**
     * D-029 forbids silent migration, so a project reshaped on read says so
     * (D-044.2). The notes themselves are the service's own text.
     */
    migratedHeading: 'This project was updated to the current storage format',
    migratedIntro:
      'Your saved answers were reshaped when this project was opened. Every change is listed below; nothing else was altered, and stored results were not touched.',
  },

  wizard: {
    stepLabel: (n: number, total: number) => `Step ${n} of ${total}`,
    back: 'Back',
    continue: 'Continue',
    runAssessment: 'Run assessment',
    running: 'Running…',
    saved: 'Saved',
    saving: 'Saving…',
    saveFailed: 'Auto-save failed — check that the API is running',
    blockedByErrors: 'Fix the errors in this step to continue.',
    stepHasErrors: (step: string) => `Step “${step}” has errors.`,
    optionalHint: 'Optional — leave blank to skip.',
    unknownOption: 'Unknown / not sure',
    explain: {
      open: (field: string) => `What does “${field}” mean?`,
      close: 'Close',
      whatHeading: 'What this means',
      affectsHeading: 'What it affects',
      methodologyLink: 'Read the full methodology',
    },
    unansweredOption: '(not answered)',
    warningsHeading: 'Warnings',
    warningsNeverBlock: 'Warnings never block the assessment; they are recorded with the result.',
    evaluateInvalid: 'Some answers are missing or invalid. The steps concerned are marked above.',
    frozenNotice:
      'This assessment has been evaluated, so its answers are frozen. Duplicate it to explore a change.',
    steps: {
      project: {
        title: 'Project information',
        intro: 'Who and where this assessment is for. The shortest step.',
      },
      site: {
        title: 'Site characteristics',
        intro: 'The heaviest step: the physical description of the site as it is today.',
      },
      climate: {
        title: 'Climate and heat exposure',
        intro: 'The climate zone is required; measured values are optional and raise confidence.',
      },
      vulnerability: {
        title: 'Vulnerability and equity',
        intro: 'Who uses this place, and how exposed they are. All optional.',
      },
      intervention: {
        title: 'NbS intervention',
        intro:
          'Choose the intervention, or several to assess as a package. Cards are grouped by family, ordered and annotated by fit to the site you have described — an unsuitable option stays selectable, and its flag follows into the results.',
      },
      cost: {
        title: 'Cost and energy',
        intro:
          'Entirely optional. Without figures the tool reports costs as “not estimated” — it ships no default cost values.',
      },
    },
  },

  confidence: {
    heading: 'Confidence',
    intro: 'Live, per output block. Skipping is free — this shows what it costs.',
    blocks: {
      cooling: 'Cooling',
      energy: 'Energy',
      economic: 'Economic',
      equity: 'Equity',
    },
    overall: 'Overall',
    completeness: (pct: number) => `${Math.round(pct)}% of inputs supplied`,
    hintRaises: (fields: string, level: string) => `Adding ${fields} would raise this to ${level}`,
    hintNext: (fields: string) => `Most useful next: ${fields}`,
    hintOr: ' or ',
    stepRef: (step: string) => ` (step: ${step})`,
    evidenceCap:
      'Cooling confidence is capped at Medium because published evidence for this typology is limited. Complete inputs cannot compensate for thin evidence.',
  },

  /**
   * Every questionnaire parameter (D-041).
   *
   * `help` is the one line rendered under the label; it is omitted where the
   * explanation belongs in the popover instead, so the default view of the
   * form stays short. `what` says what the parameter means in plain language,
   * `affects` says what it changes in the scoring. Both are stated in the same
   * language the Methodology Report uses so the two cannot drift.
   */
  fields: {
    project_name: {
      label: 'Project name',
      help: 'Shown on the report.',
      what: 'A name for the site or study being assessed. It identifies the assessment on screen and on the exported report.',
      affects: 'Nothing in the scoring — it is a label only.',
    },
    assessment_scale: {
      label: 'Assessment scale',
      what: 'The spatial scale this assessment describes, from a whole city down to a single building. Choose the scale at which the decision will actually be taken.',
      affects:
        'Nothing directly in the formulas today; it is recorded with the result and frames how the outputs should be read — a city-scale answer is not a statement about any one street.',
    },
    country: {
      label: 'Country code',
      help: 'ISO code, e.g. “GR” or “BRA”.',
      what: 'The two- or three-letter ISO code of the country the site is in.',
      affects:
        'Lets the tool fall back to published country defaults for the electricity grid emission factor where you do not supply one. It never overrides a figure you enter.',
    },
    site_area_m2: {
      label: 'Site area',
      unit: 'm²',
      what: 'The total ground area of the site being assessed — the whole area under consideration, not only the part you intend to plant.',
      affects:
        'Compared against each typology’s minimum viable area to produce the suitability space sub-score, and used with the intervention area to derive the scale condition of the site adjustment factor. A site below a typology’s minimum raises a “not suitable” flag.',
    },
    existing_tree_canopy_percent: {
      label: 'Existing tree canopy',
      unit: '%',
      what: 'The share of the site that already sits under tree canopy when viewed from above, today.',
      affects:
        'Drives the canopy condition of the site adjustment factor: a site with little existing canopy has more to gain from new planting, so it scores a higher adjustment than an already shaded site. It also feeds the vegetation-deficit part of the Heat Exposure Score.',
    },
    existing_green_cover_percent: {
      label: 'Existing green cover',
      unit: '%',
      what: 'The share of the site that is vegetated in any form — grass, shrubs, beds, and tree canopy together. Always at least as large as the canopy figure.',
      affects:
        'The vegetation-deficit component of the Heat Exposure Score, and cooling-block confidence.',
    },
    impervious_surface_percent: {
      label: 'Impervious surface',
      unit: '%',
      what: 'The share of the site sealed by asphalt, concrete, paving, or roofs — surfaces water cannot pass through.',
      affects:
        'A direct component of the Heat Exposure Score. Sealed surfaces store and re-radiate heat: ziter2019 found impervious cover raises air temperature roughly linearly, with the effect persisting into the night.',
    },
    soil_availability: {
      label: 'Soil availability',
      what: 'How much plantable, unsealed soil of usable depth the site offers — not how fertile it is, but how much of it there is to plant into.',
      affects:
        'Matched against each typology’s soil requirement for the suitability soil sub-score, and combined with irrigation into the soil-and-water condition of the site adjustment factor. Falling below a typology’s requirement raises a “not suitable” flag.',
    },
    irrigation_availability: {
      label: 'Irrigation availability',
      what: 'How reliably the planting can be watered once established — “reliable” means a guaranteed supply through a drought summer, not merely a nearby tap.',
      affects:
        'The suitability water sub-score and the soil-and-water condition of the site adjustment. Water availability governs evapotranspiration, which is one of the two mechanisms by which vegetation cools.',
    },
    current_shade_level: {
      label: 'Current shade level',
      what: 'How shaded the site is at the hottest part of a summer day today, from any source — trees, buildings, or structures.',
      affects:
        'Counts toward cooling-block confidence as part of describing the site’s cooling context. It does not enter a scoring formula in this version; this is stated openly rather than implied.',
    },
    land_use: {
      label: 'Land use',
      what: 'The dominant use of the site: a street corridor, a residential block, a school or campus, a park, a memorial landscape, and so on.',
      affects:
        'Compared against each typology’s documented use contexts to produce the urban-context sub-score of suitability. Being outside a typology’s usual context is a caution, never a disqualification — the context lists are typical, not exhaustive. It also selects which interventions are offered for this site.',
    },
    // The four availability questions (D-044.1). Each `affects` says plainly
    // that the answer changes which interventions are offered and enters no
    // formula — the same openness D-031 applied to `current_shade_level`.
    includes_railway: {
      label: 'Does the site include a railway or tram corridor?',
      what: 'Whether an active or disused railway line, tram track, or their immediate verges fall inside the site.',
      affects:
        'Only which interventions are offered: it unlocks the green tram corridor and railway green corridor typologies, which need a track to sit alongside. It feeds no score. Your answer cannot raise or lower any result.',
    },
    existing_woodland: {
      label: 'Is there existing woodland or forest on the site?',
      what: 'Whether the site already carries woodland or forest — a stand of established trees with a woodland structure, not scattered street trees.',
      affects:
        'Only which interventions are offered: woodland *restoration* types need existing woodland to restore. Woodland *creation* types — microforest, Miyawaki planting, afforestation — are offered either way, subject to area. It feeds no score.',
    },
    waterfront_type: {
      label: 'Waterfront type',
      what: 'The kind of water body the site adjoins, if any: a lake, an open river, a dry river bed, a river culverted beneath the site, or the sea. Leave unanswered if the site has no water body.',
      affects:
        'Only which interventions are offered, and which ones: a covered river offers stream daylighting; an open river offers river restoration, riparian buffers, and floodplain restoration; a lake offers lake restoration and floating wetlands; the sea offers living shorelines and coastal parks. Constructed water features — wetlands, retention ponds, water squares — are offered regardless, because they need no existing water body. It feeds no score.',
    },
    productive_governance: {
      label: 'Who could deliver a productive landscape here?',
      help: 'Select every party that could plausibly run it, or leave it blank to see them all.',
      what: 'Which parties could realistically deliver and run food-growing on this site: a community group, individual residents, an institution such as a school or hospital, or a commercial operator. This asks who can deliver, not who is interested.',
      affects:
        'Only which productive-landscape interventions are offered — a community garden needs a community, an urban farm needs a commercial or institutional operator. Leaving it blank hides nothing: an unanswered question is not evidence that no one could deliver, so every productive option stays on offer until you narrow it. It feeds no score.',
    },
    climate_zone: {
      label: 'Climate zone',
      what: 'The broad climate the site sits in — tropical wet, tropical dry, arid, semi-arid, or temperate.',
      affects:
        'The climate condition of the site adjustment factor, and the hard climate-suitability flags. This matters more than it might appear: keravec2026 found that adding climate subzone raised the variance explained in NbS cooling effectiveness from 12% to 78%.',
    },
    lst_anomaly_c: {
      label: 'Land surface temperature anomaly',
      unit: '°C',
      what: 'How much hotter this site’s land surface runs than the average for the city, in °C, measured from satellite thermal imagery. A value of +4 °C means the surface here reads four degrees above the city mean. Municipal heat maps and Landsat or Sentinel derivatives are the usual sources; leave it blank if you have none.',
      affects:
        'The strongest single component of the Heat Exposure Score, and it switches the assessment onto the measured (data-rich) path. Important caveat: this is a *surface* temperature, which venter2021 shows runs far above air temperature — roughly sixfold. The tool therefore uses it only to rank which parts of a city are hotter, never as a predicted air temperature, and never converts it into a °C result.',
    },
    heat_exposure_level: {
      label: 'Heat exposure level',
      what: 'Your qualitative reading of how hot this site runs compared with the rest of the city.',
      affects:
        'Used in place of the measured anomaly when you have no satellite figure, putting the assessment on the qualitative (data-poor) path. Supplying either one completes the same confidence slot.',
    },
    solar_exposure: {
      label: 'Solar exposure',
      what: 'How much direct sun reaches the site through a summer day, given surrounding buildings and existing shade.',
      affects: 'A component of the Heat Exposure Score on the measured path.',
    },
    population_density: {
      label: 'Population density',
      what: 'How densely populated the surroundings are — how many people are actually exposed to the heat at this location.',
      affects:
        'The largest component of the Vulnerability Score, alongside vulnerable-group presence. sera2019 found higher population density associated with a greater mortality effect of heat across 340 cities.',
    },
    vulnerable_population_presence: {
      label: 'Vulnerable population presence',
      what: 'How present heat-vulnerable groups are at this place: young children, people over 65, those with chronic illness, outdoor workers, or people without secure housing.',
      affects:
        'A principal component of the Vulnerability Score and the largest sub-indicator of the Equity Score. Because vulnerability enters the headline score twice by design, this is one of the most influential answers in the questionnaire.',
    },
    access_to_cooled_indoor_space: {
      label: 'Access to cooled indoor space',
      what: 'How easily the people who use this place can reach an air-conditioned or otherwise actively cooled indoor space — a home with cooling, a workplace, a library or mall acting as a refuge.',
      affects:
        'One of the two indicators of the cooling-refuge access dimension of the Vulnerability Score. The scale is inverted: *low* access means *higher* vulnerability. reid2009 found air-conditioning prevalence to be an independent dimension of heat vulnerability.',
    },
    access_to_cool_outdoor_refuge: {
      label: 'Access to cool outdoor refuge',
      what: 'How easily the people who use this place can reach cool outdoor space — a shaded park, a tree-lined street, a river or waterfront — within a short walk. This is about the surroundings, not about the site itself.',
      affects:
        'The second indicator of the cooling-refuge access dimension, inverted like its indoor counterpart. burkart2016 measured the effect directly in Lisbon: above the 99th temperature percentile, deaths among over-65s rose 14.7% per °C in the least green areas against 3.0% in the greenest, and 7.1% per °C beyond 4 km from water against 2.1% within it. Answering either indicator completes the same confidence slot; answering both averages them.',
    },
    safety_concern: {
      label: 'Safety and comfort concern',
      what: 'How significant the safety or comfort problems of this place are today — whether people avoid it, feel unsafe, or simply cannot stay in it comfortably in hot weather.',
      affects:
        'A sub-indicator of the Equity Score. Read as a deficit: a place with greater problems has more to gain from a well-designed intervention.',
    },
    public_accessibility: {
      label: 'Public accessibility',
      what: 'How freely the general public can enter and use the site — open at all hours, restricted to certain users, or effectively private.',
      affects:
        'A sub-indicator of the Equity Score. The Equity Score is reported with its own confidence and deliberately does not enter the headline score; equity reaches the headline through vulnerability instead.',
    },
    community_participation: {
      label: 'Community participation',
      what: 'How involved local residents and users are in shaping what happens to this place.',
      affects: 'A sub-indicator of the Equity Score.',
    },
    nbs_type: {
      label: 'Intervention typology',
      what: 'The nature-based intervention, or package of interventions, being assessed. Each entry inherits a cited cooling envelope from one evidence class, along with suitability conditions and co-benefit defaults.',
      affects:
        'Everything downstream: the cooling envelope, the suitability conditions checked against your site, the co-benefit defaults, and whether building-energy savings can be derived at all. Where you select several, each is scored and reported separately, and the package’s headline temperature estimate is capped at the best-evidenced component rather than summed.',
    },
    intervention_area_m2: {
      label: 'Intervention area',
      unit: 'm²',
      what: 'The area the intervention itself will occupy, which is normally smaller than the site.',
      affects: 'The scale condition of the site adjustment factor, via its ratio to the site area.',
    },
    new_canopy_area_at_maturity_m2: {
      label: 'New canopy area at maturity',
      unit: 'm²',
      what: 'The additional tree canopy the intervention will cast once fully grown, measured as ground area shaded from above.',
      affects:
        'The canopy condition of the site adjustment factor, and the derived shade-potential output. Without it, shade potential is reported as not estimated rather than guessed.',
    },
    expected_maturity_period_years: {
      label: 'Expected maturity period',
      unit: 'years',
      what: 'How many years until the intervention delivers its full effect — near zero for a shade structure with climbers, a decade or more for forest planting.',
      affects:
        'The time-to-benefit class reported with the result. No discount is applied to the cooling values; instead the delay is stated openly, so a slow-maturing intervention is never presented as cooling the site immediately.',
    },
    implementation_complexity: {
      label: 'Implementation complexity',
      what: 'How demanding the intervention is to deliver: permits, utilities, ground works, disruption, and coordination.',
      affects:
        'The derived cost-feasibility score and investment readiness. The scale is inverted — *low* complexity is favourable and raises feasibility.',
    },
    maintenance_intensity: {
      label: 'Maintenance intensity',
      what: 'How demanding the intervention is to keep alive and functioning, year after year, once built.',
      affects:
        'Both the suitability maintenance sub-score and cost feasibility, inverted in each — low maintenance is favourable. High ongoing demand is a well-documented failure mode for urban greening, so it lowers suitability without disqualifying.',
    },
    co_benefit_biodiversity: {
      label: 'Biodiversity',
      what: 'Override the library’s cited default for this typology’s biodiversity benefit, if you know this site differs.',
      affects:
        'The biodiversity sub-score of the Co-benefit Score. Leave blank to use the cited default.',
    },
    co_benefit_stormwater: {
      label: 'Stormwater',
      what: 'Override the library’s cited default for this typology’s stormwater benefit.',
      affects:
        'The stormwater sub-score of the Co-benefit Score. Leave blank to use the cited default.',
    },
    co_benefit_public_health: {
      label: 'Public health',
      what: 'Override the library’s cited default for this typology’s public-health benefit.',
      affects:
        'The public-health sub-score of the Co-benefit Score. Leave blank to use the cited default.',
    },
    co_benefit_social_inclusion: {
      label: 'Social inclusion',
      what: 'Override the library’s cited default for this typology’s social-inclusion benefit.',
      affects:
        'The social-inclusion sub-score of the Co-benefit Score. Leave blank to use the cited default.',
    },
    co_benefit_urban_quality: {
      label: 'Urban quality',
      what: 'Override the library’s cited default for this typology’s urban-quality benefit.',
      affects:
        'The urban-quality sub-score of the Co-benefit Score. Leave blank to use the cited default.',
    },
    nearby_building_cooling_demand_relevant: {
      label: 'Is nearby building cooling demand relevant?',
      what: 'Whether buildings close enough to benefit from this intervention actually use active cooling that it could reduce. Answer no for an intervention with no conditioned buildings nearby.',
      affects:
        'Gates the entire energy and greenhouse-gas block. Answering no reports those outputs as not applicable rather than as zero.',
    },
    annual_cooling_energy_demand_kwh: {
      label: 'Annual cooling energy demand',
      unit: 'kWh/year',
      what: 'The yearly electricity used for cooling by the relevant nearby buildings, from meter readings or an energy audit.',
      affects:
        'The basis of the energy-saving estimate, which is derived as demand × temperature reduction × a sensitivity of 2–4% per °C from akbari2001 — not from a stored per-typology saving factor.',
    },
    energy_price_per_kwh: {
      label: 'Energy price',
      help: 'In the currency below.',
      unit: 'per kWh',
      what: 'What a kilowatt-hour of electricity costs at this site, in the currency selected below.',
      affects:
        'Converts the energy saving into an annual cost saving, and through it the payback period.',
    },
    capital_cost: {
      label: 'Capital cost',
      what: 'Your estimate of what the intervention will cost to build.',
      affects:
        'The payback period, the derived cost-feasibility score, and investment readiness. The tool ships no default cost values: worldbank2021 documents order-of-magnitude cost variation between contexts, so an invented default would generate the most decision-relevant output from a fabricated input.',
    },
    currency: {
      label: 'Currency',
      help: 'Three-letter code, e.g. EUR.',
      what: 'The currency your cost and energy-price figures are expressed in.',
      affects: 'Labels the economic outputs. The tool performs no currency conversion.',
    },
    grid_emission_factor_kgco2e_per_kwh: {
      label: 'Grid emission factor',
      help: 'Leave blank to use the country default where available.',
      unit: 'kgCO₂e/kWh',
      what: 'The greenhouse gas emitted per kilowatt-hour of electricity on the local grid.',
      affects:
        'Converts the energy saving into emissions avoided. Left blank, the country default is used where one exists, and the result states which of the two was applied.',
    },
  } as Record<
    string,
    { label: string; help?: string; unit?: string; what: string; affects: string }
  >,

  options: {
    assessment_scale: {
      city: 'City',
      district: 'District',
      neighbourhood: 'Neighbourhood',
      site: 'Site',
      building: 'Building',
    },
    climate_zone: {
      tropical_wet: 'Tropical wet',
      tropical_dry: 'Tropical dry',
      arid: 'Arid',
      semi_arid: 'Semi-arid',
      temperate: 'Temperate',
      other: 'Other',
    },
    land_use: {
      street_corridor: 'Street corridor',
      residential: 'Residential',
      mixed_use: 'Mixed use',
      commercial: 'Commercial',
      public_space: 'Public space',
      park: 'Park',
      school: 'School',
      campus: 'Campus',
      healthcare: 'Healthcare',
      memorial: 'Memorial',
      industrial: 'Industrial',
      other: 'Other',
    },
    waterfront_type: {
      lake: 'Lake',
      river: 'River',
      dry_river: 'Dry river bed',
      covered_river: 'Covered river (culverted)',
      sea: 'Sea',
    },
    productive_governance: {
      community: 'A community group',
      individual: 'Individual residents',
      institutional: 'An institution (school, hospital, campus)',
      commercial: 'A commercial operator',
    },
    levels: {
      none: 'None',
      very_low: 'Very low',
      limited: 'Limited',
      occasional: 'Occasional',
      moderate: 'Moderate',
      low: 'Low',
      medium: 'Medium',
      high: 'High',
      very_high: 'Very high',
      reliable: 'Reliable',
      yes: 'Yes',
      no: 'No',
      unknown: 'Unknown / not sure',
    } as Record<string, string>,
  },

  /**
   * The catalogue's fourteen families (D-043): five element families — the
   * discrete things you build — then the composite families, each a coherent
   * spatial system made of elements. The order below is the order the picker
   * renders, elements first.
   */
  families: {
    // Typed as plain strings: the family list is the catalogue's, and a family
    // the catalogue adds later must be appendable without a type change.
    order: [
      'tree_based',
      'ground_level',
      'green_roof',
      'vertical_greening',
      'vegetated_shelter',
      'street',
      'public_space',
      'park',
      'woodland_forest',
      'water_landscape',
      'ecological_network',
      'productive_landscape',
      'building',
      'district',
    ] as readonly string[],
    labels: {
      tree_based: 'Trees and tree planting',
      ground_level: 'Ground-level planting',
      green_roof: 'Green roofs',
      vertical_greening: 'Vertical greening',
      vegetated_shelter: 'Vegetated shelters',
      street: 'Street scale',
      public_space: 'Public space scale',
      park: 'Park scale',
      woodland_forest: 'Woodland and forest scale',
      water_landscape: 'Water landscape scale',
      ecological_network: 'Ecological network scale',
      productive_landscape: 'Productive landscape scale',
      building: 'Building scale',
      district: 'District scale',
    } as Record<string, string>,
    kinds: {
      element: 'Element — a discrete thing you build',
      composite: 'Composite — a spatial system made of elements',
    } as Record<string, string>,
  },

  cost: {
    gate: 'Do you have cost or energy data for this site?',
    gateYes: 'Yes — enter figures',
    gateNo: 'No — skip this step',
    gateSkipNote:
      'Skipped. Capital cost, payback, and cost feasibility will be reported as “not estimated”.',
    coBenefits: 'Co-benefit overrides',
    coBenefitsHelp:
      'The library provides cited defaults for this typology. Override them only if you know this site differs.',
  },

  picker: {
    fit: {
      suited: 'Well suited to this site',
      unsuitablePrefix: 'Not suitable',
      selectable: 'not suitable — selectable',
      belowMinimumArea: (min: string) => `site below the ${min} m² minimum`,
      insufficientSoil: (req: string) => `soil below the “${req}” requirement`,
      insufficientIrrigation: (req: string) => `irrigation below the “${req}” requirement`,
      unsuitableClimate: 'not suited to this climate zone',
      needsSoil: (req: string) => `Needs ${req} soil`,
      needsIrrigation: (req: string) => `Needs ${req} irrigation`,
      unanswered: 'not yet answered',
    },
    cooling: (min: string, max: string) => `Cooling ${min}–${max} °C`,
    evidence: (level: string) => `Evidence: ${level}`,
    selected: 'Selected',
    sizingHeading: 'Size the intervention',

    /**
     * The catalogue picker (D-043, D-044). 110 entries across fourteen
     * families is not a flat card list, so the menu groups by family and the
     * copy states what the entries are: catalogue entries inheriting a cited
     * evidence class, not solution-specific measurements.
     */
    intro:
      'Select one intervention, or several to assess them together as a package. Entries are grouped by family and annotated by fit to the site you have described.',
    introPackage:
      'At this scale an assessment composes a package: select the interventions that together make up the proposal. Each is scored and reported separately.',
    filterLabel: 'Filter by name',
    filterPlaceholder: 'e.g. tree, roof, wetland',
    filterNoMatch: 'No entry matches this filter.',
    clearFilter: 'Clear filter',
    groupCount: (shown: number) => (shown === 1 ? '1 entry' : `${shown} entries`),
    expandGroup: (family: string) => `Show the ${family} entries`,
    offeredHeading: 'Offered for this site',
    offeredIntro: (n: number) =>
      n === 1
        ? 'One entry is offered for the scale, land use, and site conditions you described.'
        : `${n} entries are offered for the scale, land use, and site conditions you described.`,
    notOfferedHeading: 'Not offered for this site',
    notOfferedIntro:
      'These are not part of what the service offers for the scale and conditions you described. They stay fully selectable — a deliberate hypothesis is never overridden — and the choice is recorded with the result.',
    notOfferedBadge: 'Not offered here',
    evidenceClass: (archetype: string) => `Evidence class: ${archetype}`,
    evidenceClassNote:
      'Each entry inherits its cooling envelope from the cited evidence class named on its card, not from measurements of that entry alone.',
    inherited: 'suitability inherited',
    selectionHeading: 'Selected interventions',
    selectionEmpty: 'Nothing selected yet. Choose at least one intervention below.',
    selectionCount: (n: number) => (n === 1 ? '1 component' : `${n} components`),
    remove: 'Remove',
    removeLabel: (name: string) => `Remove ${name} from the selection`,
    representativeHint: 'Order is preserved as you selected it.',
    /** D-044.4: unbounded, but the honest consequence is stated. */
    sizeWarning: (limit: number) =>
      `This package has more than ${limit} components. Adding a further component will not raise the temperature estimate — the package is reported at its best-evidenced component's range, never summed. More components add co-benefit breadth and cost.`,
    unknownEntry: (nbsType: string) =>
      `${nbsType} — this entry is not in the current library and must be re-selected.`,
  },

  results: {
    heading: 'Results',
    heatPriority: 'Heat Priority Index',
    heatPriorityScale: '/ 100 — how much this site deserves attention',
    opportunity: 'NbS Cooling Opportunity Score',
    opportunityScale: '/ 100 — the headline comparison score',
    confidenceBadge: (level: string) => `Confidence: ${level}`,
    overallConfidence: 'Overall confidence',
    flagsHeading: 'Flags',
    lowOverallConfidence:
      'Overall confidence is low: treat these results as a prompt for further investigation, not a verdict.',
    recommendationHeading: 'Recommendation',
    blocks: {
      cooling: 'Cooling',
      energy: 'Energy',
      ghg: 'Greenhouse gas',
      costs: 'Economic',
      coBenefits: 'Co-benefits',
      equity: 'Equity',
    },
    cooling: {
      potential: 'Cooling Potential Score',
      deltaT: 'Indicative temperature reduction',
      deltaTNote: 'Daytime, pedestrian-level air temperature; clipped to the literature envelope.',
      // Shade potential and time to benefit depend on intervention sizing
      // inputs, not on cost data, so they carry a neutral wording instead of
      // the economic statuses.not_estimated sentence (D-034).
      notEstimated: 'Not estimated — the required input was not provided.',
      heatIndexImprovement: 'Heat-index improvement',
      shadePotential: 'Shade potential',
      timeToBenefit: 'Time to benefit',
      adjustment: 'Site adjustment factor',
      adjustmentConditions: {
        canopy: 'Canopy',
        soil_water: 'Soil and water',
        scale: 'Scale',
        climate: 'Climate',
      },
    },
    energy: {
      savings: 'Cooling-energy savings',
      unit: 'kWh/year',
    },
    ghg: {
      avoided: 'Emissions avoided',
      unit: 'kgCO₂e/year',
      factor: 'Emission factor',
      origin: {
        user_supplied: 'user supplied',
        country_default: 'country default',
      },
    },
    costs: {
      annualSavings: 'Annual cost savings',
      payback: 'Simple payback',
      paybackUnit: 'years',
      paybackCentral: 'central',
      feasibility: 'Cost feasibility score',
      readiness: 'Investment readiness',
      bracket: {
        short: 'Short (< 5 years)',
        medium: 'Medium (5–10 years)',
        long: 'Long (10–20 years)',
        very_long: 'Very long (≥ 20 years)',
      } as Record<string, string>,
    },
    statuses: {
      calculated: 'Calculated',
      derived: 'Derived',
      not_applicable:
        'Not applicable: nearby building cooling demand is not relevant to this intervention.',
      missing_energy_demand: 'Not estimated — annual cooling energy demand was not provided.',
      typology_not_applicable:
        'Not estimated — this typology’s benefit is principally amenity-level, not building energy.',
      relevance_not_confirmed:
        'Not estimated — it was not confirmed that nearby building cooling demand is relevant.',
      missing_emission_factor: 'Not estimated — no grid emission factor was available.',
      energy_not_calculated: 'Not estimated — the energy saving itself was not calculated.',
      missing_energy_price: 'Not estimated — no energy price was supplied.',
      missing_capital_cost:
        'Capital cost not estimated — no cost data supplied. This tool ships no default cost values.',
      annual_savings_unavailable: 'Not estimated — annual cost savings were unavailable.',
      // D-034: this string is rendered for the *economic* block, whose
      // not_estimated genuinely means cost data is missing. The cooling
      // block's own not_estimated statuses (shade potential, time to
      // benefit) depend on intervention sizing inputs and render
      // results.cooling.notEstimated instead.
      not_estimated: 'Not estimated — requires cost data. This tool ships no default cost values.',
    } as Record<string, string>,
    subScores: {
      heading: 'Sub-scores',
      heatExposure: 'Heat exposure',
      heatExposurePath: {
        data_rich: 'measured (data-rich path)',
        data_poor: 'qualitative (data-poor path)',
      },
      vulnerability: 'Vulnerability',
      suitability: 'Suitability',
      space: 'Space',
      soil: 'Soil',
      water: 'Water',
      maintenance: 'Maintenance',
      urbanContext: 'Urban context',
      biodiversity: 'Biodiversity',
      stormwater: 'Stormwater',
      publicHealth: 'Public health',
      socialInclusion: 'Social inclusion',
      urbanQuality: 'Urban quality',
      vulnerableUserBenefit: 'Vulnerable-user benefit',
      publicAccessibility: 'Public accessibility',
      safetyComfort: 'Safety and comfort',
      participationRelevance: 'Participation relevance',
      equityNote:
        'The Equity Score is reported with its own confidence and deliberately does not enter the final aggregation; equity influences the headline score through the Vulnerability Score instead.',
    },
    opportunityComponents: {
      heading: 'How the score is composed',
      component: 'Component',
      score: 'Score',
      nominalWeight: 'Nominal weight',
      appliedWeight: 'Applied weight',
      excluded: (names: string) => `Not estimated and excluded, weight redistributed: ${names}`,
    },
    /**
     * The package block (D-038, D-044.4). The combination rules are served as
     * text by the engine and rendered verbatim; the strings here are the
     * column headings and labels around them, never a restatement of a rule.
     */
    packageSection: {
      heading: 'The package, component by component',
      intro: (n: number) =>
        `This assessment proposes ${n} interventions. Each is scored on its own values and reported on its own terms below.`,
      representative: 'Carries the headline estimate',
      representativeWhy: 'Why this component',
      component: 'Component',
      cooling: 'Temperature reduction',
      evidenceClass: 'Evidence class',
      evidenceConfidence: 'Evidence confidence',
      suitability: 'Suitability',
      flags: 'Flags',
      noFlags: '—',
      rulesHeading: 'How the components were combined',
      rules: {
        cooling: 'Temperature',
        coBenefits: 'Co-benefits',
        suitability: 'Suitability',
        cost: 'Cost',
        energy: 'Energy',
      },
      energyComponent: (name: string) =>
        `Derived from ${name} alone; component savings are never summed.`,
      energyNoComponent: 'No component of this package is building-energy applicable.',
      inheritedNote: (archetype: string) =>
        `Values inherited from the ${archetype} evidence class.`,
    },
    assumptionsHeading: 'Assumptions applied',
    assumptionsIntro: 'Every default the engine used in place of an answer:',
    assumptionsNone:
      'No defaults were applied: every input the formulas used came from your answers.',
    methodNoteHeading: 'Method note and limitations',
    versions: (methodology: string, engine: string) =>
      `Methodology version ${methodology} · engine ${engine}`,
    methodologyUpdateAvailable:
      'A newer methodology version is now loaded. This stored result is never recomputed; re-running under the newer methodology creates a new assessment.',
    warningsHeading: 'Warnings recorded with this result',
    actions: {
      exportPdf: 'Export report (PDF)',
      exportXlsx: 'Export data (XLSX)',
      compare: 'Compare another option',
      backToProject: 'Back to project',
    },
    formulaLink: 'Formula and sources',
    draftNotice: 'This assessment has not been evaluated yet.',
    continueDraft: 'Continue the questionnaire',
  },

  compare: {
    heading: 'Compare options',
    intro:
      'Same site, options side by side. Rows where the options differ are highlighted; the decision is yours — the tool does not pick a winner.',
    pickOptions: 'Options to compare',
    needTwo: 'Select at least two evaluated options.',
    row: {
      typology: 'Typology',
      components: 'Components',
      opportunity: 'Opportunity Score',
      category: 'Category',
      heatPriority: 'Heat Priority Index',
      deltaT: 'Temperature reduction',
      energySavings: 'Energy savings',
      payback: 'Payback (central)',
      confidence: 'Overall confidence',
      flags: 'Flags',
      evidence: 'Evidence confidence',
    },
    noFlags: '—',
    identicalNote: 'Rows in grey are identical across the selected options.',
    addOption: 'Add another option',
  },

  methodology: {
    heading: 'Methodology',
    intro:
      'This page renders the live configuration the engine scores with — the same data, verbatim. Every value cites its source; the full scientific basis is in the Methodology Report and the paper.',
    version: (v: string) => `Methodology version ${v}`,
    sections: {
      scores: 'Scores and bands',
      weights: 'Weights',
      effectiveWeights: 'Effective final-score weights',
      typologies: 'Typology library',
      adjustment: 'Adjustment factors',
      normalisation: 'Input normalisation',
      derived: 'Derived scores and rules',
      confidence: 'Confidence model',
      energy: 'Energy model',
      countryDefaults: 'Country defaults',
      recommendation: 'Recommendation templates',
    },
    bands: {
      score: 'Score',
      label: 'Band',
      heatPriority: 'Heat Priority Index bands',
      opportunity: 'Opportunity Score bands',
      bandRange: (min: string | number | null, max: string | number | null) =>
        min === null ? `≤ ${max}` : max === null ? `> ${min}` : `> ${min} – ≤ ${max}`,
    },
    effectiveWeightsNote:
      'Vulnerability contributes twice by design — inside the Heat Priority Index and directly. The effective weights below are the products of the served weights (shown), so the tool weights who is affected above how physically hot the site is. Deliberate and disclosed (D-007).',
    effectiveWeightsColumns: {
      component: 'Component',
      derivation: 'Derivation',
      effective: 'Effective weight',
    },
    suitabilityHeading: 'Suitability conditions',
    suitability: {
      minArea: 'Minimum site area',
      soil: 'Requires soil',
      irrigation: 'Requires irrigation',
      climate: 'Unsuitable climate zones',
      none: 'none',
    },
    familyCount: (n: number) => (n === 1 ? '1 entry' : `${n} entries`),
    archetypeLabel: 'Evidence class',
    inheritedSuitability: 'Suitability inherited from the evidence class',
    typology: {
      baseScore: 'Base cooling score',
      envelope: 'Temperature reduction envelope',
      evidence: 'Evidence confidence',
      mechanism: 'Primary cooling mechanism',
      energyApplicable: 'Building energy applicable',
      context: 'Typical use context',
      coBenefits: 'Co-benefit defaults',
      caveats: 'Output caveats',
      sources: 'Sources',
      notes: 'Notes',
      yes: 'yes',
      no: 'no',
    },
    rationaleLabel: 'Rationale',
    sourcesLabel: 'Sources',
    reportLink: 'Methodology Report (docs/methodology/METHODOLOGY.md)',
  },
} as const;

/** Display name for a qualitative option value, falling back to the raw value. */
export function optionLabel(value: string): string {
  return messages.options.levels[value] ?? value;
}

/** Label for an input field, falling back to the raw field name. */
export function fieldLabel(field: string): string {
  return messages.fields[field]?.label ?? field;
}
