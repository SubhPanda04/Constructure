from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class EmailMessage(BaseModel):
    id: str
    thread_id: str
    sender: str
    sender_email: str
    subject: str
    snippet: str
    body: str
    date: datetime
    labels: List[str] = []


class EmailSummary(BaseModel):
    id: str
    sender: str
    sender_email: str
    subject: str
    summary: str
    date: datetime


class EmailReply(BaseModel):
    email_id: str
    reply_content: str


class GeneratedReply(BaseModel):
    email_id: str
    original_subject: str
    original_sender: str
    reply_content: str


class DeleteEmailRequest(BaseModel):
    email_id: Optional[str] = None
    sender: Optional[str] = None
    subject_keyword: Optional[str] = None
    reference_number: Optional[int] = None
