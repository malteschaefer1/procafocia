"""Circularity engine definitions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ..models.bom import BOMItem
from ..models.product import Product
from ..models.scenario import Scenario


@dataclass
class CircularityResult:
    """Container for PCI outputs."""

    pci_score: float
    sub_indicators: dict[str, float]
    notes: list[str]


class CircularityEngine(Protocol):
    """Defines the interface for circularity (PCI) engines."""

    def calculate_pci(self, product: Product, bom: list[BOMItem], scenario: Scenario, pci_profile: dict | None = None) -> CircularityResult:
        raise NotImplementedError
