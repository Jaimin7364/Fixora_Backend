from sqlalchemy import Column, Integer, String, Enum as SQLEnum, ForeignKey, UniqueConstraint
from app.database.base import Base
from app.models.ticket import TicketPriority


class SLAPolicy(Base):
    __tablename__ = "sla_policies"
    __table_args__ = (
        UniqueConstraint("organization_id", "priority", name="uq_sla_org_priority"),
    )

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), index=True)
    priority = Column(SQLEnum(TicketPriority), nullable=False)
    
    # Response and resolution times in hours
    response_time_hours = Column(Integer, nullable=False)  # Time to first response
    resolution_time_hours = Column(Integer, nullable=False)  # Time to resolve
    
    description = Column(String(500))
