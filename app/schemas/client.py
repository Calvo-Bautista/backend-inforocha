from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.client import ClientStatus, Priority


class ClientBase(BaseModel):
    """Base client schema with common fields"""
    name: str
    phone: str
    address: Optional[str] = None
    industry: Optional[str] = None
    maquinas: Optional[str] = None  # Deprecated: use printers instead
    priority: Optional[Priority] = None  # Renamed from tipo_cliente
    proveedor_actual: Optional[str] = None
    status: ClientStatus = ClientStatus.PROSPECT


class PrinterBase(BaseModel):
    """Base printer schema"""
    printer_model: str


class PrinterCreate(PrinterBase):
    """Schema for creating a new printer"""
    pass


class PrinterResponse(PrinterBase):
    """Schema for printer response"""
    id: int
    client_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ClientCreate(ClientBase):
    """Schema for creating a new client"""
    legajo: Optional[str] = None
    printers: Optional[List[str]] = []  # List of printer models


class ClientUpdate(BaseModel):
    """Schema for updating a client"""
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    industry: Optional[str] = None
    maquinas: Optional[str] = None  # Deprecated
    priority: Optional[Priority] = None  # Renamed from tipo_cliente
    proveedor_actual: Optional[str] = None
    status: Optional[ClientStatus] = None
    printers: Optional[List[str]] = None  # List of printer models to replace existing


class ClientResponse(ClientBase):
    """Schema for client response"""
    id: int
    legajo: Optional[str]
    created_at: datetime
    updated_at: datetime
    printers: List[PrinterResponse] = []  # List of associated printers

    class Config:
        from_attributes = True
