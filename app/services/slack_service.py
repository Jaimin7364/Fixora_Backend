import requests
from typing import Optional, Dict, Any
from app.core.config import settings


class SlackService:
    
    @staticmethod
    def send_message(channel: str, text: str, blocks: Optional[list] = None) -> Dict[str, Any]:
        """Send a message to Slack channel or user"""
        if not settings.SLACK_BOT_TOKEN:
            return {"ok": False, "error": "Slack token not configured"}
        
        url = "https://slack.com/api/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {settings.SLACK_BOT_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "channel": channel,
            "text": text
        }
        
        if blocks:
            payload["blocks"] = blocks
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            return response.json()
        except Exception as e:
            return {"ok": False, "error": str(e)}
    
    @staticmethod
    def send_ticket_created_notification(
        slack_user_id: str,
        ticket_number: str,
        title: str,
        priority: str
    ) -> Dict[str, Any]:
        """Send notification when ticket is created"""
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"✅ *Ticket Created Successfully*"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Ticket Number:*\n{ticket_number}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Priority:*\n{priority.upper()}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Title:*\n{title}"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Details"
                        },
                        "value": ticket_number,
                        "action_id": "view_ticket"
                    }
                ]
            }
        ]
        
        return SlackService.send_message(
            channel=slack_user_id,
            text=f"Ticket {ticket_number} created",
            blocks=blocks
        )
    
    @staticmethod
    def send_status_update_notification(
        slack_user_id: str,
        ticket_number: str,
        old_status: str,
        new_status: str,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send notification when ticket status changes"""
        emoji_map = {
            "open": "🔵",
            "in_progress": "🟡",
            "waiting_on_user": "🟠",
            "resolved": "✅",
            "closed": "⚫",
            "cancelled": "❌"
        }
        
        emoji = emoji_map.get(new_status, "🔔")
        text = f"{emoji} *Ticket Status Updated*\n\n"
        text += f"*Ticket:* {ticket_number}\n"
        text += f"*Status:* {old_status.replace('_', ' ').title()} → {new_status.replace('_', ' ').title()}"
        
        if message:
            text += f"\n\n*Message:* {message}"
        
        return SlackService.send_message(
            channel=slack_user_id,
            text=text
        )
    
    @staticmethod
    def send_assignment_notification(
        slack_user_id: str,
        ticket_number: str,
        title: str,
        assigned_by: str
    ) -> Dict[str, Any]:
        """Send notification when ticket is assigned to IT staff"""
        text = f"🎯 *New Ticket Assigned to You*\n\n"
        text += f"*Ticket:* {ticket_number}\n"
        text += f"*Title:* {title}\n"
        text += f"*Assigned by:* {assigned_by}"
        
        return SlackService.send_message(
            channel=slack_user_id,
            text=text
        )
    
    @staticmethod
    def send_comment_notification(
        slack_user_id: str,
        ticket_number: str,
        commenter_name: str,
        comment: str
    ) -> Dict[str, Any]:
        """Send notification when someone comments on ticket"""
        text = f"💬 *New Comment on Your Ticket*\n\n"
        text += f"*Ticket:* {ticket_number}\n"
        text += f"*From:* {commenter_name}\n"
        text += f"*Comment:* {comment}"
        
        return SlackService.send_message(
            channel=slack_user_id,
            text=text
        )
