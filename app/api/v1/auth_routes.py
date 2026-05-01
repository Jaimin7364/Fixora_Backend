from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
)
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import BootstrapAdminRequest, RefreshTokenRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse, UserRole
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/bootstrap-admin", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def bootstrap_admin(payload: BootstrapAdminRequest, db: Session = Depends(get_db)):
    users_count = db.query(User).count()
    if users_count > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bootstrap is disabled once users exist."
        )

    organization = UserService.get_organization_by_slug(db, "default-organization")
    if not organization:
        organization = UserService.create_organization(db, "Default Organization")

    admin = UserService.create_user(
        db,
        UserCreate(
            email=payload.email,
            full_name=payload.full_name,
            password=payload.password,
            department=payload.department,
            phone=payload.phone,
            role=UserRole.ADMIN,
        ),
        organization.id,
    )
    return admin


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = UserService.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=str(user.id), role=user.role.value)
    refresh_token = create_refresh_token(subject=str(user.id), role=user.role.value)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    decoded = decode_token(payload.refresh_token)

    if decoded.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = decoded.get("sub")
    role = decoded.get("role")

    try:
        user_id_int = int(user_id) if user_id else None
    except (TypeError, ValueError):
        user_id_int = None

    user = db.query(User).filter(User.id == user_id_int).first() if user_id_int else None
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive or missing user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=str(user.id), role=role or user.role.value)
    refresh_token = create_refresh_token(subject=str(user.id), role=role or user.role.value)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout")
def logout(_current_user: User = Depends(get_current_user)):
    return {"message": "Logged out. Please discard tokens client-side."}
