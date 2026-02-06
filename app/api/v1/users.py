from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.api.deps import get_current_user
from app.core.security import get_password_hash

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def get_users(
    response: Response,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role_filter: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of users with optional filtering.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        role_filter: Filter by user role
        search: Search in name, email, or legajo
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of users
    """
    # Only admin and owner can view all users
    if current_user.role not in ["admin", "owner"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    query = db.query(User)
    
    # Filter by role
    if role_filter:
        query = query.filter(User.role == role_filter)
    
    # Search in multiple fields
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (User.name.ilike(search_filter)) |
            (User.email.ilike(search_filter)) |
            (User.legajo.ilike(search_filter))
        )
    
    # Calculate total count before pagination
    total_count = query.count()
    response.headers["X-Total-Count"] = str(total_count)

    users = query.offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific user by ID.
    
    Args:
        user_id: User ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        User data
        
    Raises:
        HTTPException: If user not found or no permissions
    """
    # Only admin/owner can view other users, or user can view themselves
    if current_user.role not in ["admin", "owner"] and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new user.
    
    Args:
        user: User data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Created user
        
    Raises:
        HTTPException: If email or legajo already exists, or no permissions
    """
    # Only admin and owner can create users
    if current_user.role not in ["admin", "owner"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Check if legajo already exists
    existing_legajo = db.query(User).filter(User.legajo == user.legajo).first()
    if existing_legajo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this legajo already exists"
        )
    
    # Create new user with hashed password
    user_data = user.model_dump(exclude={"password"})
    user_data["password_hash"] = get_password_hash(user.password)
    
    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a user.
    
    Args:
        user_id: User ID
        user: Updated user data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Updated user
        
    Raises:
        HTTPException: If user not found or no permissions
    """
    # Only admin/owner can update other users, or user can update themselves
    if current_user.role not in ["admin", "owner"] and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent users from changing their own role (only admin/owner can)
    if current_user.id == user_id and user.role and current_user.role not in ["admin", "owner"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot change your own role"
        )
    
    # Update user fields
    update_data = user.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a user.
    
    Args:
        user_id: User ID
        db: Database session
        current_user: Current authenticated user
        
    Raises:
        HTTPException: If user not found, no permissions, or trying to delete self
    """
    # Only admin and owner can delete users
    if current_user.role not in ["admin", "owner"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Prevent users from deleting themselves
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(db_user)
    db.commit()
    
    return None


@router.put("/{user_id}/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_user_password(
    user_id: int,
    new_password: str = Query(..., min_length=6),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Change a user's password.
    
    Args:
        user_id: User ID
        new_password: New password
        db: Database session
        current_user: Current authenticated user
        
    Raises:
        HTTPException: If user not found or no permissions
    """
    # Only admin/owner can change other users' passwords, or user can change their own
    if current_user.role not in ["admin", "owner"] and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    db_user.password_hash = get_password_hash(new_password)
    db.commit()
    
    return None
