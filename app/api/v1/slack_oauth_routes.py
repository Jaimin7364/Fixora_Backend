import base64
import hashlib
import hmac
import time
from typing import Optional

import requests
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import get_db
from app.services.user_service import UserService
from app.services.slack_installation_service import SlackInstallationService

router = APIRouter(prefix="/slack/oauth", tags=["Slack OAuth"])


def _sign_state(payload: str) -> str:
    return hmac.new(settings.SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()


def _build_state(team_hint: Optional[str]) -> str:
    ts = str(int(time.time()))
    payload = f"{ts}:{team_hint or ''}"
    signature = _sign_state(payload)
    return base64.urlsafe_b64encode(f"{payload}:{signature}".encode()).decode()


def _verify_state(state: str) -> Optional[str]:
    try:
        decoded = base64.urlsafe_b64decode(state.encode()).decode()
        ts, team_hint, signature = decoded.rsplit(":", 2)
        payload = f"{ts}:{team_hint}"
        if not hmac.compare_digest(signature, _sign_state(payload)):
            return None
        if int(time.time()) - int(ts) > 900:
            return None
        return team_hint or None
    except Exception:
        return None


@router.get("/install")
def slack_install(request: Request, team_hint: Optional[str] = None):
    if not settings.SLACK_CLIENT_ID or not settings.SLACK_OAUTH_REDIRECT_URI:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Slack OAuth settings are not configured",
        )

    state = _build_state(team_hint)
    params = {
        "client_id": settings.SLACK_CLIENT_ID,
        "scope": settings.SLACK_OAUTH_SCOPES,
        "redirect_uri": settings.SLACK_OAUTH_REDIRECT_URI,
        "state": state,
    }
    query = "&".join([f"{key}={requests.utils.quote(str(value))}" for key, value in params.items()])
    install_url = f"https://slack.com/oauth/v2/authorize?{query}"
    return {"install_url": install_url}


@router.get("/callback")
def slack_oauth_callback(code: str, state: str, db: Session = Depends(get_db)):
    if not settings.SLACK_CLIENT_ID or not settings.SLACK_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Slack OAuth settings are not configured",
        )

    team_hint = _verify_state(state)
    if state and team_hint is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state")

    response = requests.post(
        "https://slack.com/api/oauth.v2.access",
        data={
            "client_id": settings.SLACK_CLIENT_ID,
            "client_secret": settings.SLACK_CLIENT_SECRET,
            "code": code,
            "redirect_uri": settings.SLACK_OAUTH_REDIRECT_URI,
        },
        timeout=30,
    )

    data = response.json()
    if not data.get("ok"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=data.get("error", "Slack OAuth failed"),
        )

    team = data.get("team", {})
    team_id = team.get("id")
    team_name = team.get("name")
    bot_token = data.get("access_token")
    bot_user_id = data.get("bot_user_id")
    scope = data.get("scope")
    installed_by = data.get("authed_user", {}).get("id")

    if not team_id or not bot_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slack OAuth response missing team_id or access_token",
        )

    slug = f"slack-{team_id.lower()}"
    organization = UserService.get_organization_by_slug(db, slug)
    if not organization:
        organization = UserService.create_organization(db, team_name or f"Slack {team_id}")
        organization.slug = slug
        db.commit()
        db.refresh(organization)

    SlackInstallationService.upsert_installation(
        db=db,
        team_id=team_id,
        team_name=team_name,
        organization_id=organization.id,
        bot_user_id=bot_user_id,
        bot_token=bot_token,
        scope=scope,
        installed_by=installed_by,
    )

    return {
        "status": "ok",
        "team_id": team_id,
        "team_name": team_name,
        "organization_id": organization.id,
    }
