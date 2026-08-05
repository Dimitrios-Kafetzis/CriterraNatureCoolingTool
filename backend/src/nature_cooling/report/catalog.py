"""The report's module-level English string catalog (D-033).

Every interface string the exported report renders lives here, mirroring the
frontend's externalisation contract (``frontend/src/i18n/en.ts``): translation
never requires a code change. Strings that *state a result* — scores,
categories, flag messages, recommendation text, warning texts, assumption
texts, the method note — are NOT here: they come from the stored result and
are rendered verbatim. This catalog holds interface language only: labels,
headings, display names for enum values, and status texts for the statuses
the result reports.
"""

from __future__ import annotations

from typing import Final

# --- Interface strings -------------------------------------------------------

STRINGS: Final[dict[str, str]] = {
    "app_title": "Nature for Cooling",
    "app_subtitle": "Rapid Assessment Tool",
    "report_title": "Assessment report",
    "by_line": "by Criterra",
    # The report carries a copyright line rather than a by-line (D-042). No
    # year: the document's own creation date is stamped on page 1, and a
    # literal year here would either go stale or reintroduce a clock into a
    # builder that must stay byte-deterministic (D-033).
    "copyright_line": "© Criterra · a Criterra product",
    "license_line": "Apache-2.0 · open methodology",
    "page1_heading": "Summary",
    "page2_heading": "Detail",
    "created": "Created",
    "typology": "Intervention typology",
    "assessment_label": "Assessment",
    "project": "Project",
    "heat_priority": "Heat Priority Index",
    "heat_priority_scale": "/ 100 — how much this site deserves attention",
    "opportunity": "NbS Cooling Opportunity Score",
    "opportunity_scale": "/ 100 — the headline comparison score",
    "category": "Category",
    "flags_heading": "Flags",
    "recommendation_heading": "Recommendation",
    "confidence_heading": "Confidence",
    "confidence_overall": "Overall",
    "confidence_value": "{level} · {percent}% of inputs supplied",
    "evidence_cap": (
        "Cooling confidence is capped at Medium because published evidence for "
        "this typology is limited. Complete inputs cannot compensate for thin evidence."
    ),
    "low_overall_confidence": (
        "Overall confidence is low: treat these results as a prompt for further "
        "investigation, not a verdict."
    ),
    "block_cooling": "Cooling",
    "block_energy": "Energy",
    "block_ghg": "Greenhouse gas",
    "block_costs": "Economic",
    "block_co_benefits": "Co-benefits",
    "block_equity": "Equity",
    "confidence_badge": "Confidence: {level}",
    "cooling_potential": "Cooling Potential Score",
    "cooling_delta_t": "Indicative temperature reduction",
    "cooling_delta_t_note": (
        "Daytime, pedestrian-level air temperature; clipped to the literature envelope."
    ),
    "cooling_heat_index_improvement": "Heat-index improvement",
    "cooling_shade_potential": "Shade potential",
    "cooling_time_to_benefit": "Time to benefit",
    "cooling_adjustment": "Site adjustment factor",
    "adjustment_canopy": "Canopy",
    "adjustment_soil_water": "Soil and water",
    "adjustment_scale": "Scale",
    "adjustment_climate": "Climate",
    "sub_scores_heading": "Adjustment and suitability sub-scores",
    "sub_heat_exposure": "Heat exposure",
    "sub_vulnerability": "Vulnerability",
    "sub_suitability": "Suitability",
    "sub_space": "Space",
    "sub_soil": "Soil",
    "sub_water": "Water",
    "sub_maintenance": "Maintenance",
    "sub_urban_context": "Urban context",
    "sub_biodiversity": "Biodiversity",
    "sub_stormwater": "Stormwater",
    "sub_public_health": "Public health",
    "sub_social_inclusion": "Social inclusion",
    "sub_urban_quality": "Urban quality",
    "sub_vulnerable_user_benefit": "Vulnerable-user benefit",
    "sub_public_accessibility": "Public accessibility",
    "sub_safety_comfort": "Safety and comfort",
    "sub_participation_relevance": "Participation relevance",
    "equity_note": (
        "The Equity Score is reported with its own confidence and deliberately does "
        "not enter the final aggregation; equity influences the headline score "
        "through the Vulnerability Score instead."
    ),
    "energy_savings": "Cooling-energy savings",
    "energy_unit": "kWh/year",
    "ghg_avoided": "Emissions avoided",
    "ghg_unit": "kgCO2e/year",
    "ghg_factor": "Emission factor",
    "origin_user_supplied": "user supplied",
    "origin_country_default": "country default",
    "costs_annual_savings": "Annual cost savings",
    "costs_payback": "Simple payback",
    "costs_payback_unit": "years",
    "costs_payback_central": "central",
    "costs_feasibility": "Cost feasibility score",
    "costs_readiness": "Investment readiness",
    "score": "Score",
    "assumptions_heading": "Assumptions applied",
    "assumptions_intro": "Every default the engine used in place of an answer:",
    "assumptions_truncated": (
        "… and {count} further assumption(s), itemised in full on the workbook's "
        "Assumptions & Warnings sheet."
    ),
    "assumptions_none": (
        "No defaults were applied: every input the formulas used came from the answers."
    ),
    "warnings_heading": "Warnings recorded with this result",
    "method_note_heading": "Method note and limitations",
    "versions": "Methodology version {methodology} · engine {engine}",
    "components_heading": "How the Opportunity Score is composed",
    "component": "Component",
    "component_nominal_weight": "Nominal weight",
    "component_applied_weight": "Applied weight",
    "components_excluded": "Not estimated and excluded, weight redistributed: {names}",
    "sheet_inputs": "Inputs",
    "sheet_results": "Results",
    "sheet_assumptions": "Assumptions & Warnings",
    "inputs_field": "Field",
    "inputs_value": "Supplied value",
    "inputs_marker": "Provenance",
    "inputs_note": (
        "An unmarked value was supplied by the user. Fields marked as not supplied "
        "fall back to the methodology's documented rules, and every default the "
        "engine actually applied is itemised on the Assumptions & Warnings sheet. "
        "Fields marked as filled from the map were derived from a location the user "
        "chose, and were overridable at every point."
    ),
    "not_answered": "(not answered)",
    "none_selected": "(none selected)",
    "not_supplied_marker": "not supplied — methodology fallback applies",
    "answered_unknown_marker": "answered “unknown” — counts as not supplied",
    "autofilled_marker": "filled from the map ({source})",
    "results_block": "Block",
    "results_item": "Item",
    "results_value": "Value",
    "heading_identity": "Assessed under",
    # --- Package reporting (D-038, D-044.4) ---------------------------------
    "package_heading": "Package components, scored individually",
    "package_component": "Component",
    "package_archetype": "Evidence class",
    "package_evidence": "Evidence",
    "package_range": "Cooling range",
    "package_suitability": "Suitability",
    "package_representative": "carries the package estimate",
    "package_rule": (
        "The package's temperature estimate is the best-evidenced component's and is "
        "never the sum of its parts: no retrieved source quantifies super-additive "
        "cooling from combining measures. Co-benefits take the union across "
        "components, suitability takes the lowest, and capital cost is entered once "
        "for the whole package."
    ),
    "package_heading_more": "{components} and {count} further component(s)",
    "package_single": "Single intervention — this assessment has one component.",
    "package_truncated": (
        "… and {count} further component(s), itemised in full on the workbook's Results sheet."
    ),
    "evidence_class_note": (
        "Cooling values are inherited from the {archetype} evidence class "
        "({provenance}); see the Methodology Report evidence tables."
    ),
    # --- Comparison report (v2.4) -------------------------------------------
    "comparison_title": "Comparison report",
    "comparison_scenarios_heading": "Scenarios compared",
    "comparison_scenario_scale": "Assessment scale",
    "comparison_scenario_created": "Created",
    "comparison_table_heading": "Side by side",
    "comparison_criterion": "Criterion",
    "comparison_cooling_potential": "Cooling Potential Score",
    "comparison_suitability": "Suitability score",
    "comparison_co_benefits": "Co-benefit Score",
    "comparison_confidence": "Overall confidence",
    "comparison_best_note": (
        "The best value on a criterion is marked •; ties are marked together. "
        "A criterion where any scenario reports a status instead of a figure "
        "is never marked, and nothing ranks the scenarios overall."
    ),
    "comparison_identical_note": "Values identical across every scenario carry no emphasis.",
    "comparison_narrative_heading": "What the table shows",
    "comparison_best_single": "{scenario} has the {superlative} {criterion} ({value}).",
    "comparison_best_tied": "{scenarios} share the {superlative} {criterion} ({value}).",
    "comparison_superlative_highest": "highest",
    "comparison_superlative_lowest": "lowest",
    "comparison_narrative_empty": (
        "The compared scenarios are equal on every criterion where a best value could be marked."
    ),
    "comparison_cross_scale": (
        "These scenarios were assessed at different scales ({scales}), so their "
        "figures describe differently sized objects and are not like for like. "
        "They are shown side by side for reference only; no value is marked as "
        "best and no comparative statement is made."
    ),
    "comparison_methodology_differs": (
        "The scenarios were evaluated under different methodology versions "
        "({versions}). Each figure is reported exactly as stored under its own "
        "version; nothing is recomputed for comparability."
    ),
    "comparison_site_heading": "Site context, shared by every scenario",
    "comparison_site_note": (
        "These answers are identical across the compared scenarios and are "
        "printed once. An unmarked value was supplied by the user; every "
        "default the engine applied in place of an answer is itemised per "
        "scenario below."
    ),
    "comparison_site_differs_heading": "Site answers that differ between scenarios",
    "comparison_site_differs_note": (
        "The scenarios describe the site differently on the answers below, so "
        "their results do not compare a change of intervention alone."
    ),
    "provenance_differs": "provenance differs between scenarios",
    "comparison_scenario_detail": "{label} — flags, assumptions and warnings",
    "comparison_no_scenario_detail": (
        "No flags were raised, no defaults were applied, and no warnings were "
        "recorded for this scenario."
    ),
    "comparison_flags_heading": "Flags",
    "comparison_sheet_overview": "Comparison",
    "comparison_sheet_site": "Site context",
    "comparison_sheet_scenarios": "Scenario detail",
    "comparison_best_marker": "• ",
    "comparison_kind": "Kind",
    "comparison_kind_flag": "Flag",
    "comparison_kind_assumption": "Assumption",
    "comparison_kind_warning": "Warning",
    "comparison_scenario_column": "Scenario",
    "comparison_text_column": "Text",
    "comparison_versions_column": "Evaluated under",
}

