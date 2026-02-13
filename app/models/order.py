from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, Date, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class OrderStatus(str, enum.Enum):
    """Order status enumeration"""
    PENDIENTE = "pendiente"
    PREPARACION = "preparacion"
    ENVIADO = "enviado"
    ENTREGADO = "entregado"
    CANCELADO = "cancelado"


class Order(Base):
    """
    Order model for purchase orders.
    Stores order information, pricing, and status.
    """
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="RESTRICT"), nullable=False, index=True)
    seller_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    order_date = Column(Date, nullable=False, index=True)
    subtotal = Column(Numeric(12, 2), nullable=False)
    discount = Column(Numeric(12, 2), default=0)
    discount_percent = Column(Numeric(5, 2), default=0)
    shipping = Column(Numeric(10, 2), default=0)
    shipping_discount = Column(Boolean, default=False)
    total = Column(Numeric(12, 2), nullable=False)
    factura_a = Column(Boolean, default=False)
    status = Column(Enum(OrderStatus, values_callable=lambda x: [e.value for e in x]), default=OrderStatus.PENDIENTE, index=True)
    notes = Column(Text)
    repair_description = Column(Text, nullable=True)
    repair_amount = Column(Numeric(10, 2), default=0, nullable=False)
    payment_method = Column(Enum('transferencia', 'efectivo', 'tarjeta', name='paymentmethod'), nullable=False, default='efectivo')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    client = relationship("Client", back_populates="orders")
    seller = relationship("User")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order(id={self.id}, order_number='{self.order_number}', status='{self.status}')>"


class OrderItem(Base):
    """
    OrderItem model for order line items.
    Stores individual products within an order.
    """
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    price_at_time = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

    def __repr__(self):
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, product_id={self.product_id})>"
