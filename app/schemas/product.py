from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.models.product import ProductCategory


class ProductBase(BaseModel):
    """Base product schema with common fields"""
    articulo: str
    description: str
    price: Decimal = Field(..., gt=0, decimal_places=4)
    stock: int = Field(default=0, ge=0)
    category: str
    is_active: bool = True


class ProductCreate(ProductBase):
    """Schema for creating a new product"""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product"""
    articulo: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0, decimal_places=4)
    stock: Optional[int] = Field(None, ge=0)
    category: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    """Schema for product response"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
