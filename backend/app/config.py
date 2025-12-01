from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App Configuration
    app_name: str = "AI Email Assistant"
    environment: str = "development"
    
    # Google OAuth Configuration
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str
    
    # JWT Configuration
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours
    
    # AI Provider Configuration
    openai_api_key: str
    
    # Frontend URL
    frontend_url: str = "http://localhost:5173"
    
    # Gmail API Scopes
    gmail_scopes: list[str] = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
