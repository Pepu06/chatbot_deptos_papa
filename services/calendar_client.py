"""
Google Calendar client
Handles calendar event creation
"""
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from config.settings import settings
from datetime import datetime
from typing import Optional, Dict, Any
import os.path
import pickle


# If modifying these scopes, delete the file token.pickle
SCOPES = ['https://www.googleapis.com/auth/calendar']


class CalendarService:
    """Service for interacting with Google Calendar API"""
    
    def __init__(self):
        self.credentials = None
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Calendar API"""
        try:
            # Token file stores the user's access and refresh tokens
            token_file = settings.google_calendar_token_file
            
            if os.path.exists(token_file):
                with open(token_file, 'rb') as token:
                    self.credentials = pickle.load(token)
            
            # If there are no (valid) credentials available, let the user log in
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    print("⚠️  Google Calendar requires manual authentication.")
                    print("Run the authentication flow separately or credentials are missing.")
                    # For production, you'd need a proper OAuth flow
                    # For now, we'll create credentials from client config
                    return
                
                # Save the credentials for the next run
                with open(token_file, 'wb') as token:
                    pickle.dump(self.credentials, token)
            
            # Build the service
            if self.credentials:
                self.service = build('calendar', 'v3', credentials=self.credentials)
                print("✅ Google Calendar authenticated successfully")
        
        except Exception as e:
            print(f"❌ Error authenticating with Google Calendar: {e}")
            print("Calendar functionality will be limited.")
    
    async def create_event(
        self,
        title: str,
        start_datetime: str,
        end_datetime: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        timezone: str = "America/Argentina/Buenos_Aires"
    ) -> Optional[Dict[str, Any]]:
        """
        Create a calendar event
        
        Args:
            title: Event title
            start_datetime: ISO format datetime string
            end_datetime: ISO format datetime string (optional, defaults to +1 hour)
            description: Event description
            location: Event location
            timezone: Timezone for the event
            
        Returns:
            Created event data or None if failed
        """
        if not self.service:
            print("❌ Calendar service not initialized")
            return None
        
        try:
            # Parse start time
            start_dt = datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
            
            # If no end time provided, default to +1 hour
            if not end_datetime:
                from datetime import timedelta
                end_dt = start_dt + timedelta(hours=1)
                end_datetime = end_dt.isoformat()
            
            event = {
                'summary': title,
                'start': {
                    'dateTime': start_datetime,
                    'timeZone': timezone,
                },
                'end': {
                    'dateTime': end_datetime,
                    'timeZone': timezone,
                },
            }
            
            if description:
                event['description'] = description
            
            if location:
                event['location'] = location
            
            # Create the event
            created_event = self.service.events().insert(
                calendarId=settings.google_calendar_id,
                body=event
            ).execute()
            
            print(f"✅ Event created: {created_event.get('htmlLink')}")
            return created_event
        
        except Exception as e:
            print(f"❌ Error creating calendar event: {e}")
            return None


# Global instance
calendar_service = CalendarService()
