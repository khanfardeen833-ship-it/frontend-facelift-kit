#!/usr/bin/env python3
"""
Google Meet Helper - Provides instructions and tools for creating real Google Meet meetings
This module helps HR create actual Google Meet meetings to replace placeholder links.
"""

import json
from datetime import datetime
from typing import Dict, List, Any
import webbrowser
import urllib.parse

class GoogleMeetHelper:
    """Helper class for creating real Google Meet meetings"""
    
    @staticmethod
    def generate_meet_creation_url(interview_details: Dict[str, Any]) -> str:
        """Generate a URL that opens Google Meet with pre-filled meeting details"""
        # Create a Google Meet creation URL with parameters
        base_url = "https://meet.google.com/new"
        
        # Prepare meeting details for URL parameters
        params = {
            'title': interview_details.get('meeting_title', 'Interview Meeting'),
            'date': interview_details.get('scheduled_date', ''),
            'time': interview_details.get('scheduled_time', ''),
            'duration': interview_details.get('duration_minutes', 60)
        }
        
        # Note: Google Meet doesn't support direct URL parameters for scheduling
        # This is a placeholder for future Google Calendar integration
        return base_url
    
    @staticmethod
    def create_meeting_instructions(interview_details: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed instructions for setting up a real Google Meet meeting"""
        
        instructions = {
            "title": "How to Create a Real Google Meet Meeting",
            "steps": [
                {
                    "step": 1,
                    "title": "Go to Google Meet",
                    "description": "Open your web browser and go to https://meet.google.com",
                    "action": "Click here to open Google Meet",
                    "url": "https://meet.google.com"
                },
                {
                    "step": 2,
                    "title": "Create New Meeting",
                    "description": "Click on 'New meeting' or 'Schedule a meeting' button",
                    "action": "Look for the 'New meeting' button on the main page"
                },
                {
                    "step": 3,
                    "title": "Set Meeting Details",
                    "description": "Fill in the meeting information",
                    "details": {
                        "meeting_title": interview_details.get('meeting_title', 'Interview Meeting'),
                        "date": interview_details.get('scheduled_date', ''),
                        "time": interview_details.get('scheduled_time', ''),
                        "duration": f"{interview_details.get('duration_minutes', 60)} minutes"
                    }
                },
                {
                    "step": 4,
                    "title": "Add Participants",
                    "description": "Add the candidate and interviewers to the meeting",
                    "participants": {
                        "candidate": {
                            "name": interview_details.get('candidate_name', 'Candidate'),
                            "email": interview_details.get('candidate_email', '')
                        },
                        "interviewers": interview_details.get('interviewer_names', [])
                    }
                },
                {
                    "step": 5,
                    "title": "Generate Meeting Link",
                    "description": "Google Meet will generate a real meeting link",
                    "note": "Copy this link and replace the placeholder link in the system"
                },
                {
                    "step": 6,
                    "title": "Send Invitations",
                    "description": "Send the real meeting link to all participants",
                    "note": "Make sure to include the meeting details and any special instructions"
                }
            ],
            "meeting_details": {
                "title": interview_details.get('meeting_title', 'Interview Meeting'),
                "date": interview_details.get('scheduled_date', ''),
                "time": interview_details.get('scheduled_time', ''),
                "duration": f"{interview_details.get('duration_minutes', 60)} minutes",
                "type": interview_details.get('interview_type', 'video_call'),
                "round": interview_details.get('round_name', 'Interview'),
                "notes": interview_details.get('notes', '')
            },
            "participants": {
                "candidate": {
                    "name": interview_details.get('candidate_name', 'Candidate'),
                    "email": interview_details.get('candidate_email', '')
                },
                "interviewers": interview_details.get('interviewer_names', [])
            },
            "important_notes": [
                "⚠️  The current link is a PLACEHOLDER and will not work",
                "You must create a real Google Meet meeting to get a working link",
                "Test the real meeting link before sending it to participants",
                "Make sure all participants have the correct meeting link",
                "Consider setting up a calendar invite with the meeting link"
            ]
        }
        
        return instructions
    
    @staticmethod
    def create_calendar_invite_data(interview_details: Dict[str, Any]) -> Dict[str, Any]:
        """Create data for Google Calendar invite (for manual calendar creation)"""
        
        # Parse date and time
        scheduled_date = interview_details.get('scheduled_date', '')
        scheduled_time = interview_details.get('scheduled_time', '')
        duration_minutes = interview_details.get('duration_minutes', 60)
        
        # Create calendar event data
        calendar_data = {
            "title": interview_details.get('meeting_title', 'Interview Meeting'),
            "description": f"""
Interview Details:
- Candidate: {interview_details.get('candidate_name', 'Candidate')}
- Round: {interview_details.get('round_name', 'Interview')}
- Duration: {duration_minutes} minutes
- Type: {interview_details.get('interview_type', 'video_call')}

Notes: {interview_details.get('notes', 'None')}

Participants:
- Candidate: {interview_details.get('candidate_name', 'Candidate')} ({interview_details.get('candidate_email', '')})
""",
            "date": scheduled_date,
            "time": scheduled_time,
            "duration": duration_minutes,
            "attendees": []
        }
        
        # Add candidate email if available
        if interview_details.get('candidate_email'):
            calendar_data["attendees"].append(interview_details['candidate_email'])
        
        # Add interviewer emails if available
        for interviewer in interview_details.get('interviewer_names', []):
            if '@' in interviewer:  # If it looks like an email
                calendar_data["attendees"].append(interviewer)
        
        return calendar_data
    
    @staticmethod
    def generate_meeting_checklist(interview_details: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate a checklist for meeting preparation"""
        
        checklist = [
            {
                "item": "Create real Google Meet meeting",
                "status": "pending",
                "description": "Go to https://meet.google.com and create a new meeting",
                "priority": "high"
            },
            {
                "item": "Set meeting details",
                "status": "pending", 
                "description": f"Set title: {interview_details.get('meeting_title', 'Interview Meeting')}",
                "priority": "high"
            },
            {
                "item": "Schedule meeting time",
                "status": "pending",
                "description": f"Set date: {interview_details.get('scheduled_date', '')} at {interview_details.get('scheduled_time', '')}",
                "priority": "high"
            },
            {
                "item": "Add participants",
                "status": "pending",
                "description": f"Add candidate: {interview_details.get('candidate_name', 'Candidate')}",
                "priority": "high"
            },
            {
                "item": "Add interviewers",
                "status": "pending",
                "description": f"Add interviewers: {', '.join(interview_details.get('interviewer_names', []))}",
                "priority": "medium"
            },
            {
                "item": "Test meeting link",
                "status": "pending",
                "description": "Test the real meeting link to ensure it works",
                "priority": "high"
            },
            {
                "item": "Send invitations",
                "status": "pending",
                "description": "Send the real meeting link to all participants",
                "priority": "high"
            },
            {
                "item": "Update system with real link",
                "status": "pending",
                "description": "Replace the placeholder link in the HRMS system",
                "priority": "medium"
            }
        ]
        
        return checklist

def create_meeting_helper_response(interview_details: Dict[str, Any]) -> Dict[str, Any]:
    """Create a comprehensive response with meeting creation help"""
    
    helper = GoogleMeetHelper()
    
    return {
        "success": True,
        "type": "meeting_creation_helper",
        "data": {
            "instructions": helper.create_meeting_instructions(interview_details),
            "calendar_data": helper.create_calendar_invite_data(interview_details),
            "checklist": helper.generate_meeting_checklist(interview_details),
            "meet_url": helper.generate_meet_creation_url(interview_details),
            "message": "This is a placeholder meeting link. Use the instructions below to create a real Google Meet meeting."
        }
    }

# Example usage
if __name__ == "__main__":
    # Test data
    test_interview = {
        "candidate_name": "John Doe",
        "candidate_email": "john.doe@example.com",
        "scheduled_date": "2024-01-15",
        "scheduled_time": "14:00",
        "duration_minutes": 60,
        "interview_type": "video_call",
        "round_name": "Technical Round",
        "interviewer_names": ["Jane Smith", "Bob Johnson"],
        "meeting_title": "Technical Interview - John Doe",
        "notes": "Focus on Python and system design"
    }
    
    # Generate helper response
    response = create_meeting_helper_response(test_interview)
    
    print("Google Meet Helper Response:")
    print(json.dumps(response, indent=2))
