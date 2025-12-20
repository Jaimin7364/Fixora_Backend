from fastapi import FastAPI
from app.database.base import Base
from app.database.session import engine
from app.api.v1.api_router import api_router

app = FastAPI(title="AI IT Support Backend")

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

app.include_router(api_router, prefix="/api/v1")
