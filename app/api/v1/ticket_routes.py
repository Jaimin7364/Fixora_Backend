from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database.session import get_db
from app.core.security import get_current_user, require_roles
from app.models.user import User, UserRole
from app.schemas.ticket import (
    TicketCreate, TicketUpdate, TicketResponse, TicketListResponse,
    TicketStatusUpdate, TicketAssignment, CommentCreate,
    TicketStatus, TicketPriority, TicketCategory, TicketActivityResponse
)
from app.services.ticket_service import TicketService
from app.services.n8n_service import N8nService

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(
    ticket_data: TicketCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new support ticket
    
    - **title**: Brief description of the issue (5-500 characters)
    - **description**: Detailed description (minimum 10 characters)
    - **category**: Issue category (hardware, software, network, etc.)
    """
    user_id = current_user.id
    
    # Create ticket
    ticket = TicketService.create_ticket(db, ticket_data, user_id)
    
    # Send to n8n for AI classification (async in production)
    try:
        classification_result = N8nService.send_for_classification(
            ticket_id=ticket.id,
            title=ticket.title,
            description=ticket.description
        )
        
        if classification_result.get("success") and classification_result.get("data"):
            parsed = N8nService.parse_classification_result(classification_result["data"])
            if parsed:
                TicketService.update_ai_classification(
                    db,
                    ticket.id,
                    parsed["category"],
                    parsed["priority"],
                    parsed["confidence"]
                )
                db.refresh(ticket)
    except Exception as e:
        # Log error but don't fail ticket creation
        print(f"AI classification failed: {e}")
    
    return ticket


@router.get("/", response_model=TicketListResponse)
def list_tickets(
    status_filter: Optional[TicketStatus] = Query(None, alias="status"),
    priority: Optional[TicketPriority] = None,
    category: Optional[TicketCategory] = None,
    user_id: Optional[int] = None,
    assigned_to_id: Optional[int] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all tickets with optional filters
    
    - **status**: Filter by status (open, in_progress, resolved, etc.)
    - **priority**: Filter by priority (low, medium, high, urgent)
    - **category**: Filter by category
    - **user_id**: Filter by ticket creator
    - **assigned_to_id**: Filter by assigned IT staff
    - **search**: Search in title, description, or ticket number
    - **page**: Page number (starts at 1)
    - **page_size**: Items per page (1-100)
    """
    skip = (page - 1) * page_size

    if current_user.role == UserRole.EMPLOYEE:
        user_id = current_user.id
        assigned_to_id = None
    
    tickets, total = TicketService.list_tickets(
        db=db,
        status=status_filter,
        priority=priority,
        category=category,
        user_id=user_id,
        assigned_to_id=assigned_to_id,
        search=search,
        skip=skip,
        limit=page_size
    )
    
    return TicketListResponse(
        tickets=tickets,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific ticket
    """
    ticket = TicketService.get_ticket(db, ticket_id)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID {ticket_id} not found"
        )

    if current_user.role == UserRole.EMPLOYEE and ticket.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this ticket"
        )
    
    return ticket


@router.get("/number/{ticket_number}", response_model=TicketResponse)
def get_ticket_by_number(
    ticket_number: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get ticket by ticket number (e.g., TKT-2026-0001)
    """
    ticket = TicketService.get_ticket_by_number(db, ticket_number)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket {ticket_number} not found"
        )

    if current_user.role == UserRole.EMPLOYEE and ticket.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this ticket"
        )
    
    return ticket


@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: int,
    ticket_update: TicketUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update ticket information
    
    Can update: title, description, category, priority, status, assigned_to_id
    """
    existing_ticket = TicketService.get_ticket(db, ticket_id)
    if not existing_ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID {ticket_id} not found"
        )

    if current_user.role == UserRole.EMPLOYEE and existing_ticket.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this ticket"
        )
    
    ticket = TicketService.update_ticket(db, ticket_id, ticket_update, current_user.id)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID {ticket_id} not found"
        )
    
    return ticket


@router.patch("/{ticket_id}/status", response_model=TicketResponse)
def change_ticket_status(
    ticket_id: int,
    status_update: TicketStatusUpdate,
    current_user: User = Depends(
        require_roles([UserRole.ADMIN, UserRole.IT_SUPPORT, UserRole.MANAGER])
    ),
    db: Session = Depends(get_db)
):
    """
    Change ticket status
    
    Available statuses:
    - open
    - in_progress
    - waiting_on_user
    - resolved
    - closed
    - cancelled
    """
    ticket = TicketService.change_status(db, ticket_id, status_update, current_user.id)
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID {ticket_id} not found"
        )
    
    return ticket


@router.patch("/{ticket_id}/assign", response_model=TicketResponse)
def assign_ticket(
    ticket_id: int,
    assignment: TicketAssignment,
    current_user: User = Depends(
        require_roles([UserRole.ADMIN, UserRole.IT_SUPPORT, UserRole.MANAGER])
    ),
    db: Session = Depends(get_db)
):
    """
    Assign ticket to IT support staff
    """
    ticket = TicketService.assign_ticket(
        db, ticket_id, assignment.assigned_to_id, current_user.id
    )
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID {ticket_id} not found"
        )
    
    return ticket


@router.post("/{ticket_id}/comments", response_model=TicketActivityResponse)
def add_comment(
    ticket_id: int,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a comment to a ticket
    """
    # Verify ticket exists
    ticket = TicketService.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID {ticket_id} not found"
        )
    
    if current_user.role == UserRole.EMPLOYEE and ticket.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to comment on this ticket"
        )

    activity = TicketService.add_comment(db, ticket_id, comment_data, current_user.id)
    
    return activity


@router.get("/{ticket_id}/activities", response_model=List[TicketActivityResponse])
def get_ticket_activities(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all activities/history for a ticket
    """
    # Verify ticket exists
    ticket = TicketService.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID {ticket_id} not found"
        )

    if current_user.role == UserRole.EMPLOYEE and ticket.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this ticket activity"
        )
    
    activities = TicketService.get_ticket_activities(db, ticket_id)
    
    return activities


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(
    ticket_id: int,
    _current_user: User = Depends(
        require_roles([UserRole.ADMIN, UserRole.IT_SUPPORT, UserRole.MANAGER])
    ),
    db: Session = Depends(get_db)
):
    """
    Delete a ticket (sets status to cancelled)
    """
    success = TicketService.delete_ticket(db, ticket_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID {ticket_id} not found"
        )
    
    return None


@router.get("/user/{user_id}", response_model=TicketListResponse)
def get_user_tickets(
    user_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all tickets for a specific user
    """
    if current_user.role == UserRole.EMPLOYEE and user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own tickets"
        )

    skip = (page - 1) * page_size
    
    tickets, total = TicketService.list_tickets(
        db=db,
        user_id=user_id,
        skip=skip,
        limit=page_size
    )
    
    return TicketListResponse(
        tickets=tickets,
        total=total,
        page=page,
        page_size=page_size
    )
