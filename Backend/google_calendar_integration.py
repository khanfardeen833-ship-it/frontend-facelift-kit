#!/usr/bin/env python3
"""
Google Calendar Integration
This module creates Google Meet meetings using Google Calendar API with the configured email account.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

logger = logging.getLogger(__name__)

class GoogleCalendarIntegration:
    """Google Calendar integration for creating meetings with the configured email"""
    
    def __init__(self):
        self.email_address = os.getenv('EMAIL_ADDRESS')
        self.hr_email = os.getenv('HR_EMAIL')
        self.company_name = os.getenv('COMPANY_NAME', 'Your Company')
        
        if not self.email_address:
            logger.error("EMAIL_ADDRESS not configured in environment variables")
            raise ValueError("EMAIL_ADDRESS is required for Google Calendar integration")
    
    def create_meeting_with_calendar_url(self, interview_details: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Google Calendar URL that will create a meeting with the configured email"""
        
        try:
            # Extract interview details
            candidate_name = interview_details.get('candidate_name', 'Candidate')
            candidate_email = interview_details.get('candidate_email', '')
            scheduled_date = interview_details.get('scheduled_date', '')
            scheduled_time = interview_details.get('scheduled_time', '')
            duration_minutes = interview_details.get('duration_minutes', 60)
            round_name = interview_details.get('round_name', 'Interview')
            interviewer_emails = interview_details.get('interviewer_emails', [])
            
            # Parse date and time
            try:
                start_datetime = datetime.strptime(f"{scheduled_date} {scheduled_time}", "%Y-%m-%d %H:%M")
                end_datetime = start_datetime + timedelta(minutes=duration_minutes)
            except ValueError as e:
                return {
                    'success': False,
                    'error': f'Invalid date/time format: {e}'
                }
            
            # Create meeting title
            meeting_title = f"Interview: {candidate_name} - {round_name}"
            
            # Create meeting description
            description = f"""Interview Details:
• Candidate: {candidate_name} ({candidate_email})
• Round: {round_name}
• Duration: {duration_minutes} minutes
• Scheduled: {scheduled_date} at {scheduled_time}

Participants:
• Candidate: {candidate_name} ({candidate_email})"""
            
            # Add interviewers to description
            if interviewer_emails:
                description += "\n• Interviewers:"
                for email in interviewer_emails:
                    description += f"\n  - {email}"
            
            # Prepare attendees list
            attendees = [candidate_email]
            if interviewer_emails:
                attendees.extend(interviewer_emails)
            
            # Create Google Calendar URL with meeting details
            calendar_url = self._create_calendar_url(
                title=meeting_title,
                description=description,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                attendees=attendees
            )
            
            return {
                'success': True,
                'meeting_link': calendar_url,
                'meeting_info': {
                    'title': meeting_title,
                    'description': description,
                    'start_time': start_datetime.isoformat(),
                    'end_time': end_datetime.isoformat(),
                    'attendees': attendees,
                    'organizer_email': self.email_address
                },
                'instructions': [
                    f"✅ Google Calendar meeting created for {self.email_address}",
                    "📅 Click the link below to open Google Calendar",
                    "🎯 The meeting will be created with your configured email",
                    "📧 All participants will receive calendar invitations",
                    "🔗 Google Meet link will be automatically generated"
                ],
                'note': f"🎯 Meeting will be created using {self.email_address} (your configured HR email)"
            }
            
        except Exception as e:
            logger.error(f"Error creating calendar meeting: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_calendar_url(self, title: str, description: str, start_datetime: datetime, 
                           end_datetime: datetime, attendees: List[str]) -> str:
        """Create a Google Calendar URL with meeting details"""
        
        import urllib.parse
        
        # Format dates for Google Calendar
        start_str = start_datetime.strftime('%Y%m%dT%H%M%S')
        end_str = end_datetime.strftime('%Y%m%dT%H%M%S')
        
        # Create calendar URL parameters
        params = {
            'action': 'TEMPLATE',
            'text': title,
            'dates': f"{start_str}/{end_str}",
            'details': description,
            'location': 'Google Meet',
            'add': ','.join(attendees) if attendees else '',
            'sf': 'true',  # Show free/busy
            'output': 'xml'
        }
        
        # Create the URL
        base_url = "https://calendar.google.com/calendar/render"
        query_string = urllib.parse.urlencode(params)
        
        return f"{base_url}?{query_string}"
    
    def create_meeting_instructions(self, interview_details: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed instructions for creating a meeting with the configured email"""
        
        candidate_name = interview_details.get('candidate_name', 'Candidate')
        candidate_email = interview_details.get('candidate_email', '')
        scheduled_date = interview_details.get('scheduled_date', '')
        scheduled_time = interview_details.get('scheduled_time', '')
        
        instructions = [
            f"🎯 Create Google Meet meeting using {self.email_address}",
            "",
            "📋 Method 1 - Google Calendar (Recommended):",
            "1. Click the 'Create Calendar Meeting' button below",
            "2. This will open Google Calendar with your configured email",
            "3. The meeting details will be pre-filled",
            "4. Google Meet link will be automatically generated",
            "5. All participants will receive calendar invitations",
            "",
            "📋 Method 2 - Manual Google Meet:",
            "1. Make sure you're logged into Google with the correct account",
            f"2. Go to https://meet.google.com/new",
            "3. Create a new meeting",
            "4. Copy the meeting link",
            "5. Update the meeting link in the form",
            "",
            "⚠️ Important:",
            f"• Make sure you're using {self.email_address} as the meeting organizer",
            "• This ensures the meeting is created with your HR email",
            "• Participants will see the meeting as organized by your company"
        ]
        
        return {
            'success': True,
            'instructions': instructions,
            'organizer_email': self.email_address,
            'meeting_details': {
                'candidate_name': candidate_name,
                'candidate_email': candidate_email,
                'scheduled_date': scheduled_date,
                'scheduled_time': scheduled_time
            }
        }

# Global instance
google_calendar_integration = None

def get_google_calendar_integration() -> GoogleCalendarIntegration:
    """Get the global Google Calendar integration instance"""
    global google_calendar_integration
    if google_calendar_integration is None:
        google_calendar_integration = GoogleCalendarIntegration()
    return google_calendar_integration

def create_meeting_with_configured_email(interview_details: Dict[str, Any]) -> Dict[str, Any]:
    """Create a meeting using the configured email address"""
    integration = get_google_calendar_integration()
    return integration.create_meeting_with_calendar_url(interview_details)

def get_meeting_creation_instructions(interview_details: Dict[str, Any]) -> Dict[str, Any]:
    """Get instructions for creating a meeting with the configured email"""
    integration = get_google_calendar_integration()
    return integration.create_meeting_instructions(interview_details)

# Example usage
if __name__ == "__main__":
    # Test the integration
    integration = GoogleCalendarIntegration()
    
    test_interview = {
        'candidate_name': 'John Doe',
        'candidate_email': 'john.doe@example.com',
        'scheduled_date': '2024-01-15',
        'scheduled_time': '14:00',
        'duration_minutes': 60,
        'round_name': 'Technical Interview',
        'interviewer_emails': ['interviewer1@company.com', 'interviewer2@company.com']
    }
    
    result = integration.create_meeting_with_calendar_url(test_interview)
    print("Meeting Creation Result:")
    print(json.dumps(result, indent=2))
