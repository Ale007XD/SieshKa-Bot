"""States for admin workflow."""

from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    """States for admin workflow."""
    
    # Main menu
    main_menu = State()
    
    # Menu management
    menu_management = State()
    category_management = State()
    creating_category = State()
    editing_category = State()
    category_selecting_parent = State()
    
    product_management = State()
    creating_product = State()
    editing_product = State()
    product_selecting_category = State()
    product_setting_modifiers = State()
    
    # Modifier management
    modifier_management = State()
    creating_modifier = State()
    editing_modifier = State()
    adding_modifier_options = State()
    
    # Archive management
    archive_menu = State()
    archive_viewing_categories = State()
    archive_viewing_products = State()
    archive_confirm_action = State()
    
    # Staff management
    staff_menu = State()
    staff_list = State()
    staff_add_user_id = State()
    staff_select_role = State()
    staff_confirm_remove = State()
    
    # Order management
    order_management = State()
    viewing_active_orders = State()
    viewing_order_details = State()
    
    # Statistics
    statistics_menu = State()
    viewing_daily_stats = State()
    viewing_period_stats = State()
    viewing_top_products = State()
    
    # Settings
    settings_menu = State()
    editing_company_info = State()
    editing_working_hours = State()
    editing_delivery_settings = State()
    editing_payment_settings = State()
    
    # Import/Export
    import_export_menu = State()
    import_menu_data = State()
    confirming_import = State()
    export_selecting_format = State()
