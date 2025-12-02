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
import asyncio
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from utils.logger import log_gmail_call, log_gmail_success, log_gmail_error

settings = get_settings()

class GmailService:
    def get_service(self, token_data):
        """Build Gmail API service from token data."""
        creds = Credentials(
            token=token_data.access_token,
            refresh_token=token_data.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret
        )
        return build('gmail', 'v1', credentials=creds)

    def fetch_recent_emails(self, token_data, limit: int = 5) -> List[EmailSummary]:
        """
        Fetch recent emails and generate AI summaries in parallel.
        """
        try:
            log_gmail_call("fetch_recent_emails", "me")
            service = self.get_service(token_data)
            
            # List messages
            results = service.users().messages().list(userId='me', maxResults=limit, labelIds=['INBOX']).execute()
            messages = results.get('messages', [])
            
            def process_single_email(msg):
                """Process a single email and return EmailSummary"""
                try:
                    # Create a new service instance for this thread to avoid SSL issues
                    thread_service = self.get_service(token_data)
                    msg_detail = thread_service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
                    
                    headers = msg_detail['payload']['headers']
                    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
                    sender = next((h['value'] for h in headers if h['name'] == 'From'), '(Unknown)')
                    date_str = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                    body = ""
                    html_body = ""
                    
                    # Extract both plain text and HTML
                    if 'parts' in msg_detail['payload']:
                        for part in msg_detail['payload']['parts']:
                            if part['mimeType'] == 'text/plain':
                                data = part['body'].get('data')
                                if data:
                                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                                    break
                            elif part['mimeType'] == 'text/html' and not body:
                                data = part['body'].get('data')
                                if data:
                                    html_body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    elif 'body' in msg_detail['payload']:
                        data = msg_detail['payload']['body'].get('data')
                        if data:
                            decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                            if msg_detail['payload'].get('mimeType') == 'text/html':
                                html_body = decoded
                            else:
                                body = decoded
                    
                    # If no plain text, extract text from HTML
                    if not body and html_body:
                        soup = BeautifulSoup(html_body, 'html.parser')
                        # Remove script and style elements
                        for script in soup(["script", "style"]):
                            script.decompose()
                        body = soup.get_text(separator=' ', strip=True)
                
                    # AI summarization (this is the slow part)
                    summary = ai_service.summarize_email(body, subject)
                    
                    parsed_date = datetime.now()  # Fallback
                    
                    return EmailSummary(
                        id=msg['id'],
                        sender=sender,
                        sender_email=sender,
                        subject=subject,
                        summary=summary,
                        date=parsed_date
                    )
                except Exception as e:
                    print(f"Error processing email {msg.get('id')}: {e}")
                    return None
            
            # Process emails in parallel using ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=5) as executor:
                email_summaries = list(executor.map(process_single_email, messages))
            
            # Filter out None values (failed emails)
            email_summaries = [e for e in email_summaries if e is not None]
            
            log_gmail_success("fetch_recent_emails", "me")
            return email_summaries

        except HttpError as error:
            log_gmail_error("fetch_recent_emails", "me", str(error))
            print(f"An error occurred: {error}")
            return []

    def send_reply(self, token_data: dict, email_id: str, reply_content: str) -> bool:
        """Send a reply to a specific email."""
        try:
            log_gmail_call("send_reply", "me")
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
            log_gmail_success("send_reply", "me")
            return True
            
        except HttpError as error:
            log_gmail_error("send_reply", "me", str(error))
            print(f"An error occurred: {error}")
            return False

    def delete_email(self, token_data, email_id: str) -> bool:
        """Delete (trash) a specific email."""
        try:
            log_gmail_call("delete_email", "me")
            service = self.get_service(token_data)
            service.users().messages().trash(userId='me', id=email_id).execute()
            log_gmail_success("delete_email", "me")
            return True
        except HttpError as error:
            log_gmail_error("delete_email", "me", str(error))
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
