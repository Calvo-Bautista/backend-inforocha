from sqlalchemy import Column, Integer, String, Text, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class CallLog(Base):
    """
    CallLog model for sales call tracking.
    Stores information about sales calls made to clients.
    """
    __tablename__ = "call_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    seller_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    call_date = Column(Date, nullable=False, index=True)
    industry = Column(String(255))
    uses_printers = Column(Boolean, default=False)
    printer_type = Column(String(255))
    interested_in_quote = Column(Boolean, default=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    client = relationship("Client", back_populates="call_logs")
    seller = relationship("User")

    def __repr__(self):
        return f"<CallLog(id={self.id}, client_id={self.client_id}, call_date='{self.call_date}')>"
