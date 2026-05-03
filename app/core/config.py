from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Fixora"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Slack Configuration
    SLACK_BOT_TOKEN: Optional[str] = None
    SLACK_SIGNING_SECRET: Optional[str] = None
    SLACK_CLIENT_ID: Optional[str] = None
    SLACK_CLIENT_SECRET: Optional[str] = None
    SLACK_OAUTH_REDIRECT_URI: Optional[str] = None
    SLACK_OAUTH_SCOPES: str = "commands,app_mentions:read,chat:write"
    SLACK_ENCRYPTION_KEY: Optional[str] = None

    # Internal API (testing only)
    INTERNAL_API_TOKEN: Optional[str] = None
    INTERNAL_USER_ID: Optional[int] = None
    
    # Gemini AI
    GEMINI_API_KEY: Optional[str] = None
    
    # n8n Integration
    N8N_WEBHOOK_URL: Optional[str] = None
    N8N_SOLUTION_WEBHOOK_URL: Optional[str] = None
    N8N_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"


settings = Settings()

