"""Manager handlers for manager workflow."""

from aiogram import Router, F
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.services.order_service import OrderService
from app.services.notification_service import NotificationService
from app.utils.enums import OrderStatus
from app.utils.formatters import Formatters
from app.states.staff import ManagerStates

router = Router()


@router.message(F.text == "📋 Панель менеджера")
async def manager_panel(message: Message):
    """Show manager panel."""
    await message.answer(
        "📋 <b>Панель менеджера</b>\n\n"
        "Выберите действие:",
        reply_markup=get_manager_keyboard()
    )


@router.callback_query(F.data == "manager:new_orders")
async def view_new_orders(callback: CallbackQuery, session: AsyncSession):
    """View new orders."""
    await callback.answer()
    order_service = OrderService(session)
    orders = await order_service.get_orders_by_status(OrderStatus.NEW, limit=20)
    
    if not orders:
        await callback.message.edit_text(
            "🆕 Новых заказов нет",
            reply_markup=get_manager_keyboard()
        )
        return
    
    await callback.message.edit_text(
        f"🆕 Новые заказы ({len(orders)}):",
        reply_markup=get_orders_list_keyboard(orders, "manager")
    )


@router.callback_query(F.data.startswith("manager:order:"))
async def view_order_details(callback: CallbackQuery, session: AsyncSession):
    """View order details."""
    order_id = int(callback.data.split(":")[2])
    order_service = OrderService(session)
    
    try:
        order = await order_service.get_order_by_id(order_id)
        text = (
            f"📦 <b>Заказ {Formatters.format_order_number(order.order_number)}</b>\n\n"
            f"👤 Клиент: {order.user.full_name}\n"
            f"📞 Телефон: {Formatters.format_phone(order.delivery_phone)}\n"
            f"📍 Адрес: {order.delivery_address}\n"
            f"💰 Сумма: {Formatters.format_price(order.total)}\n"
            f"💳 Оплата: {Formatters.format_payment_method(order.payment_method)}\n\n"
            f"<b>Состав:</b>\n"
        )
        
        for item in order.items:
            text += f"• {item.product_name} x{item.quantity}\n"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_order_actions_keyboard(order, "manager")
        )
    except Exception:
        await callback.answer("Заказ не найден", show_alert=True)


@router.callback_query(F.data.startswith("confirm_order:"))
async def confirm_order(callback: CallbackQuery, session: AsyncSession, user: User):
    """Confirm order."""
    order_id = int(callback.data.split(":")[1])
    order_service = OrderService(session)
    
    try:
        order = await order_service.transition_status(
            order_id=order_id,
            new_status=OrderStatus.CONFIRMED,
            changed_by_id=user.id
        )
        await callback.answer("✅ Заказ подтвержден")
        
        # Notify customer
        # notification_service = NotificationService()
        # await notification_service.notify_order_status_changed(order, "NEW", "CONFIRMED")
        
        await view_new_orders(callback, session)
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


@router.callback_query(F.data.startswith("cancel_order:"))
async def cancel_order_start(callback: CallbackQuery, state: FSMContext):
    """Start cancel order process."""
    order_id = int(callback.data.split(":")[1])
    await state.update_data(order_id=order_id)
    await state.set_state(ManagerStates.cancelling_order)
    await callback.answer()
    await callback.message.edit_text(
        "Введите причину отмены заказа:"
    )


@router.message(ManagerStates.cancelling_order)
async def process_cancel_reason(message: Message, state: FSMContext, session: AsyncSession, user: User):
    """Process cancellation reason."""
    data = await state.get_data()
    order_id = data["order_id"]
    reason = message.text
    
    order_service = OrderService(session)
    
    try:
        order = await order_service.cancel_order(
            order_id=order_id,
            cancelled_by_id=user.id,
            reason=reason
        )
        await state.clear()
        await message.answer(f"✅ Заказ {order.order_number} отменен")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")


@router.callback_query(F.data.startswith("mark_paid:"))
async def mark_paid(callback: CallbackQuery, session: AsyncSession, user: User):
    """Mark order as paid."""
    order_id = int(callback.data.split(":")[1])
    order_service = OrderService(session)
    
    try:
        order = await order_service.transition_status(
            order_id=order_id,
            new_status=OrderStatus.PAID,
            changed_by_id=user.id
        )
        await callback.answer("✅ Заказ отмечен как оплаченный")
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


def get_manager_keyboard():
    """Get manager main keyboard."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🆕 Новые заказы", callback_data="manager:new_orders")],
        [InlineKeyboardButton(text="✅ Подтвержденные", callback_data="manager:confirmed")],
        [InlineKeyboardButton(text="💳 Оплата", callback_data="manager:payments")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back")]
    ])


def get_orders_list_keyboard(orders, prefix):
    """Get orders list keyboard."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = []
    for order in orders:
        btn_text = f"#{order.order_number} - {Formatters.format_price(order.total)}"
        buttons.append([InlineKeyboardButton(
            text=btn_text,
            callback_data=f"{prefix}:order:{order.id}"
        )])
    
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_order_actions_keyboard(order, prefix):
    """Get order actions keyboard."""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = []
    
    if order.status == OrderStatus.NEW.value:
        buttons.append([
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm_order:{order.id}"),
            InlineKeyboardButton(text="❌ Отменить", callback_data=f"cancel_order:{order.id}")
        ])
    elif order.status == OrderStatus.CONFIRMED.value:
        buttons.append([
            InlineKeyboardButton(text="💳 Отмечено оплаченным", callback_data=f"mark_paid:{order.id}"),
            InlineKeyboardButton(text="❌ Отменить", callback_data=f"cancel_order:{order.id}")
        ])
    
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data=f"{prefix}:back")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
