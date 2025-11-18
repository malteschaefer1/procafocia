"""Repositories for product and BOM persistence."""
from __future__ import annotations

from typing import Callable, Iterable

from sqlalchemy import delete, select

from ..db.base import get_session
from ..db.models import BOMItemModel, ProductModel
from ..models.bom import BOMItem
from ..models.product import Product


class ProductRepository:
    def __init__(self, session_factory: Callable = get_session):
        self._session_factory = session_factory

    # Product operations
    def list_products(self) -> list[Product]:
        with self._session_factory() as session:
            models = session.scalars(select(ProductModel)).all()
            return [self._to_domain_product(model) for model in models]

    def create_product(self, product: Product) -> Product:
        with self._session_factory() as session:
            existing = session.get(ProductModel, product.id)
            if existing:
                raise ValueError("Product already exists")
            model = ProductModel(
                id=product.id,
                name=product.name,
                version=product.version,
                functional_unit=product.functional_unit,
                lifetime_years=product.lifetime_years,
                use_profile=product.use_profile,
            )
            session.add(model)
            session.commit()
            session.refresh(model)
            return self._to_domain_product(model)

    def get_product(self, product_id: str) -> Product | None:
        with self._session_factory() as session:
            model = session.get(ProductModel, product_id)
            if not model:
                return None
            return self._to_domain_product(model)

    # BOM operations
    def replace_bom(self, product_id: str, items: Iterable[BOMItem]) -> list[BOMItem]:
        with self._session_factory() as session:
            product = session.get(ProductModel, product_id)
            if not product:
                raise ValueError("Product not found")
            session.execute(delete(BOMItemModel).where(BOMItemModel.product_id == product_id))
            for item in items:
                session.add(self._to_model_bom(item))
            session.commit()
        return list(items)

    def get_bom(self, product_id: str) -> list[BOMItem]:
        with self._session_factory() as session:
            models = session.scalars(select(BOMItemModel).where(BOMItemModel.product_id == product_id)).all()
            return [self._to_domain_bom(model) for model in models]

    # Conversion helpers
    def _to_domain_product(self, model: ProductModel) -> Product:
        return Product(
            id=model.id,
            name=model.name,
            version=model.version,
            functional_unit=model.functional_unit,
            lifetime_years=model.lifetime_years,
            use_profile=model.use_profile,
        )

    def _to_domain_bom(self, model: BOMItemModel) -> BOMItem:
        return BOMItem(
            id=model.id,
            product_id=model.product_id,
            parent_bom_item_id=model.parent_bom_item_id,
            description=model.description,
            quantity=model.quantity,
            unit=model.unit,
            mass_kg=model.mass_kg,
            material_family=model.material_family,
            material_code=model.material_code,
            classification_unspsc=model.classification_unspsc,
            supplier_id=model.supplier_id,
            component_code=model.component_code,
            recycled_content_share=model.recycled_content_share,
            reused_share=model.reused_share,
            remanufactured_share=model.remanufactured_share,
            recyclability_rate=model.recyclability_rate,
            landfill_rate=model.landfill_rate,
            incineration_rate=model.incineration_rate,
            country_of_origin=model.country_of_origin,
            manufacturing_location=model.manufacturing_location,
            lci_dataset_id=model.lci_dataset_id,
        )

    def _to_model_bom(self, item: BOMItem) -> BOMItemModel:
        return BOMItemModel(
            id=item.id,
            product_id=item.product_id,
            parent_bom_item_id=item.parent_bom_item_id,
            description=item.description,
            quantity=item.quantity,
            unit=item.unit,
            mass_kg=item.mass_kg,
            material_family=item.material_family,
            material_code=item.material_code,
            classification_unspsc=item.classification_unspsc,
            supplier_id=item.supplier_id,
            component_code=item.component_code,
            recycled_content_share=item.recycled_content_share,
            reused_share=item.reused_share,
            remanufactured_share=item.remanufactured_share,
            recyclability_rate=item.recyclability_rate,
            landfill_rate=item.landfill_rate,
            incineration_rate=item.incineration_rate,
            country_of_origin=item.country_of_origin,
            manufacturing_location=item.manufacturing_location,
            lci_dataset_id=item.lci_dataset_id,
        )
