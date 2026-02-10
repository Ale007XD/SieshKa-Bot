from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'admin_cleanup_log',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=sa.func.now())
    )


def downgrade():
    op.drop_table('admin_cleanup_log')
