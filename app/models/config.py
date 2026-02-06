from sqlalchemy import Column, Integer, Numeric, CheckConstraint, JSON
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
    
    
    # Store discounts as a list of objects: [{"threshold": 100000, "percentage": 5}, ...]
    discounts = Column(JSON, default=list)

    # Store role permissions: {"vendedor": ["productos", "clientes"], ...}
    role_permissions = Column(JSON, default=dict)

    def __repr__(self):
        return "<BusinessConfig>"
