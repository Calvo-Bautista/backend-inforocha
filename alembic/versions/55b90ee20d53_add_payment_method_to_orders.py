"""add payment method to orders

Revision ID: 55b90ee20d53
Revises: c7e4f1e744fc
Create Date: 2026-02-10 19:09:35.283829

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '55b90ee20d53'
down_revision: Union[str, None] = 'c7e4f1e744fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add payment_method column to orders table
    op.add_column('orders', sa.Column('payment_method', 
                                       sa.Enum('transferencia', 'efectivo', 'tarjeta', name='paymentmethod'),
                                       nullable=False,
                                       server_default='efectivo'))


def downgrade() -> None:
    # Remove payment_method column from orders table
    op.drop_column('orders', 'payment_method')
    # Drop the ENUM type
    op.execute("DROP TYPE IF EXISTS paymentmethod")
