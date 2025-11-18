"""PCI implementation following Bracquene et al. (2020)."""
from __future__ import annotations

from dataclasses import replace
from typing import Dict, List

from ..models.bom import BOMItem
from ..models.pci import PCIMaterialFlows, PCIMaterialInputs, PCIResult
from ..models.product import Product
from ..models.scenario import Scenario
from .circularity_engine_base import CircularityEngine

EPS = 1e-9


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


class Bracquene2020CircularityEngine(CircularityEngine):
    """Implements the PCI and LFI formulation from Bracquené et al. (2020)."""

    def calculate_pci(self, product: Product, bom: list[BOMItem], scenario: Scenario) -> PCIResult:
        utility_factor = scenario.compute_utility_factor()
        per_material: List[PCIMaterialFlows] = []
        total_mass = 0.0
        aggregated = {"V": 0.0, "W": 0.0, "R_net": 0.0, "C_net": 0.0, "V_linear": 0.0, "W_linear": 0.0}
        weighted_pci = 0.0

        for item in bom:
            mass = (item.mass_kg or 0) * (item.quantity or 0)
            if mass <= 0:
                continue
            params = self._resolve_material_parameters(item, scenario)
            if not params:
                raise ValueError(f"Missing material parameters for {item.material_code or item.material_family}")
            inputs = PCIMaterialInputs(
                material_key=item.material_code or item.material_family or item.id,
                mass=mass,
                reused_share=_clamp(item.reused_share or 0.0),
                recycled_content_share=_clamp(item.recycled_content_share or 0.0),
                efficiency_feedstock_production=_clamp(params.efficiency_feedstock_production),
                efficiency_component_production=_clamp(params.efficiency_component_production),
                recovered_fraction_feedstock_losses=_clamp(params.recovered_fraction_feedstock_losses),
                recovered_fraction_component_losses=_clamp(params.recovered_fraction_component_losses),
                efficiency_material_separation_eol=_clamp(params.efficiency_material_separation_eol),
                efficiency_recycled_feedstock_production=_clamp(params.efficiency_recycled_feedstock_production),
                collection_fraction_for_reuse=_clamp(scenario.collection_fraction_for_reuse),
                collection_fraction_for_recycling=_clamp(scenario.collection_fraction_for_recycling),
            )
            flows = self._compute_material_flows(inputs, utility_factor)
            per_material.append(flows)
            total_mass += mass
            weighted_pci += flows.PCI_material * mass
            aggregated["V"] += flows.V
            aggregated["W"] += flows.W_total
            aggregated["R_net"] += flows.R_net
            aggregated["C_net"] += flows.C_net
            aggregated["V_linear"] += flows.V_linear
            aggregated["W_linear"] += flows.W_linear

        lfi_denom = max(aggregated["V_linear"] + aggregated["W_linear"], EPS)
        lfi_product = (aggregated["V"] + aggregated["W"] + abs(aggregated["R_net"]) + abs(aggregated["C_net"])) / lfi_denom
        pci_product = 0.0
        if total_mass > 0:
            pci_product = max(0.0, 1.0 - (lfi_product / max(utility_factor, EPS)))
            pci_product = min(1.0, pci_product)

        if total_mass > 0 and per_material:
            pci_mass_weighted = weighted_pci / total_mass
            # Align aggregated PCI with per-material weighting to avoid rounding discrepancies
            pci_product = min(1.0, max(0.0, pci_mass_weighted))

        notes = [
            "PCI derived from Bracquené et al. (2020) mass flow equations",
            "Utility factor defaults to 1 if not provided",
        ]

        return PCIResult(
            pci_product=pci_product,
            utility_factor=utility_factor,
            lfi_product=lfi_product,
            mass_total=total_mass,
            per_material_flows=per_material,
            notes=notes,
        )

    # --- helpers ---
    def _resolve_material_parameters(self, item: BOMItem, scenario: Scenario):
        key_candidates = [item.material_code, item.material_family]
        for key in key_candidates:
            if key and key in scenario.material_parameters:
                return scenario.material_parameters[key]
        if scenario.material_parameters:
            default_key = next(iter(scenario.material_parameters))
            return scenario.material_parameters[default_key]
        return None

    def _compute_material_flows(self, inputs: PCIMaterialInputs, utility_factor: float) -> PCIMaterialFlows:
        actual = self._flow_terms(inputs)
        linear_inputs = replace(
            inputs,
            reused_share=0.0,
            recycled_content_share=0.0,
            collection_fraction_for_reuse=0.0,
            collection_fraction_for_recycling=0.0,
        )
        linear = self._flow_terms(linear_inputs)
        denom = max(linear["V"] + linear["W_total"], EPS)
        lfi = (actual["V"] + actual["W_total"] + abs(actual["R_net"]) + abs(actual["C_net"])) / denom
        pci_material = max(0.0, 1.0 - (lfi / max(utility_factor, EPS)))
        pci_material = min(1.0, pci_material)

        return PCIMaterialFlows(
            material_key=inputs.material_key,
            mass=inputs.mass,
            reused_share=inputs.reused_share,
            recycled_content_share=inputs.recycled_content_share,
            V=actual["V"],
            W_fp=actual["W_fp"],
            W_cp=actual["W_cp"],
            W_u=actual["W_u"],
            W_ms=actual["W_ms"],
            W_rfp=actual["W_rfp"],
            W_total=actual["W_total"],
            R_in=actual["R_in"],
            R_fp=actual["R_fp"],
            R_cp=actual["R_cp"],
            R_EoL=actual["R_EoL"],
            R_out=actual["R_out"],
            R_net=actual["R_net"],
            C_net=actual["C_net"],
            V_linear=linear["V"],
            W_linear=linear["W_total"],
            LFI_material=lfi,
            PCI_material=pci_material,
        )

    def _flow_terms(self, inputs: PCIMaterialInputs) -> Dict[str, float]:
        mass = max(inputs.mass, 0.0)
        Fu = _clamp(inputs.reused_share)
        Fr = _clamp(inputs.recycled_content_share)
        E_cp = max(_clamp(inputs.efficiency_component_production), EPS)
        E_fp = max(_clamp(inputs.efficiency_feedstock_production), EPS)
        C_cp = _clamp(inputs.recovered_fraction_component_losses)
        C_fp = _clamp(inputs.recovered_fraction_feedstock_losses)
        E_ms = _clamp(inputs.efficiency_material_separation_eol)
        E_rfp = _clamp(inputs.efficiency_recycled_feedstock_production)
        C_u = _clamp(inputs.collection_fraction_for_reuse)
        C_r = _clamp(inputs.collection_fraction_for_recycling)

        net_new_mass = mass * max(1.0 - Fu, 0.0)
        component_input = net_new_mass / E_cp if net_new_mass > 0 else 0.0
        feedstock_input = component_input / E_fp if component_input > 0 else 0.0
        R_in = Fr * feedstock_input
        V = max(feedstock_input - R_in, 0.0)

        component_waste_total = max(component_input - net_new_mass, 0.0)
        feedstock_waste_total = max(feedstock_input - component_input, 0.0)
        W_cp = component_waste_total * (1 - C_cp)
        R_cp = component_waste_total * C_cp
        W_fp = feedstock_waste_total * (1 - C_fp)
        R_fp = feedstock_waste_total * C_fp

        W_u = mass * max(1.0 - C_u - C_r, 0.0)
        mass_rec = mass * C_r
        mass_after_sep = mass_rec * E_ms
        W_ms = mass_rec * (1 - E_ms)
        mass_after_rfp = mass_after_sep * E_rfp
        W_rfp = mass_after_sep * (1 - E_rfp)
        R_EoL = mass_after_rfp

        W_total = W_fp + W_cp + W_u + W_ms + W_rfp
        R_out = R_fp + R_cp + R_EoL
        R_net = R_in - R_out
        C_net = mass * (Fu - C_u)

        return {
            "V": V,
            "W_fp": W_fp,
            "W_cp": W_cp,
            "W_u": W_u,
            "W_ms": W_ms,
            "W_rfp": W_rfp,
            "W_total": W_total,
            "R_in": R_in,
            "R_fp": R_fp,
            "R_cp": R_cp,
            "R_EoL": R_EoL,
            "R_out": R_out,
            "R_net": R_net,
            "C_net": C_net,
        }
