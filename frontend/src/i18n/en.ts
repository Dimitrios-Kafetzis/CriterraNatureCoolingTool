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
    nav: {
      projects: 'Projects',
      methodology: 'Methodology',
    },
    footer: {
      license: 'Apache-2.0 · open methodology',
      engine: 'Engine',
      methodologyVersion: 'Methodology',
    },
    loading: 'Loading…',
    apiError: 'The assessment service could not be reached. Is the API running?',
    notFound: 'This page does not exist.',
  },

  entry: {
    heading: 'Evaluate nature-based solutions for urban cooling',
    what: 'This tool turns a structured description of a site and a proposed nature-based intervention — street trees, an urban forest, a green roof, and eleven other typologies — into transparent, literature-grounded scores: a Heat Priority Index, a cooling opportunity score with an indicative temperature-reduction range, and energy, cost, equity, and co-benefit estimates.',
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
          'Choose the intervention to assess. Cards are ordered and annotated by fit to the site you have described — an unsuitable option stays selectable, and its flag follows into the results.',
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

  fields: {
    project_name: {
      label: 'Project name',
      help: 'Shown on the report.',
    },
    assessment_scale: {
      label: 'Assessment scale',
      help: 'The spatial scale this assessment describes.',
    },
    country: {
      label: 'Country code',
      help: 'ISO code, e.g. “GR” or “BRA”. Enables country default values for emission factors and energy prices.',
    },
    site_area_m2: {
      label: 'Site area',
      help: 'The total area of the site being assessed.',
      unit: 'm²',
    },
    existing_tree_canopy_percent: {
      label: 'Existing tree canopy',
      help: 'Share of the site currently under tree canopy.',
      unit: '%',
    },
    existing_green_cover_percent: {
      label: 'Existing green cover',
      help: 'Share of the site currently vegetated (including canopy).',
      unit: '%',
    },
    impervious_surface_percent: {
      label: 'Impervious surface',
      help: 'Share of the site that is sealed (asphalt, concrete, roofs).',
      unit: '%',
    },
    soil_availability: {
      label: 'Soil availability',
      help: 'How much plantable soil the site offers.',
    },
    irrigation_availability: {
      label: 'Irrigation availability',
      help: 'How reliably the site can be watered.',
    },
    current_shade_level: {
      label: 'Current shade level',
      help: 'How shaded the site is today.',
    },
    land_use: {
      label: 'Land use',
      help: 'The dominant use of the site.',
    },
    climate_zone: {
      label: 'Climate zone',
      help: 'The broad climate this site sits in.',
    },
    lst_anomaly_c: {
      label: 'Land surface temperature anomaly',
      help: 'From satellite data, relative to the city mean. If you have GIS-derived data, this is the single most valuable heat input.',
      unit: '°C',
    },
    heat_exposure_level: {
      label: 'Heat exposure level',
      help: 'Your qualitative reading of how hot this site runs. Used when no measured anomaly is available.',
    },
    solar_exposure: {
      label: 'Solar exposure',
      help: 'How much direct sun the site receives.',
    },
    population_density: {
      label: 'Population density',
      help: 'How densely populated the surroundings are.',
    },
    vulnerable_population_presence: {
      label: 'Vulnerable population presence',
      help: 'Children, elderly people, or other heat-vulnerable groups using this place.',
    },
    access_to_cooled_indoor_space: {
      label: 'Access to cooled indoor space',
      help: 'How easily local users can reach air-conditioned or cool indoor refuge.',
    },
    safety_concern: {
      label: 'Safety and comfort concern',
      help: 'How significant the safety or comfort problems of this place are today.',
    },
    public_accessibility: {
      label: 'Public accessibility',
      help: 'How freely the public can access the site.',
    },
    community_participation: {
      label: 'Community participation',
      help: 'How involved the local community is in shaping this place.',
    },
    nbs_type: {
      label: 'Intervention typology',
      help: '',
    },
    intervention_area_m2: {
      label: 'Intervention area',
      help: 'The area the intervention itself will occupy.',
      unit: 'm²',
    },
    new_canopy_area_at_maturity_m2: {
      label: 'New canopy area at maturity',
      help: 'The additional canopy the intervention will provide once mature.',
      unit: 'm²',
    },
    expected_maturity_period_years: {
      label: 'Expected maturity period',
      help: 'Years until the intervention delivers its full effect.',
      unit: 'years',
    },
    implementation_complexity: {
      label: 'Implementation complexity',
      help: 'How demanding the intervention is to deliver.',
    },
    maintenance_intensity: {
      label: 'Maintenance intensity',
      help: 'How demanding the intervention is to keep alive and functional.',
    },
    co_benefit_biodiversity: {
      label: 'Biodiversity',
      help: '',
    },
    co_benefit_stormwater: {
      label: 'Stormwater',
      help: '',
    },
    co_benefit_public_health: {
      label: 'Public health',
      help: '',
    },
    co_benefit_social_inclusion: {
      label: 'Social inclusion',
      help: '',
    },
    co_benefit_urban_quality: {
      label: 'Urban quality',
      help: '',
    },
    nearby_building_cooling_demand_relevant: {
      label: 'Is nearby building cooling demand relevant?',
      help: 'Whether buildings near the intervention use active cooling that the intervention could reduce.',
    },
    annual_cooling_energy_demand_kwh: {
      label: 'Annual cooling energy demand',
      help: 'The cooling electricity demand of the relevant nearby buildings.',
      unit: 'kWh/year',
    },
    energy_price_per_kwh: {
      label: 'Energy price',
      help: 'In the currency below.',
      unit: 'per kWh',
    },
    capital_cost: {
      label: 'Capital cost',
      help: 'Your estimate of the intervention’s capital cost. The tool ships no default cost values.',
    },
    currency: {
      label: 'Currency',
      help: 'Three-letter code, e.g. EUR.',
    },
    grid_emission_factor_kgco2e_per_kwh: {
      label: 'Grid emission factor',
      help: 'Leave blank to use the country default where available.',
      unit: 'kgCO₂e/kWh',
    },
  } as Record<string, { label: string; help: string; unit?: string }>,

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
      healthcare: 'Healthcare',
      industrial: 'Industrial',
      other: 'Other',
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
