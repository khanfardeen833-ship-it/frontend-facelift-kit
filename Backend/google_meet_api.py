#!/usr/bin/env python3
"""
Google Meet API Integration
This module provides real Google Meet link generation using Google Calendar API
"""

import os
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import time

# Google API imports
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    print("✅ Google API libraries imported successfully")
except ImportError as e:
    print(f"❌ Google API libraries not available: {e}")
    print("Please install: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    service_account = None
    build = None
    HttpError = None

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleMeetAPI:
    """Google Meet API integration for creating real meetings"""
    
    def __init__(self, credentials_file: str = None, service_account_email: str = None):
        self.credentials_file = credentials_file or os.getenv('GOOGLE_CREDENTIALS_FILE')
        self.service_account_email = service_account_email or os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL')
        self.service = None
        self.credentials = None
        
        if not self.credentials_file:
            logger.warning("No Google credentials file provided. Real meeting creation will not be available.")
            return
        
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize the Google Calendar service"""
        try:
            if not os.path.exists(self.credentials_file):
                logger.error(f"Credentials file not found: {self.credentials_file}")
                return
            
            # Define the scopes needed
            SCOPES = ['https://www.googleapis.com/auth/calendar']
            
            # Load credentials
            self.credentials = service_account.Credentials.from_service_account_file(
                self.credentials_file, scopes=SCOPES
            )
            
            # If using domain-wide delegation, impersonate a user
            if self.service_account_email:
                self.credentials = self.credentials.with_subject(self.service_account_email)
            
            # Build the service
            self.service = build('calendar', 'v3', credentials=self.credentials)
            logger.info("✅ Google Calendar service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Calendar service: {e}")
            self.service = None
    
    def create_meeting(
        self,
        title: str,
        start_time: str,
        end_time: str,
        attendees: List[str] = None,
        description: str = "",
        timezone: str = "UTC",
        location: str = ""
    ) -> Dict[str, Any]:
        """Create a real Google Meet meeting"""
        
        if not self.service:
            return {
                "success": False,
                "error": "Google Calendar service not initialized. Please check credentials.",
                "meeting_link": None
            }
        
        try:
            # Generate unique request ID
            request_id = f"meet-{uuid.uuid4().hex[:8]}"
            
            # Create the event
            event = {
                'summary': title,
                'description': description,
                'location': location,
                'start': {
                    'dateTime': start_time,
                    'timeZone': timezone,
                },
                'end': {
                    'dateTime': end_time,
                    'timeZone': timezone,
                },
                'attendees': [{'email': email} for email in (attendees or [])],
                'guestsCanInviteOthers': True,
                'guestsCanModify': False,
                'guestsCanSeeOtherGuests': True,
                'visibility': 'public',
                'anyoneCanAddSelf': True,
                'conferenceData': {
                    'createRequest': {
                        'requestId': request_id,
                        'conferenceSolutionKey': {'type': 'hangoutsMeet'},
                    },
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                        {'method': 'popup', 'minutes': 10},       # 10 minutes before
                    ],
                },
            }
            
            # Insert the event with conference data
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event,
                conferenceDataVersion=1
            ).execute()
            
            # Extract meeting information
            meeting_link = created_event.get('hangoutLink')
            meeting_id = created_event.get('id')
            meeting_code = self._extract_meeting_code(meeting_link)
            
            logger.info(f"✅ Real Google Meet meeting created: {meeting_link}")
            
            return {
                "success": True,
                "meeting_link": meeting_link,
                "meeting_id": meeting_id,
                "meeting_code": meeting_code,
                "event_id": created_event.get('id'),
                "request_id": request_id,
                "created_at": datetime.now().isoformat(),
                "event_details": {
                    "title": created_event.get('summary'),
                    "start_time": created_event.get('start', {}).get('dateTime'),
                    "end_time": created_event.get('end', {}).get('dateTime'),
                    "attendees": [att.get('email') for att in created_event.get('attendees', [])],
                    "description": created_event.get('description'),
                    "location": created_event.get('location')
                }
            }
            
        except HttpError as e:
            error_msg = f"Google API error: {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "meeting_link": None
            }
        except Exception as e:
            error_msg = f"Unexpected error creating meeting: {e}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "meeting_link": None
            }
    
    def _extract_meeting_code(self, meeting_link: str) -> str:
        """Extract meeting code from Google Meet link"""
        if not meeting_link:
            return ""
        
        # Google Meet links are typically: https://meet.google.com/abc-defg-hij
        # Extract the code part
        try:
            code_part = meeting_link.split('/')[-1]
            return code_part
        except:
            return ""
    
    def create_interview_meeting(
        self,
        candidate_name: str,
        candidate_email: str,
        scheduled_date: str,
        scheduled_time: str,
        duration_minutes: int = 60,
        round_name: str = "Interview",
        interviewer_emails: List[str] = None,
        notes: str = "",
        timezone: str = "UTC"
    ) -> Dict[str, Any]:
        """Create a meeting specifically for interviews"""
        
        # Parse date and time
        try:
            # Parse the scheduled date and time
            if isinstance(scheduled_date, str) and isinstance(scheduled_time, str):
                # Combine date and time
                datetime_str = f"{scheduled_date}T{scheduled_time}:00"
                start_datetime = datetime.fromisoformat(datetime_str)
            else:
                start_datetime = datetime.now()
            
            # Calculate end time
            end_datetime = start_datetime + timedelta(minutes=duration_minutes)
            
            # Format for Google Calendar API
            start_time_iso = start_datetime.isoformat()
            end_time_iso = end_datetime.isoformat()
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Invalid date/time format: {e}",
                "meeting_link": None
            }
        
        # Create meeting title
        meeting_title = f"Interview: {candidate_name} - {round_name}"
        
        # Create meeting description
        meeting_description = f"""
Interview Details:
- Candidate: {candidate_name}
- Round: {round_name}
- Duration: {duration_minutes} minutes
- Scheduled: {scheduled_date} at {scheduled_time}

Notes: {notes}

Participants:
- Candidate: {candidate_name} ({candidate_email})
"""
        
        # Add interviewers to description
        if interviewer_emails:
            meeting_description += "\nInterviewers:\n"
            for interviewer in interviewer_emails:
                meeting_description += f"- {interviewer}\n"
        
        # Prepare attendees list
        attendees = [candidate_email]
        if interviewer_emails:
            attendees.extend(interviewer_emails)
        
        # Create the meeting
        return self.create_meeting(
            title=meeting_title,
            start_time=start_time_iso,
            end_time=end_time_iso,
            attendees=attendees,
            description=meeting_description.strip(),
            timezone=timezone
        )
    
    def test_connection(self) -> Dict[str, Any]:
        """Test the Google Calendar API connection"""
        if not self.service:
            return {
                "success": False,
                "error": "Service not initialized"
            }
        
        try:
            # Try to list calendars
            calendar_list = self.service.calendarList().list().execute()
            calendars = calendar_list.get('items', [])
            
            return {
                "success": True,
                "message": "Connection successful",
                "calendars_count": len(calendars),
                "primary_calendar": any(cal.get('primary', False) for cal in calendars)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Connection test failed: {e}"
            }

# Global instance
google_meet_api = None

def initialize_google_meet_api(credentials_file: str = None, service_account_email: str = None) -> GoogleMeetAPI:
    """Initialize the global Google Meet API instance"""
    global google_meet_api
    if google_meet_api is None:
        google_meet_api = GoogleMeetAPI(credentials_file, service_account_email)
    return google_meet_api

def create_real_meeting_link(
    candidate_name: str,
    candidate_email: str,
    scheduled_date: str,
    scheduled_time: str,
    duration_minutes: int = 60,
    round_name: str = "Interview",
    interviewer_emails: List[str] = None,
    notes: str = "",
    timezone: str = "UTC"
) -> Dict[str, Any]:
    """Convenience function to create a real meeting link"""
    global google_meet_api
    
    if google_meet_api is None:
        google_meet_api = initialize_google_meet_api()
    
    return google_meet_api.create_interview_meeting(
        candidate_name=candidate_name,
        candidate_email=candidate_email,
        scheduled_date=scheduled_date,
        scheduled_time=scheduled_time,
        duration_minutes=duration_minutes,
        round_name=round_name,
        interviewer_emails=interviewer_emails,
        notes=notes,
        timezone=timezone
    )

# Example usage and testing
if __name__ == "__main__":
    # Test the API (without real credentials)
    api = GoogleMeetAPI()
    
    # Test connection
    connection_test = api.test_connection()
    print("Connection Test:", json.dumps(connection_test, indent=2))
    
    # Example meeting creation (will fail without real credentials)
    if connection_test.get("success"):
        meeting_result = create_real_meeting_link(
            candidate_name="John Doe",
            candidate_email="john.doe@example.com",
            scheduled_date="2024-01-15",
            scheduled_time="14:00",
            duration_minutes=60,
            round_name="Technical Round",
            interviewer_emails=["interviewer1@example.com", "interviewer2@example.com"],
            notes="Focus on Python and system design"
        )
        
        print("Meeting Creation Result:", json.dumps(meeting_result, indent=2))
    else:
        print("❌ Cannot test meeting creation - API not properly configured")
        print("To enable real meeting creation:")
        print("1. Set up Google Cloud Project")
        print("2. Enable Google Calendar API")
        print("3. Create service account credentials")
        print("4. Set GOOGLE_CREDENTIALS_FILE environment variable")
        print("5. Set GOOGLE_SERVICE_ACCOUNT_EMAIL environment variable (optional)")
