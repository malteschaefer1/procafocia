"""Method profile abstraction."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class MethodStandard(str, Enum):
    """High level standards."""

    PACT = "PACT"
    ISO14067 = "ISO14067"
    PEF = "PEF"
    TFS = "TfS"
    CATENAX = "Catena-X"
    CUSTOM = "CUSTOM"


class PCFMethodID(str, Enum):
    """Identifier for supported PCF methodologies."""

    PACT_V3 = "PACT_V3"
    ISO14067_GENERIC = "ISO14067_GENERIC"
    PEF_GENERIC = "PEF_GENERIC"
    TFS_CHEMICALS = "TFS_CHEMICALS"
    CATENAX_PCF = "CATENAX_PCF"


@dataclass
class MethodProfile:
    """Configuration metadata for how PCF should be calculated."""

    id: PCFMethodID
    name: str
    short_description: str
    reference_url: str
    standard: MethodStandard
    system_boundary: str
    life_cycle_stages_included: List[str]
    ghg_aggregation_method: Optional[str] = None
    pcf_output_schema: Optional[str] = None
    data_priority_hierarchy: Optional[List[str]] = None
    requires_dqr_scoring: bool = False
    notes: Optional[str] = None


PCF_METHOD_PROFILES: Dict[PCFMethodID, MethodProfile] = {
    PCFMethodID.PACT_V3: MethodProfile(
        id=PCFMethodID.PACT_V3,
        name="PACT Methodology V3",
        short_description=(
            "WBCSD PACT PCF Methodology V3, cradle-to-gate accounting + exchange format."
        ),
        reference_url="https://www.wbcsd.org/publications/pcf-methodology",
        standard=MethodStandard.PACT,
        system_boundary="cradle_to_gate",
        life_cycle_stages_included=[
            "raw_materials",
            "upstream_transport",
            "own_operations",
            "purchased_energy",
        ],
        ghg_aggregation_method="IPCC_AR6_GWP100",
        pcf_output_schema="PACT_PDS",
        data_priority_hierarchy=[
            "Primary data for own operations",
            "Primary or high-quality secondary for tier 1",
            "Secondary databases",
        ],
        requires_dqr_scoring=True,
        notes="See PACT Methodology V3 for details on data quality scoring and exchange requirements.",
    ),
    PCFMethodID.ISO14067_GENERIC: MethodProfile(
        id=PCFMethodID.ISO14067_GENERIC,
        name="ISO 14067 Generic",
        short_description="Generic ISO 14067 cradle-to-grave PCF approach.",
        reference_url="https://www.iso.org/standard/71206.html",
        standard=MethodStandard.ISO14067,
        system_boundary="cradle_to_grave",
        life_cycle_stages_included=[
            "raw_materials",
            "upstream_transport",
            "own_operations",
            "use_phase",
            "end_of_life",
        ],
        ghg_aggregation_method="IPCC_AR6_GWP100",
        pcf_output_schema="Generic_ISO14067",
        requires_dqr_scoring=False,
    ),
    PCFMethodID.PEF_GENERIC: MethodProfile(
        id=PCFMethodID.PEF_GENERIC,
        name="PEF Generic",
        short_description="EU Product Environmental Footprint (PEF) general guidance.",
        reference_url="https://environment.ec.europa.eu/topics/circular-economy/product-environmental-footprint-pef_en",
        standard=MethodStandard.PEF,
        system_boundary="cradle_to_grave",
        life_cycle_stages_included=[
            "raw_materials",
            "upstream_transport",
            "own_operations",
            "use_phase",
            "end_of_life",
        ],
        ghg_aggregation_method="EF3.0",
        pcf_output_schema="PEF",
        requires_dqr_scoring=False,
    ),
    PCFMethodID.TFS_CHEMICALS: MethodProfile(
        id=PCFMethodID.TFS_CHEMICALS,
        name="Together for Sustainability (TfS) PCF Guideline",
        short_description="TfS chemical-sector PCF guideline for cradle-to-gate footprints.",
        reference_url="https://tfs-initiative.com/pcf-guideline/",
        standard=MethodStandard.TFS,
        system_boundary="cradle_to_gate",
        life_cycle_stages_included=[
            "raw_materials",
            "upstream_transport",
            "own_operations",
            "purchased_energy",
        ],
        ghg_aggregation_method="IPCC_AR6_GWP100",
        pcf_output_schema="TfS_PCF",
        requires_dqr_scoring=False,
    ),
    PCFMethodID.CATENAX_PCF: MethodProfile(
        id=PCFMethodID.CATENAX_PCF,
        name="Catena-X PCF",
        short_description="Catena-X PCF specification for automotive supply chains.",
        reference_url="https://catena-x.net",
        standard=MethodStandard.CATENAX,
        system_boundary="cradle_to_gate",
        life_cycle_stages_included=[
            "raw_materials",
            "upstream_transport",
            "own_operations",
            "purchased_energy",
        ],
        ghg_aggregation_method="IPCC_AR6_GWP100",
        pcf_output_schema="CatenaX_PCF",
        requires_dqr_scoring=True,
    ),
}
