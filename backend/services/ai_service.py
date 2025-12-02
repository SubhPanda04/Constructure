from groq import Groq
from app.config import get_settings
from models.chat import IntentClassification, ChatMessage
from typing import List, Optional
import json
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from utils.logger import log_ai_call, log_ai_success, log_ai_error, log_ai_retry

settings = get_settings()


class AIService:
    def __init__(self):
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = "llama-3.3-70b-versatile"  # Fast and high-quality 
    
    def parse_intent(self, user_message: str, conversation_history: List[ChatMessage] = None) -> IntentClassification:
        """
        Parse user intent from their message using AI.
        
        Args:
            user_message: The user's message
            conversation_history: Previous conversation messages for context
            
        Returns:
            IntentClassification with intent type and parameters
        """
        system_prompt = """You are an intent classifier for an email assistant. 
Analyze the user's message and classify it into one of these intents:

- READ_EMAILS: User wants to see/read their recent emails
- GENERATE_REPLIES: User wants to generate AI replies for emails
- DELETE_EMAIL: User wants to delete a specific email
- SEND_REPLY: User wants to send a generated reply
- GREETING: User is greeting or starting conversation
- GENERAL_QUERY: General questions or unclear intent

Return a JSON object with:
{
    "intent": "INTENT_NAME",
    "confidence": 0.0-1.0,
    "parameters": {
        // For DELETE_EMAIL: {"sender": "name", "subject_keyword": "word", "reference_number": 1}
        // For SEND_REPLY: {"reply_number": 1}
        // For others: {}
    }
}

Examples:
- "Show me my recent emails" -> READ_EMAILS
- "Generate replies for these" -> GENERATE_REPLIES
- "Delete the email from John" -> DELETE_EMAIL with {"sender": "John"}
- "Send reply number 2" -> SEND_REPLY with {"reply_number": 2}
"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if conversation_history:
            for msg in conversation_history[-5:]:  # Last 5 messages for context
                messages.append({"role": msg.role, "content": msg.content})
        
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return IntentClassification(
                intent=result.get("intent", "GENERAL_QUERY"),
                confidence=result.get("confidence", 0.5),
                parameters=result.get("parameters", {})
            )
        except Exception as e:
            print(f"Intent parsing error: {e}")
            return IntentClassification(
                intent="GENERAL_QUERY",
                confidence=0.0,
                parameters={}
            )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        before_sleep=lambda retry_state: log_ai_retry("email_summary", retry_state.attempt_number)
    )
    def summarize_email(self, email_body: str, subject: str) -> str:
        """
        Generate a concise summary of an email with retry logic.
        
        Args:
            email_body: The email content
            subject: The email subject
            
        Returns:
            AI-generated summary
        """
        log_ai_call("email_summary", "system")
        prompt = f"""Summarize this email in 2-3 concise sentences. Focus on the main point and any action items.

Subject: {subject}

Email:
{email_body[:10000]}  # Limit to first 10000 chars

Summary:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful email summarizer. Be concise and clear."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=120
            )
            result = response.choices[0].message.content.strip()
            log_ai_success("email_summary", "system")
            return result
        except Exception as e:
            log_ai_error("email_summary", "system", str(e))
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        before_sleep=lambda retry_state: log_ai_retry("email_reply", retry_state.attempt_number)
    )
    def generate_email_reply(self, email_body: str, subject: str, sender: str) -> str:
        """
        Generate a professional email reply with retry logic.
        
        Args:
            email_body: Original email content
            subject: Original email subject
            sender: Sender's name
            
        Returns:
            AI-generated reply
        """
        log_ai_call("email_reply", "system")
        prompt = f"""Generate a professional and context-aware reply to this email.
The reply should be polite, clear, and address the main points.

IMPORTANT: Do NOT include a subject line in your response. Only provide the email body text.

From: {sender}
Subject: {subject}

Original Email:
{email_body[:1500]}

Generate a professional reply (body text only, no subject line):"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional email assistant. Write clear, polite, and helpful email replies."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=250
            )
            result = response.choices[0].message.content.strip()
            log_ai_success("email_reply", "system")
            return result
        except Exception as e:
            log_ai_error("email_reply", "system", str(e))
            raise
    
    def generate_chat_response(
        self, 
        user_message: str, 
        conversation_history: List[ChatMessage] = None,
        context_data: dict = None
    ) -> str:
        """
        Generate a conversational response to user message.
        
        Args:
            user_message: User's message
            conversation_history: Previous messages
            context_data: Additional context (emails, etc.)
            
        Returns:
            AI-generated response
        """
        system_prompt = """You are a helpful AI email assistant. You help users manage their Gmail inbox.

Your capabilities:
- Read and summarize recent emails
- Generate professional email replies
- Delete specific emails
- Send replies on behalf of the user

Be friendly, concise, and helpful. When users ask about your capabilities, explain what you can do.
"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-10:]:  # Last 10 messages
                messages.append({"role": msg.role, "content": msg.content})
        
        # Add context if available
        if context_data:
            context_msg = f"Context: {json.dumps(context_data, default=str)}"
            messages.append({"role": "system", "content": context_msg})
        
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Chat response error: {e}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again."


# Singleton instance
ai_service = AIService()
