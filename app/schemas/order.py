from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from typing_extensions import Literal
from datetime import date, datetime
from decimal import Decimal
from app.models.order import OrderStatus, InvoiceType


# Nested schemas for related data
class ClientBasic(BaseModel):
    """Basic client info for order response"""
    id: int
    name: str
    phone: Optional[str] = None
    cuit: Optional[str] = None
    address: Optional[str] = None
    
    class Config:
        from_attributes = True


class UserBasic(BaseModel):
    """Basic user info for order response"""
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


class ProductBasic(BaseModel):
    """Basic product info for order item response"""
    id: int
    description: str
    articulo: str
    
    class Config:
        from_attributes = True


class OrderItemBase(BaseModel):
    """Base order item schema"""
    product_id: int
    quantity: int = Field(..., gt=0)
    price_at_time: Decimal = Field(..., ge=0, decimal_places=2)


class OrderItemCreate(OrderItemBase):
    """Schema for creating an order item"""
    pass


class OrderItemResponse(OrderItemBase):
    """Schema for order item response"""
    id: int
    order_id: int
    product: Optional[ProductBasic] = None
    created_at: datetime

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    """Base order schema with common fields"""
    client_id: int
    order_date: date
    subtotal: Decimal = Field(..., ge=0, decimal_places=2)
    discount: Decimal = Field(default=0, ge=0, decimal_places=2)
    discount_percent: Decimal = Field(default=0, ge=0, le=100, decimal_places=2)
    shipping: Decimal = Field(default=0, ge=0, decimal_places=2)
    shipping_discount: bool = False
    total: Decimal = Field(..., ge=0, decimal_places=2)
    invoice_type: Optional[InvoiceType] = None
    status: OrderStatus = OrderStatus.PENDIENTE
    notes: Optional[str] = None
    repair_description: Optional[str] = None
    repair_amount: Decimal = Field(default=0, ge=0, decimal_places=2)
    payment_method: Literal['transferencia', 'efectivo', 'tarjeta'] = 'efectivo'


class OrderCreate(OrderBase):
    """Schema for creating a new order"""
    items: List[OrderItemCreate]


class OrderUpdate(BaseModel):
    """Schema for updating an order"""
    status: Optional[OrderStatus] = None
    notes: Optional[str] = None


class OrderResponse(OrderBase):
    """Schema for order response"""
    id: int
    order_number: str
    seller_id: int
    seller: Optional[UserBasic] = None
    client: Optional[ClientBasic] = None
    items: List[OrderItemResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderStats(BaseModel):
    """Schema for order statistics"""
    total_orders: int
    total_revenue: Decimal
    by_status: dict[str, int]
