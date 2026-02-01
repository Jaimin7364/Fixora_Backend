from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_ON_USER = "waiting_on_user"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketCategory(str, Enum):
    HARDWARE = "hardware"
    SOFTWARE = "software"
    NETWORK = "network"
    ACCESS = "access"
    EMAIL = "email"
    PRINTER = "printer"
    ACCOUNT = "account"
    OTHER = "other"


class TicketBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=500)
    description: str = Field(..., min_length=10)
    category: TicketCategory


class TicketCreate(TicketBase):
    user_id: Optional[int] = None  # Can be set from auth context


class TicketUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=500)
    description: Optional[str] = Field(None, min_length=10)
    category: Optional[TicketCategory] = None
    priority: Optional[TicketPriority] = None
    status: Optional[TicketStatus] = None
    assigned_to_id: Optional[int] = None


class TicketStatusUpdate(BaseModel):
    status: TicketStatus


class TicketAssignment(BaseModel):
    assigned_to_id: int


class CommentCreate(BaseModel):
    comment: str = Field(..., min_length=1, max_length=2000)


class UserInfo(BaseModel):
    id: int
    email: str
    full_name: str
    
    class Config:
        from_attributes = True


class TicketActivityResponse(BaseModel):
    id: int
    ticket_id: int
    user_id: int
    activity_type: str
    description: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    created_at: datetime
    user: Optional[UserInfo] = None
    
    class Config:
        from_attributes = True


class TicketResponse(TicketBase):
    id: int
    ticket_number: str
    user_id: int
    assigned_to_id: Optional[int] = None
    priority: TicketPriority
    status: TicketStatus
    ai_classification: Optional[str] = None
    ai_confidence: Optional[float] = None
    sla_deadline: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Related data
    user: Optional[UserInfo] = None
    assigned_to: Optional[UserInfo] = None
    activities: List[TicketActivityResponse] = []
    
    class Config:
        from_attributes = True


class TicketListResponse(BaseModel):
    tickets: List[TicketResponse]
    total: int
    page: int
    page_size: int


class DashboardStats(BaseModel):
    total_tickets: int
    open_tickets: int
    in_progress_tickets: int
    resolved_today: int
    average_resolution_hours: float
