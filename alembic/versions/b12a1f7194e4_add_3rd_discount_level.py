"""add 3rd discount level

Revision ID: b12a1f7194e4
Revises: 6149834ee3d1
Create Date: 2026-02-06 01:20:46.682366

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'b12a1f7194e4'
down_revision: Union[str, None] = '6149834ee3d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('business_configs', sa.Column('discount_threshold_3', sa.Numeric(10, 2), default=500000))
    op.add_column('business_configs', sa.Column('discount_percentage_3', sa.Numeric(5, 2), default=15))

def downgrade() -> None:
    op.drop_column('business_configs', 'discount_threshold_3')
    op.drop_column('business_configs', 'discount_percentage_3')
