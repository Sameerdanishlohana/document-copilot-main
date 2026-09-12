"""FastAPI authentication dependencies using Supabase Auth."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase_auth.types import User

from app.database.supabase import get_anon_client

security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> User:
    """Verify the Supabase Bearer token from the HTTP Authorization header.

    Returns:
        User: The authenticated Supabase User object.

    Raises:
        HTTPException: HTTP 401 Unauthorized if the token is missing, invalid, or expired.
    """
    token = credentials.credentials
    try:
        supabase = get_anon_client()
        response = supabase.auth.get_user(token)
        if not response or not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return response.user
    except HTTPException:
        raise
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(err)}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from err
