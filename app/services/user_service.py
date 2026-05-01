from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.user import User, UserRole
from app.models.auth_credential import AuthCredential
from app.models.organization import Organization
from app.models.organization_membership import OrganizationMembership
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class UserService:

    @staticmethod
    def _slugify_org_name(name: str) -> str:
        return "-".join(name.lower().strip().split())

    @staticmethod
    def create_organization(db: Session, name: str) -> Organization:
        """Create a new organization"""
        base_slug = UserService._slugify_org_name(name)
        slug = base_slug
        counter = 1

        while db.query(Organization).filter(Organization.slug == slug).first():
            counter += 1
            slug = f"{base_slug}-{counter}"

        organization = Organization(name=name, slug=slug, is_active=True)
        db.add(organization)
        db.commit()
        db.refresh(organization)
        return organization

    @staticmethod
    def get_organization(db: Session, organization_id: int) -> Optional[Organization]:
        return db.query(Organization).filter(Organization.id == organization_id).first()

    @staticmethod
    def get_organization_by_slug(db: Session, slug: str) -> Optional[Organization]:
        return db.query(Organization).filter(Organization.slug == slug).first()
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate, organization_id: Optional[int] = None) -> User:
        """Create a new user"""
        target_organization_id = organization_id or user_data.organization_id
        user = User(
            organization_id=target_organization_id,
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

        if target_organization_id:
            existing_membership = db.query(OrganizationMembership).filter(
                OrganizationMembership.organization_id == target_organization_id,
                OrganizationMembership.user_id == user.id,
            ).first()
            if not existing_membership:
                membership = OrganizationMembership(
                    organization_id=target_organization_id,
                    user_id=user.id,
                    role=user.role.value,
                )
                db.add(membership)
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
    def get_user(db: Session, user_id: int, organization_id: Optional[int] = None) -> Optional[User]:
        """Get user by ID"""
        query = db.query(User).filter(User.id == user_id)
        if organization_id is not None:
            query = query.filter(User.organization_id == organization_id)
        return query.first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str, organization_id: Optional[int] = None) -> Optional[User]:
        """Get user by email"""
        query = db.query(User).filter(User.email == email)
        if organization_id is not None:
            query = query.filter(User.organization_id == organization_id)
        return query.first()
    
    @staticmethod
    def get_user_by_slack_id(db: Session, slack_id: str, organization_id: Optional[int] = None) -> Optional[User]:
        """Get user by Slack/Teams user ID"""
        query = db.query(User).filter(User.teams_user_id == slack_id)
        if organization_id is not None:
            query = query.filter(User.organization_id == organization_id)
        return query.first()
    
    @staticmethod
    def list_users(
        db: Session,
        role: Optional[UserRole] = None,
        department: Optional[str] = None,
        is_active: Optional[bool] = None,
        organization_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[User], int]:
        """List users with filters and pagination"""
        query = db.query(User)
        if organization_id is not None:
            query = query.filter(User.organization_id == organization_id)
        
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
        user_update: UserUpdate,
        organization_id: Optional[int] = None,
    ) -> Optional[User]:
        """Update user information"""
        query = db.query(User).filter(User.id == user_id)
        if organization_id is not None:
            query = query.filter(User.organization_id == organization_id)
        user = query.first()
        if not user:
            return None
        
        update_data = user_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def delete_user(db: Session, user_id: int, organization_id: Optional[int] = None) -> bool:
        """Deactivate user (soft delete)"""
        query = db.query(User).filter(User.id == user_id)
        if organization_id is not None:
            query = query.filter(User.organization_id == organization_id)
        user = query.first()
        if not user:
            return False
        
        user.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def get_it_staff(db: Session, organization_id: Optional[int] = None) -> List[User]:
        """Get all IT support staff and admins"""
        query = db.query(User).filter(
            User.role.in_([UserRole.IT_SUPPORT, UserRole.ADMIN]),
            User.is_active == True
        )
        if organization_id is not None:
            query = query.filter(User.organization_id == organization_id)
        return query.all()
