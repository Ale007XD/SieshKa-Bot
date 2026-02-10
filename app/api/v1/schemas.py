"""API v1 schemas using Pydantic."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict


# Category Schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True


class CategoryCreate(CategoryBase):
    parent_id: Optional[int] = None


class CategoryUpdate(CategoryBase):
    name: Optional[str] = None


class CategoryResponse(CategoryBase):
    id: int
    level: int
    is_archived: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Product Schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal = Field(..., ge=0)
    category_id: int
    sort_order: int = 0
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: int
    is_archived: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# Order Item Schemas
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., ge=1)
    modifiers: Optional[List[Dict[str, Any]]] = None
    special_instructions: Optional[str] = None


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_price: Decimal
    quantity: int
    item_total: Decimal
    model_config = ConfigDict(from_attributes=True)


# Order Schemas
class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    delivery_address: str
    delivery_phone: str
    payment_method: str
    delivery_comment: Optional[str] = None
    promo_code: Optional[str] = None


class OrderUpdate(BaseModel):
    status: Optional[str] = None
    payment_status: Optional[str] = None
    courier_id: Optional[int] = None


class OrderResponse(BaseModel):
    id: int
    order_number: str
    status: str
    payment_method: str
    payment_status: str
    subtotal: Decimal
    delivery_fee: Decimal
    discount_amount: Decimal
    total: Decimal
    delivery_address: str
    delivery_phone: str
    delivery_comment: Optional[str]
    created_at: datetime
    items: List[OrderItemResponse]
    model_config = ConfigDict(from_attributes=True)


# Settings Schemas
class SettingsResponse(BaseModel):
    company_name: str
    company_phone: Optional[str]
    company_address: Optional[str]
    working_hours_start: str
    working_hours_end: str
    delivery_enabled: bool
    delivery_fee: Decimal
    min_order_amount: Decimal
    cash_payment_enabled: bool
    card_courier_enabled: bool
    transfer_payment_enabled: bool
    model_config = ConfigDict(from_attributes=True)


class SettingsUpdate(BaseModel):
    company_name: Optional[str] = None
    company_phone: Optional[str] = None
    company_address: Optional[str] = None
    delivery_fee: Optional[Decimal] = None
    min_order_amount: Optional[Decimal] = None


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserLogin(BaseModel):
    username: str
    password: str


# Stats Schemas
class DailyStatsResponse(BaseModel):
    date: str
    total_orders: int
    cancelled_orders: int
    total_revenue: float
    average_order_value: float


class TopProductResponse(BaseModel):
    product_id: int
    product_name: str
    total_quantity: int
    total_revenue: float


# Health Response
class HealthResponse(BaseModel):
    status: str
    version: str
    services: Dict[str, str]