# --- Status texts (mirroring the frontend's ``results.statuses`` catalog) ----

STATUS_TEXTS: Final[dict[str, str]] = {
    "calculated": "Calculated",
    "derived": "Derived",
    "not_applicable": (
        "Not applicable: nearby building cooling demand is not relevant to this intervention."
    ),
    "missing_energy_demand": "Not estimated — annual cooling energy demand was not provided.",
    "typology_not_applicable": (
        "Not estimated — this typology's benefit is principally amenity-level, not building energy."
    ),
    "relevance_not_confirmed": (
        "Not estimated — it was not confirmed that nearby building cooling demand is relevant."
    ),
    "missing_emission_factor": "Not estimated — no grid emission factor was available.",
    "energy_not_calculated": "Not estimated — the energy saving itself was not calculated.",
    "missing_energy_price": "Not estimated — no energy price was supplied.",
    "missing_capital_cost": (
        "Capital cost not estimated — no cost data supplied. "
        "This tool ships no default cost values."
    ),
    "annual_savings_unavailable": "Not estimated — annual cost savings were unavailable.",
    "not_estimated": "Not estimated — requires cost data. This tool ships no default cost values.",
    # The cooling block's own not-estimated outputs (shade potential, time to
    # benefit) depend on intervention sizing inputs, not on cost data, so they
    # carry a neutral wording instead of the economic one.
    "not_estimated_input": "Not estimated — the required input was not provided.",
}

