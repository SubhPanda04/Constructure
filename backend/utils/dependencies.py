from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.jwt_handler import verify_token
from models.user import TokenData, UserProfile
from services.auth_service import auth_service
from typing import Optional

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserProfile:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer token from request header
        
    Returns:
        UserProfile object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    
    # Verify JWT token
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract user data from token
    email: str = payload.get("sub")
    google_id: str = payload.get("google_id")
    
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user session
    session = auth_service.get_user_session(email)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired. Please login again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return session['profile']


async def get_google_credentials(
    current_user: UserProfile = Depends(get_current_user)
) -> dict:
    """
    Dependency to get Google OAuth credentials for the current user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Dictionary containing Google tokens
        
    Raises:
        HTTPException: If credentials not found
    """
    session = auth_service.get_user_session(current_user.email)
    if session is None or 'google_tokens' not in session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google credentials not found. Please re-authenticate.",
        )
    
    return session['google_tokens']
