from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    """User role enumeration"""
    VENDEDOR = "vendedor"
    LOGISTICA = "logistica"
    ADMIN = "admin"
    OWNER = "owner"


class User(Base):
    """
    User model for system users.
    Represents employees who can access the system.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, index=True)
    legajo = Column(String(50), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    clients = relationship("Client", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
