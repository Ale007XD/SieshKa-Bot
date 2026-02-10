"""States for staff workflow (manager, kitchen, packer, courier)."""

from aiogram.fsm.state import State, StatesGroup


# Manager States
class ManagerStates(StatesGroup):
    """States for manager workflow."""
    
    main_menu = State()
    
    # Order management
    viewing_new_orders = State()
    viewing_confirmed_orders = State()
    viewing_paid_orders = State()
    viewing_all_orders = State()
    
    order_details = State()
    confirming_order = State()
    cancelling_order = State()
    entering_cancellation_reason = State()
    marking_paid = State()
    
    # Statistics
    viewing_statistics = State()


# Kitchen States
class KitchenStates(StatesGroup):
    """States for kitchen workflow."""
    
    main_menu = State()
    
    # Order preparation
    viewing_paid_orders = State()
    viewing_in_progress_orders = State()
    
    order_details = State()
    starting_preparation = State()
    marking_ready = State()
    
    # Stats
    viewing_daily_stats = State()


# Packer States
class PackerStates(StatesGroup):
    """States for packer workflow."""
    
    main_menu = State()
    
    # Packing
    viewing_ready_orders = State()
    viewing_packed_orders = State()
    
    order_details = State()
    marking_packed = State()


# Courier States
class CourierStates(StatesGroup):
    """States for courier workflow."""
    
    main_menu = State()
    
    # Delivery
    viewing_available_orders = State()
    viewing_my_orders = State()
    viewing_in_delivery = State()
    
    order_details = State()
    taking_order = State()
    confirming_delivery = State()
    marking_delivered = State()
    
    # Stats
    viewing_my_stats = State()
