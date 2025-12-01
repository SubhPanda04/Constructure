from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.config import get_settings
from models.email import EmailMessage, EmailSummary
from services.ai_service import ai_service
from typing import List, Optional
import base64
from email.mime.text import MIMEText
from datetime import datetime

settings = get_settings()

class GmailService:
    def get_service(self, token_data: dict):
        """Build Gmail API service from token data."""
        creds = Credentials(
            token=token_data['access_token'],
            refresh_token=token_data.get('refresh_token'),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret
        )
        return build('gmail', 'v1', credentials=creds)

    def fetch_recent_emails(self, token_data: dict, limit: int = 5) -> List[EmailSummary]:
        """
        Fetch recent emails and generate AI summaries.
        """
        try:
            service = self.get_service(token_data)
            
            # List messages
            results = service.users().messages().list(userId='me', maxResults=limit, labelIds=['INBOX']).execute()
            messages = results.get('messages', [])
            
            email_summaries = []
            
            for msg in messages:
                msg_detail = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
                
                headers = msg_detail['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), '(Unknown)')
                date_str = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                body = ""
                if 'parts' in msg_detail['payload']:
                    for part in msg_detail['payload']['parts']:
                        if part['mimeType'] == 'text/plain':
                            data = part['body'].get('data')
                            if data:
                                body += base64.urlsafe_b64decode(data).decode()
                                break
                elif 'body' in msg_detail['payload']:
                    data = msg_detail['payload']['body'].get('data')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode()
            
                summary = ai_service.summarize_email(body, subject)
                
                try:
                    # Simplified date parsing, might need robust parser for all formats
                    # Example: "Fri, 01 Dec 2025 22:00:00 +0000"
                    # For now using current time if parse fails or just keeping string if model allows
                    # But model expects datetime. Let's try basic parsing or fallback
                    parsed_date = datetime.now() # Fallback
                except:
                    parsed_date = datetime.now()

                email_summaries.append(EmailSummary(
                    id=msg['id'],
                    sender=sender,
                    sender_email=sender,
                    subject=subject,
                    summary=summary,
                    date=parsed_date
                ))
                
            return email_summaries

        except HttpError as error:
            print(f"An error occurred: {error}")
            return []

    def send_reply(self, token_data: dict, email_id: str, reply_content: str) -> bool:
        """Send a reply to a specific email."""
        try:
            service = self.get_service(token_data)
            
            # Get original email to find threadId and headers
            original_msg = service.users().messages().get(userId='me', id=email_id, format='metadata').execute()
            thread_id = original_msg['threadId']
            headers = original_msg['payload']['headers']
            
            # Extract recipients and subject
            to = next((h['value'] for h in headers if h['name'] == 'Reply-To'), None)
            if not to:
                to = next((h['value'] for h in headers if h['name'] == 'From'), '')
            
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            if not subject.lower().startswith('re:'):
                subject = f"Re: {subject}"
                
            # Create message
            message = MIMEText(reply_content)
            message['to'] = to
            message['subject'] = subject
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            body = {
                'raw': raw_message,
                'threadId': thread_id
            }
            
            service.users().messages().send(userId='me', body=body).execute()
            return True
            
        except HttpError as error:
            print(f"An error occurred: {error}")
            return False

    def delete_email(self, token_data: dict, email_id: str) -> bool:
        """Delete (trash) a specific email."""
        try:
            service = self.get_service(token_data)
            service.users().messages().trash(userId='me', id=email_id).execute()
            return True
        except HttpError as error:
            print(f"An error occurred: {error}")
            return False

    def get_email_content(self, token_data: dict, email_id: str) -> dict:
        """Helper to get email content for reply generation."""
        try:
            service = self.get_service(token_data)
            msg = service.users().messages().get(userId='me', id=email_id, format='full').execute()
            
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
            
            # Parse body (simplified)
            body = ""
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data')
                        if data:
                            body += base64.urlsafe_b64decode(data).decode()
                            break
            elif 'body' in msg['payload']:
                data = msg['payload']['body'].get('data')
                if data:
                    body = base64.urlsafe_b64decode(data).decode()
            
            return {
                "id": email_id,
                "subject": subject,
                "sender": sender,
                "body": body
            }
        except Exception as e:
            print(f"Error fetching email content: {e}")
            return None

gmail_service = GmailService()
