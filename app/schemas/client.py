from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.client import ClientStatus, ClientType


class ClientBase(BaseModel):
    """Base client schema with common fields"""
    name: str
    phone: str
    address: Optional[str] = None
    industry: Optional[str] = None
    maquinas: Optional[str] = None
    tipo_cliente: Optional[ClientType] = None
    proveedor_actual: Optional[str] = None
    status: ClientStatus = ClientStatus.PROSPECT


class ClientCreate(ClientBase):
    """Schema for creating a new client"""
    legajo: Optional[str] = None


class ClientUpdate(BaseModel):
    """Schema for updating a client"""
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    industry: Optional[str] = None
    maquinas: Optional[str] = None
    tipo_cliente: Optional[ClientType] = None
    proveedor_actual: Optional[str] = None
    status: Optional[ClientStatus] = None


class ClientResponse(ClientBase):
    """Schema for client response"""
    id: int
    legajo: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
