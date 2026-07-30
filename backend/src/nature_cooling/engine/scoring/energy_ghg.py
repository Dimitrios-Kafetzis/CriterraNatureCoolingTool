"""Cooling-energy savings and avoided GHG emissions (Methodology Report 5.6-5.7).

Energy savings are derived from the tool's own cooling estimate
(``demand x delta-T x sensitivity``, akbari2001), never stored per typology
(D-015). All three preconditions are enforced; a quantity that cannot be
computed carries an explicit status, never a zero.
"""

from __future__ import annotations

from typing import Any, Literal

from nature_cooling.engine.config import MethodologyConfig, Typology
from nature_cooling.engine.models import (
    AssessmentInput,
    CoolingBlock,
    EnergyBlock,
    EnergyStatus,
    GhgBlock,
    GhgStatus,
)


def _energy_status(inp: AssessmentInput, typology: Typology) -> EnergyStatus:
    """Precedence: intervention-level facts before user-supplied data gaps."""
    if not typology.building_energy_applicable:
        return "typology_not_applicable"
    if inp.nearby_building_cooling_demand_relevant == "no":
        return "not_applicable"
    if inp.nearby_building_cooling_demand_relevant in (None, "unknown"):
        return "relevance_not_confirmed"
    if inp.annual_cooling_energy_demand_kwh is None:
        return "missing_energy_demand"
    return "calculated"


def compute_energy(
    inp: AssessmentInput, typology: Typology, cooling: CoolingBlock, config: MethodologyConfig
) -> EnergyBlock:
    """Return the energy block, calculated only when all preconditions hold."""
    status = _energy_status(inp, typology)
    message = str(config.energy_model["statuses"][status])
    if status != "calculated":
        return EnergyBlock(
            status=status,
            status_message=message,
            savings_min_kwh_per_year=None,
            savings_max_kwh_per_year=None,
        )

    assert inp.annual_cooling_energy_demand_kwh is not None
    sensitivity: dict[str, Any] = config.energy_model["derivation"]["sensitivity_per_c"]
    demand = inp.annual_cooling_energy_demand_kwh
    savings_min = demand * cooling.delta_t_min_c * float(sensitivity["min"])
    savings_max = demand * cooling.delta_t_max_c * float(sensitivity["max"])
    return EnergyBlock(
        status=status,
        status_message=message,
        savings_min_kwh_per_year=round(savings_min, 1),
        savings_max_kwh_per_year=round(savings_max, 1),
    )


def _emission_factor(
    inp: AssessmentInput, config: MethodologyConfig
) -> tuple[float, Literal["user_supplied", "country_default"]] | None:
    if inp.grid_emission_factor_kgco2e_per_kwh is not None:
        return inp.grid_emission_factor_kgco2e_per_kwh, "user_supplied"
    countries: dict[str, Any] = config.country_defaults["countries"] or {}
    if inp.country is not None and inp.country in countries:
        entry = countries[inp.country]["electricity_emission_factor_kgco2e_per_kwh"]
        return float(entry["value"]), "country_default"
    return None


def compute_ghg(inp: AssessmentInput, energy: EnergyBlock, config: MethodologyConfig) -> GhgBlock:
    """Return the GHG block: energy savings times the grid emission factor."""
    status: GhgStatus
    if energy.status != "calculated":
        return GhgBlock(
            status="energy_not_calculated",
            avoided_min_kgco2e_per_year=None,
            avoided_max_kgco2e_per_year=None,
            emission_factor_kgco2e_per_kwh=None,
            emission_factor_origin=None,
        )
    factor = _emission_factor(inp, config)
    if factor is None:
        return GhgBlock(
            status="missing_emission_factor",
            avoided_min_kgco2e_per_year=None,
            avoided_max_kgco2e_per_year=None,
            emission_factor_kgco2e_per_kwh=None,
            emission_factor_origin=None,
        )
    value, origin = factor
    assert energy.savings_min_kwh_per_year is not None
    assert energy.savings_max_kwh_per_year is not None
    status = "calculated"
    return GhgBlock(
        status=status,
        avoided_min_kgco2e_per_year=round(energy.savings_min_kwh_per_year * value, 1),
        avoided_max_kgco2e_per_year=round(energy.savings_max_kwh_per_year * value, 1),
        emission_factor_kgco2e_per_kwh=value,
        emission_factor_origin=origin,
    )
