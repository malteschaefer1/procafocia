"""Method profile abstraction."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MethodStandard(str, Enum):
    """Known PCF standards for quick filtering."""

    PACT = "PACT"
    ISO14067 = "ISO14067"
    CUSTOM = "CUSTOM"


@dataclass
class MethodProfile:
    """Configuration for how PCF/PCI results should be calculated."""

    id: str
    name: str
    standard: MethodStandard
    boundary: str
    allocation_rules: str
    recycling_handling: str
    cut_off_rules: str
    notes: str = ""
