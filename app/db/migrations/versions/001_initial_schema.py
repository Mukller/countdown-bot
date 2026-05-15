"""Initial schema with users and countdowns tables

Revision ID: 001
Revises:
Create Date: 2026-05-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('notification_time', sa.Time(), nullable=False, server_default='09:00:00'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_id')
    )

    op.create_index('idx_users_notification_time', 'users', ['notification_time'])

    # Create countdowns table
    op.create_table(
        'countdowns',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('emoji', sa.String(10), nullable=False),
        sa.Column('target_date', sa.Date(), nullable=False),
        sa.Column('repeat_type', sa.String(20), nullable=False, server_default='none'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )

    op.create_index('idx_countdowns_user_id', 'countdowns', ['user_id'])


def downgrade() -> None:
    op.drop_index('idx_countdowns_user_id')
    op.drop_table('countdowns')
    op.drop_index('idx_users_notification_time')
    op.drop_table('users')
