from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.user import User, UserRole
from app.models.auth_credential import AuthCredential
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class UserService:
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user"""
        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            teams_user_id=user_data.teams_user_id,
            department=user_data.department,
            role=user_data.role,
            phone=user_data.phone,
            is_active=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)

        if user_data.password:
            credential = AuthCredential(
                user_id=user.id,
                password_hash=get_password_hash(user_data.password),
            )
            db.add(credential)
            db.commit()
        
        return user

    @staticmethod
    def set_password(db: Session, user_id: int, plain_password: str) -> Optional[AuthCredential]:
        """Create or update password hash for a user"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        credential = db.query(AuthCredential).filter(AuthCredential.user_id == user_id).first()
        password_hash = get_password_hash(plain_password)

        if credential:
            credential.password_hash = password_hash
        else:
            credential = AuthCredential(user_id=user_id, password_hash=password_hash)
            db.add(credential)

        db.commit()
        db.refresh(credential)
        return credential

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user by email and password"""
        user = db.query(User).filter(User.email == email).first()
        if not user or not user.is_active:
            return None

        credential = db.query(AuthCredential).filter(AuthCredential.user_id == user.id).first()
        if not credential:
            return None

        if not verify_password(password, credential.password_hash):
            return None

        return user
    
    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_slack_id(db: Session, slack_id: str) -> Optional[User]:
        """Get user by Slack/Teams user ID"""
        return db.query(User).filter(User.teams_user_id == slack_id).first()
    
    @staticmethod
    def list_users(
        db: Session,
        role: Optional[UserRole] = None,
        department: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[User], int]:
        """List users with filters and pagination"""
        query = db.query(User)
        
        if role:
            query = query.filter(User.role == role)
        if department:
            query = query.filter(User.department == department)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        total = query.count()
        users = query.offset(skip).limit(limit).all()
        
        return users, total
    
    @staticmethod
    def update_user(
        db: Session,
        user_id: int,
        user_update: UserUpdate
    ) -> Optional[User]:
        """Update user information"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        update_data = user_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Deactivate user (soft delete)"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        user.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def get_it_staff(db: Session) -> List[User]:
        """Get all IT support staff and admins"""
        return db.query(User).filter(
            User.role.in_([UserRole.IT_SUPPORT, UserRole.ADMIN]),
            User.is_active == True
        ).all()
