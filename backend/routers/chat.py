from fastapi import APIRouter, Depends, HTTPException, status
from models.chat import ChatRequest, ChatResponse, ChatMessage, ConversationContext
from models.user import UserProfile
from utils.dependencies import get_current_user
from services.ai_service import ai_service
from datetime import datetime
from typing import Dict

router = APIRouter(prefix="/api/chat", tags=["Chat"])
conversations: Dict[str, ConversationContext] = {}


def get_or_create_conversation(user_email: str) -> ConversationContext:
    """Get existing conversation or create new one."""
    if user_email not in conversations:
        conversations[user_email] = ConversationContext(
            user_email=user_email,
            messages=[]
        )
    return conversations[user_email]


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Send a chat message and get AI response.
    
    Args:
        request: Chat message request
        current_user: Authenticated user
        
    Returns:
        ChatResponse with AI reply and intent classification
    """
    try:
        # Get conversation context
        conversation = get_or_create_conversation(current_user.email)
        
        # Add user message to history
        user_message = ChatMessage(
            role="user",
            content=request.message,
            timestamp=datetime.utcnow()
        )
        conversation.messages.append(user_message)
        
        # Parse intent
        intent = ai_service.parse_intent(
            request.message,
            conversation.messages
        )
        
        # Generate appropriate response based on intent
        if intent.intent == "GREETING":
            response_text = f"Hello {current_user.name}! 👋 I'm your AI email assistant. I can help you:\n\n" \
                          "• Read and summarize your recent emails\n" \
                          "• Generate professional replies\n" \
                          "• Delete specific emails\n" \
                          "• Send replies on your behalf\n\n" \
                          "Just tell me what you'd like to do!"
        
        elif intent.intent == "READ_EMAILS":
            response_text = "I'll fetch your recent emails now. Please wait a moment..."
            # The actual email fetching will be handled by the frontend calling the emails endpoint
        
        elif intent.intent == "GENERATE_REPLIES":
            if conversation.recent_emails:
                response_text = "I'll generate professional replies for your recent emails. This may take a moment..."
            else:
                response_text = "I don't see any emails to generate replies for. Would you like me to fetch your recent emails first?"
        
        elif intent.intent == "DELETE_EMAIL":
            response_text = "I'll help you delete that email. Let me confirm the details first..."
        
        elif intent.intent == "SEND_REPLY":
            response_text = "I'll send that reply for you. Please confirm you want to proceed."
        
        else:
            response_text = ai_service.generate_chat_response(
                request.message,
                conversation.messages,
                {
                    "has_recent_emails": conversation.recent_emails is not None,
                    "has_generated_replies": conversation.generated_replies is not None
                }
            )
        
        # Add assistant response to history
        assistant_message = ChatMessage(
            role="assistant",
            content=response_text,
            timestamp=datetime.utcnow()
        )
        conversation.messages.append(assistant_message)
        
        return ChatResponse(
            message=response_text,
            intent=intent,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )


@router.get("/history")
async def get_chat_history(
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Get conversation history for current user.
    
    Returns:
        List of chat messages
    """
    conversation = get_or_create_conversation(current_user.email)
    return {
        "messages": conversation.messages,
        "total": len(conversation.messages)
    }


@router.delete("/history")
async def clear_chat_history(
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Clear conversation history for current user.
    
    Returns:
        Success message
    """
    if current_user.email in conversations:
        conversations[current_user.email] = ConversationContext(
            user_email=current_user.email,
            messages=[]
        )
    
    return {"message": "Chat history cleared"}


@router.post("/context/emails")
async def update_email_context(
    emails: list,
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Update conversation context with recent emails.
    
    Args:
        emails: List of recent emails
        
    Returns:
        Success message
    """
    conversation = get_or_create_conversation(current_user.email)
    conversation.recent_emails = emails
    
    return {"message": "Email context updated", "count": len(emails)}
