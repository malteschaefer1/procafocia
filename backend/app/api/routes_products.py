"""Product routes."""
from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, HTTPException

from ..models.product import Product
from ..schemas.product_schema import ProductCreate, ProductResponse
from ..services.product_repository import ProductRepository

router = APIRouter(prefix="/products", tags=["products"])
_repository = ProductRepository()


@router.get("", response_model=list[ProductResponse])
def list_products() -> list[ProductResponse]:
    products = _repository.list_products()
    return [ProductResponse(**asdict(product)) for product in products]


@router.post("", response_model=ProductResponse)
def create_product(payload: ProductCreate) -> ProductResponse:
    product = Product(
        id=payload.id,
        name=payload.name,
        version=payload.version,
        functional_unit=payload.functional_unit,
        lifetime_years=payload.lifetime_years,
        use_profile=payload.use_profile,
    )
    try:
        stored = _repository.create_product(product)
    except ValueError as exc:  # duplicate id
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ProductResponse(**asdict(stored))
