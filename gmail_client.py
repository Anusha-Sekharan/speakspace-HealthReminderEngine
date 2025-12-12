import os.path
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from auth_config import SCOPES

# If modifying these scopes, delete the file token.json.

CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

def get_gmail_service():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    
    # 1. Try environment variable (for Render/Production)
    token_data = os.environ.get('GOOGLE_TOKEN_DATA')
    if token_data:
        try:
            import json
            info = json.loads(token_data)
            creds = Credentials.from_authorized_user_info(info, SCOPES)
        except Exception as e:
            print(f"Error loading creds from env: {e}")
            creds = None

    # 2. Try local file if env var didn't work
    if not can_use_env_creds(creds):
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                # If refresh fails (e.g. scopes changed or token revoked), re-auth
                creds = None
        
        if not creds:
            # We cannot do interactive login in production/headless
            if not os.path.exists(CREDENTIALS_FILE) and not os.environ.get('GOOGLE_TOKEN_DATA'):
                 # If we are here, we are likely in prod but env var failed or missing
                 print("WARNING: No credentials found and interactive login is not possible in this environment.")
            
            if os.path.exists(CREDENTIALS_FILE):
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service

def can_use_env_creds(creds):
    return creds and creds.valid

def send_email(service, to, subject, text_body, html_body=None, cc=None, bcc=None):
    """Create and send an email message
    Print the returned  message id
    Returns: Message object, including message Id

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    try:
        message = MIMEMultipart('alternative')
        message['to'] = to
        message['subject'] = subject
        
        if cc:
            message['cc'] = cc
        if bcc:
            message['bcc'] = bcc

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        part1 = MIMEText(text_body, 'plain')
        message.attach(part1)

        if html_body:
            part2 = MIMEText(html_body, 'html')
            message.attach(part2)

        # Encode the message (Base64url)
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {
            'raw': encoded_message
        }
        # pylint: disable=E1101
        send_message = (service.users().messages().send
                        (userId="me", body=create_message).execute())
        
        return send_message

    except HttpError as error:
        print(f'An error occurred: {error}')
        send_message = None
        raise error

# Placeholder for future PDF attachment functionality
def send_email_with_attachments(service, to, subject, body, file_attachments=None):
    """
    Future implementation to support sending emails with PDF attachments.
    :param file_attachments: List of file paths or byte streams
    """
    raise NotImplementedError("Attachment support is not yet implemented.")
