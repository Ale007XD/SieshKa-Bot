"""Client handlers for customer workflow."""

from aiogram import Router, F
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from typing import Any
# NOTE: 'User' here is the ORM model (DB entity) defined in app/models/user.py.
# The bot layer uses this entity as the user context (id, etc).
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.services.menu_service import MenuService
from app.services.cart_service import CartService
from app.services.order_service import OrderService
from app.services.settings_service import SettingsService
from app.keyboards.client import (
    get_client_menu_keyboard,
    get_categories_keyboard,
    get_products_keyboard,
    get_product_detail_keyboard,
    get_cart_keyboard,
    get_checkout_keyboard,
    get_payment_methods_keyboard,
    get_orders_keyboard
)
from app.utils.templates import Templates
from app.utils.formatters import Formatters
from app.utils.validators import Validators
from app.states.client import ClientStates
from app.utils.enums import OrderStatus

router = Router()


# Main menu
@router.message(F.text == "📋 Меню")
async def show_menu(message: Message, session: AsyncSession, user: User) -> None:
    """Show menu categories."""
    menu_service = MenuService(session)
    categories = await menu_service.get_category_tree(include_inactive=False, include_archived=False)
    
    if not categories:
        await message.answer("😔 Меню пока пусто")
        return
    
    await message.answer(
        Templates.menu_header(),
        reply_markup=get_categories_keyboard(categories)
    )


@router.callback_query(F.data.startswith("category:"))
async def show_category(callback: CallbackQuery, session: AsyncSession):
    """Show category contents."""
    category_id = int(callback.data.split(":")[1])
    menu_service = MenuService(session)
    
    # Get subcategories
    subcategories = await menu_service.get_category_tree(
        parent_id=category_id,
        include_inactive=False,
        include_archived=False
    )
    
    # Get products
    products = await menu_service.get_products_by_category(category_id)
    
    if subcategories:
        # Show subcategories
        await callback.message.edit_text(
            "📁 Выберите подкатегорию:",
            reply_markup=get_categories_keyboard(subcategories, parent_id=category_id)
        )
    elif products:
        # Show products
        await callback.message.edit_text(
            "🍽 Выберите блюдо:",
            reply_markup=get_products_keyboard(products, category_id)
        )
    else:
        await callback.answer("В этой категории пока ничего нет", show_alert=True)


@router.callback_query(F.data.startswith("product:"))
async def show_product(callback: CallbackQuery, session: AsyncSession):
    """Show product details."""
    product_id = int(callback.data.split(":")[1])
    menu_service = MenuService(session)
    
    try:
        product = await menu_service.get_product_by_id(product_id)
        
        text = Templates.product_details(
            name=product.name,
            price=float(product.price),
            description=product.description
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_product_detail_keyboard(product)
        )
    except Exception:
        await callback.answer("Товар не найден", show_alert=True)


@router.callback_query(F.data.startswith("add_to_cart:"))
async def add_to_cart(callback: CallbackQuery, session: AsyncSession, user: User):
    """Add product to cart."""
    product_id = int(callback.data.split(":")[1])
    cart_service = CartService(session)
    
    try:
        await cart_service.add_item(user.id, product_id)
        await callback.answer("✅ Добавлено в корзину!")
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


# Cart
@router.message(F.text == "🛒 Корзина")
async def show_cart(message: Message, session: AsyncSession, user: User):
    """Show cart contents."""
    cart_service = CartService(session)
    cart_summary = await cart_service.get_cart_summary(user.id)
    
    if not cart_summary["items"]:
        await message.answer(Templates.empty_cart())
        return
    
    text = Templates.cart_header()
    for idx, item in enumerate(cart_summary["items"], 1):
        text += Templates.cart_item(
            index=idx,
            name=item.product_name,
            quantity=item.quantity,
            price=item.product_price
        )
    
    text += Templates.cart_footer(cart_summary["subtotal"])
    
    await message.answer(
        text,
        reply_markup=get_cart_keyboard(cart_summary["items"])
    )


@router.callback_query(F.data == "view_cart")
async def view_cart_callback(callback: CallbackQuery, session: AsyncSession, user: User):
    """View cart from callback."""
    cart_service = CartService(session)
    cart_summary = await cart_service.get_cart_summary(user.id)
    
    if not cart_summary["items"]:
        await callback.message.edit_text(Templates.empty_cart())
        return
    
    text = Templates.cart_header()
    for idx, item in enumerate(cart_summary["items"], 1):
        text += Templates.cart_item(
            index=idx,
            name=item.product_name,
            quantity=item.quantity,
            price=item.product_price
        )
    
    text += Templates.cart_footer(cart_summary["subtotal"])
    
    await callback.message.edit_text(
        text,
        reply_markup=get_cart_keyboard(cart_summary["items"])
    )


@router.callback_query(F.data == "clear_cart")
async def clear_cart(callback: CallbackQuery, session: AsyncSession, user: User):
    """Clear cart."""
    cart_service = CartService(session)
    await cart_service.clear_cart(user.id)
    await callback.answer("🗑 Корзина очищена")
    await callback.message.edit_text(Templates.empty_cart())


