from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class CallLogBase(BaseModel):
    """Base call log schema with common fields"""
    client_id: int
    call_date: date
    industry: Optional[str] = None
    uses_printers: bool = False
    printer_type: Optional[str] = None
    interested_in_quote: bool = False
    notes: Optional[str] = None


class CallLogCreate(CallLogBase):
    """Schema for creating a new call log"""
    pass


class CallLogUpdate(BaseModel):
    """Schema for updating a call log"""
    call_date: Optional[date] = None
    industry: Optional[str] = None
    uses_printers: Optional[bool] = None
    printer_type: Optional[str] = None
    interested_in_quote: Optional[bool] = None
    notes: Optional[str] = None


class CallLogResponse(CallLogBase):
    """Schema for call log response"""
    id: int
    seller_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
