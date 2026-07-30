/**
 * The form body of one questionnaire step. Field placement per steps.ts
 * (D-031); every optional field is skippable in one click and offers the
 * explicit "unknown" level the methodology distinguishes from a skip.
 */

import { useState } from 'react';
import { LevelField, NumberField, TextField } from '../components/FieldControls';
import { messages } from '../i18n/en';
import { OPTIONS, type StepId } from './steps';
import { TypologyPicker } from './TypologyPicker';
import type {
  AssessmentInput,
  DraftInput,
  InputField,
  MethodologyData,
  TypologyLibrary,
} from '../api/types';

export interface StepFormProps {
  step: StepId;
  draft: DraftInput;
  errors: Partial<Record<string, string>>;
  setField: <F extends InputField>(field: F, value: AssessmentInput[F] | undefined) => void;
  library: TypologyLibrary | null;
  methodology: MethodologyData | null;
}

export function StepForm(props: StepFormProps) {
  switch (props.step) {
    case 'project':
      return <ProjectStep {...props} />;
    case 'site':
      return <SiteStep {...props} />;
    case 'climate':
      return <ClimateStep {...props} />;
    case 'vulnerability':
      return <VulnerabilityStep {...props} />;
    case 'intervention':
      return <InterventionStep {...props} />;
    case 'cost':
      return <CostStep {...props} />;
  }
}

function ProjectStep({ draft, errors, setField }: StepFormProps) {
  return (
    <fieldset>
      <TextField
        field="project_name"
        value={draft.project_name}
        error={errors.project_name}
        onChange={(value) => setField('project_name', value)}
      />
      <LevelField
        field="assessment_scale"
        required
        value={draft.assessment_scale}
        options={OPTIONS.assessment_scale}
        withUnknown={false}
        error={errors.assessment_scale}
        onChange={(value) =>
          setField('assessment_scale', value as AssessmentInput['assessment_scale'] | undefined)
        }
      />
      <TextField
        field="country"
        value={draft.country}
        error={errors.country}
        onChange={(value) => setField('country', value)}
      />
    </fieldset>
  );
}

function SiteStep({ draft, errors, setField }: StepFormProps) {
  return (
    <fieldset>
      <NumberField
        field="site_area_m2"
        required
        value={draft.site_area_m2}
        error={errors.site_area_m2}
        onChange={(value) => setField('site_area_m2', value as number)}
      />
      <NumberField
        field="existing_tree_canopy_percent"
        value={draft.existing_tree_canopy_percent}
        error={errors.existing_tree_canopy_percent}
        onChange={(value) => setField('existing_tree_canopy_percent', value)}
      />
      <NumberField
        field="existing_green_cover_percent"
        value={draft.existing_green_cover_percent}
        error={errors.existing_green_cover_percent}
        onChange={(value) => setField('existing_green_cover_percent', value)}
      />
      <NumberField
        field="impervious_surface_percent"
        value={draft.impervious_surface_percent}
        error={errors.impervious_surface_percent}
        onChange={(value) => setField('impervious_surface_percent', value)}
      />
      <LevelField
        field="soil_availability"
        value={draft.soil_availability}
        options={OPTIONS.soil_availability}
        error={errors.soil_availability}
        onChange={(value) =>
          setField('soil_availability', value as AssessmentInput['soil_availability'] | undefined)
        }
      />
      <LevelField
        field="irrigation_availability"
        value={draft.irrigation_availability}
        options={OPTIONS.irrigation_availability}
        error={errors.irrigation_availability}
        onChange={(value) =>
          setField(
            'irrigation_availability',
            value as AssessmentInput['irrigation_availability'] | undefined,
          )
        }
      />
      <LevelField
        field="current_shade_level"
        value={draft.current_shade_level}
        options={OPTIONS.current_shade_level}
        error={errors.current_shade_level}
        onChange={(value) =>
          setField(
            'current_shade_level',
            value as AssessmentInput['current_shade_level'] | undefined,
          )
        }
      />
      <LevelField
        field="land_use"
        value={draft.land_use}
        options={OPTIONS.land_use}
        withUnknown={false}
        error={errors.land_use}
        onChange={(value) => setField('land_use', value as AssessmentInput['land_use'] | undefined)}
      />
    </fieldset>
  );
}

