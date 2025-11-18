"""Product routes."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..models.product import Product
from ..schemas.product_schema import ProductCreate, ProductResponse
from ..services import state

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductResponse])
def list_products() -> list[ProductResponse]:
    return [ProductResponse(**product.__dict__) for product in state.products.values()]


@router.post("", response_model=ProductResponse)
def create_product(payload: ProductCreate) -> ProductResponse:
    if payload.id in state.products:
        raise HTTPException(status_code=400, detail="Product already exists")
    product = Product(
        id=payload.id,
        name=payload.name,
        version=payload.version,
        functional_unit=payload.functional_unit,
        lifetime_years=payload.lifetime_years,
        use_profile=payload.use_profile,
    )
    state.products[product.id] = product
    return ProductResponse(**product.__dict__)
