"""BOM ingestion utilities."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable
import csv

from ..models.bom import BOMItem


class IngestionService:
    """Simple ingestion pipeline for CSV or JSON BOM files."""

    def load_bom_from_csv(self, path: Path) -> list[BOMItem]:
        """Load BOM items from a CSV file.

        This is intentionally light-weight; validation hooks can be added later.
        """

        items: list[BOMItem] = []
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                items.append(
                    BOMItem(
                        id=row["id"],
                        product_id=row["product_id"],
                        description=row.get("description", ""),
                        classification=row.get("classification"),
                        material_code=row.get("material_code"),
                        component_code=row.get("component_code"),
                        mass_kg=float(row.get("mass_kg", 0) or 0),
                        quantity=float(row.get("quantity", 1) or 1),
                        origin_country=row.get("origin_country"),
                        manufacturing_location=row.get("manufacturing_location"),
                        supplier_id=row.get("supplier_id"),
                        recycled_content_share=self._nullable_float(row.get("recycled_content_share")),
                        reused_share=self._nullable_float(row.get("reused_share")),
                        remanufactured_share=self._nullable_float(row.get("remanufactured_share")),
                        recyclability_rate=self._nullable_float(row.get("recyclability_rate")),
                        landfill_rate=self._nullable_float(row.get("landfill_rate")),
                        incineration_rate=self._nullable_float(row.get("incineration_rate")),
                    )
                )
        return items

    def _nullable_float(self, value: str | None) -> float | None:
        if value in (None, ""):
            return None
        return float(value)

    def load_bom_from_iterable(self, rows: Iterable[dict[str, str]]) -> list[BOMItem]:
        """Load BOM data from an iterable of dictionaries."""

        items: list[BOMItem] = []
        for row in rows:
            items.append(
                BOMItem(
                    id=row["id"],
                    product_id=row["product_id"],
                    description=row.get("description", ""),
                    classification=row.get("classification"),
                    material_code=row.get("material_code"),
                    component_code=row.get("component_code"),
                    mass_kg=float(row.get("mass_kg", 0) or 0),
                    quantity=float(row.get("quantity", 1) or 1),
                    origin_country=row.get("origin_country"),
                    manufacturing_location=row.get("manufacturing_location"),
                    supplier_id=row.get("supplier_id"),
                    recycled_content_share=self._nullable_float(row.get("recycled_content_share")),
                    reused_share=self._nullable_float(row.get("reused_share")),
                    remanufactured_share=self._nullable_float(row.get("remanufactured_share")),
                    recyclability_rate=self._nullable_float(row.get("recyclability_rate")),
                    landfill_rate=self._nullable_float(row.get("landfill_rate")),
                    incineration_rate=self._nullable_float(row.get("incineration_rate")),
                )
            )
        return items
