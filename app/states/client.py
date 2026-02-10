"""States package for Finite State Machine."""

from aiogram.fsm.state import State, StatesGroup


class ClientStates(StatesGroup):
    """States for client workflow."""
    
    # Menu browsing
    browsing_menu = State()
    viewing_category = State()
    viewing_product = State()
    
    # Cart
    viewing_cart = State()
    
    # Checkout
    checkout_entering_phone = State()
    checkout_entering_address = State()
    checkout_entering_comment = State()
    checkout_confirming = State()
    
    # Orders
    viewing_orders = State()
    viewing_order_details = State()


class AdminStates(StatesGroup):
    """States for admin workflow."""
    
    # Menu management
    menu_selecting_action = State()
    menu_creating_category = State()
    menu_editing_category = State()
    menu_creating_product = State()
    menu_editing_product = State()
    menu_setting_price = State()
    
    # Archive management
    archive_viewing = State()
    archive_confirming_unarchive = State()
    
    # Staff management
    staff_selecting_action = State()
    staff_adding = State()
    staff_selecting_role = State()
    staff_removing = State()
    
    # Settings
    settings_viewing = State()
    settings_editing = State()


class StaffStates(StatesGroup):
    """States for staff workflow."""
    
    # Manager states
    manager_viewing_orders = State()
    manager_viewing_order_details = State()
    manager_confirming_order = State()
    manager_cancelling_order = State()
    manager_marking_paid = State()
    
    # Kitchen states
    kitchen_viewing_orders = State()
    kitchen_preparing_order = State()
    
    # Packer states
    packer_viewing_ready = State()
    packer_packing_order = State()
    
    # Courier states
    courier_viewing_orders = State()
    courier_viewing_assigned = State()
    courier_confirming_delivery = State()
