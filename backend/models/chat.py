from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import datetime


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    message: str


class IntentClassification(BaseModel):
    intent: Literal[
        "READ_EMAILS",
        "GENERATE_REPLIES", 
        "DELETE_EMAIL",
        "SEND_REPLY",
        "GENERAL_QUERY",
        "GREETING"
    ]
    confidence: float
    parameters: Optional[dict] = None


class ChatResponse(BaseModel):
    message: str
    intent: Optional[IntentClassification] = None
    data: Optional[dict] = None
    timestamp: datetime


class ConversationContext(BaseModel):
    user_email: str
    messages: List[ChatMessage] = []
    recent_emails: Optional[List[dict]] = None
    generated_replies: Optional[dict] = None
