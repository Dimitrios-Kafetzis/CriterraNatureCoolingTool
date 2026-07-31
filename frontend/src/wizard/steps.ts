/**
 * The six questionnaire steps (UX specification §3; D-018 single guided flow).
 *
 * Field placement implements D-031: `heat_index_concern` is not asked (it
 * feeds no formula and no confidence block, so its cost of skipping is zero
 * and the confidence panel could not honestly present it);
 * `current_shade_level` is asked in step 2; no "planted area" field exists.
 * Co-benefit overrides are asked with the intervention they describe
 * (D-029 treats them as part of the intervention group).
 *
 * Option lists are type-checked against the generated OpenAPI schema, so a
 * schema change that renames or removes a level fails `tsc` rather than
 * silently drifting.
 */

import { messages } from '../i18n/en';
import type { AssessmentInput, InputField } from '../api/types';

export type StepId = 'project' | 'site' | 'climate' | 'vulnerability' | 'intervention' | 'cost';

export interface Step {
  id: StepId;
  fields: InputField[];
}

export const STEPS: Step[] = [
  {
    id: 'project',
    fields: ['project_name', 'assessment_scale', 'country'],
  },
  {
    id: 'site',
    fields: [
      'site_area_m2',
      'existing_tree_canopy_percent',
      'existing_green_cover_percent',
      'impervious_surface_percent',
      'soil_availability',
      'irrigation_availability',
      'current_shade_level',
      'land_use',
    ],
  },
  {
    id: 'climate',
    fields: ['climate_zone', 'lst_anomaly_c', 'heat_exposure_level', 'solar_exposure'],
  },
  {
    id: 'vulnerability',
    fields: [
      'population_density',
      'vulnerable_population_presence',
      'access_to_cooled_indoor_space',
      'access_to_cool_outdoor_refuge',
      'safety_concern',
      'public_accessibility',
      'community_participation',
    ],
  },
  {
    id: 'intervention',
    fields: [
      'nbs_type',
      'intervention_area_m2',
      'new_canopy_area_at_maturity_m2',
      'expected_maturity_period_years',
      'implementation_complexity',
      'maintenance_intensity',
      'co_benefit_biodiversity',
      'co_benefit_stormwater',
      'co_benefit_public_health',
      'co_benefit_social_inclusion',
      'co_benefit_urban_quality',
    ],
  },
  {
    id: 'cost',
    fields: [
      'nearby_building_cooling_demand_relevant',
      'annual_cooling_energy_demand_kwh',
      'energy_price_per_kwh',
      'capital_cost',
      'currency',
      'grid_emission_factor_kgco2e_per_kwh',
    ],
  },
];

export function stepTitle(id: StepId): string {
  return messages.wizard.steps[id].title;
}

/** The step a field is asked in, for the confidence panel's step references. */
export function stepOfField(field: string): Step | undefined {
  return STEPS.find((step) => (step.fields as string[]).includes(field));
}

type NonNull<F extends InputField> = NonNullable<AssessmentInput[F]>;

/** Qualitative option lists, excluding `unknown` (offered by the control itself). */
export const OPTIONS = {
  assessment_scale: ['city', 'district', 'neighbourhood', 'site', 'building'],
  climate_zone: ['tropical_wet', 'tropical_dry', 'arid', 'semi_arid', 'temperate', 'other'],
  land_use: [
    'street_corridor',
    'residential',
    'mixed_use',
    'commercial',
    'public_space',
    'park',
    'school',
    'campus',
    'healthcare',
    'memorial',
    'industrial',
    'other',
  ],
  soil_availability: ['none', 'limited', 'moderate', 'high'],
  irrigation_availability: ['none', 'occasional', 'reliable'],
  current_shade_level: ['very_low', 'low', 'medium', 'high'],
  standard: ['low', 'medium', 'high', 'very_high'],
  inverted: ['low', 'medium', 'high'],
  yes_no: ['yes', 'no'],
} as const satisfies {
  assessment_scale: readonly NonNull<'assessment_scale'>[];
  climate_zone: readonly NonNull<'climate_zone'>[];
  land_use: readonly Exclude<NonNull<'land_use'>, 'unknown'>[];
  soil_availability: readonly Exclude<NonNull<'soil_availability'>, 'unknown'>[];
  irrigation_availability: readonly Exclude<NonNull<'irrigation_availability'>, 'unknown'>[];
  current_shade_level: readonly Exclude<NonNull<'current_shade_level'>, 'unknown'>[];
  standard: readonly Exclude<NonNull<'heat_exposure_level'>, 'unknown'>[];
  inverted: readonly Exclude<NonNull<'implementation_complexity'>, 'unknown'>[];
  yes_no: readonly Exclude<NonNull<'nearby_building_cooling_demand_relevant'>, 'unknown'>[];
};
