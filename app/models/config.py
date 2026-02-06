from sqlalchemy import Column, Integer, Numeric, CheckConstraint
from sqlalchemy.sql import func
from app.database import Base

class BusinessConfig(Base):
    """
    Business configuration settings.
    Stores customizable values for the business logic.
    Only one row is expected in this table.
    """
    __tablename__ = "business_configs"

    id = Column(Integer, primary_key=True, index=True)
    shipping_cost = Column(Numeric(10, 2), default=0)
    
    # Discount Level 1
    discount_threshold_1 = Column(Numeric(10, 2), default=100000)
    discount_percentage_1 = Column(Numeric(5, 2), default=5)
    
    # Discount Level 2
    discount_threshold_2 = Column(Numeric(10, 2), default=300000)
    discount_percentage_2 = Column(Numeric(5, 2), default=10)

    # Discount Level 3
    discount_threshold_3 = Column(Numeric(10, 2), default=500000)
    discount_percentage_3 = Column(Numeric(5, 2), default=15)

    def __repr__(self):
        return "<BusinessConfig>"
