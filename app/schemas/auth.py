from pydantic import BaseModel, EmailStr, Field
from app.schemas.user import UserRole


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    role: str
    type: str = "access"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class BootstrapAdminRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    department: str | None = Field(None, max_length=100)
    phone: str | None = Field(None, max_length=20)
    role: UserRole = UserRole.ADMIN
