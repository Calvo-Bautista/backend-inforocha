from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class ClientStatus(str, enum.Enum):
    """Client status enumeration"""
    ACTIVE = "active"
    PROSPECT = "prospect"


class Priority(str, enum.Enum):
    """Client priority enumeration"""
    ALTA = "ALTA"
    MEDIA = "MEDIA"
    BAJA = "BAJA"


class Client(Base):
    """
    Client model for customers/buyers.
    Stores customer information and contact details.
    """
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    legajo = Column(String(50), unique=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    phone = Column(String(50), nullable=False)
    cuit = Column(String(20), nullable=True)
    address = Column(Text)
    industry = Column(String(255))
    maquinas = Column(Text)  # Deprecated: use printers relationship instead
    priority = Column(Enum(Priority), nullable=True, index=True)  # Renamed from tipo_cliente
    proveedor_actual = Column(String(255))
    status = Column(Enum(ClientStatus), default=ClientStatus.PROSPECT, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # Relationships
    orders = relationship("Order", back_populates="client")

    user = relationship("User", back_populates="clients")
    printers = relationship("ClientPrinter", back_populates="client", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Client(id={self.id}, name='{self.name}', legajo='{self.legajo}')>"
