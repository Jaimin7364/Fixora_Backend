from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import Dict, Any, List
from app.database.session import get_db
from app.models.ticket import Ticket, TicketStatus, TicketPriority, TicketCategory
from app.schemas.ticket import DashboardStats

router = APIRouter(prefix="/metrics", tags=["Metrics & Analytics"])


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Get overall dashboard statistics
    
    Returns:
    - Total tickets
    - Open tickets
    - In-progress tickets
    - Resolved today
    - Average resolution time in hours
    """
    # Total tickets
    total_tickets = db.query(func.count(Ticket.id)).scalar()
    
    # Open tickets
    open_tickets = db.query(func.count(Ticket.id)).filter(
        Ticket.status == TicketStatus.OPEN
    ).scalar()
    
    # In-progress tickets
    in_progress_tickets = db.query(func.count(Ticket.id)).filter(
        Ticket.status == TicketStatus.IN_PROGRESS
    ).scalar()
    
    # Resolved today
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    resolved_today = db.query(func.count(Ticket.id)).filter(
        and_(
            Ticket.status == TicketStatus.RESOLVED,
            Ticket.resolved_at >= today_start
        )
    ).scalar()
    
    # Average resolution time
    resolved_tickets = db.query(
        Ticket.created_at,
        Ticket.resolved_at
    ).filter(
        Ticket.resolved_at.isnot(None)
    ).limit(100).all()
    
    if resolved_tickets:
        total_hours = sum([
            (t.resolved_at - t.created_at).total_seconds() / 3600
            for t in resolved_tickets
        ])
        avg_resolution_hours = round(total_hours / len(resolved_tickets), 2)
    else:
        avg_resolution_hours = 0.0
    
    return DashboardStats(
        total_tickets=total_tickets or 0,
        open_tickets=open_tickets or 0,
        in_progress_tickets=in_progress_tickets or 0,
        resolved_today=resolved_today or 0,
        average_resolution_hours=avg_resolution_hours
    )


@router.get("/tickets-by-category")
def get_tickets_by_category(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Get ticket count grouped by category
    
    Returns list of {category, count}
    """
    results = db.query(
        Ticket.category,
        func.count(Ticket.id).label('count')
    ).group_by(Ticket.category).all()
    
    return [
        {
            "category": category.value if category else "unknown",
            "count": count
        }
        for category, count in results
    ]


@router.get("/tickets-by-status")
def get_tickets_by_status(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Get ticket count grouped by status
    
    Returns list of {status, count}
    """
    results = db.query(
        Ticket.status,
        func.count(Ticket.id).label('count')
    ).group_by(Ticket.status).all()
    
    return [
        {
            "status": status.value if status else "unknown",
            "count": count
        }
        for status, count in results
    ]


@router.get("/tickets-by-priority")
def get_tickets_by_priority(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Get ticket count grouped by priority
    
    Returns list of {priority, count}
    """
    results = db.query(
        Ticket.priority,
        func.count(Ticket.id).label('count')
    ).group_by(Ticket.priority).all()
    
    return [
        {
            "priority": priority.value if priority else "unknown",
            "count": count
        }
        for priority, count in results
    ]


@router.get("/ticket-trends")
def get_ticket_trends(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get daily ticket creation trends
    
    - **days**: Number of days to include (1-365)
    
    Returns list of {date, count}
    """
    start_date = datetime.now() - timedelta(days=days)
    
    results = db.query(
        func.date(Ticket.created_at).label('date'),
        func.count(Ticket.id).label('count')
    ).filter(
        Ticket.created_at >= start_date
    ).group_by(
        func.date(Ticket.created_at)
    ).order_by('date').all()
    
    return [
        {
            "date": str(date),
            "count": count
        }
        for date, count in results
    ]


@router.get("/resolution-time-by-priority")
def get_resolution_time_by_priority(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Get average resolution time grouped by priority
    
    Returns list of {priority, avg_hours}
    """
    results = []
    
    for priority in TicketPriority:
        tickets = db.query(Ticket).filter(
            and_(
                Ticket.priority == priority,
                Ticket.resolved_at.isnot(None)
            )
        ).limit(50).all()
        
        if tickets:
            total_hours = sum([
                (t.resolved_at - t.created_at).total_seconds() / 3600
                for t in tickets
            ])
            avg_hours = round(total_hours / len(tickets), 2)
        else:
            avg_hours = 0.0
        
        results.append({
            "priority": priority.value,
            "avg_hours": avg_hours,
            "ticket_count": len(tickets)
        })
    
    return results


@router.get("/sla-compliance")
def get_sla_compliance(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get SLA compliance statistics
    
    Returns:
    - Total tickets with SLA
    - Met SLA count
    - Missed SLA count
    - Compliance percentage
    """
    # Tickets with SLA deadline
    tickets_with_sla = db.query(Ticket).filter(
        Ticket.sla_deadline.isnot(None),
        Ticket.resolved_at.isnot(None)
    ).all()
    
    if not tickets_with_sla:
        return {
            "total": 0,
            "met": 0,
            "missed": 0,
            "compliance_percentage": 0.0
        }
    
    met_sla = sum(1 for t in tickets_with_sla if t.resolved_at <= t.sla_deadline)
    missed_sla = len(tickets_with_sla) - met_sla
    compliance = round((met_sla / len(tickets_with_sla)) * 100, 2)
    
    return {
        "total": len(tickets_with_sla),
        "met": met_sla,
        "missed": missed_sla,
        "compliance_percentage": compliance
    }


@router.get("/top-issues")
def get_top_issues(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get most common issues/keywords from ticket titles
    
    Returns top issues by category
    """
    results = db.query(
        Ticket.category,
        func.count(Ticket.id).label('count')
    ).filter(
        Ticket.created_at >= datetime.now() - timedelta(days=30)
    ).group_by(
        Ticket.category
    ).order_by(
        func.count(Ticket.id).desc()
    ).limit(limit).all()
    
    return [
        {
            "category": category.value if category else "unknown",
            "count": count
        }
        for category, count in results
    ]


@router.get("/agent-performance")
def get_agent_performance(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Get performance metrics for IT support agents
    
    Returns list of {agent_id, assigned_count, resolved_count, avg_resolution_hours}
    """
    # Get all tickets assigned to agents
    assigned_tickets = db.query(
        Ticket.assigned_to_id,
        func.count(Ticket.id).label('assigned_count')
    ).filter(
        Ticket.assigned_to_id.isnot(None)
    ).group_by(Ticket.assigned_to_id).all()
    
    results = []
    
    for agent_id, assigned_count in assigned_tickets:
        # Get resolved tickets
        resolved = db.query(Ticket).filter(
            and_(
                Ticket.assigned_to_id == agent_id,
                Ticket.resolved_at.isnot(None)
            )
        ).all()
        
        resolved_count = len(resolved)
        
        if resolved:
            total_hours = sum([
                (t.resolved_at - t.created_at).total_seconds() / 3600
                for t in resolved
            ])
            avg_hours = round(total_hours / resolved_count, 2)
        else:
            avg_hours = 0.0
        
        results.append({
            "agent_id": agent_id,
            "assigned_count": assigned_count,
            "resolved_count": resolved_count,
            "avg_resolution_hours": avg_hours
        })
    
    return sorted(results, key=lambda x: x['resolved_count'], reverse=True)
