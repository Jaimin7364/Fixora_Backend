from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.database.base import Base


class SlackInstallation(Base):
    __tablename__ = "slack_installations"
    __table_args__ = (
        UniqueConstraint("team_id", name="uq_slack_installations_team_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    team_id = Column(String(100), nullable=False, index=True)
    team_name = Column(String(255))
    bot_user_id = Column(String(100))
    bot_token_encrypted = Column(String(500), nullable=False)
    scope = Column(String(500))
    installed_by = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
