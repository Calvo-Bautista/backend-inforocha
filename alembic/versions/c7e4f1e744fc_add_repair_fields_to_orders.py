"""add repair fields to orders

Revision ID: c7e4f1e744fc
Revises: d3c03fbeee2b
Create Date: 2026-02-10 18:01:42.596919

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7e4f1e744fc'
down_revision: Union[str, None] = 'd3c03fbeee2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add repair fields to orders table
    op.add_column('orders', sa.Column('repair_description', sa.Text(), nullable=True))
    op.add_column('orders', sa.Column('repair_amount', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0'))


def downgrade() -> None:
    # Remove repair fields from orders table
    op.drop_column('orders', 'repair_amount')
    op.drop_column('orders', 'repair_description')
