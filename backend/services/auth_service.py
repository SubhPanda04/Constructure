from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from app.config import get_settings
from models.user import UserProfile, GoogleTokens
from typing import Tuple, Optional
import os
from utils.logger import log_auth_attempt, log_auth_success, log_auth_failure

settings = get_settings()

# In-memory storage for user sessions (in production, use Redis or database)
user_sessions = {}


class AuthService:
    def __init__(self):
        self.client_config = {
            "web": {
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.google_redirect_uri]
            }
        }
    
    def get_authorization_url(self, state: str) -> str:
        """
        Generate Google OAuth authorization URL.
        
        Args:
            state: Random state string for CSRF protection
            
        Returns:
            Authorization URL string
        """
        flow = Flow.from_client_config(
            self.client_config,
            scopes=settings.gmail_scopes,
            redirect_uri=settings.google_redirect_uri
        )
        
        authorization_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=state,
            prompt='consent'  # Force consent to get refresh token
        )
        
        return authorization_url
    
    def exchange_code_for_tokens(self, code: str) -> Tuple[GoogleTokens, UserProfile]:
        """
        Exchange authorization code for access tokens and user profile.
        
        Args:
            code: Authorization code from Google
            
        Returns:
            Tuple of (GoogleTokens, UserProfile)
        """
        flow = Flow.from_client_config(
            self.client_config,
            scopes=settings.gmail_scopes,
            redirect_uri=settings.google_redirect_uri
        )
        
        log_auth_attempt("unknown")
        
        # Exchange code for tokens
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Get user info
        user_info_service = build('oauth2', 'v2', credentials=credentials)
        user_info = user_info_service.userinfo().get().execute()
        
        # Create token model
        google_tokens = GoogleTokens(
            access_token=credentials.token,
            refresh_token=credentials.refresh_token,
            expires_in=3600,  # Default 1 hour
            scope=' '.join(settings.gmail_scopes),
            token_type='Bearer'
        )
        
        # Create user profile
        user_profile = UserProfile(
            email=user_info['email'],
            name=user_info.get('name', ''),
            picture=user_info.get('picture'),
            google_id=user_info['id']
        )
        
        # Store tokens in session (in-memory)
        user_sessions[user_profile.email] = {
            'google_tokens': google_tokens,
            'profile': user_profile
        }
        
        log_auth_success(user_profile.email)
        return google_tokens, user_profile
    
    def get_user_session(self, email: str) -> Optional[dict]:
        """
        Retrieve user session data.
        
        Args:
            email: User email address
            
        Returns:
            Session data or None
        """
        return user_sessions.get(email)
    
    def refresh_access_token(self, email: str) -> Optional[str]:
        """
        Refresh Google access token using refresh token.
        
        Args:
            email: User email address
            
        Returns:
            New access token or None
        """
        session = user_sessions.get(email)
        if not session or not session['google_tokens'].refresh_token:
            return None
        
        credentials = Credentials(
            token=session['google_tokens'].access_token,
            refresh_token=session['google_tokens'].refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret
        )
        
        # Refresh the token
        credentials.refresh(Request())
        
        # Update session
        session['google_tokens'].access_token = credentials.token
        
        return credentials.token
    
    def logout_user(self, email: str) -> bool:
        """
        Remove user session.
        
        Args:
            email: User email address
            
        Returns:
            True if successful
        """
        if email in user_sessions:
            del user_sessions[email]
            log_auth_success(f"Logout: {email}")
            return True
        return False


# Singleton instance
auth_service = AuthService()
