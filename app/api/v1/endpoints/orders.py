"""Orders API endpoints."""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

from app.api.v1.schemas import OrderCreate, OrderResponse, OrderUpdate
from app.api.v1.dependencies import get_db_session, get_current_admin
from app.services.order_service import OrderService
from app.utils.enums import OrderStatus
from app.utils.validators import Validators

router = APIRouter()


@router.get("", response_model=List[OrderResponse])
async def get_orders(
    status: Optional[str] = None,
    user_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_admin)
):
    """Get orders (admin only)."""
    order_service = OrderService(session)
    
    if status:
        try:
            order_status = OrderStatus(status)
            orders = await order_service.get_orders_by_status(order_status, limit=limit)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")
    else:
        # Get all orders with pagination
        orders = await order_service.get_orders(
            skip=skip,
            limit=limit
        )
    
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_admin)
):
    """Get order by ID (admin only)."""
    order_service = OrderService(session)
    try:
        order = await order_service.get_order_by_id(order_id)
        return order
    except Exception:
        logger.exception(f"Failed to get order {order_id}")
        raise HTTPException(status_code=404, detail="Order not found")


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(
    order: OrderCreate,
    session: AsyncSession = Depends(get_db_session)
):
    """Create new order."""
    order_service = OrderService(session)
    
    try:
        # Convert items to dict format
        items_data = []
        for item in order.items:
            items_data.append({
                "product_id": item.product_id,
                "quantity": item.quantity,
                "modifiers": item.modifiers,
                "special_instructions": item.special_instructions
            })
        
        # For API orders, we need user_id - this would come from auth
        # For now, we'll raise an error
        raise HTTPException(
            status_code=501,
            detail="API order creation requires authentication"
        )
        
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to create order")
        raise HTTPException(status_code=400, detail="Failed to create order")


@router.patch("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_update: OrderUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(get_current_admin)
):
    """Update order (admin only)."""
    order_service = OrderService(session)
    
    try:
        if order_update.status:
            new_status = OrderStatus(order_update.status)
            order = await order_service.transition_status(
                order_id=order_id,
                new_status=new_status,
                changed_by_id=current_user["id"]
            )
            return order
        
        raise HTTPException(status_code=400, detail="No fields to update")
    except HTTPException:
        raise
    except Exception:
        logger.exception(f"Failed to update order {order_id}")
        raise HTTPException(status_code=400, detail="Failed to update order")


@router.get("/{order_number}/status")
async def get_order_status(
    order_number: str,
    phone: str = Query(..., description="Phone number for verification"),
    session: AsyncSession = Depends(get_db_session)
):
    """Get order status by order number (public, requires phone verification)."""
    order_service = OrderService(session)
    
    try:
        order = await order_service.get_order_by_number(order_number)
        # Verify phone number matches for privacy (normalized comparison)
        normalized_db_phone = Validators.validate_phone(order.delivery_phone)
        normalized_input_phone = Validators.validate_phone(phone)
        if normalized_db_phone != normalized_input_phone:
            raise HTTPException(status_code=404, detail="Order not found")
        return {
            "order_number": order.order_number,
            "status": order.status,
            "created_at": order.created_at
        }
    except HTTPException:
        raise
    except Exception:
        logger.exception(f"Failed to get order status for {order_number}")
        raise HTTPException(status_code=404, detail="Order not found")
