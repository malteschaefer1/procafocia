"""SQLAlchemy ORM models for persistence."""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ProductModel(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    version: Mapped[str] = mapped_column(String, nullable=False)
    functional_unit: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bom_items: Mapped[list["BOMItemModel"]] = relationship("BOMItemModel", back_populates="product")


class BOMItemModel(Base):
    __tablename__ = "bom_items"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    product_id: Mapped[str] = mapped_column(String, ForeignKey("products.id"), nullable=False)
    parent_bom_item_id: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    unit: Mapped[str | None] = mapped_column(String, nullable=True)
    mass_kg: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    material_family: Mapped[str | None] = mapped_column(String, nullable=True)
    material_code: Mapped[str | None] = mapped_column(String, nullable=True)
    classification_unspsc: Mapped[str | None] = mapped_column(String, nullable=True)
    supplier_id: Mapped[str | None] = mapped_column(String, nullable=True)
    component_code: Mapped[str | None] = mapped_column(String, nullable=True)
    recycled_content_share: Mapped[float | None] = mapped_column(Float, nullable=True)
    reused_share: Mapped[float | None] = mapped_column(Float, nullable=True)
    remanufactured_share: Mapped[float | None] = mapped_column(Float, nullable=True)
    recyclability_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    landfill_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    incineration_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    country_of_origin: Mapped[str | None] = mapped_column(String, nullable=True)
    manufacturing_location: Mapped[str | None] = mapped_column(String, nullable=True)
    lci_dataset_id: Mapped[str | None] = mapped_column(String, nullable=True)

    product: Mapped[ProductModel] = relationship(ProductModel, back_populates="bom_items")


class MappingRuleModel(Base):
    __tablename__ = "mapping_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    rule_code: Mapped[str] = mapped_column(String, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    material_code: Mapped[str | None] = mapped_column(String, nullable=True)
    material_family: Mapped[str | None] = mapped_column(String, nullable=True)
    classification_unspsc_prefix: Mapped[str | None] = mapped_column(String, nullable=True)
    supplier_id: Mapped[str | None] = mapped_column(String, nullable=True)
    dataset_id: Mapped[str] = mapped_column(String, nullable=False)
    provider: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MappingDecisionModel(Base):
    __tablename__ = "mapping_decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[str] = mapped_column(String, nullable=False)
    bom_item_id: Mapped[str] = mapped_column(String, nullable=False)
    scenario_id: Mapped[str | None] = mapped_column(String, nullable=True)
    selected_dataset_id: Mapped[str | None] = mapped_column(String, nullable=True)
    selected_provider: Mapped[str | None] = mapped_column(String, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    rule_applied: Mapped[str | None] = mapped_column(String, nullable=True)
    user_id: Mapped[str | None] = mapped_column(String, nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    decision_payload: Mapped[str | None] = mapped_column(Text, nullable=True)
    auto_selected: Mapped[bool] = mapped_column(Boolean, default=True)
    is_override: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
