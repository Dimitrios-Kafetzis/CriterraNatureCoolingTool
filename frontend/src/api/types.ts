/**
 * Aliases over the generated OpenAPI types (D-030: generated, never
 * hand-written — `schema.ts` is produced from the service's schema and
 * committed; CI regenerates and fails on drift).
 */

import type { components } from './schema';

export type Schemas = components['schemas'];

export type AssessmentInput = Schemas['AssessmentInput'];
export type AssessmentResult = Schemas['AssessmentResult'];
export type ValidateResponse = Schemas['ValidateResponse'];
export type ConfidencePreview = Schemas['ConfidencePreview'];
export type BlockConfidencePreview = Schemas['BlockConfidencePreview'];
export type FieldIssue = Schemas['FieldIssue'];
export type MetaResponse = Schemas['MetaResponse'];
export type TypologyLibrary = Schemas['TypologyLibrary'];
export type Typology = Schemas['Typology'];
export type ProjectSummary = Schemas['ProjectSummary'];
export type ProjectView = Schemas['ProjectView'];
export type AssessmentView = Schemas['AssessmentView'];
export type ConfidenceLevel = BlockConfidencePreview['level'];

/**
 * A draft questionnaire state: any subset of the engine's input fields
 * (D-029 — drafts are stored as partial JSON and validated as a complete
 * `AssessmentInput` only at explicit evaluation).
 */
export type DraftInput = Partial<AssessmentInput>;

export type InputField = keyof AssessmentInput;

/**
 * The stored result of an evaluated assessment.
 *
 * The storage schema deliberately types `result` as an opaque JSON object
 * (stored results are never re-validated against later engine schemas,
 * D-029), so the OpenAPI type is `unknown`-shaped. Results only ever enter
 * storage from the engine, so reading one back as `AssessmentResult` is the
 * single narrowing this client performs.
 */
export function storedResult(assessment: AssessmentView): AssessmentResult | null {
  return (assessment.result as AssessmentResult | null | undefined) ?? null;
}

/**
 * `GET /api/methodology` returns the loaded configuration verbatim
 * (`dict[str, Any]` — the YAML documents themselves, schema-free by design:
 * the methodology is data, not code). This type names only the parts the
 * methodology browser addresses directly; everything else is rendered
 * generically as a configuration tree.
 */
export interface MethodologyData {
  version: string;
  weights: Record<string, unknown>;
  adjustment_factors: Record<string, unknown>;
  input_mapping: Record<string, unknown>;
  energy_model: Record<string, unknown>;
  country_defaults: Record<string, unknown>;
  derived_scores: {
    score_bands?: Record<string, ScoreBand[]>;
    confidence?: Record<string, unknown>;
    suitability_sub_indicators?: {
      requirement_match?: {
        soil_ranks?: Record<string, number>;
        irrigation_ranks?: Record<string, number>;
      };
    };
    [key: string]: unknown;
  };
  recommendation_templates: Record<string, unknown>;
}

export interface ScoreBand {
  min?: number;
  max?: number;
  label: string;
}
