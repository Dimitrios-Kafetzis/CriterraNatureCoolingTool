"""Assessment input and result schemas.

``AssessmentInput`` is the complete, validated description of one site and one
proposed intervention. ``AssessmentResult`` is everything the engine reports
about it. Both are frozen: an input is never mutated during scoring, and a
result is never edited after assembly.

Two schema-wide conventions implement the methodology's missing-data policy
(Methodology Report section 6.3):

* Optional qualitative fields accept the explicit level ``"unknown"`` as well
  as ``None``. Both normalise to the neutral 50 and both count as *not
  supplied* for block confidence; every such default is itemised in
  ``assumptions_applied``.
* Optional quantitative fields are ``None`` when absent, and absence propagates
  to an explicit status (``not_estimated``, ``missing_energy_demand``, ...) —
  never to a silent zero.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from nature_cooling.engine.config import CategoryName, ConfidenceLevel

AssessmentScale = Literal["city", "district", "neighbourhood", "site", "building"]
ClimateZone = Literal["tropical_wet", "tropical_dry", "arid", "semi_arid", "temperate", "other"]
StandardLevel = Literal["low", "medium", "high", "very_high", "unknown"]
InvertedLevel = Literal["low", "medium", "high", "unknown"]
SoilAvailability = Literal["none", "limited", "moderate", "high", "unknown"]
IrrigationAvailability = Literal["none", "occasional", "reliable", "unknown"]
ShadeLevel = Literal["very_low", "low", "medium", "high", "unknown"]
YesNo = Literal["yes", "no", "unknown"]
LandUse = Literal[
    "street_corridor",
    "residential",
    "mixed_use",
    "commercial",
    "public_space",
    "park",
    "school",
    "healthcare",
    "industrial",
    "other",
]

ConditionLevel = Literal["poor", "moderate", "good", "excellent", "unknown"]
HeatPriorityCategory = Literal["low", "medium", "high", "critical"]
OpportunityCategory = Literal["low", "moderate", "strong", "high_priority"]
HeatIndexImprovement = Literal["low", "medium", "high"]
TimeToBenefit = Literal["immediate", "short_term", "medium_term", "long_term"]
EnergyStatus = Literal[
    "calculated",
    "not_applicable",
    "missing_energy_demand",
    "typology_not_applicable",
    "relevance_not_confirmed",
]
GhgStatus = Literal["calculated", "missing_emission_factor", "energy_not_calculated"]
AnnualSavingsStatus = Literal["calculated", "energy_not_calculated", "missing_energy_price"]
PaybackStatus = Literal["calculated", "missing_capital_cost", "annual_savings_unavailable"]
DerivedStatus = Literal["derived", "not_estimated"]
CalculatedStatus = Literal["calculated", "not_estimated"]
SuitabilityFlagCode = Literal[
    "below_minimum_area",
    "insufficient_soil",
    "insufficient_irrigation",
    "unsuitable_climate",
]
PaybackBracket = Literal["short", "medium", "long", "very_long"]
ReadinessLevel = Literal["low", "medium", "high"]


class _FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class AssessmentInput(_FrozenModel):
    """One site plus one proposed NbS intervention, as described by the user.

    Required fields are those without which a documented formula cannot be
    evaluated at all; everything else is optional, and absence reduces
    confidence but never blocks the assessment.
    """

    # Project information
    project_name: str | None = None
    assessment_scale: AssessmentScale
    country: str | None = Field(default=None, min_length=2, max_length=3)

    # Site characteristics
    site_area_m2: float = Field(gt=0)
    existing_tree_canopy_percent: float | None = Field(default=None, ge=0, le=100)
    existing_green_cover_percent: float | None = Field(default=None, ge=0, le=100)
    impervious_surface_percent: float | None = Field(default=None, ge=0, le=100)
    soil_availability: SoilAvailability | None = None
    irrigation_availability: IrrigationAvailability | None = None
    current_shade_level: ShadeLevel | None = None
    land_use: LandUse | None = None

    # Climate and heat exposure
    climate_zone: ClimateZone
    lst_anomaly_c: float | None = None
    heat_exposure_level: StandardLevel | None = None
    solar_exposure: StandardLevel | None = None
    heat_index_concern: StandardLevel | None = None

    # Vulnerability and equity
    population_density: StandardLevel | None = None
    vulnerable_population_presence: StandardLevel | None = None
    access_to_cooled_indoor_space: InvertedLevel | None = None
    safety_concern: StandardLevel | None = None
    public_accessibility: StandardLevel | None = None
    community_participation: StandardLevel | None = None

    # NbS intervention
    nbs_type: str
    intervention_area_m2: float | None = Field(default=None, gt=0)
    new_canopy_area_at_maturity_m2: float | None = Field(default=None, ge=0)
    expected_maturity_period_years: float | None = Field(default=None, ge=0)
    implementation_complexity: InvertedLevel | None = None
    maintenance_intensity: InvertedLevel | None = None

    # Co-benefit overrides (library defaults apply where absent)
    co_benefit_biodiversity: StandardLevel | None = None
    co_benefit_stormwater: StandardLevel | None = None
    co_benefit_public_health: StandardLevel | None = None
    co_benefit_social_inclusion: StandardLevel | None = None
    co_benefit_urban_quality: StandardLevel | None = None

    # Cost and energy
    nearby_building_cooling_demand_relevant: YesNo | None = None
    annual_cooling_energy_demand_kwh: float | None = Field(default=None, gt=0)
    energy_price_per_kwh: float | None = Field(default=None, gt=0)
    capital_cost: float | None = Field(default=None, gt=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    grid_emission_factor_kgco2e_per_kwh: float | None = Field(default=None, gt=0)


class TypologySummary(_FrozenModel):
    """The library values the assessment was computed against."""

    nbs_id: str
    nbs_type: str
    display_name: str
    category: CategoryName
    evidence_confidence: ConfidenceLevel
    base_cooling_score: float
    temp_reduction_min_c: float
    temp_reduction_max_c: float


class HeatExposureBlock(_FrozenModel):
    """Heat Exposure Score (Methodology Report 5.1)."""

    score: float
    path: Literal["data_rich", "data_poor"]


class VulnerabilityBlock(_FrozenModel):
    """Vulnerability Score (Methodology Report 5.2)."""

    score: float


class HeatPriorityBlock(_FrozenModel):
    """Heat Priority Index (Methodology Report 5.3)."""

    score: float
    category: HeatPriorityCategory


class AdjustmentCondition(_FrozenModel):
    """One derived site condition and the factor it resolved to."""

    level: ConditionLevel
    factor: float
    detail: str | None = None


class AdjustmentBlock(_FrozenModel):
    """Site adjustment factor and its four derived conditions (5.4)."""

    factor: float
    canopy: AdjustmentCondition
    soil_water: AdjustmentCondition
    scale: AdjustmentCondition
    climate: AdjustmentCondition


class SuitabilityFlag(_FrozenModel):
    """A hard 'not suitable for this site' condition (D-009)."""

    code: SuitabilityFlagCode
    message: str


class SuitabilityBlock(_FrozenModel):
    """NbS Suitability Score, its sub-indicators, and hard flags (D-022)."""

    score: float
    space: float
    soil: float
    water: float
    maintenance: float
    urban_context: float
    flags: list[SuitabilityFlag]
    suitable: bool


class CoolingBlock(_FrozenModel):
    """Cooling Potential Score and clipped temperature range (5.5, D-008)."""

    potential_score: float
    delta_t_min_c: float
    delta_t_max_c: float
    delta_t_midpoint_c: float
    heat_index_improvement: HeatIndexImprovement
    shade_potential_percent: float | None
    shade_potential_status: CalculatedStatus
    time_to_benefit: TimeToBenefit | None
    time_to_benefit_status: DerivedStatus


class EnergyBlock(_FrozenModel):
    """Derived cooling-energy savings (5.6, D-015)."""

    status: EnergyStatus
    status_message: str
    savings_min_kwh_per_year: float | None
    savings_max_kwh_per_year: float | None


class GhgBlock(_FrozenModel):
    """Greenhouse gas emissions avoided (5.7)."""

    status: GhgStatus
    avoided_min_kgco2e_per_year: float | None
    avoided_max_kgco2e_per_year: float | None
    emission_factor_kgco2e_per_kwh: float | None
    emission_factor_origin: Literal["user_supplied", "country_default"] | None


class CostsBlock(_FrozenModel):
    """Cost outputs: savings, payback, derived feasibility, readiness (5.8)."""

    annual_savings_status: AnnualSavingsStatus
    annual_savings_min: float | None
    annual_savings_max: float | None
    currency: str | None
    payback_status: PaybackStatus
    payback_years_min: float | None
    payback_years_max: float | None
    payback_years_central: float | None
    cost_feasibility_status: DerivedStatus
    cost_feasibility_score: float | None
    payback_bracket: PaybackBracket | None
    investment_readiness_status: DerivedStatus
    investment_readiness: ReadinessLevel | None


class CoBenefitsBlock(_FrozenModel):
    """Co-benefit Score and its five sub-indicators."""

    score: float
    biodiversity: float
    stormwater: float
    public_health: float
    social_inclusion: float
    urban_quality: float


class EquityBlock(_FrozenModel):
    """Equity Score (reported with its own confidence; not aggregated).

    The Equity Score deliberately does not enter the final aggregation:
    equity influences the headline score through the Vulnerability Score
    instead. This is disclosed in the Methodology Report.
    """

    score: float
    vulnerable_user_benefit: float
    public_accessibility: float
    safety_comfort: float
    participation_relevance: float


class OpportunityComponent(_FrozenModel):
    """One component of the final aggregation, with the weight applied."""

    name: str
    score: float
    nominal_weight: float
    applied_weight: float


class OpportunityBlock(_FrozenModel):
    """NbS Cooling Opportunity Score (5.9), with full weight transparency."""

    score: float
    category: OpportunityCategory
    components: list[OpportunityComponent]
    excluded_components: list[str]


class ConfidenceBlock(_FrozenModel):
    """Branched per-block confidence (D-011/OQ-09, D-024)."""

    cooling: ConfidenceLevel
    energy: ConfidenceLevel
    economic: ConfidenceLevel
    equity: ConfidenceLevel
    overall: ConfidenceLevel
    cooling_capped_by_evidence: bool
    completeness_percent: dict[str, float]


class AssessmentResult(_FrozenModel):
    """Everything the engine reports for one assessment run."""

    engine_version: str
    methodology_version: str
    typology: TypologySummary
    heat_exposure: HeatExposureBlock
    vulnerability: VulnerabilityBlock
    heat_priority: HeatPriorityBlock
    adjustment: AdjustmentBlock
    suitability: SuitabilityBlock
    cooling: CoolingBlock
    energy: EnergyBlock
    ghg: GhgBlock
    costs: CostsBlock
    co_benefits: CoBenefitsBlock
    equity: EquityBlock
    opportunity: OpportunityBlock
    confidence: ConfidenceBlock
    recommendation: str
    method_note: str
    assumptions_applied: list[str]
    warnings: list[str]
