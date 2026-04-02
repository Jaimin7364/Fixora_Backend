from datetime import datetime, timedelta, timezone
from typing import Optional, Iterable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import get_db
from app.models.user import User, UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
	return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
	return pwd_context.hash(password)


def _create_token(subject: str, role: str, token_type: str, expires_delta: timedelta) -> str:
	expire = datetime.now(timezone.utc) + expires_delta
	to_encode = {"sub": subject, "role": role, "type": token_type, "exp": expire}
	return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(subject: str, role: str, expires_delta: Optional[timedelta] = None) -> str:
	delta = expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
	return _create_token(subject, role, "access", delta)


def create_refresh_token(subject: str, role: str, expires_delta: Optional[timedelta] = None) -> str:
	delta = expires_delta or timedelta(days=7)
	return _create_token(subject, role, "refresh", delta)


def decode_token(token: str) -> dict:
	try:
		return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
	except JWTError:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Could not validate credentials",
			headers={"WWW-Authenticate": "Bearer"},
		)


def get_current_user(
	db: Session = Depends(get_db),
	token: str = Depends(oauth2_scheme),
) -> User:
	payload = decode_token(token)

	if payload.get("type") != "access":
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid token type",
			headers={"WWW-Authenticate": "Bearer"},
		)

	user_id = payload.get("sub")
	if not user_id:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid token payload",
			headers={"WWW-Authenticate": "Bearer"},
		)

	try:
		user_id_int = int(user_id)
	except (TypeError, ValueError):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid token payload",
			headers={"WWW-Authenticate": "Bearer"},
		)

	user = db.query(User).filter(User.id == user_id_int).first()
	if not user or not user.is_active:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Inactive or missing user",
			headers={"WWW-Authenticate": "Bearer"},
		)

	return user


def require_roles(allowed_roles: Iterable[UserRole]):
	def dependency(current_user: User = Depends(get_current_user)) -> User:
		if current_user.role not in allowed_roles:
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail="You do not have permission to perform this action",
			)
		return current_user

	return dependency