function ClimateStep({ draft, errors, setField }: StepFormProps) {
  return (
    <fieldset>
      <LevelField
        field="climate_zone"
        required
        value={draft.climate_zone}
        options={OPTIONS.climate_zone}
        withUnknown={false}
        error={errors.climate_zone}
        onChange={(value) =>
          setField('climate_zone', value as AssessmentInput['climate_zone'] | undefined)
        }
      />
      <NumberField
        field="lst_anomaly_c"
        value={draft.lst_anomaly_c}
        error={errors.lst_anomaly_c}
        onChange={(value) => setField('lst_anomaly_c', value)}
      />
      <LevelField
        field="heat_exposure_level"
        value={draft.heat_exposure_level}
        options={OPTIONS.standard}
        error={errors.heat_exposure_level}
        onChange={(value) =>
          setField(
            'heat_exposure_level',
            value as AssessmentInput['heat_exposure_level'] | undefined,
          )
        }
      />
      <LevelField
        field="solar_exposure"
        value={draft.solar_exposure}
        options={OPTIONS.standard}
        error={errors.solar_exposure}
        onChange={(value) =>
          setField('solar_exposure', value as AssessmentInput['solar_exposure'] | undefined)
        }
      />
    </fieldset>
  );
}

const VULNERABILITY_FIELDS = [
  'population_density',
  'vulnerable_population_presence',
  'access_to_cooled_indoor_space',
  'safety_concern',
  'public_accessibility',
  'community_participation',
] as const;

function VulnerabilityStep({ draft, errors, setField }: StepFormProps) {
  return (
    <fieldset>
      {VULNERABILITY_FIELDS.map((field) => (
        <LevelField
          key={field}
          field={field}
          value={draft[field]}
          options={field === 'access_to_cooled_indoor_space' ? OPTIONS.inverted : OPTIONS.standard}
          error={errors[field]}
          onChange={(value) => setField(field, value as (typeof draft)[typeof field])}
        />
      ))}
    </fieldset>
  );
}

const CO_BENEFIT_FIELDS = [
  'co_benefit_biodiversity',
  'co_benefit_stormwater',
  'co_benefit_public_health',
  'co_benefit_social_inclusion',
  'co_benefit_urban_quality',
] as const;

function InterventionStep({ draft, errors, setField, library, methodology }: StepFormProps) {
  if (!library || !methodology) {
    return <p className="muted">{messages.app.loading}</p>;
  }
  return (
    <fieldset>
      {errors.nbs_type ? <p className="error-text">{errors.nbs_type}</p> : null}
      <TypologyPicker
        library={library}
        methodology={methodology}
        draft={draft}
        onSelect={(nbsType) => setField('nbs_type', nbsType)}
      />
      {draft.nbs_type ? (
        <>
          <h3>{messages.picker.sizingHeading}</h3>
          <NumberField
            field="intervention_area_m2"
            value={draft.intervention_area_m2}
            error={errors.intervention_area_m2}
            onChange={(value) => setField('intervention_area_m2', value)}
          />
          <NumberField
            field="new_canopy_area_at_maturity_m2"
            value={draft.new_canopy_area_at_maturity_m2}
            error={errors.new_canopy_area_at_maturity_m2}
            onChange={(value) => setField('new_canopy_area_at_maturity_m2', value)}
          />
          <NumberField
            field="expected_maturity_period_years"
            value={draft.expected_maturity_period_years}
            error={errors.expected_maturity_period_years}
            onChange={(value) => setField('expected_maturity_period_years', value)}
          />
          <LevelField
            field="implementation_complexity"
            value={draft.implementation_complexity}
            options={OPTIONS.inverted}
            error={errors.implementation_complexity}
            onChange={(value) =>
              setField(
                'implementation_complexity',
                value as AssessmentInput['implementation_complexity'] | undefined,
              )
            }
          />
          <LevelField
            field="maintenance_intensity"
            value={draft.maintenance_intensity}
            options={OPTIONS.inverted}
            error={errors.maintenance_intensity}
            onChange={(value) =>
              setField(
                'maintenance_intensity',
                value as AssessmentInput['maintenance_intensity'] | undefined,
              )
            }
          />
          <details className="collapsible">
            <summary>{messages.cost.coBenefits}</summary>
            <p className="field__help">{messages.cost.coBenefitsHelp}</p>
            {CO_BENEFIT_FIELDS.map((field) => (
              <LevelField
                key={field}
                field={field}
                value={draft[field]}
                options={OPTIONS.standard}
                error={errors[field]}
                onChange={(value) => setField(field, value as (typeof draft)[typeof field])}
              />
            ))}
          </details>
        </>
      ) : null}
    </fieldset>
  );
}

