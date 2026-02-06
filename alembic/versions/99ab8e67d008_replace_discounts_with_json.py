"""replace discounts with json

Revision ID: 99ab8e67d008
Revises: b12a1f7194e4
Create Date: 2026-02-06 01:38:40.297809

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '99ab8e67d008'
down_revision: Union[str, None] = 'b12a1f7194e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new JSON column
    op.add_column('business_configs', sa.Column('discounts', sa.JSON(), nullable=True))
    
    # Drop old columns
    op.drop_column('business_configs', 'discount_threshold_1')
    op.drop_column('business_configs', 'discount_percentage_1')
    op.drop_column('business_configs', 'discount_threshold_2')
    op.drop_column('business_configs', 'discount_percentage_2')
    op.drop_column('business_configs', 'discount_threshold_3')
    op.drop_column('business_configs', 'discount_percentage_3')

def downgrade() -> None:
    # Add old columns back
    op.add_column('business_configs', sa.Column('discount_threshold_1', mysql.DECIMAL(10, 2), nullable=True))
    op.add_column('business_configs', sa.Column('discount_percentage_1', mysql.DECIMAL(5, 2), nullable=True))
    op.add_column('business_configs', sa.Column('discount_threshold_2', mysql.DECIMAL(10, 2), nullable=True))
    op.add_column('business_configs', sa.Column('discount_percentage_2', mysql.DECIMAL(5, 2), nullable=True))
    op.add_column('business_configs', sa.Column('discount_threshold_3', mysql.DECIMAL(10, 2), nullable=True))
    op.add_column('business_configs', sa.Column('discount_percentage_3', mysql.DECIMAL(5, 2), nullable=True))
    
    # Drop JSON column
    op.drop_column('business_configs', 'discounts')
