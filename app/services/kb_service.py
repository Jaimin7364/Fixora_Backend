from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from app.models.knowledge_base import KnowledgeBase
from app.schemas.kb import KBCreate, KBUpdate
from app.schemas.ticket import TicketCategory


class KBService:
    
    @staticmethod
    def create_article(db: Session, kb_data: KBCreate) -> KnowledgeBase:
        """Create a new knowledge base article"""
        article = KnowledgeBase(
            title=kb_data.title,
            question=kb_data.question,
            answer=kb_data.answer,
            category=kb_data.category,
            keywords=kb_data.keywords,
            is_active=kb_data.is_active,
            is_featured=kb_data.is_featured,
            view_count=0,
            helpful_count=0,
            not_helpful_count=0
        )
        
        db.add(article)
        db.commit()
        db.refresh(article)
        
        return article
    
    @staticmethod
    def get_article(db: Session, article_id: int) -> Optional[KnowledgeBase]:
        """Get article by ID and increment view count"""
        article = db.query(KnowledgeBase).filter(
            KnowledgeBase.id == article_id
        ).first()
        
        if article:
            article.view_count += 1
            db.commit()
            db.refresh(article)
        
        return article
    
    @staticmethod
    def list_articles(
        db: Session,
        category: Optional[TicketCategory] = None,
        is_active: bool = True,
        is_featured: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[KnowledgeBase], int]:
        """List knowledge base articles with filters"""
        query = db.query(KnowledgeBase)
        
        if is_active is not None:
            query = query.filter(KnowledgeBase.is_active == is_active)
        if is_featured is not None:
            query = query.filter(KnowledgeBase.is_featured == is_featured)
        if category:
            query = query.filter(KnowledgeBase.category == category)
        
        total = query.count()
        articles = query.order_by(
            KnowledgeBase.is_featured.desc(),
            KnowledgeBase.view_count.desc()
        ).offset(skip).limit(limit).all()
        
        return articles, total
    
    @staticmethod
    def search_articles(
        db: Session,
        query_text: str,
        category: Optional[TicketCategory] = None,
        limit: int = 10
    ) -> List[KnowledgeBase]:
        """Search knowledge base articles"""
        search_filter = f"%{query_text}%"
        
        query = db.query(KnowledgeBase).filter(
            KnowledgeBase.is_active == True,
            or_(
                KnowledgeBase.title.ilike(search_filter),
                KnowledgeBase.question.ilike(search_filter),
                KnowledgeBase.answer.ilike(search_filter),
                KnowledgeBase.keywords.ilike(search_filter)
            )
        )
        
        if category:
            query = query.filter(KnowledgeBase.category == category)
        
        return query.order_by(
            KnowledgeBase.helpful_count.desc(),
            KnowledgeBase.view_count.desc()
        ).limit(limit).all()
    
    @staticmethod
    def update_article(
        db: Session,
        article_id: int,
        kb_update: KBUpdate
    ) -> Optional[KnowledgeBase]:
        """Update knowledge base article"""
        article = db.query(KnowledgeBase).filter(
            KnowledgeBase.id == article_id
        ).first()
        
        if not article:
            return None
        
        update_data = kb_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(article, field, value)
        
        db.commit()
        db.refresh(article)
        
        return article
    
    @staticmethod
    def mark_helpful(db: Session, article_id: int, helpful: bool = True) -> Optional[KnowledgeBase]:
        """Mark article as helpful or not helpful"""
        article = db.query(KnowledgeBase).filter(
            KnowledgeBase.id == article_id
        ).first()
        
        if not article:
            return None
        
        if helpful:
            article.helpful_count += 1
        else:
            article.not_helpful_count += 1
        
        db.commit()
        db.refresh(article)
        
        return article
    
    @staticmethod
    def delete_article(db: Session, article_id: int) -> bool:
        """Deactivate article (soft delete)"""
        article = db.query(KnowledgeBase).filter(
            KnowledgeBase.id == article_id
        ).first()
        
        if not article:
            return False
        
        article.is_active = False
        db.commit()
        return True
