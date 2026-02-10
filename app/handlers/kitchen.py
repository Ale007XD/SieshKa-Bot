"""Kitchen handlers for kitchen staff workflow."""

from aiogram import Router, F
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from app.models.user import User

from app.services.order_service import OrderService
from app.utils.enums import OrderStatus
from app.utils.formatters import Formatters

router = Router()


@router.message(F.text == "👨‍🍳 Панель кухни")
async def kitchen_panel(message: Message) -> None:
    """Show kitchen panel."""
    await message.answer(
        "👨‍🍳 <b>Панель кухни</b>\n\n"
        "Выберите действие:",
        reply_markup=get_kitchen_keyboard()
    )


@router.callback_query(F.data == "kitchen:paid_orders")
async def view_paid_orders(callback: CallbackQuery, session: AsyncSession) -> None:
    """View paid orders (ready for cooking)."""
    await callback.answer()
    order_service = OrderService(session)
    orders = await order_service.get_orders_by_status(OrderStatus.PAID, limit=20)
    
    if not orders:
        await callback.message.edit_text(
            "💳 Нет заказов ожидающих приготовления",
            reply_markup=get_kitchen_keyboard()
        )
        return
    
    await callback.message.edit_text(
        f"👨‍🍳 Заказы к приготовлению ({len(orders)}):",
        reply_markup=get_kitchen_orders_keyboard(orders)
    )


@router.callback_query(F.data == "kitchen:in_progress")
async def view_in_progress(callback: CallbackQuery, session: AsyncSession) -> None:
    """View orders in progress."""
    await callback.answer()
    order_service = OrderService(session)
    orders = await order_service.get_orders_by_status(OrderStatus.IN_PROGRESS, limit=20)
    
    if not orders:
        await callback.message.edit_text(
            "👨‍🍳 Нет заказов в работе",
            reply_markup=get_kitchen_keyboard()
        )
        return
    
    await callback.message.edit_text(
        f"🔥 Готовятся ({len(orders)}):",
        reply_markup=get_kitchen_orders_keyboard(orders, show_ready=True)
    )


@router.callback_query(F.data.startswith("kitchen:order:"))
async def view_order_details(callback: CallbackQuery, session: AsyncSession) -> None:
    """View order details for kitchen."""
    order_id = int(callback.data.split(":")[2])
    order_service = OrderService(session)
    
    try:
        order = await order_service.get_order_by_id(order_id)
        
        text = f"📦 <b>Заказ #{order.order_number}</b>\n\n"
        text += "<b>Блюда:</b>\n"
        
        for item in order.items:
            text += f"🔸 {item.product_name} x{item.quantity}\n"
            if item.special_instructions:
                text += f"   💬 {item.special_instructions}\n"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_kitchen_order_actions_keyboard(order)
        )
    except Exception:
        await callback.answer("Заказ не найден", show_alert=True)


@router.callback_query(F.data.startswith("start_cooking:"))
async def start_cooking(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    """Start cooking order."""
    order_id = int(callback.data.split(":")[1])
    order_service = OrderService(session)
    
    try:
        await order_service.transition_status(
            order_id=order_id,
            new_status=OrderStatus.IN_PROGRESS,
            changed_by_id=user.id
        )
        await callback.answer("✅ Начато приготовление")
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


@router.callback_query(F.data.startswith("mark_ready:"))
async def mark_ready(callback: CallbackQuery, session: AsyncSession, user):
    """Mark order as ready."""
    order_id = int(callback.data.split(":")[1])
    order_service = OrderService(session)
    
    try:
        await order_service.transition_status(
            order_id=order_id,
            new_status=OrderStatus.READY,
            changed_by_id=user.id
        )
        await callback.answer("🔥 Отмечено как готовое")
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


def get_kitchen_keyboard() -> InlineKeyboardMarkup:
    """Get kitchen main keyboard."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Заказы к приготовлению", callback_data="kitchen:paid_orders")],
        [InlineKeyboardButton(text="🔥 Готовятся", callback_data="kitchen:in_progress")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back")]
    ])


def get_kitchen_orders_keyboard(orders, show_ready=False) -> InlineKeyboardMarkup:
    """Get kitchen orders keyboard."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = []
    for order in orders:
        btn_text = f"#{order.order_number}"
        buttons.append([InlineKeyboardButton(
            text=btn_text,
            callback_data=f"kitchen:order:{order.id}"
        )])
    
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_kitchen_order_actions_keyboard(order) -> InlineKeyboardMarkup:
    """Get kitchen order actions keyboard."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = []
    
    if order.status == OrderStatus.PAID.value:
        buttons.append([InlineKeyboardButton(
            text="▶️ Начать приготовление",
            callback_data=f"start_cooking:{order.id}"
        )])
    elif order.status == OrderStatus.IN_PROGRESS.value:
        buttons.append([InlineKeyboardButton(
            text="🔥 Отметить готовым",
            callback_data=f"mark_ready:{order.id}"
        )])
    
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="kitchen:back")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
