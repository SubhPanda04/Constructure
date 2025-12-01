from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from models.email import EmailSummary, EmailReply, GeneratedReply
from models.user import UserProfile
from utils.dependencies import get_current_user, get_google_credentials
from services.gmail_service import gmail_service
from services.ai_service import ai_service
from services.auth_service import auth_service

router = APIRouter(prefix="/api/emails", tags=["Emails"])

@router.get("/recent", response_model=List[EmailSummary])
async def get_recent_emails(
    current_user: UserProfile = Depends(get_current_user),
    credentials: dict = Depends(get_google_credentials)
):
    """Fetch and summarize recent emails."""
    emails = gmail_service.fetch_recent_emails(credentials, limit=5)
    
    # Update conversation context with these emails
    # We need to access the chat service or shared state
    # For now, we'll rely on the frontend to send context back if needed
    # or update the in-memory store if we import it
    from routers.chat import get_or_create_conversation
    conversation = get_or_create_conversation(current_user.email)
    conversation.recent_emails = [e.dict() for e in emails]
    
    return emails

@router.post("/generate-reply", response_model=GeneratedReply)
async def generate_reply(
    request: dict, # Expecting {"email_id": "..."}
    current_user: UserProfile = Depends(get_current_user),
    credentials: dict = Depends(get_google_credentials)
):
    """Generate an AI reply for a specific email."""
    email_id = request.get("email_id")
    if not email_id:
        raise HTTPException(status_code=400, detail="Email ID required")
        
    # Fetch full email content
    email_data = gmail_service.get_email_content(credentials, email_id)
    if not email_data:
        raise HTTPException(status_code=404, detail="Email not found")
        
    # Generate reply
    reply_content = ai_service.generate_email_reply(
        email_data['body'],
        email_data['subject'],
        email_data['sender']
    )
    
    return GeneratedReply(
        email_id=email_id,
        original_subject=email_data['subject'],
        original_sender=email_data['sender'],
        reply_content=reply_content
    )

@router.post("/send-reply")
async def send_reply(
    reply: EmailReply,
    current_user: UserProfile = Depends(get_current_user),
    credentials: dict = Depends(get_google_credentials)
):
    """Send a reply via Gmail."""
    success = gmail_service.send_reply(credentials, reply.email_id, reply.reply_content)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send email")
        
    return {"message": "Reply sent successfully"}

@router.delete("/delete/{email_id}")
async def delete_email(
    email_id: str,
    current_user: UserProfile = Depends(get_current_user),
    credentials: dict = Depends(get_google_credentials)
):
    """Delete an email."""
    success = gmail_service.delete_email(credentials, email_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete email")
        
    return {"message": "Email deleted successfully"}
