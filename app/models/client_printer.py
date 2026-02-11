from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class ClientPrinter(Base):
    """
    ClientPrinter model for storing multiple printers per client.
    Replaces the single 'maquinas' text field with a proper relational structure.
    """
    __tablename__ = "client_printers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    printer_model = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    client = relationship("Client", back_populates="printers")

    def __repr__(self):
        return f"<ClientPrinter(id={self.id}, client_id={self.client_id}, model='{self.printer_model}')>"
