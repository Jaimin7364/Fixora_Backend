from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base
import enum


class ActivityType(str, enum.Enum):
    CREATED = "created"
    UPDATED = "updated"
    COMMENT = "comment"
    STATUS_CHANGED = "status_changed"
    ASSIGNED = "assigned"
    PRIORITY_CHANGED = "priority_changed"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"


class TicketActivity(Base):
    __tablename__ = "ticket_activities"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    activity_type = Column(SQLEnum(ActivityType), nullable=False)
    description = Column(Text)  # Human-readable description
    old_value = Column(String(255))  # Previous value (for updates)
    new_value = Column(String(255))  # New value (for updates)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ticket = relationship("Ticket", backref="activities")
    user = relationship("User", backref="activities")
