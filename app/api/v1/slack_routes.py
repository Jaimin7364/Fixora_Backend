from fastapi import APIRouter, Request, Response, HTTPException, status
from sqlalchemy.orm import Session
from fastapi import Depends
import hmac
import hashlib
from typing import Dict, Any
from app.database.session import get_db
from app.services.ticket_service import TicketService
from app.services.user_service import UserService
from app.schemas.ticket import TicketCreate
from app.core.config import settings

router = APIRouter(prefix="/slack", tags=["Slack Integration"])


def verify_slack_signature(request: Request, body: bytes) -> bool:
    """Verify that request came from Slack"""
    if not settings.SLACK_SIGNING_SECRET:
        return True  # Skip verification if not configured
    
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    slack_signature = request.headers.get("X-Slack-Signature", "")
    
    # Create signature
    sig_basestring = f"v0:{timestamp}:{body.decode()}"
    my_signature = "v0=" + hmac.new(
        settings.SLACK_SIGNING_SECRET.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(my_signature, slack_signature)


@router.post("/events")
async def slack_events(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle Slack events (messages, mentions, etc.)
    """
    body = await request.body()
    
    # Verify signature
    if not verify_slack_signature(request, body):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Slack signature"
        )
    
    data = await request.json()
    
    # Handle URL verification challenge
    if data.get("type") == "url_verification":
        return {"challenge": data.get("challenge")}
    
    # Handle events
    event = data.get("event", {})
    event_type = event.get("type")
    
    if event_type == "app_mention":
        # Handle @mention
        text = event.get("text", "")
        user_id = event.get("user")
        channel = event.get("channel")
        
        # Create ticket from mention
        # Extract text after mention
        ticket_text = text.split(">", 1)[-1].strip()
        
        if ticket_text:
            # Find or create user
            user = UserService.get_user_by_slack_id(db, user_id)
            if not user:
                # Auto-create user (in production, get details from Slack API)
                from app.schemas.user import UserCreate
                user = UserService.create_user(db, UserCreate(
                    email=f"{user_id}@slack.local",
                    full_name=f"Slack User {user_id}",
                    teams_user_id=user_id
                ))
            
            # Create ticket
            ticket_data = TicketCreate(
                title=ticket_text[:100],  # Use first 100 chars as title
                description=ticket_text,
                category="other"
            )
            ticket = TicketService.create_ticket(db, ticket_data, user.id)
            
            return {
                "status": "success",
                "ticket_number": ticket.ticket_number
            }
    
    return {"status": "ok"}


@router.post("/commands")
async def slack_commands(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle Slack slash commands
    
    Supported commands:
    - /ticket [description] - Create a ticket
    - /status [ticket_number] - Check ticket status
    - /mytickets - List my tickets
    """
    form_data = await request.form()
    
    command = form_data.get("command")
    text = form_data.get("text", "")
    user_id = form_data.get("user_id")
    
    if command == "/ticket":
        # Create ticket
        if not text:
            return {
                "response_type": "ephemeral",
                "text": "Please provide a description: /ticket My laptop won't start"
            }
        
        # Find or create user
        user = UserService.get_user_by_slack_id(db, user_id)
        if not user:
            from app.schemas.user import UserCreate
            user = UserService.create_user(db, UserCreate(
                email=f"{user_id}@slack.local",
                full_name=f"Slack User {user_id}",
                teams_user_id=user_id
            ))
        
        # Create ticket
        ticket_data = TicketCreate(
            title=text[:100],
            description=text,
            category="other"
        )
        ticket = TicketService.create_ticket(db, ticket_data, user.id)
        
        return {
            "response_type": "in_channel",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"✅ *Ticket Created*\n\n*Ticket Number:* {ticket.ticket_number}\n*Priority:* {ticket.priority.value.upper()}\n*Status:* {ticket.status.value.replace('_', ' ').title()}"
                    }
                }
            ]
        }
    
    elif command == "/status":
        # Check ticket status
        if not text:
            return {
                "response_type": "ephemeral",
                "text": "Please provide a ticket number: /status TKT-2026-0001"
            }
        
        ticket = TicketService.get_ticket_by_number(db, text.strip())
        
        if not ticket:
            return {
                "response_type": "ephemeral",
                "text": f"Ticket {text} not found"
            }
        
        return {
            "response_type": "ephemeral",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Ticket:* {ticket.ticket_number}\n*Title:* {ticket.title}\n*Status:* {ticket.status.value.replace('_', ' ').title()}\n*Priority:* {ticket.priority.value.upper()}\n*Created:* {ticket.created_at.strftime('%Y-%m-%d %H:%M')}"
                    }
                }
            ]
        }
    
    elif command == "/mytickets":
        # List user's tickets
        user = UserService.get_user_by_slack_id(db, user_id)
        
        if not user:
            return {
                "response_type": "ephemeral",
                "text": "No tickets found. Create one with /ticket"
            }
        
        tickets, total = TicketService.list_tickets(db, user_id=user.id, limit=5)
        
        if not tickets:
            return {
                "response_type": "ephemeral",
                "text": "You have no tickets"
            }
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Your Recent Tickets* (Total: {total})"
                }
            }
        ]
        
        for ticket in tickets:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"• *{ticket.ticket_number}* - {ticket.title}\n  Status: {ticket.status.value.replace('_', ' ').title()} | Priority: {ticket.priority.value.upper()}"
                }
            })
        
        return {
            "response_type": "ephemeral",
            "blocks": blocks
        }
    
    return {
        "response_type": "ephemeral",
        "text": f"Unknown command: {command}"
    }


@router.post("/interactions")
async def slack_interactions(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle Slack interactive components (button clicks, etc.)
    """
    form_data = await request.form()
    import json
    
    payload = json.loads(form_data.get("payload", "{}"))
    
    action_type = payload.get("type")
    
    if action_type == "block_actions":
        actions = payload.get("actions", [])
        
        for action in actions:
            action_id = action.get("action_id")
            
            if action_id == "view_ticket":
                ticket_number = action.get("value")
                ticket = TicketService.get_ticket_by_number(db, ticket_number)
                
                if ticket:
                    return {
                        "text": f"*Ticket: {ticket.ticket_number}*\n\n*Title:* {ticket.title}\n*Description:* {ticket.description}\n*Status:* {ticket.status.value}\n*Priority:* {ticket.priority.value}"
                    }
    
    return {"status": "ok"}


@router.post("/webhook/classification")
async def receive_classification(
    data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Receive AI classification results from n8n
    
    Expected format:
    {
        "ticket_id": 123,
        "classification": {
            "category": "hardware",
            "priority": "high",
            "confidence": "high"
        }
    }
    """
    ticket_id = data.get("ticket_id")
    classification = data.get("classification", {})
    
    if not ticket_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ticket_id is required"
        )
    
    from app.services.n8n_service import N8nService
    
    parsed = N8nService.parse_classification_result(data)
    
    if parsed:
        ticket = TicketService.update_ai_classification(
            db,
            ticket_id,
            parsed["category"],
            parsed["priority"],
            parsed["confidence"]
        )
        
        if ticket:
            return {
                "status": "success",
                "ticket_number": ticket.ticket_number,
                "classification": {
                    "category": ticket.category.value,
                    "priority": ticket.priority.value,
                    "confidence": ticket.ai_confidence
                }
            }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Ticket not found or classification failed"
    )
