"""Courier handlers for courier workflow."""

from aiogram import Router, F
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message, CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.models.user import User

from app.services.order_service import OrderService
from app.utils.enums import OrderStatus
from app.utils.formatters import Formatters

router = Router()


@router.message(F.text == "🚚 Панель курьера")
async def courier_panel(message: Message) -> None:
    """Show courier panel."""
    await message.answer(
        "🚚 <b>Панель курьера</b>\n\n"
        "Выберите действие:",
        reply_markup=get_courier_keyboard()
    )


@router.callback_query(F.data == "courier:available")
async def view_available_orders(callback: CallbackQuery, session: AsyncSession) -> None:
    """View available orders for delivery."""
    await callback.answer()
    order_service = OrderService(session)
    orders = await order_service.get_orders_by_status(OrderStatus.PACKED, limit=20)
    
    if not orders:
        await callback.message.edit_text(
            "📦 Нет доступных заказов",
            reply_markup=get_courier_keyboard()
        )
        return
    
    await callback.message.edit_text(
        f"🚚 Доступно для доставки ({len(orders)}):",
        reply_markup=get_available_orders_keyboard(orders)
    )


@router.callback_query(F.data == "courier:my_orders")
async def view_my_orders(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    """View courier's assigned orders."""
    await callback.answer()
    order_service = OrderService(session)
    
    # Get orders assigned to this courier
    from sqlalchemy import select, and_
    from app.models.order import Order as OrderModel
    
    result = await session.execute(
        select(OrderModel).where(
            and_(
                OrderModel.courier_id == user.id,
                OrderModel.status.in_([OrderStatus.ASSIGNED.value, OrderStatus.IN_DELIVERY.value])
            )
        )
    )
    orders = result.scalars().all()
    
    if not orders:
        await callback.message.edit_text(
            "👤 У вас нет активных заказов",
            reply_markup=get_courier_keyboard()
        )
        return
    
    await callback.message.edit_text(
        f"🚚 Ваши заказы ({len(orders)}):",
        reply_markup=get_courier_orders_keyboard(orders)
    )


@router.callback_query(F.data.startswith("courier:order:"))
async def view_order_details(callback: CallbackQuery, session: AsyncSession) -> None:
    """View order details for courier."""
    order_id = int(callback.data.split(":")[2])
    order_service = OrderService(session)
    
    try:
        order = await order_service.get_order_by_id(order_id)
        
        text = (
            f"📦 <b>Заказ #{order.order_number}</b>\n\n"
            f"📍 Адрес: {order.delivery_address}\n"
            f"📞 Телефон: {Formatters.format_phone(order.delivery_phone)}\n"
            f"💰 Сумма: {Formatters.format_price(order.total)}\n"
        )
        
        if order.delivery_comment:
            text += f"💬 Комментарий: {order.delivery_comment}\n"
        
        text += f"\n<b>Состав:</b>\n"
        for item in order.items:
            text += f"• {item.product_name} x{item.quantity}\n"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_courier_actions_keyboard(order)
        )
    except Exception:
        await callback.answer("Заказ не найден", show_alert=True)


@router.callback_query(F.data.startswith("take_order:"))
async def take_order(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    """Take order for delivery."""
    order_id = int(callback.data.split(":")[1])
    order_service = OrderService(session)
    
    try:
        # Assign courier
        await order_service.assign_courier(order_id, user.id, user.id)
        
        # Transition to ASSIGNED
        await order_service.transition_status(
            order_id=order_id,
            new_status=OrderStatus.ASSIGNED,
            changed_by_id=user.id
        )
        
        await callback.answer("✅ Заказ взят в доставку")
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


@router.callback_query(F.data.startswith("start_delivery:"))
async def start_delivery(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    """Start delivery."""
    order_id = int(callback.data.split(":")[1])
    order_service = OrderService(session)
    
    try:
        await order_service.transition_status(
            order_id=order_id,
            new_status=OrderStatus.IN_DELIVERY,
            changed_by_id=user.id
        )
        await callback.answer("🚚 Доставка начата")
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


@router.callback_query(F.data.startswith("mark_delivered:"))
async def mark_delivered(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    """Mark order as delivered."""
    order_id = int(callback.data.split(":")[1])
    order_service = OrderService(session)
    
    try:
        await order_service.transition_status(
            order_id=order_id,
            new_status=OrderStatus.DELIVERED,
            changed_by_id=user.id
        )
        await callback.answer("🎉 Доставлено!")
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


def get_courier_keyboard() -> InlineKeyboardMarkup:
    """Get courier main keyboard."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Доступные заказы", callback_data="courier:available")],
        [InlineKeyboardButton(text="👤 Мои заказы", callback_data="courier:my_orders")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back")]
    ])


def get_available_orders_keyboard(orders) -> InlineKeyboardMarkup:
    """Get available orders keyboard."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = []
    for order in orders:
        buttons.append([InlineKeyboardButton(
            text=f"Взять #{order.order_number}",
            callback_data=f"take_order:{order.id}"
        )])
    
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_courier_orders_keyboard(orders) -> InlineKeyboardMarkup:
    """Get courier's orders keyboard."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = []
    for order in orders:
        buttons.append([InlineKeyboardButton(
            text=f"#{order.order_number}",
            callback_data=f"courier:order:{order.id}"
        )])
    
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_courier_actions_keyboard(order) -> InlineKeyboardMarkup:
    """Get courier actions keyboard."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = []
    
    if order.status == OrderStatus.PACKED.value:
        buttons.append([InlineKeyboardButton(
            text="✋ Взять заказ",
            callback_data=f"take_order:{order.id}"
        )])
    elif order.status == OrderStatus.ASSIGNED.value:
        buttons.append([InlineKeyboardButton(
            text="🚚 Начать доставку",
            callback_data=f"start_delivery:{order.id}"
        )])
    elif order.status == OrderStatus.IN_DELIVERY.value:
        buttons.append([InlineKeyboardButton(
            text="🎉 Доставлено",
            callback_data=f"mark_delivered:{order.id}"
        )])
    
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="courier:back")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
