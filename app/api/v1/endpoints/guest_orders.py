"""Guest (unauthenticated) orders API endpoints."""

from typing import List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.api.v1.dependencies import get_db_session
from app.config import settings

router = APIRouter()


class GuestOrderItem(BaseModel):
    product_id: str
    quantity: int = 1
    modifiers: List[str] | None = None
    special_instructions: str | None = None


class GuestOrderCreate(BaseModel):
    name: str
    phone: str
    address: str
    items: List[GuestOrderItem]
    notes: str | None = None


class GuestOrderResponse(BaseModel):
    order_id: int
    status: str


_guest_orders_store = []  # in-memory store for MVP
_next_order_id = 1


async def _notify_order(order_id: int, order: GuestOrderCreate):  # pragma: no cover
    # Lightweight Telegram notification (optional)
    try:
        token = getattr(settings, "telegram_bot_token", None)
        chat_id = getattr(settings, "order_telegram_chat_id", None)
        if not token or not chat_id:
            return
        import httpx  # imported lazily to avoid a hard dependency in tests
        text = (
            f"New guest order #{order_id} from {order.name}, {order.phone}.\n"
            f"Address: {order.address}\n"
            f"Items: {', '.join([f'{it.quantity}x {it.product_id}' for it in order.items])}"
        )
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        async with httpx.AsyncClient() as client:
            await client.post(url, json=payload, timeout=5)
    except Exception:
        pass


@router.post("/guest", response_model=GuestOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_guest_order(order: GuestOrderCreate, session: AsyncSession = Depends(get_db_session)):
    global _next_order_id
    order_id = _next_order_id
    _next_order_id += 1
    # Persist in-memory (simple MVP)
    _guest_orders_store.append({
        "order_id": order_id,
        "name": order.name,
        "phone": order.phone,
        "address": order.address,
        "items": [item.dict() for item in order.items],
        "notes": order.notes,
        "status": "received",
    })

    # Attempt notification
    await _notify_order(order_id, order)

    return {"order_id": order_id, "status": "received"}
