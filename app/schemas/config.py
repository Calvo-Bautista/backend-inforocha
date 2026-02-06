from pydantic import BaseModel, Field, field_validator
from decimal import Decimal

class ConfigBase(BaseModel):
    shipping_cost: Decimal = Field(..., ge=0, description="Costo de envío")
    discount_threshold_1: Decimal = Field(..., ge=0, description="Umbral para primer descuento")
    discount_percentage_1: Decimal = Field(..., ge=0, le=100, description="Porcentaje primer descuento")
    discount_threshold_2: Decimal = Field(..., ge=0, description="Umbral para segundo descuento")
    discount_percentage_2: Decimal = Field(..., ge=0, le=100, description="Porcentaje segundo descuento")
    discount_threshold_3: Decimal = Field(..., ge=0, description="Umbral para tercer descuento")
    discount_percentage_3: Decimal = Field(..., ge=0, le=100, description="Porcentaje tercer descuento")

    @field_validator('discount_percentage_1', 'discount_percentage_2', 'discount_percentage_3')
    def validate_percentage(cls, v):
        if v < 0 or v > 100:
            raise ValueError('El porcentaje debe estar entre 0 y 100')
        return v

class ConfigUpdate(ConfigBase):
    pass

class ConfigResponse(ConfigBase):
    class Config:
        from_attributes = True
