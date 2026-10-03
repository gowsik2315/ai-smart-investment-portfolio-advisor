"""
Shared FastAPI Dependencies
Reusable request-scoped dependencies, primarily authentication.

The `get_current_user` body below previously existed as five
near-identical copies across the API routers. It lives here now so
there is a single place to change auth behaviour.
"""

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.user import User


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> int:
    """
    Resolve the authenticated user from the Authorization header.

    Args:
        authorization: `Bearer <jwt>` header value
        db: Database session

    Returns:
        The authenticated user's ID

    Raises:
        HTTPException 401: Header missing/malformed, or token invalid/expired
        HTTPException 404: Token valid but the user no longer exists
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    token = authorization.replace("Bearer ", "")
    user_id = get_current_user_id(token)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    # Verify the user still exists — a token can outlive its account
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user_id
