"""
Shared FastAPI Dependencies
Reusable request-scoped dependencies, primarily authentication.

The `get_current_user` body below previously existed as five
near-identical copies across the API routers. It lives here now so
there is a single place to change auth behaviour.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.user import User

# Declared as a security scheme so the OpenAPI document actually says
# these routes need a bearer token. Reading the raw header worked, but
# left every operation documented as public, so Swagger's "Authorize"
# button did nothing and "Try it out" failed on protected routes.
#
# auto_error=False keeps the existing contract: FastAPI's own 403
# "Not authenticated" is suppressed so the 401 below is raised instead.
bearer_scheme = HTTPBearer(auto_error=False, description="JWT from /api/auth/login")


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> int:
    """
    Resolve the authenticated user from the Authorization header.

    Args:
        credentials: parsed `Authorization: Bearer <jwt>` header
        db: Database session

    Returns:
        The authenticated user's ID

    Raises:
        HTTPException 401: Header missing/malformed, or token invalid/expired
        HTTPException 404: Token valid but the user no longer exists
    """
    if credentials is None or not (credentials.credentials or "").strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    user_id = get_current_user_id(credentials.credentials)

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
