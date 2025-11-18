"""Simple in-memory state for demo purposes."""
from __future__ import annotations

from typing import Dict, List

from ..models.bom import BOMItem
from ..models.product import Product

products: Dict[str, Product] = {}
boms: Dict[str, List[BOMItem]] = {}
