"""Packer handlers for packer workflow."""

from aiogram import Router, F
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from app.models.user import User

from app.services.order_service import OrderService
from app.utils.enums import OrderStatus

router = Router()


@router.message(F.text == "📦 Панель упаковщика")
async def packer_panel(message: Message) -> None:
    """Show packer panel."""
    await message.answer(
        "📦 <b>Панель упаковщика</b>\n\n"
        "Выберите действие:",
        reply_markup=get_packer_keyboard()
    )


@router.callback_query(F.data == "packer:ready_orders")
async def view_ready_orders(callback: CallbackQuery, session: AsyncSession) -> None:
    """View ready orders (for packing)."""
    await callback.answer()
    order_service = OrderService(session)
    orders = await order_service.get_orders_by_status(OrderStatus.READY, limit=20)
    
    if not orders:
        await callback.message.edit_text(
            "🔥 Нет готовых блюд для упаковки",
            reply_markup=get_packer_keyboard()
        )
        return
    
    await callback.message.edit_text(
        f"📦 К упаковке ({len(orders)}):",
        reply_markup=get_packer_orders_keyboard(orders)
    )


@router.callback_query(F.data.startswith("packer:order:"))
async def view_order_details(callback: CallbackQuery, session: AsyncSession) -> None:
    """View order details for packer."""
    order_id = int(callback.data.split(":")[2])
    order_service = OrderService(session)
    
    try:
        order = await order_service.get_order_by_id(order_id)
        
        text = f"📦 <b>Заказ #{order.order_number}</b>\n\n"
        text += "<b>Упаковать:</b>\n"
        
        for item in order.items:
            text += f"✓ {item.product_name} x{item.quantity}\n"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_packer_actions_keyboard(order)
        )
    except Exception:
        await callback.answer("Заказ не найден", show_alert=True)


@router.callback_query(F.data.startswith("mark_packed:"))
async def mark_packed(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    """Mark order as packed."""
    order_id = int(callback.data.split(":")[1])
    order_service = OrderService(session)
    
    try:
        await order_service.transition_status(
            order_id=order_id,
            new_status=OrderStatus.PACKED,
            changed_by_id=user.id
        )
        await callback.answer("✅ Упаковано")
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


def get_packer_keyboard():
    """Get packer main keyboard."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Готовые к упаковке", callback_data="packer:ready_orders")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back")]
    ])


def get_packer_orders_keyboard(orders):
    """Get packer orders keyboard."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = []
    for order in orders:
        buttons.append([InlineKeyboardButton(
            text=f"#{order.order_number}",
            callback_data=f"packer:order:{order.id}"
        )])
    
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_packer_actions_keyboard(order):
    """Get packer actions keyboard."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Упаковано", callback_data=f"mark_packed:{order.id}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="packer:back")]
    ])
