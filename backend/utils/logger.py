import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Create loggers for different components
auth_logger = logging.getLogger('auth')
gmail_logger = logging.getLogger('gmail')
ai_logger = logging.getLogger('ai')
api_logger = logging.getLogger('api')

def log_auth_attempt(email: str):
    auth_logger.info(f"Authentication attempt for user: {email}")

def log_auth_success(email: str):
    auth_logger.info(f"Authentication successful for user: {email}")

def log_auth_failure(email: str, error: str):
    auth_logger.error(f"Authentication failed for user: {email} - Error: {error}")

def log_gmail_call(action: str, email: str):
    gmail_logger.info(f"Gmail API call - Action: {action}, User: {email}")

def log_gmail_success(action: str, email: str):
    gmail_logger.info(f"Gmail API success - Action: {action}, User: {email}")

def log_gmail_error(action: str, email: str, error: str):
    gmail_logger.error(f"Gmail API error - Action: {action}, User: {email}, Error: {error}")

def log_ai_call(operation: str, user: str):
    ai_logger.info(f"AI API call - Operation: {operation}, User: {user}")

def log_ai_success(operation: str, user: str):
    ai_logger.info(f"AI API success - Operation: {operation}, User: {user}")

def log_ai_error(operation: str, user: str, error: str):
    ai_logger.error(f"AI API error - Operation: {operation}, User: {user}, Error: {error}")

def log_ai_retry(operation: str, attempt: int):
    ai_logger.warning(f"AI API retry - Operation: {operation}, Attempt: {attempt}")
