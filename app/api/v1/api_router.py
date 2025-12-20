from fastapi import APIRouter
from app.api.v1 import ticket_routes

api_router = APIRouter()

api_router.include_router(ticket_routes.router, prefix="/tickets", tags=["Tickets"])

