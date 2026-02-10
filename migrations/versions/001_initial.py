"""Initial migration - create all tables."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('first_name', sa.String(length=255), nullable=True),
        sa.Column('last_name', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('employee_code', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('employee_code'),
        sa.UniqueConstraint('telegram_id')
    )
    op.create_index('ix_users_telegram_id', 'users', ['telegram_id'], unique=True)
    
    # Create categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('is_archived', sa.Boolean(), nullable=False),
        sa.Column('archived_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('archived_by_user_id', sa.Integer(), nullable=True),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['archived_by_user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['parent_id'], ['categories.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create products table
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_archived', sa.Boolean(), nullable=False),
        sa.Column('archived_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('archived_by_user_id', sa.Integer(), nullable=True),
        sa.Column('stock_quantity', sa.Integer(), nullable=True),
        sa.Column('track_stock', sa.Boolean(), nullable=False),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['archived_by_user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create modifiers table
    op.create_table(
        'modifiers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('is_required', sa.Boolean(), nullable=False),
        sa.Column('is_multiple', sa.Boolean(), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create modifier_options table
    op.create_table(
        'modifier_options',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('modifier_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('price_adjustment', sa.Numeric(10, 2), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['modifier_id'], ['modifiers.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create product_modifiers table
    op.create_table(
        'product_modifiers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('modifier_id', sa.Integer(), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['modifier_id'], ['modifiers.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create promo_codes table
    op.create_table(
        'promo_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('discount_type', sa.String(length=10), nullable=False),
        sa.Column('discount_value', sa.Numeric(10, 2), nullable=False),
        sa.Column('max_uses', sa.Integer(), nullable=True),
        sa.Column('current_uses', sa.Integer(), nullable=False),
        sa.Column('min_order_amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('max_discount_amount', sa.Numeric(10, 2), nullable=True),
        sa.Column('valid_from', sa.DateTime(timezone=True), nullable=True),
        sa.Column('valid_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index('ix_promo_codes_code', 'promo_codes', ['code'], unique=True)
    
    # Create delivery_zones table
    op.create_table(
        'delivery_zones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('boundary', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('delivery_fee', sa.Numeric(10, 2), nullable=False),
        sa.Column('free_delivery_threshold', sa.Numeric(10, 2), nullable=True),
        sa.Column('min_order_amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('estimated_delivery_time', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create orders table
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('order_number', sa.String(length=20), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('payment_method', sa.String(length=20), nullable=False),
        sa.Column('payment_status', sa.String(length=20), nullable=False),
        sa.Column('subtotal', sa.Numeric(10, 2), nullable=False),
        sa.Column('delivery_fee', sa.Numeric(10, 2), nullable=False),
        sa.Column('discount_amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('total', sa.Numeric(10, 2), nullable=False),
        sa.Column('delivery_address', sa.Text(), nullable=False),
        sa.Column('delivery_phone', sa.String(length=20), nullable=False),
        sa.Column('delivery_comment', sa.Text(), nullable=True),
        sa.Column('courier_id', sa.Integer(), nullable=True),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('in_progress_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ready_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('packed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('assigned_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('in_delivery_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancellation_reason', sa.Text(), nullable=True),
        sa.Column('cancelled_by_id', sa.Integer(), nullable=True),
        sa.Column('promo_code_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['cancelled_by_id'], ['users.id']),
        sa.ForeignKeyConstraint(['courier_id'], ['users.id']),
        sa.ForeignKeyConstraint(['promo_code_id'], ['promo_codes.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_number')
    )
    op.create_index('ix_orders_order_number', 'orders', ['order_number'], unique=True)
    op.create_index('ix_orders_user_id', 'orders', ['user_id'])
    
    # Create order_items table
    op.create_table(
        'order_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('product_name', sa.String(length=255), nullable=False),
        sa.Column('product_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('modifiers', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('modifiers_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('item_total', sa.Numeric(10, 2), nullable=False),
        sa.Column('special_instructions', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create order_status_logs table
    op.create_table(
        'order_status_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('old_status', sa.String(length=20), nullable=True),
        sa.Column('new_status', sa.String(length=20), nullable=False),
        sa.Column('changed_by_id', sa.Integer(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['changed_by_id'], ['users.id']),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create app_settings table
    op.create_table(
        'app_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('company_name', sa.String(length=255), nullable=False),
        sa.Column('company_phone', sa.String(length=20), nullable=True),
        sa.Column('company_address', sa.Text(), nullable=True),
        sa.Column('working_hours_start', sa.String(length=5), nullable=False),
        sa.Column('working_hours_end', sa.String(length=5), nullable=False),
        sa.Column('delivery_enabled', sa.Boolean(), nullable=False),
        sa.Column('delivery_fee', sa.Numeric(10, 2), nullable=False),
        sa.Column('free_delivery_threshold', sa.Numeric(10, 2), nullable=True),
        sa.Column('min_order_amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('auto_confirm_orders', sa.Boolean(), nullable=False),
        sa.Column('estimated_delivery_time', sa.Integer(), nullable=False),
        sa.Column('notification_channel_id', sa.String(length=50), nullable=True),
        sa.Column('manager_notification_enabled', sa.Boolean(), nullable=False),
        sa.Column('cash_payment_enabled', sa.Boolean(), nullable=False),
        sa.Column('card_courier_enabled', sa.Boolean(), nullable=False),
        sa.Column('transfer_payment_enabled', sa.Boolean(), nullable=False),
        sa.Column('transfer_details', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create reviews table
    op.create_table(
        'reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('food_rating', sa.Integer(), nullable=False),
        sa.Column('delivery_rating', sa.Integer(), nullable=False),
        sa.Column('service_rating', sa.Integer(), nullable=False),
        sa.Column('overall_rating', sa.Numeric(3, 2), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('is_approved', sa.Boolean(), nullable=False),
        sa.Column('is_visible', sa.Boolean(), nullable=False),
        sa.Column('moderated_by_id', sa.Integer(), nullable=True),
        sa.Column('response', sa.Text(), nullable=True),
        sa.Column('responded_by_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['moderated_by_id'], ['users.id']),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id']),
        sa.ForeignKeyConstraint(['responded_by_id'], ['users.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create daily_counters table
    op.create_table(
        'daily_counters',
        sa.Column('counter_date', sa.Date(), nullable=False),
        sa.Column('counter', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('counter_date')
    )
    
    # Create admin_audit_logs table
    op.create_table(
        'admin_audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('old_values', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('new_values', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('admin_audit_logs')
    op.drop_table('daily_counters')
    op.drop_table('reviews')
    op.drop_table('app_settings')
    op.drop_table('order_status_logs')
    op.drop_table('order_items')
    op.drop_index('ix_orders_user_id', table_name='orders')
    op.drop_index('ix_orders_order_number', table_name='orders')
    op.drop_table('orders')
    op.drop_table('delivery_zones')
    op.drop_index('ix_promo_codes_code', table_name='promo_codes')
    op.drop_table('promo_codes')
    op.drop_table('product_modifiers')
    op.drop_table('modifier_options')
    op.drop_table('modifiers')
    op.drop_table('products')
    op.drop_table('categories')
    op.drop_index('ix_users_telegram_id', table_name='users')
    op.drop_table('users')
