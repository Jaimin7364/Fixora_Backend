from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.ticket import TicketCategory


class KBBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=500)
    question: str = Field(..., min_length=10)
    answer: str = Field(..., min_length=20)
    category: TicketCategory
    keywords: Optional[str] = Field(None, max_length=500)


class KBCreate(KBBase):
    is_active: bool = True
    is_featured: bool = False


class KBUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=500)
    question: Optional[str] = Field(None, min_length=10)
    answer: Optional[str] = Field(None, min_length=20)
    category: Optional[TicketCategory] = None
    keywords: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None


class KBResponse(KBBase):
    id: int
    view_count: int
    helpful_count: int
    not_helpful_count: int
    is_active: bool
    is_featured: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class KBListResponse(BaseModel):
    articles: List[KBResponse]
    total: int
    page: int
    page_size: int


class KBSearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=200)
    category: Optional[TicketCategory] = None


class KBSearchResponse(BaseModel):
    results: List[KBResponse]
    total: int