const COST_VALUE_FIELDS = [
  'annual_cooling_energy_demand_kwh',
  'energy_price_per_kwh',
  'capital_cost',
  'currency',
  'grid_emission_factor_kgco2e_per_kwh',
] as const;

function CostStep({ draft, errors, setField }: StepFormProps) {
  const anySupplied =
    draft.nearby_building_cooling_demand_relevant != null ||
    COST_VALUE_FIELDS.some((field) => draft[field] != null);
  const [gateOpen, setGateOpen] = useState<boolean | null>(anySupplied ? true : null);
  const open = gateOpen ?? anySupplied;

  return (
    <fieldset>
      <div className="field">
        <span className="field__label" id="cost-gate-label">
          {messages.cost.gate}
        </span>
        <div role="group" aria-labelledby="cost-gate-label" className="actions-row">
          <button
            type="button"
            className={open ? 'button' : 'button button--quiet'}
            aria-pressed={open}
            onClick={() => setGateOpen(true)}
          >
            {messages.cost.gateYes}
          </button>
          <button
            type="button"
            className={gateOpen === false ? 'button' : 'button button--quiet'}
            aria-pressed={gateOpen === false}
            onClick={() => setGateOpen(false)}
          >
            {messages.cost.gateNo}
          </button>
        </div>
      </div>

      {gateOpen === false ? <p className="notice">{messages.cost.gateSkipNote}</p> : null}

      {open ? (
        <>
          <LevelField
            field="nearby_building_cooling_demand_relevant"
            value={draft.nearby_building_cooling_demand_relevant}
            options={OPTIONS.yes_no}
            error={errors.nearby_building_cooling_demand_relevant}
            onChange={(value) =>
              setField(
                'nearby_building_cooling_demand_relevant',
                value as AssessmentInput['nearby_building_cooling_demand_relevant'] | undefined,
              )
            }
          />
          <NumberField
            field="annual_cooling_energy_demand_kwh"
            value={draft.annual_cooling_energy_demand_kwh}
            error={errors.annual_cooling_energy_demand_kwh}
            onChange={(value) => setField('annual_cooling_energy_demand_kwh', value)}
          />
          <NumberField
            field="energy_price_per_kwh"
            value={draft.energy_price_per_kwh}
            error={errors.energy_price_per_kwh}
            onChange={(value) => setField('energy_price_per_kwh', value)}
          />
          <NumberField
            field="capital_cost"
            value={draft.capital_cost}
            error={errors.capital_cost}
            onChange={(value) => setField('capital_cost', value)}
          />
          <TextField
            field="currency"
            value={draft.currency}
            error={errors.currency}
            onChange={(value) => setField('currency', value)}
          />
          <NumberField
            field="grid_emission_factor_kgco2e_per_kwh"
            value={draft.grid_emission_factor_kgco2e_per_kwh}
            error={errors.grid_emission_factor_kgco2e_per_kwh}
            onChange={(value) => setField('grid_emission_factor_kgco2e_per_kwh', value)}
          />
        </>
      ) : null}
    </fieldset>
  );
}
