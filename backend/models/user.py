from pydantic import BaseModel, EmailStr
from typing import Optional


class UserProfile(BaseModel):
    email: EmailStr
    name: str
    picture: Optional[str] = None
    google_id: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None
    google_id: Optional[str] = None


class GoogleTokens(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    expires_in: int
    scope: str
    token_type: str
