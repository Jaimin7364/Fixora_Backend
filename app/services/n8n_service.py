import requests
from typing import Dict, Any, Optional
from app.core.config import settings
from app.schemas.ticket import TicketCategory, TicketPriority


class N8nService:
    
    @staticmethod
    def send_for_classification(
        ticket_id: int,
        title: str,
        description: str
    ) -> Dict[str, Any]:
        """Send ticket to n8n for AI classification"""
        if not settings.N8N_WEBHOOK_URL:
            return {
                "success": False,
                "error": "n8n webhook URL not configured"
            }
        
        payload = {
            "ticket_id": ticket_id,
            "title": title,
            "description": description
        }
        
        try:
            response = requests.post(
                settings.N8N_WEBHOOK_URL,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def parse_classification_result(
        result_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Parse AI classification result from n8n"""
        try:
            classification = result_data.get("classification", {})
            
            # Map string values to enums
            category_str = classification.get("category", "other")
            priority_str = classification.get("priority", "medium")
            
            # Convert to proper enum values
            try:
                category = TicketCategory(category_str)
            except ValueError:
                category = TicketCategory.OTHER
            
            try:
                priority = TicketPriority(priority_str)
            except ValueError:
                priority = TicketPriority.MEDIUM
            
            # Calculate confidence score
            confidence_level = classification.get("confidence", "medium")
            confidence_map = {
                "high": 0.9,
                "medium": 0.7,
                "low": 0.5
            }
            confidence = confidence_map.get(confidence_level, 0.7)
            
            return {
                "category": category,
                "priority": priority,
                "confidence": confidence,
                "suggested_team": classification.get("suggested_team"),
                "reasoning": classification.get("reasoning")
            }
        except Exception as e:
            print(f"Error parsing classification result: {e}")
            return None
    
    @staticmethod
    def request_solution_suggestion(
        ticket_id: int,
        title: str,
        description: str,
        category: str
    ) -> Dict[str, Any]:
        """Request AI-suggested solutions for a ticket"""
        if not settings.N8N_SOLUTION_WEBHOOK_URL:
            return {
                "success": False,
                "error": "n8n solution webhook URL not configured"
            }
        
        payload = {
            "ticket_id": ticket_id,
            "title": title,
            "description": description,
            "category": category
        }
        
        try:
            response = requests.post(
                settings.N8N_SOLUTION_WEBHOOK_URL,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "suggestions": response.json().get("suggestions", [])
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
