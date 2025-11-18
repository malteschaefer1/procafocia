"""Schemas for PCI result payloads."""
from __future__ import annotations

from pydantic import BaseModel, Field


class PCIMaterialFlowsSchema(BaseModel):
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


class PCIResultSchema(BaseModel):
    pci_product: float
    utility_factor: float
    lfi_product: float
    mass_total: float
    per_material_flows: list[PCIMaterialFlowsSchema] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
