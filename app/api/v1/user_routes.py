from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database.session import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse, UserRole
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new user (Admin only)
    
    - **email**: User email (must be unique)
    - **full_name**: Full name
    - **teams_user_id**: Slack/Teams user ID
    - **department**: Department
    - **role**: User role (employee, it_support, admin, manager)
    - **phone**: Phone number
    """
    # Check if user already exists
    existing_user = UserService.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    if user_data.teams_user_id:
        existing_slack = UserService.get_user_by_slack_id(db, user_data.teams_user_id)
        if existing_slack:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this Slack ID already exists"
            )
    
    user = UserService.create_user(db, user_data)
    return user


@router.get("/", response_model=UserListResponse)
def list_users(
    role: Optional[UserRole] = None,
    department: Optional[str] = None,
    is_active: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    List all users with optional filters
    
    - **role**: Filter by role
    - **department**: Filter by department
    - **is_active**: Filter by active status
    - **page**: Page number
    - **page_size**: Items per page
    """
    skip = (page - 1) * page_size
    
    users, total = UserService.list_users(
        db=db,
        role=role,
        department=department,
        is_active=is_active,
        skip=skip,
        limit=page_size
    )
    
    return UserListResponse(
        users=users,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get user by ID
    """
    user = UserService.get_user(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return user


@router.get("/email/{email}", response_model=UserResponse)
def get_user_by_email(
    email: str,
    db: Session = Depends(get_db)
):
    """
    Get user by email
    """
    user = UserService.get_user_by_email(db, email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {email} not found"
        )
    
    return user


@router.get("/slack/{slack_id}", response_model=UserResponse)
def get_user_by_slack_id(
    slack_id: str,
    db: Session = Depends(get_db)
):
    """
    Get user by Slack/Teams user ID
    """
    user = UserService.get_user_by_slack_id(db, slack_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with Slack ID {slack_id} not found"
        )
    
    return user


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    Update user information
    """
    user = UserService.update_user(db, user_id, user_update)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Deactivate user (soft delete)
    """
    success = UserService.delete_user(db, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return None


@router.get("/it-staff/list", response_model=UserListResponse)
def get_it_staff(
    db: Session = Depends(get_db)
):
    """
    Get all IT support staff and admins
    """
    staff = UserService.get_it_staff(db)
    
    return UserListResponse(
        users=staff,
        total=len(staff),
        page=1,
        page_size=len(staff)
    )
