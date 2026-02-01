from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
from typing import Optional, List
from app.models.ticket import Ticket, TicketStatus, TicketPriority, TicketCategory
from app.models.ticket_activity import TicketActivity, ActivityType
from app.models.sla_policy import SLAPolicy
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketStatusUpdate, CommentCreate


class TicketService:
    
    @staticmethod
    def generate_ticket_number(db: Session) -> str:
        """Generate unique ticket number in format TKT-YYYY-XXXX"""
        current_year = datetime.now().year
        
        # Get the last ticket number for current year
        last_ticket = db.query(Ticket).filter(
            Ticket.ticket_number.like(f"TKT-{current_year}-%")
        ).order_by(Ticket.ticket_number.desc()).first()
        
        if last_ticket:
            # Extract sequence number and increment
            last_sequence = int(last_ticket.ticket_number.split('-')[-1])
            new_sequence = last_sequence + 1
        else:
            new_sequence = 1
        
        return f"TKT-{current_year}-{new_sequence:04d}"
    
    @staticmethod
    def calculate_sla_deadline(db: Session, priority: TicketPriority) -> Optional[datetime]:
        """Calculate SLA deadline based on priority"""
        sla_policy = db.query(SLAPolicy).filter(
            SLAPolicy.priority == priority.value
        ).first()
        
        if sla_policy:
            return datetime.now() + timedelta(hours=sla_policy.resolution_time_hours)
        return None
    
    @staticmethod
    def create_ticket(
        db: Session, 
        ticket_data: TicketCreate, 
        user_id: int
    ) -> Ticket:
        """Create a new ticket"""
        # Generate ticket number
        ticket_number = TicketService.generate_ticket_number(db)
        
        # Set default priority if not specified
        priority = TicketPriority.MEDIUM
        
        # Calculate SLA deadline
        sla_deadline = TicketService.calculate_sla_deadline(db, priority)
        
        # Create ticket
        ticket = Ticket(
            ticket_number=ticket_number,
            user_id=user_id,
            title=ticket_data.title,
            description=ticket_data.description,
            category=ticket_data.category,
            priority=priority,
            status=TicketStatus.OPEN,
            sla_deadline=sla_deadline
        )
        
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        
        # Create activity log
        activity = TicketActivity(
            ticket_id=ticket.id,
            user_id=user_id,
            activity_type=ActivityType.CREATED,
            description=f"Ticket created: {ticket.title}"
        )
        db.add(activity)
        db.commit()
        
        return ticket
    
    @staticmethod
    def get_ticket(db: Session, ticket_id: int) -> Optional[Ticket]:
        """Get ticket by ID"""
        return db.query(Ticket).filter(Ticket.id == ticket_id).first()
    
    @staticmethod
    def get_ticket_by_number(db: Session, ticket_number: str) -> Optional[Ticket]:
        """Get ticket by ticket number"""
        return db.query(Ticket).filter(Ticket.ticket_number == ticket_number).first()
    
    @staticmethod
    def list_tickets(
        db: Session,
        status: Optional[TicketStatus] = None,
        priority: Optional[TicketPriority] = None,
        category: Optional[TicketCategory] = None,
        user_id: Optional[int] = None,
        assigned_to_id: Optional[int] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Ticket], int]:
        """List tickets with filters and pagination"""
        query = db.query(Ticket)
        
        # Apply filters
        if status:
            query = query.filter(Ticket.status == status)
        if priority:
            query = query.filter(Ticket.priority == priority)
        if category:
            query = query.filter(Ticket.category == category)
        if user_id:
            query = query.filter(Ticket.user_id == user_id)
        if assigned_to_id:
            query = query.filter(Ticket.assigned_to_id == assigned_to_id)
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    Ticket.title.ilike(search_filter),
                    Ticket.description.ilike(search_filter),
                    Ticket.ticket_number.ilike(search_filter)
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        tickets = query.order_by(Ticket.created_at.desc()).offset(skip).limit(limit).all()
        
        return tickets, total
    
    @staticmethod
    def update_ticket(
        db: Session,
        ticket_id: int,
        ticket_update: TicketUpdate,
        user_id: int
    ) -> Optional[Ticket]:
        """Update ticket"""
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            return None
        
        update_data = ticket_update.model_dump(exclude_unset=True)
        
        # Track changes for activity log
        changes = []
        for field, value in update_data.items():
            if hasattr(ticket, field) and getattr(ticket, field) != value:
                old_value = getattr(ticket, field)
                setattr(ticket, field, value)
                changes.append((field, old_value, value))
        
        if changes:
            db.commit()
            db.refresh(ticket)
            
            # Create activity logs for each change
            for field, old_value, new_value in changes:
                activity = TicketActivity(
                    ticket_id=ticket.id,
                    user_id=user_id,
                    activity_type=ActivityType.UPDATED,
                    description=f"Updated {field}",
                    old_value=str(old_value),
                    new_value=str(new_value)
                )
                db.add(activity)
            
            db.commit()
        
        return ticket
    
    @staticmethod
    def change_status(
        db: Session,
        ticket_id: int,
        status_update: TicketStatusUpdate,
        user_id: int
    ) -> Optional[Ticket]:
        """Change ticket status"""
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            return None
        
        old_status = ticket.status
        ticket.status = status_update.status
        
        # Set resolved_at or closed_at timestamps
        if status_update.status == TicketStatus.RESOLVED:
            ticket.resolved_at = datetime.now()
        elif status_update.status == TicketStatus.CLOSED:
            ticket.closed_at = datetime.now()
        
        db.commit()
        db.refresh(ticket)
        
        # Create activity log
        activity = TicketActivity(
            ticket_id=ticket.id,
            user_id=user_id,
            activity_type=ActivityType.STATUS_CHANGED,
            description=f"Status changed from {old_status.value} to {status_update.status.value}",
            old_value=old_status.value,
            new_value=status_update.status.value
        )
        db.add(activity)
        db.commit()
        
        return ticket
    
    @staticmethod
    def assign_ticket(
        db: Session,
        ticket_id: int,
        assigned_to_id: int,
        user_id: int
    ) -> Optional[Ticket]:
        """Assign ticket to IT staff"""
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            return None
        
        old_assignee = ticket.assigned_to_id
        ticket.assigned_to_id = assigned_to_id
        
        # Update status to in_progress if it was open
        if ticket.status == TicketStatus.OPEN:
            ticket.status = TicketStatus.IN_PROGRESS
        
        db.commit()
        db.refresh(ticket)
        
        # Create activity log
        activity = TicketActivity(
            ticket_id=ticket.id,
            user_id=user_id,
            activity_type=ActivityType.ASSIGNED,
            description=f"Ticket assigned to user {assigned_to_id}",
            old_value=str(old_assignee) if old_assignee else None,
            new_value=str(assigned_to_id)
        )
        db.add(activity)
        db.commit()
        
        return ticket
    
    @staticmethod
    def add_comment(
        db: Session,
        ticket_id: int,
        comment_data: CommentCreate,
        user_id: int
    ) -> TicketActivity:
        """Add comment to ticket"""
        activity = TicketActivity(
            ticket_id=ticket_id,
            user_id=user_id,
            activity_type=ActivityType.COMMENT,
            description=comment_data.comment
        )
        
        db.add(activity)
        db.commit()
        db.refresh(activity)
        
        return activity
    
    @staticmethod
    def get_ticket_activities(
        db: Session,
        ticket_id: int
    ) -> List[TicketActivity]:
        """Get all activities for a ticket"""
        return db.query(TicketActivity).filter(
            TicketActivity.ticket_id == ticket_id
        ).order_by(TicketActivity.created_at.desc()).all()
    
    @staticmethod
    def delete_ticket(db: Session, ticket_id: int) -> bool:
        """Delete ticket (soft delete by setting status to cancelled)"""
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            return False
        
        ticket.status = TicketStatus.CANCELLED
        db.commit()
        return True
    
    @staticmethod
    def update_ai_classification(
        db: Session,
        ticket_id: int,
        category: TicketCategory,
        priority: TicketPriority,
        confidence: float
    ) -> Optional[Ticket]:
        """Update ticket with AI classification results"""
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            return None
        
        ticket.category = category
        ticket.priority = priority
        ticket.ai_classification = f"{category.value}_{priority.value}"
        ticket.ai_confidence = confidence
        
        # Recalculate SLA deadline based on new priority
        ticket.sla_deadline = TicketService.calculate_sla_deadline(db, priority)
        
        db.commit()
        db.refresh(ticket)
        
        return ticket
