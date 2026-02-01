from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database.session import get_db
from app.schemas.kb import (
    KBCreate, KBUpdate, KBResponse, KBListResponse,
    KBSearchRequest, KBSearchResponse
)
from app.schemas.ticket import TicketCategory
from app.services.kb_service import KBService

router = APIRouter(prefix="/kb", tags=["Knowledge Base"])


@router.post("/", response_model=KBResponse, status_code=status.HTTP_201_CREATED)
def create_article(
    kb_data: KBCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new knowledge base article (Admin only)
    
    - **title**: Article title
    - **question**: The question being answered
    - **answer**: The solution/answer
    - **category**: Category (hardware, software, etc.)
    - **keywords**: Comma-separated keywords for search
    """
    # TODO: Add admin role check
    article = KBService.create_article(db, kb_data)
    return article


@router.get("/", response_model=KBListResponse)
def list_articles(
    category: Optional[TicketCategory] = None,
    is_featured: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List all knowledge base articles
    
    - **category**: Filter by category
    - **is_featured**: Show only featured articles
    - **page**: Page number
    - **page_size**: Items per page
    """
    skip = (page - 1) * page_size
    
    articles, total = KBService.list_articles(
        db=db,
        category=category,
        is_featured=is_featured,
        skip=skip,
        limit=page_size
    )
    
    return KBListResponse(
        articles=articles,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/search", response_model=KBSearchResponse)
def search_articles(
    q: str = Query(..., min_length=2, max_length=200),
    category: Optional[TicketCategory] = None,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Search knowledge base articles
    
    - **q**: Search query (searches in title, question, answer, keywords)
    - **category**: Filter by category
    - **limit**: Maximum results to return
    """
    results = KBService.search_articles(
        db=db,
        query_text=q,
        category=category,
        limit=limit
    )
    
    return KBSearchResponse(
        results=results,
        total=len(results)
    )


@router.get("/{article_id}", response_model=KBResponse)
def get_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific knowledge base article
    
    This automatically increments the view count
    """
    article = KBService.get_article(db, article_id)
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with ID {article_id} not found"
        )
    
    return article


@router.patch("/{article_id}", response_model=KBResponse)
def update_article(
    article_id: int,
    kb_update: KBUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a knowledge base article (Admin only)
    """
    # TODO: Add admin role check
    article = KBService.update_article(db, article_id, kb_update)
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with ID {article_id} not found"
        )
    
    return article


@router.post("/{article_id}/helpful", response_model=KBResponse)
def mark_helpful(
    article_id: int,
    helpful: bool = Query(True),
    db: Session = Depends(get_db)
):
    """
    Mark an article as helpful or not helpful
    
    - **helpful**: True for helpful, False for not helpful
    """
    article = KBService.mark_helpful(db, article_id, helpful)
    
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with ID {article_id} not found"
        )
    
    return article


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(
    article_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a knowledge base article (Admin only)
    
    This performs a soft delete by setting is_active to False
    """
    # TODO: Add admin role check
    success = KBService.delete_article(db, article_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Article with ID {article_id} not found"
        )
    
    return None


@router.get("/featured/list", response_model=KBListResponse)
def get_featured_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get all featured knowledge base articles
    """
    skip = (page - 1) * page_size
    
    articles, total = KBService.list_articles(
        db=db,
        is_featured=True,
        skip=skip,
        limit=page_size
    )
    
    return KBListResponse(
        articles=articles,
        total=total,
        page=page,
        page_size=page_size
    )