# --- Display names for enum values the result and input carry ----------------

OPTION_LABELS: Final[dict[str, str]] = {
    # Qualitative levels (shared across many fields)
    "none": "None",
    "very_low": "Very low",
    "limited": "Limited",
    "occasional": "Occasional",
    "moderate": "Moderate",
    "low": "Low",
    "medium": "Medium",
    "high": "High",
    "very_high": "Very high",
    "reliable": "Reliable",
    "yes": "Yes",
    "no": "No",
    "unknown": "Unknown / not sure",
    # Derived condition levels
    "poor": "Poor",
    "good": "Good",
    "excellent": "Excellent",
    # Heat Priority Index categories
    "critical": "Critical",
    # Opportunity Score categories
    "strong": "Strong",
    "high_priority": "High priority",
    # Time to benefit
    "immediate": "Immediate",
    "short_term": "Short term",
    "medium_term": "Medium term",
    "long_term": "Long term",
    # Assessment scale
    "city": "City",
    "district": "District",
    "neighbourhood": "Neighbourhood",
    "site": "Site",
    "building": "Building",
    # Climate zones
    "tropical_wet": "Tropical wet",
    "tropical_dry": "Tropical dry",
    "arid": "Arid",
    "semi_arid": "Semi-arid",
    "temperate": "Temperate",
    "other": "Other",
    # Land use
    "street_corridor": "Street corridor",
    "residential": "Residential",
    "mixed_use": "Mixed use",
    "commercial": "Commercial",
    "public_space": "Public space",
    "park": "Park",
    "school": "School",
    "healthcare": "Healthcare",
    "industrial": "Industrial",
}

