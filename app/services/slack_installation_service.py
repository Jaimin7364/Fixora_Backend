import base64
import hashlib
from typing import Optional

from cryptography.fernet import Fernet
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.slack_installation import SlackInstallation


class SlackInstallationService:
    @staticmethod
    def _fernet() -> Fernet:
        if settings.SLACK_ENCRYPTION_KEY:
            key = settings.SLACK_ENCRYPTION_KEY.encode()
        else:
            digest = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
            key = base64.urlsafe_b64encode(digest)
        return Fernet(key)

    @staticmethod
    def encrypt_token(token: str) -> str:
        return SlackInstallationService._fernet().encrypt(token.encode()).decode()

    @staticmethod
    def decrypt_token(token_encrypted: str) -> str:
        return SlackInstallationService._fernet().decrypt(token_encrypted.encode()).decode()

    @staticmethod
    def get_by_team_id(db: Session, team_id: str) -> Optional[SlackInstallation]:
        return db.query(SlackInstallation).filter(SlackInstallation.team_id == team_id).first()

    @staticmethod
    def upsert_installation(
        db: Session,
        team_id: str,
        team_name: Optional[str],
        organization_id: int,
        bot_user_id: Optional[str],
        bot_token: str,
        scope: Optional[str],
        installed_by: Optional[str],
    ) -> SlackInstallation:
        installation = SlackInstallationService.get_by_team_id(db, team_id)
        token_encrypted = SlackInstallationService.encrypt_token(bot_token)

        if installation:
            installation.team_name = team_name
            installation.organization_id = organization_id
            installation.bot_user_id = bot_user_id
            installation.bot_token_encrypted = token_encrypted
            installation.scope = scope
            installation.installed_by = installed_by
            db.commit()
            db.refresh(installation)
            return installation

        installation = SlackInstallation(
            team_id=team_id,
            team_name=team_name,
            organization_id=organization_id,
            bot_user_id=bot_user_id,
            bot_token_encrypted=token_encrypted,
            scope=scope,
            installed_by=installed_by,
        )
        db.add(installation)
        db.commit()
        db.refresh(installation)
        return installation
