from pydantic import BaseModel, Field, field_validator
from decimal import Decimal

from typing import List

class DiscountRule(BaseModel):
    threshold: float = Field(..., ge=0, description="Umbral para aplicar el descuento")
    percentage: float = Field(..., ge=0, le=100, description="Porcentaje de descuento")

class ConfigBase(BaseModel):
    shipping_cost: Decimal = Field(..., ge=0, description="Costo de envío")
    discounts: List[DiscountRule] = Field(default_factory=list, description="Lista de reglas de descuento")
    role_permissions: dict = Field(default_factory=dict, description="Permisos por rol")

    @field_validator('discounts', mode='before')
    @classmethod
    def validate_discounts(cls, v):
        if v is None:
            return []
        return v

class ConfigUpdate(ConfigBase):
    pass

class ConfigResponse(ConfigBase):
    class Config:
        from_attributes = True