@router.callback_query(F.data == "checkout")
async def start_checkout(callback: CallbackQuery, state: FSMContext, session: AsyncSession, user: User):
    """Start checkout process."""
    cart_service = CartService(session)
    cart_summary = await cart_service.get_cart_summary(user.id)
    
    if not cart_summary["items"]:
        await callback.answer("Корзина пуста!", show_alert=True)
        return
    
    await state.set_state(ClientStates.checkout_entering_phone)
    await callback.message.edit_text(
        "📞 Введите номер телефона для связи:\n"
        "(в формате +7XXXXXXXXXX)"
    )


@router.message(ClientStates.checkout_entering_phone)
async def process_phone(message: Message, state: FSMContext):
    """Process phone number."""
    try:
        phone = Validators.validate_phone(message.text)
        await state.update_data(phone=phone)
        await state.set_state(ClientStates.checkout_entering_address)
        await message.answer(
            "📍 Введите адрес доставки:\n"
            "(улица, дом, квартира, подъезд, этаж)"
        )
    except Exception as e:
        await message.answer(f"❌ {str(e)}. Попробуйте еще раз:")


@router.message(ClientStates.checkout_entering_address)
async def process_address(message: Message, state: FSMContext):
    """Process delivery address."""
    try:
        address = Validators.validate_address(message.text)
        await state.update_data(address=address)
        await state.set_state(ClientStates.checkout_entering_comment)
        await message.answer(
            "💬 Хотите добавить комментарий к заказу?\n"
            "(напишите его или отправьте 'Пропустить')"
        )
    except Exception as e:
        await message.answer(f"❌ {str(e)}. Попробуйте еще раз:")


@router.message(ClientStates.checkout_entering_comment)
async def process_comment(message: Message, state: FSMContext, session):
    """Process comment and show payment options."""
    comment = None
    if message.text.lower() not in ["пропустить", "skip", "-"]:
        comment = message.text
    
    await state.update_data(comment=comment)
    
    settings_service = SettingsService(session)
    payment_methods = await settings_service.get_available_payment_methods()
    
    await state.set_state(ClientStates.checkout_confirming)
    await message.answer(
        "💳 Выберите способ оплаты:",
        reply_markup=get_payment_methods_keyboard(payment_methods)
    )


@router.callback_query(ClientStates.checkout_confirming, F.data.startswith("payment:"))
async def process_payment(callback: CallbackQuery, state: FSMContext, session, user):
    """Process payment method and create order."""
    payment_method = callback.data.split(":")[1]
    data = await state.get_data()
    
    cart_service = CartService(session)
    order_service = OrderService(session)
    
    # Get cart items
    cart_summary = await cart_service.get_cart_summary(user.id)
    
    if not cart_summary["items"]:
        await callback.answer("Корзина пуста!", show_alert=True)
        return
    
    # Prepare items for order
    order_items = []
    for item in cart_summary["items"]:
        order_items.append({
            "product_id": item.product_id,
            "quantity": item.quantity,
            "modifiers": item.modifiers,
            "special_instructions": item.special_instructions
        })
    
    try:
        # Create order
        order = await order_service.create_order(
            user_id=user.id,
            items=order_items,
            delivery_address=data["address"],
            delivery_phone=data["phone"],
            payment_method=payment_method,
            delivery_comment=data.get("comment")
        )
        
        # Clear cart
        await cart_service.clear_cart(user.id)
        await state.clear()
        
        # Send confirmation
        await callback.message.edit_text(
            Templates.order_confirmation(order)
        )
        
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


# Orders
@router.message(F.text == "📦 Мои заказы")
async def show_orders(message: Message, session, user):
    """Show user's orders."""
    order_service = OrderService(session)
    orders = await order_service.get_user_orders(user.id, limit=10)
    
    if not orders:
        await message.answer("📭 У вас пока нет заказов")
        return
    
    await message.answer(
        "📦 Ваши заказы:",
        reply_markup=get_orders_keyboard(orders)
    )


@router.callback_query(F.data.startswith("order:"))
async def show_order_details(callback: CallbackQuery, session):
    """Show order details."""
    order_id = int(callback.data.split(":")[1])
    order_service = OrderService(session)
    
    try:
        order = await order_service.get_order_by_id(order_id)
        await callback.message.edit_text(
            Templates.order_details(order),
            reply_markup=get_orders_keyboard([order], show_detail=True)
        )
    except Exception:
        await callback.answer("Заказ не найден", show_alert=True)


# Refresh menu
@router.callback_query(F.data == "refresh_menu")
async def refresh_menu(callback: CallbackQuery, session):
    """Refresh menu."""
    await callback.answer("🔄 Меню обновлено")
    menu_service = MenuService(session)
    categories = await menu_service.get_category_tree(include_inactive=False, include_archived=False)
    
    await callback.message.edit_text(
        Templates.menu_header(),
        reply_markup=get_categories_keyboard(categories)
    )
