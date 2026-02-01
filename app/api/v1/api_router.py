from fastapi import APIRouter
from app.api.v1 import ticket_routes, kb_routes, slack_routes, metrics_routes, user_routes

api_router = APIRouter()

# Include all route modules
api_router.include_router(ticket_routes.router)
api_router.include_router(user_routes.router)
api_router.include_router(kb_routes.router)
api_router.include_router(slack_routes.router)
api_router.include_router(metrics_routes.router)


