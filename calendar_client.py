import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from auth_config import SCOPES

# Minimal wrapper reusing the same token logic but for Calendar scopes
# This ensures we don't accidentally overwrite token.json with missing scopes
# unless handled carefully.Ideally, one token file has multiple scopes.

CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

def get_calendar_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        # We try to load credentials. Verify scopes in a real app.
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)

def create_event(service, summary, start_time, duration_minutes=30, description=None):
    """
    Creates a simple event in the primary calendar.
    :param service: Calendar API service instance
    :param summary: Title of the event
    :param start_time: datetime object
    :param duration_minutes: Duration in minutes
    """
    from datetime import timedelta
    from tzlocal import get_localzone_name
    
    # Get local timezone explicitly to ensure Google Calendar places it correctly
    local_tz = get_localzone_name()
    
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': local_tz, 
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': local_tz,
        },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    print(f"Event created: {event.get('htmlLink')}")
    return event