# Payback brackets carry their defining year ranges, as in the web app.
BRACKET_LABELS: Final[dict[str, str]] = {
    "short": "Short (< 5 years)",
    "medium": "Medium (5–10 years)",
    "long": "Long (10–20 years)",
    "very_long": "Very long (≥ 20 years)",
}

# Heat Exposure Score computation path.
PATH_LABELS: Final[dict[str, str]] = {
    "data_rich": "measured (data-rich path)",
    "data_poor": "qualitative (data-poor path)",
}

# --- Input field labels, units, and questionnaire order ----------------------

FIELD_LABELS: Final[dict[str, str]] = {
    "project_name": "Project name",
    "assessment_scale": "Assessment scale",
    "country": "Country code",
    "site_area_m2": "Site area",
    "existing_tree_canopy_percent": "Existing tree canopy",
    "existing_green_cover_percent": "Existing green cover",
    "impervious_surface_percent": "Impervious surface",
    "soil_availability": "Soil availability",
    "irrigation_availability": "Irrigation availability",
    "current_shade_level": "Current shade level",
    "land_use": "Land use",
    # Availability-only: these four decide which interventions are offered and
    # feed no score (D-044.1). Labelled as such on the Inputs sheet so a reader
    # never looks for their contribution to a number.
    "includes_railway": "Site includes a railway (availability only)",
    "existing_woodland": "Existing woodland or forest (availability only)",
    "waterfront_type": "Waterfront type (availability only)",
    "productive_governance": "Productive-landscape governance (availability only)",
    "climate_zone": "Climate zone",
    "lst_anomaly_c": "Land surface temperature anomaly",
    "heat_exposure_level": "Heat exposure level",
    "solar_exposure": "Solar exposure",
    "heat_index_concern": "Heat index concern",
    "population_density": "Population density",
    "vulnerable_population_presence": "Vulnerable population presence",
    "access_to_cooled_indoor_space": "Access to cooled indoor space",
    "access_to_cool_outdoor_refuge": "Access to cool outdoor refuge",
    "safety_concern": "Safety and comfort concern",
    "public_accessibility": "Public accessibility",
    "community_participation": "Community participation",
    "nbs_type": "Intervention typologies",
    "intervention_area_m2": "Intervention area",
    "new_canopy_area_at_maturity_m2": "New canopy area at maturity",
    "expected_maturity_period_years": "Expected maturity period",
    "implementation_complexity": "Implementation complexity",
    "maintenance_intensity": "Maintenance intensity",
    "co_benefit_biodiversity": "Co-benefit override — biodiversity",
    "co_benefit_stormwater": "Co-benefit override — stormwater",
    "co_benefit_public_health": "Co-benefit override — public health",
    "co_benefit_social_inclusion": "Co-benefit override — social inclusion",
    "co_benefit_urban_quality": "Co-benefit override — urban quality",
    "nearby_building_cooling_demand_relevant": "Is nearby building cooling demand relevant?",
    "annual_cooling_energy_demand_kwh": "Annual cooling energy demand",
    "energy_price_per_kwh": "Energy price",
    "capital_cost": "Capital cost",
    "currency": "Currency",
    "grid_emission_factor_kgco2e_per_kwh": "Grid emission factor",
}

FIELD_UNITS: Final[dict[str, str]] = {
    "site_area_m2": "m²",
    "existing_tree_canopy_percent": "%",
    "existing_green_cover_percent": "%",
    "impervious_surface_percent": "%",
    "lst_anomaly_c": "°C",
    "intervention_area_m2": "m²",
    "new_canopy_area_at_maturity_m2": "m²",
    "expected_maturity_period_years": "years",
    "annual_cooling_energy_demand_kwh": "kWh/year",
    "energy_price_per_kwh": "per kWh",
    "grid_emission_factor_kgco2e_per_kwh": "kgCO2e/kWh",
}

# The questionnaire order (models.AssessmentInput declaration order), used by
# the workbook's Inputs sheet.
INPUT_FIELD_ORDER: Final[tuple[str, ...]] = tuple(FIELD_LABELS)

# How the Inputs sheet names the dataset behind an autofilled value. Keyed by
# the bibliography key the lookup recorded, so the report cites the same source
# the methodology does; an unrecognised key falls through to itself rather than
# being hidden, because a provenance record the report cannot name is a fact
# the reader still needs.
SOURCE_LABELS: Final[dict[str, str]] = {
    "beck2023": "Köppen–Geiger classification, Beck et al. 2023",
    "naturalearth": "Natural Earth country boundaries",
    "drawn_polygon": "measured from the drawn boundary",
}
