"""PCI-specific domain models and dataclasses."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class MaterialCircularityParameters:
    """Parameter set describing efficiencies for a material family/code."""

    material_key: str
    efficiency_feedstock_production: float
    efficiency_component_production: float
    recovered_fraction_feedstock_losses: float
    recovered_fraction_component_losses: float
    efficiency_material_separation_eol: float
    efficiency_recycled_feedstock_production: float
    notes: str = ""


@dataclass
class PCIMaterialInputs:
    """Inputs required for the PCI computation for a single material."""

    material_key: str
    mass: float
    reused_share: float
    recycled_content_share: float
    efficiency_feedstock_production: float
    efficiency_component_production: float
    recovered_fraction_feedstock_losses: float
    recovered_fraction_component_losses: float
    efficiency_material_separation_eol: float
    efficiency_recycled_feedstock_production: float
    collection_fraction_for_reuse: float
    collection_fraction_for_recycling: float


@dataclass
class PCIMaterialFlows:
    """Captures intermediate flow results for a material slice."""

    material_key: str
    mass: float
    reused_share: float
    recycled_content_share: float
    V: float
    W_fp: float
    W_cp: float
    W_u: float
    W_ms: float
    W_rfp: float
    W_total: float
    R_in: float
    R_fp: float
    R_cp: float
    R_EoL: float
    R_out: float
    R_net: float
    C_net: float
    V_linear: float
    W_linear: float
    LFI_material: float
    PCI_material: float


@dataclass
class PCIResult:
    """Aggregate PCI result for a product."""

    pci_product: float
    utility_factor: float
    lfi_product: float
    mass_total: float
    per_material_flows: List[PCIMaterialFlows] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
