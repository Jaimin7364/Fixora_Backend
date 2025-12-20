from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    
    # File information
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)  # Storage path
    file_type = Column(String(50))  # MIME type
    file_size = Column(BigInteger)  # Size in bytes
    
    # Upload information
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ticket = relationship("Ticket", backref="attachments")
    user = relationship("User", backref="uploads")
