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
export type TypologySummary = Schemas['TypologySummary'];
export type ComponentBlock = Schemas['ComponentBlock'];
export type PackageBlock = Schemas['PackageBlock'];
export type ProjectSummary = Schemas['ProjectSummary'];
export type ProjectView = Schemas['ProjectView'];
export type AssessmentView = Schemas['AssessmentView'];
export type GeoLookupResponse = Schemas['GeoLookupResponse'];
export type GeoLookupRequest = Schemas['GeoLookupRequest'];
export type ConfidenceLevel = BlockConfidencePreview['level'];

/** The five element families and the composite families, exactly as served. */
export type TypologyFamily = Typology['family'];

/**
 * The site conditions `GET /api/typologies/available` gates on (D-043,
 * D-044.1). Assembled from a draft; every value is passed through untouched,
 * because the frontend computes no availability rule of its own — it asks.
 */
export interface AvailabilityQuery {
  assessment_scale: NonNullable<AssessmentInput['assessment_scale']>;
  land_use?: AssessmentInput['land_use'];
  waterfront_type?: AssessmentInput['waterfront_type'];
  includes_railway?: boolean | undefined;
  existing_woodland?: boolean | undefined;
  productive_governance?: AssessmentInput['productive_governance'];
}

/**
 * `GET /api/typologies/available` (D-043, D-044.1).
 *
 * Generated from the service's own response model, like every other response
 * shape: the service is the single source of truth and CI fails on drift.
 * `nbs_types` is rendered exactly as ordered there. It is not a permission
 * list — an entry absent from it stays fully selectable (D-019).
 */
export type AvailableTypologies = components['schemas']['AvailableTypologies'];

/**
 * A draft questionnaire state: any subset of the engine's input fields
 * (D-029 — drafts are stored as partial JSON and validated as a complete
 * `AssessmentInput` only at explicit evaluation).
 */
export type DraftInput = Partial<AssessmentInput>;

export type InputField = keyof AssessmentInput;

/**
 * Which of a draft's answers the map filled in, and from which dataset
 * (D-047.2). Kept beside the draft rather than inside it, because the engine's
 * input fields hold answers and the engine has no concept of where one came
 * from — nor should it, since an autofilled value counts as supplied exactly
 * as a typed one does. The provenance exists for the reader of the report.
 */
export type AutofillSources = Record<string, string>;

/**
 * `GET /api/geo/basemap` returns the bundled outlines verbatim — the browser
 * draws them and interprets nothing, so the endpoint is typed as the raw
 * document rather than as a model.
 */
export interface BasemapOutline {
  iso_a2: string;
  polygons: number[][][][];
}

export interface BasemapDocument {
  scale: string;
  licence: string;
  attribution: string;
  countries: BasemapOutline[];
  unassigned: { polygons: number[][][][] }[];
}

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
