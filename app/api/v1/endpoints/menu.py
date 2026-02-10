"""Menu API endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas import (
    CategoryResponse, CategoryCreate, CategoryUpdate,
    ProductResponse, ProductCreate, ProductUpdate
)
from app.api.v1.dependencies import get_db_session, get_current_admin
from app.services.menu_service import MenuService

router = APIRouter()


@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(
    parent_id: Optional[int] = None,
    include_inactive: bool = False,
    session: AsyncSession = Depends(get_db_session)
):
    """Get categories."""
    menu_service = MenuService(session)
    categories = await menu_service.get_category_tree(
        parent_id=parent_id,
        include_inactive=include_inactive,
        include_archived=False
    )
    return categories


@router.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    session: AsyncSession = Depends(get_db_session)
):
    """Get category by ID."""
    menu_service = MenuService(session)
    try:
        category = await menu_service.get_category_by_id(category_id)
        return category
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/categories", response_model=CategoryResponse)
async def create_category(
    category: CategoryCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_admin)
):
    """Create new category (admin only)."""
    menu_service = MenuService(session)
    try:
        new_category = await menu_service.create_category(
            name=category.name,
            parent_id=category.parent_id,
            description=category.description,
            sort_order=category.sort_order
        )
        return new_category
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/products", response_model=List[ProductResponse])
async def get_products(
    category_id: Optional[int] = None,
    include_inactive: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session)
):
    """Get products."""
    menu_service = MenuService(session)
    
    if category_id:
        products = await menu_service.get_products_by_category(
            category_id=category_id,
            include_inactive=include_inactive
        )
    else:
        products = await menu_service.get_available_products()
    
    return products[skip:skip + limit]


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    session: AsyncSession = Depends(get_db_session)
):
    """Get product by ID."""
    menu_service = MenuService(session)
    try:
        product = await menu_service.get_product_by_id(product_id)
        return product
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/products", response_model=ProductResponse)
async def create_product(
    product: ProductCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_admin)
):
    """Create new product (admin only)."""
    menu_service = MenuService(session)
    try:
        new_product = await menu_service.create_product(
            name=product.name,
            category_id=product.category_id,
            price=float(product.price),
            description=product.description,
            sort_order=product.sort_order
        )
        return new_product
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
