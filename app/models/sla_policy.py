from sqlalchemy import Column, Integer, String, Enum as SQLEnum
from app.database.base import Base
from app.models.ticket import TicketPriority


class SLAPolicy(Base):
    __tablename__ = "sla_policies"

    id = Column(Integer, primary_key=True, index=True)
    priority = Column(SQLEnum(TicketPriority), unique=True, nullable=False)
    
    # Response and resolution times in hours
    response_time_hours = Column(Integer, nullable=False)  # Time to first response
    resolution_time_hours = Column(Integer, nullable=False)  # Time to resolve
    
    description = Column(String(500))
