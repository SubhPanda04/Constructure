from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from services.auth_service import auth_service
from utils.jwt_handler import create_access_token
from models.user import Token, UserProfile
from utils.dependencies import get_current_user
from fastapi import Depends
from app.config import get_settings
import secrets

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Store state tokens for CSRF protection (in production, use Redis)
state_tokens = set()


@router.get("/google/login")
async def google_login():
    """
    Initiate Google OAuth login flow.
    
    Returns:
        Redirect to Google OAuth consent screen
    """
    # Generate random state for CSRF protection
    state = secrets.token_urlsafe(32)
    state_tokens.add(state)
    
    # Get authorization URL
    auth_url = auth_service.get_authorization_url(state)
    
    return RedirectResponse(url=auth_url)


@router.get("/google/callback")
async def google_callback(
    code: str = Query(..., description="Authorization code from Google"),
    state: str = Query(..., description="State token for CSRF protection")
):
    """
    Handle Google OAuth callback.
    
    Args:
        code: Authorization code from Google
        state: State token for CSRF verification
        
    Returns:
        Redirect to frontend with JWT token
    """
    # Verify state token
    if state not in state_tokens:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state token. Possible CSRF attack."
        )
    
    # Remove used state token
    state_tokens.discard(state)
    
    try:
        # Exchange code for tokens and get user profile
        google_tokens, user_profile = auth_service.exchange_code_for_tokens(code)
        
        # Create JWT token
        access_token = create_access_token(
            data={
                "sub": user_profile.email,
                "google_id": user_profile.google_id,
                "name": user_profile.name
            }
        )
        
        # Redirect to frontend with token
        frontend_callback_url = f"{settings.frontend_url}/callback?token={access_token}"
        return RedirectResponse(url=frontend_callback_url)
        
    except Exception as e:
        # Redirect to frontend with error
        error_url = f"{settings.frontend_url}/?error=auth_failed&message={str(e)}"
        return RedirectResponse(url=error_url)


@router.get("/me", response_model=UserProfile)
async def get_current_user_info(
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    
    Returns:
        UserProfile object
    """
    return current_user


@router.post("/logout")
async def logout(current_user: UserProfile = Depends(get_current_user)):
    """
    Logout current user by removing their session.
    
    Returns:
        Success message
    """
    auth_service.logout_user(current_user.email)
    
    return {"message": "Successfully logged out"}


@router.get("/health")
async def auth_health():
    """
    Health check endpoint for authentication service.
    
    Returns:
        Health status
    """
    return {"status": "healthy", "service": "authentication"}
