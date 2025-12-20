from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models here to ensure they are registered with Base
from app.models.user import User
from app.models.ticket import Ticket
from app.models.ticket_activity import TicketActivity
from app.models.knowledge_base import KnowledgeBase
from app.models.attachment import Attachment
from app.models.sla_policy import SLAPolicy
