"""
Models package initialization.
Imports all models to ensure SQLAlchemy can resolve relationships.
"""
from app.models.user import User, UserRole
from app.models.client import Client, ClientStatus, Priority
from app.models.client_printer import ClientPrinter
from app.models.product import Product
from app.models.order import Order, OrderStatus
from app.models.call_log import CallLog
from app.models.config import BusinessConfig

__all__ = [
    "User",
    "UserRole",
    "Client",
    "ClientStatus",
    "Priority",
    "ClientPrinter",
    "Product",
    "Order",
    "OrderStatus",
    "CallLog",
    "BusinessConfig",
]
