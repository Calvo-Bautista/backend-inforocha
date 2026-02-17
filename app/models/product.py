from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class ProductCategory(str, enum.Enum):
    """Product category enumeration"""
    TONER = "toner"
    CARTUCHO = "cartucho"
    DRUM = "drum"
    REPUESTO = "repuesto"


class Product(Base):
    """
    Product model for inventory items.
    Stores product information, pricing, and stock levels.
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    articulo = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, nullable=False, default=0, index=True)
    category = Column(Enum(ProductCategory), nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    order_items = relationship("OrderItem", back_populates="product")

    def __repr__(self):
        return f"<Product(id={self.id}, articulo='{self.articulo}', description='{self.description[:20]}...')>"
