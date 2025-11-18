"""Circularity engine definitions."""
from __future__ import annotations

from typing import Protocol

from ..models.bom import BOMItem
from ..models.pci import PCIResult
from ..models.product import Product
from ..models.scenario import Scenario


class CircularityEngine(Protocol):
    """Defines the interface for circularity (PCI) engines."""

    def calculate_pci(self, product: Product, bom: list[BOMItem], scenario: Scenario) -> PCIResult:
        raise NotImplementedError
