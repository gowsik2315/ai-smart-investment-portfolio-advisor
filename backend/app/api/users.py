"""
Users API Routes
Handles user profile management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate


router = APIRouter()


def _authorise_self(user_id: int, current_user_id: int) -> None:
    """
    Allow access only to the caller's own record.

    Both endpoints below take `user_id` from the path. Without this
    check, any caller could read or overwrite any account simply by
    changing the number in the URL — there is no admin role in this
    application, so same-user is the only legitimate access.
    """
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own user record",
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    """
    Get a user by ID. Only the authenticated user's own record.

    - **user_id**: User ID (must match the authenticated user)
    """
    _authorise_self(user_id, current_user_id)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    """
    Update a user profile. Only the authenticated user's own record.

    - **user_id**: User ID (must match the authenticated user)
    - **user_data**: Updated user information
    """
    _authorise_self(user_id, current_user_id)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update fields
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    if user_data.phone is not None:
        user.phone = user_data.phone

    db.commit()
    db.refresh(user)

    return user
