"""Default scenario definitions and material parameters."""
from __future__ import annotations

from copy import deepcopy


def default_material_parameters_dict() -> dict[str, dict[str, float]]:
    return {
        "Aluminum": {
            "material_key": "Aluminum",
            "efficiency_feedstock_production": 0.85,
            "efficiency_component_production": 0.9,
            "recovered_fraction_feedstock_losses": 0.6,
            "recovered_fraction_component_losses": 0.6,
            "efficiency_material_separation_eol": 0.85,
            "efficiency_recycled_feedstock_production": 0.9,
        },
        "Steel": {
            "material_key": "Steel",
            "efficiency_feedstock_production": 0.88,
            "efficiency_component_production": 0.93,
            "recovered_fraction_feedstock_losses": 0.7,
            "recovered_fraction_component_losses": 0.7,
            "efficiency_material_separation_eol": 0.9,
            "efficiency_recycled_feedstock_production": 0.93,
        },
        "Polymer": {
            "material_key": "Polymer",
            "efficiency_feedstock_production": 0.8,
            "efficiency_component_production": 0.9,
            "recovered_fraction_feedstock_losses": 0.4,
            "recovered_fraction_component_losses": 0.5,
            "efficiency_material_separation_eol": 0.7,
            "efficiency_recycled_feedstock_production": 0.65,
        },
        "Electronics": {
            "material_key": "Electronics",
            "efficiency_feedstock_production": 0.75,
            "efficiency_component_production": 0.85,
            "recovered_fraction_feedstock_losses": 0.5,
            "recovered_fraction_component_losses": 0.4,
            "efficiency_material_separation_eol": 0.6,
            "efficiency_recycled_feedstock_production": 0.5,
        },
        "ALU-6000": {
            "material_key": "Aluminum",
            "efficiency_feedstock_production": 0.85,
            "efficiency_component_production": 0.9,
            "recovered_fraction_feedstock_losses": 0.6,
            "recovered_fraction_component_losses": 0.6,
            "efficiency_material_separation_eol": 0.85,
            "efficiency_recycled_feedstock_production": 0.9,
        },
        "STL-FASTENER": {
            "material_key": "Steel",
            "efficiency_feedstock_production": 0.88,
            "efficiency_component_production": 0.93,
            "recovered_fraction_feedstock_losses": 0.7,
            "recovered_fraction_component_losses": 0.7,
            "efficiency_material_separation_eol": 0.9,
            "efficiency_recycled_feedstock_production": 0.93,
        },
        "ABS-HOUSING": {
            "material_key": "Polymer",
            "efficiency_feedstock_production": 0.8,
            "efficiency_component_production": 0.9,
            "recovered_fraction_feedstock_losses": 0.4,
            "recovered_fraction_component_losses": 0.5,
            "efficiency_material_separation_eol": 0.7,
            "efficiency_recycled_feedstock_production": 0.65,
        },
        "CU-WIRE": {
            "material_key": "Copper",
            "efficiency_feedstock_production": 0.9,
            "efficiency_component_production": 0.92,
            "recovered_fraction_feedstock_losses": 0.75,
            "recovered_fraction_component_losses": 0.75,
            "efficiency_material_separation_eol": 0.9,
            "efficiency_recycled_feedstock_production": 0.95,
        },
    }


def default_scenarios() -> list[dict]:
    params = default_material_parameters_dict()
    return [
        {
            "id": "default",
            "name": "EU Reference",
            "goal_scope": "Cradle-to-gate PCF",
            "system_boundary": "cradle-to-gate",
            "geography": "EU",
            "method_profile_id": "iso-basic",
            "pcf_method_id": "PACT_V3",
            "energy_mix_profile": "EU-avg",
            "end_of_life_model": "EU-2019",
            "collection_fraction_for_reuse": 0.15,
            "collection_fraction_for_recycling": 0.7,
            "utility_factor": 0.9,
            "material_parameters": deepcopy(params),
        }
    ]
