from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database.base import Base
import enum


class UserRole(str, enum.Enum):
    EMPLOYEE = "employee"
    ADMIN = "admin"
    IT_SUPPORT = "it_support"
    MANAGER = "manager"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    teams_user_id = Column(String(255), unique=True, index=True)  # Microsoft Teams ID
    department = Column(String(100))
    role = Column(SQLEnum(UserRole), default=UserRole.EMPLOYEE)
    is_active = Column(Boolean, default=True)
    phone = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
