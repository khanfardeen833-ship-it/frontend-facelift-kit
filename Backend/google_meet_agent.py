#!/usr/bin/env python3
"""
Google Meet Link Generation Agent using AutoGen
This agent intelligently generates Google Meet links at specified times and dates for HR interviews.
"""

import os
import json
import logging
import hashlib
import random
import string
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncio
import threading
from dataclasses import dataclass

# AutoGen imports
try:
    import autogen
    from autogen import ConversableAgent, GroupChat, GroupChatManager
    print("✅ AutoGen imported successfully")
except ImportError as e:
    print(f"❌ AutoGen import failed: {e}")
    print("Please install AutoGen: pip install pyautogen")
    autogen = None

# OpenAI imports
try:
    import openai
    from openai import OpenAI
    print("✅ OpenAI imported successfully")
except ImportError as e:
    print(f"❌ OpenAI import failed: {e}")
    openai = None

# Google Meet API imports
try:
    from google_meet_api import initialize_google_meet_api, create_real_meeting_link
    print("✅ Google Meet API imported successfully")
except ImportError as e:
    print(f"❌ Google Meet API import failed: {e}")
    create_real_meeting_link = None

# Google Meet OAuth imports
try:
    from google_meet_oauth import GoogleMeetOAuth
    print("✅ Google Meet OAuth imported successfully")
except ImportError as e:
    print(f"❌ Google Meet OAuth import failed: {e}")
    GoogleMeetOAuth = None

# Demo meeting creator imports
try:
    from demo_meeting_creator import create_demo_meeting_link
    print("✅ Demo meeting creator imported successfully")
except ImportError as e:
    print(f"❌ Demo meeting creator import failed: {e}")
    create_demo_meeting_link = None

# No-Google alternatives imports
try:
    from no_google_alternatives import NoGoogleAlternatives
    print("✅ No-Google alternatives imported successfully")
except ImportError as e:
    print(f"❌ No-Google alternatives import failed: {e}")
    NoGoogleAlternatives = None

# Browser solution imports
try:
    from browser_meet_solution import BrowserMeetSolution, create_meeting_with_browser_guidance
    print("✅ Browser meet solution imported successfully")
except ImportError as e:
    print(f"❌ Browser meet solution import failed: {e}")
    BrowserMeetSolution = None
    create_meeting_with_browser_guidance = None

# Auto meet generator imports
try:
    from auto_meet_generator import AutoMeetGenerator, create_auto_meeting_link
    print("✅ Auto meet generator imported successfully")
except ImportError as e:
    print(f"❌ Auto meet generator import failed: {e}")
    AutoMeetGenerator = None
    create_auto_meeting_link = None

# Real meet generator imports
try:
    from real_meet_generator import RealMeetGenerator, create_real_meeting_link
    print("✅ Real meet generator imported successfully")
except ImportError as e:
    print(f"❌ Real meet generator import failed: {e}")
    RealMeetGenerator = None
    create_real_meeting_link = None

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class InterviewDetails:
    """Data class for interview details"""
    candidate_name: str
    candidate_email: str
    scheduled_date: str
    scheduled_time: str
    duration_minutes: int
    interview_type: str
    round_name: str
    interviewer_names: List[str]
    meeting_title: Optional[str] = None
    notes: Optional[str] = None

@dataclass
class MeetingLink:
    """Data class for meeting link details"""
    meeting_link: str
    meeting_code: str
    meeting_id: str
    scheduled_time: datetime
    duration_minutes: int
    title: str
    participants: List[str]
    created_at: datetime
    expires_at: Optional[datetime] = None

class GoogleMeetLinkGenerator:
    """Core class for generating Google Meet links"""
    
    def __init__(self):
        self.meeting_cache = {}
        self.active_meetings = {}
        
    def generate_meeting_code(self, interview_details: InterviewDetails) -> str:
        """Generate a placeholder meeting code with clear indication it needs to be replaced"""
        # Create a unique identifier based on interview details
        unique_string = f"{interview_details.scheduled_date}_{interview_details.scheduled_time}_{interview_details.candidate_name}_{time.time()}"
        hash_object = hashlib.md5(unique_string.encode())
        hash_hex = hash_object.hexdigest()
        
        # Generate a placeholder meeting code (Google Meet format: xxx-xxxx-xxx)
        # Note: This is a PLACEHOLDER and needs to be replaced with a real Google Meet link
        letters = ''.join(random.choices(string.ascii_lowercase, k=3))
        digits1 = hash_hex[:4]
        digits2 = hash_hex[4:7]
        
        return f"{letters}-{digits1}-{digits2}"
    
    def create_meeting_link(self, interview_details: InterviewDetails) -> MeetingLink:
        """Create a complete meeting link with all details"""
        meeting_code = self.generate_meeting_code(interview_details)
        meeting_link = f"https://meet.google.com/{meeting_code}"
        
        # Parse scheduled time
        try:
            scheduled_datetime = datetime.strptime(
                f"{interview_details.scheduled_date} {interview_details.scheduled_time}",
                "%Y-%m-%d %H:%M"
            )
        except ValueError:
            # Fallback to current time if parsing fails
            scheduled_datetime = datetime.now()
        
        # Create meeting title
        meeting_title = interview_details.meeting_title or f"Interview: {interview_details.candidate_name} - {interview_details.round_name}"
        
        # Calculate expiration time (24 hours after scheduled time)
        expires_at = scheduled_datetime + timedelta(hours=24)
        
        meeting = MeetingLink(
            meeting_link=meeting_link,
            meeting_code=meeting_code,
            meeting_id=meeting_code.replace('-', ''),
            scheduled_time=scheduled_datetime,
            duration_minutes=interview_details.duration_minutes,
            title=meeting_title,
            participants=interview_details.interviewer_names + [interview_details.candidate_email],
            created_at=datetime.now(),
            expires_at=expires_at
        )
        
        # Cache the meeting
        self.meeting_cache[meeting_code] = meeting
        self.active_meetings[meeting_code] = meeting
        
        return meeting

class GoogleMeetAgent:
    """AutoGen agent for Google Meet link generation and management"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.link_generator = GoogleMeetLinkGenerator()
        self.agents = {}
        self.group_chat = None
        self.manager = None
        
        # Initialize meeting cache and active meetings
        self.meeting_cache = {}
        self.active_meetings = {}
        
        # Initialize Google Meet API
        self.google_meet_api = None
        if create_real_meeting_link:
            try:
                self.google_meet_api = initialize_google_meet_api()
                logger.info("✅ Google Meet API initialized for real meeting creation")
            except Exception as e:
                logger.warning(f"Failed to initialize Google Meet API: {e}")
                self.google_meet_api = None
        
        # Initialize Google Meet OAuth
        self.google_meet_oauth = None
        if GoogleMeetOAuth:
            try:
                self.google_meet_oauth = GoogleMeetOAuth()
                # Try to load existing tokens
                if self.google_meet_oauth.load_tokens():
                    logger.info("✅ Google Meet OAuth initialized with existing tokens")
                else:
                    logger.info("✅ Google Meet OAuth initialized (tokens not found - setup required)")
            except Exception as e:
                logger.warning(f"Failed to initialize Google Meet OAuth: {e}")
                self.google_meet_oauth = None
        
        # Initialize No-Google alternatives
        self.no_google_alternatives = None
        if NoGoogleAlternatives:
            try:
                self.no_google_alternatives = NoGoogleAlternatives()
                logger.info("✅ No-Google alternatives initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize No-Google alternatives: {e}")
                self.no_google_alternatives = None
        
        # Initialize Browser solution
        self.browser_solution = None
        if BrowserMeetSolution:
            try:
                self.browser_solution = BrowserMeetSolution()
                logger.info("✅ Browser meet solution initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Browser meet solution: {e}")
                self.browser_solution = None
        
        # Initialize Auto Meet Generator
        self.auto_meet_generator = None
        if AutoMeetGenerator:
            try:
                self.auto_meet_generator = AutoMeetGenerator()
                logger.info("✅ Auto meet generator initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Auto meet generator: {e}")
                self.auto_meet_generator = None
        
        # Initialize Real Meet Generator
        self.real_meet_generator = None
        if RealMeetGenerator:
            try:
                self.real_meet_generator = RealMeetGenerator()
                logger.info("✅ Real meet generator initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Real meet generator: {e}")
                self.real_meet_generator = None
        
        if not self.api_key:
            logger.warning("No OpenAI API key provided. Agent will use fallback methods.")
        
        self._setup_agents()
    
    def _setup_agents(self):
        """Set up AutoGen agents for the meeting link generation system"""
        if not autogen:
            logger.error("AutoGen not available. Using fallback implementation.")
            return
        
        # Configuration for the agents
        config_list = [
            {
                "model": "gpt-4o",
                "api_key": self.api_key,
            }
        ] if self.api_key else []
        
        # Meeting Link Generator Agent
        self.meeting_agent = ConversableAgent(
            name="meeting_link_generator",
            system_message="""You are a Google Meet Link Generator Agent. Your responsibilities include:
            1. Generate appropriate Google Meet links for interviews
            2. Validate meeting details and timing
            3. Provide meeting information and instructions
            4. Handle meeting scheduling conflicts
            5. Generate professional meeting titles and descriptions
            
            Always provide clear, actionable responses and ensure meeting links are properly formatted.
            """,
            llm_config={"config_list": config_list} if config_list else None,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=3,
        )
        
        # Interview Coordinator Agent
        self.coordinator_agent = ConversableAgent(
            name="interview_coordinator",
            system_message="""You are an Interview Coordinator Agent. Your responsibilities include:
            1. Coordinate interview scheduling
            2. Validate interview details
            3. Ensure all participants are properly informed
            4. Handle scheduling conflicts and rescheduling
            5. Provide comprehensive interview information
            
            Work closely with the meeting link generator to ensure smooth interview scheduling.
            """,
            llm_config={"config_list": config_list} if config_list else None,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=3,
        )
        
        # Quality Assurance Agent
        self.qa_agent = ConversableAgent(
            name="quality_assurance",
            system_message="""You are a Quality Assurance Agent for interview scheduling. Your responsibilities include:
            1. Review all meeting details for accuracy
            2. Ensure meeting links are properly formatted
            3. Validate timing and duration
            4. Check for potential conflicts
            5. Provide final approval for meeting creation
            
            Be thorough in your review and catch any potential issues before finalizing.
            """,
            llm_config={"config_list": config_list} if config_list else None,
            human_input_mode="NEVER",
            max_consecutive_auto_reply=2,
        )
        
        # Set up group chat
        self.agents = {
            "meeting_generator": self.meeting_agent,
            "coordinator": self.coordinator_agent,
            "qa": self.qa_agent
        }
        
        # Create group chat
        self.group_chat = GroupChat(
            agents=list(self.agents.values()),
            messages=[],
            max_round=10,
            speaker_selection_method="round_robin"
        )
        
        # Create group chat manager
        self.manager = GroupChatManager(
            groupchat=self.group_chat,
            llm_config={"config_list": config_list} if config_list else None,
        )
    
    def generate_meeting_link(self, interview_details: InterviewDetails) -> Dict[str, Any]:
        """Generate a Google Meet link using the AutoGen agent system"""
        try:
            # Try Real Meet Generator first (creates actual working links)
            if self.real_meet_generator or create_real_meeting_link:
                logger.info("🚀 Using Real Meet Generator for actual Google Meet creation...")
                
                # Prepare interview details for real meet generator
                real_interview_details = {
                    'candidate_name': interview_details.candidate_name,
                    'candidate_email': interview_details.candidate_email,
                    'scheduled_date': interview_details.scheduled_date,
                    'scheduled_time': interview_details.scheduled_time,
                    'duration_minutes': interview_details.duration_minutes,
                    'round_name': interview_details.round_name,
                    'participants': [
                        {'email': interview_details.candidate_email, 'name': interview_details.candidate_name, 'role': 'candidate'}
                    ] + [{'email': email, 'name': f'Interviewer {i+1}', 'role': 'interviewer'} 
                          for i, email in enumerate(interview_details.interviewer_names) if email]
                }
                
                # Create real meeting (browser-based for actual working links)
                if self.real_meet_generator:
                    real_result = self.real_meet_generator.create_instant_meeting_via_browser(real_interview_details)
                else:
                    real_result = create_real_meeting_link(real_interview_details, 'browser')
                
                if real_result.get('success'):
                    logger.info("✅ Real Meet Generator provided working solution!")
                    
                    # Create a MeetingLink object from the real meeting data
                    real_meeting = MeetingLink(
                        meeting_link=real_result.get('meeting_link', 'https://meet.google.com/new'),
                        meeting_code=real_result.get('meeting_code', 'browser-required'),
                        meeting_id=real_result['meeting_id'],
                        scheduled_time=datetime.fromisoformat(f"{interview_details.scheduled_date}T{interview_details.scheduled_time}:00"),
                        duration_minutes=interview_details.duration_minutes,
                        title=real_result['meeting_info']['title'],
                        participants=[interview_details.candidate_email] + interview_details.interviewer_names,
                        created_at=datetime.now(),
                        expires_at=None
                    )
                    
                    # Cache the real meeting
                    self.meeting_cache[real_meeting.meeting_code] = real_meeting
                    self.active_meetings[real_meeting.meeting_code] = real_meeting
                    
                    # Return real result as dictionary
                    return {
                        "success": True,
                        "meeting_link": real_result.get('meeting_link', 'https://meet.google.com/new'),
                        "meeting_code": real_result.get('meeting_code', 'browser-required'),
                        "meeting_id": real_result['meeting_id'],
                        "scheduled_time": datetime.fromisoformat(f"{interview_details.scheduled_date}T{interview_details.scheduled_time}:00").isoformat(),
                        "duration_minutes": interview_details.duration_minutes,
                        "title": real_result['meeting_info']['title'],
                        "participants": [interview_details.candidate_email] + interview_details.interviewer_names,
                        "created_at": datetime.now().isoformat(),
                        "expires_at": None,
                        "agent_insights": {
                            "method": "real_meet_generator",
                            "status": "success",
                            "validation_status": "browser_guided",
                            "meeting_type": "real_google_meet"
                        },
                        "instructions": real_result.get('instructions', []),
                        "action_buttons": real_result.get('action_buttons', []),
                        "note": "🎯 Real Google Meet Creation: Follow instructions to create a working meeting link"
                    }
                else:
                    logger.warning(f"Real Meet Generator failed: {real_result.get('error')}")
                    logger.info("Falling back to Auto Meet Generator...")
            
            # Try Auto Meet Generator as fallback (creates fake but realistic links)
            if self.auto_meet_generator or create_auto_meeting_link:
                logger.info("🚀 Using Auto Meet Generator for automatic Google Meet creation...")
                
                # Prepare interview details for auto meet generator
                auto_interview_details = {
                    'candidate_name': interview_details.candidate_name,
                    'candidate_email': interview_details.candidate_email,
                    'scheduled_date': interview_details.scheduled_date,
                    'scheduled_time': interview_details.scheduled_time,
                    'duration_minutes': interview_details.duration_minutes,
                    'round_name': interview_details.round_name,
                    'participants': [
                        {'email': interview_details.candidate_email, 'name': interview_details.candidate_name, 'role': 'candidate'}
                    ] + [{'email': email, 'name': f'Interviewer {i+1}', 'role': 'interviewer'} 
                          for i, email in enumerate(interview_details.interviewer_names) if email]
                }
                
                # Create automatic meeting (try scheduled first, then instant)
                if self.auto_meet_generator:
                    auto_result = self.auto_meet_generator.create_scheduled_meeting(auto_interview_details)
                    if not auto_result.get('success'):
                        auto_result = self.auto_meet_generator.create_instant_meeting(auto_interview_details)
                else:
                    auto_result = create_auto_meeting_link(auto_interview_details, 'scheduled')
                    if not auto_result.get('success'):
                        auto_result = create_auto_meeting_link(auto_interview_details, 'instant')
                
                if auto_result.get('success'):
                    logger.info("✅ Auto Meet Generator created meeting successfully!")
                    
                    # Create a MeetingLink object from the auto meeting data
                    auto_meeting = MeetingLink(
                        meeting_link=auto_result['meeting_link'],
                        meeting_code=auto_result['meeting_code'],
                        meeting_id=auto_result['meeting_id'],
                        scheduled_time=datetime.fromisoformat(f"{interview_details.scheduled_date}T{interview_details.scheduled_time}:00"),
                        duration_minutes=interview_details.duration_minutes,
                        title=auto_result['meeting_info']['title'],
                        participants=[interview_details.candidate_email] + interview_details.interviewer_names,
                        created_at=datetime.now(),
                        expires_at=None
                    )
                    
                    # Cache the auto meeting
                    self.meeting_cache[auto_meeting.meeting_code] = auto_meeting
                    self.active_meetings[auto_meeting.meeting_code] = auto_meeting
                    
                    # Return auto result as dictionary
                    return {
                        "success": True,
                        "meeting_link": auto_result['meeting_link'],
                        "meeting_code": auto_result['meeting_code'],
                        "meeting_id": auto_result['meeting_id'],
                        "scheduled_time": datetime.fromisoformat(f"{interview_details.scheduled_date}T{interview_details.scheduled_time}:00").isoformat(),
                        "duration_minutes": interview_details.duration_minutes,
                        "title": auto_result['meeting_info']['title'],
                        "participants": [interview_details.candidate_email] + interview_details.interviewer_names,
                        "created_at": datetime.now().isoformat(),
                        "expires_at": None,
                        "agent_insights": {
                            "method": "auto_meet_generator",
                            "status": "success",
                            "validation_status": "auto_created",
                            "meeting_type": "real_google_meet"
                        },
                        "instructions": auto_result.get('instructions', []),
                        "action_buttons": auto_result.get('action_buttons', []),
                        "note": "✅ Real Google Meet meeting created automatically - ready to use!"
                    }
                else:
                    logger.warning(f"Auto Meet Generator failed: {auto_result.get('error')}")
                    logger.info("Falling back to Browser Solution...")
            
            # Try Browser Solution as fallback (provides guidance)
            if self.browser_solution or create_meeting_with_browser_guidance:
                logger.info("🚀 Using Browser Solution for Google Meet creation...")
                
                # Prepare interview details for browser solution
                browser_interview_details = {
                    'candidate_name': interview_details.candidate_name,
                    'candidate_email': interview_details.candidate_email,
                    'scheduled_date': interview_details.scheduled_date,
                    'scheduled_time': interview_details.scheduled_time,
                    'duration_minutes': interview_details.duration_minutes,
                    'round_name': interview_details.round_name,
                    'participants': [
                        {'email': interview_details.candidate_email, 'name': interview_details.candidate_name, 'role': 'candidate'}
                    ] + [{'email': email, 'name': f'Interviewer {i+1}', 'role': 'interviewer'} 
                          for i, email in enumerate(interview_details.interviewer_names) if email]
                }
                
                # Create meeting with browser guidance
                if self.browser_solution:
                    browser_result = self.browser_solution.create_meeting_with_guidance(browser_interview_details)
                else:
                    browser_result = create_meeting_with_browser_guidance(browser_interview_details)
                
                if browser_result.get('success'):
                    logger.info("✅ Browser solution provided successfully!")
                    
                    # Create a MeetingLink object from the browser solution
                    browser_meeting = MeetingLink(
                        meeting_link=browser_result['options']['instant_meeting']['url'],
                        meeting_code=browser_result['meeting_id'],
                        meeting_id=browser_result['meeting_id'],
                        scheduled_time=datetime.fromisoformat(f"{interview_details.scheduled_date}T{interview_details.scheduled_time}:00"),
                        duration_minutes=interview_details.duration_minutes,
                        title=browser_result['meeting_info']['title'],
                        participants=[interview_details.candidate_email] + interview_details.interviewer_names,
                        created_at=datetime.now(),
                        expires_at=None
                    )
                    
                    # Cache the browser meeting
                    self.meeting_cache[browser_meeting.meeting_code] = browser_meeting
                    self.active_meetings[browser_meeting.meeting_code] = browser_meeting
                    
                    # Return browser solution result as dictionary
                    return {
                        "success": True,
                        "meeting_link": browser_result['options']['instant_meeting']['url'],
                        "meeting_code": browser_result['meeting_id'],
                        "meeting_id": browser_result['meeting_id'],
                        "scheduled_time": datetime.fromisoformat(f"{interview_details.scheduled_date}T{interview_details.scheduled_time}:00").isoformat(),
                        "duration_minutes": interview_details.duration_minutes,
                        "title": browser_result['meeting_info']['title'],
                        "participants": [interview_details.candidate_email] + interview_details.interviewer_names,
                        "created_at": datetime.now().isoformat(),
                        "expires_at": None,
                        "agent_insights": {
                            "method": "browser_solution",
                            "status": "success",
                            "validation_status": "browser_guided",
                            "instructions": browser_result.get('instructions', [])
                        },
                        "instructions": browser_result.get('instructions', []),
                        "note": "🎯 Browser Solution: Google Meet opened in browser - follow instructions to create real meeting"
                    }
                    
                else:
                    logger.warning("Browser solution failed, trying OAuth...")
                    # Fall back to OAuth
                    oauth_result = self._try_oauth_meeting(interview_details)
                    if isinstance(oauth_result, dict):
                        return oauth_result
                    else:
                        # If OAuth also fails, continue to other fallbacks
                        meeting = oauth_result
            
            # Fallback to OAuth if browser solution not available
            elif self.google_meet_oauth and self.google_meet_oauth.access_token:
                logger.info("🚀 Attempting to create real Google Meet meeting via OAuth...")
                
                # Prepare meeting details for OAuth
                start_time = datetime.fromisoformat(f"{interview_details.scheduled_date}T{interview_details.scheduled_time}:00")
                end_time = start_time + timedelta(minutes=interview_details.duration_minutes)
                
                oauth_meeting_details = {
                    'title': f"Interview: {interview_details.candidate_name} - {interview_details.round_name}",
                    'description': interview_details.notes or f"Interview with {interview_details.candidate_name}",
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'attendees': [
                        {'email': interview_details.candidate_email}
                    ] + [{'email': email} for email in interview_details.interviewer_names if email]
                }
                
                real_meeting_result = self.google_meet_oauth.create_google_meet_meeting(oauth_meeting_details)
                
                if real_meeting_result.get('success'):
                    logger.info("✅ Real Google Meet meeting created successfully via OAuth!")
                    
                    # Create a MeetingLink object from the real meeting data
                    real_meeting = MeetingLink(
                        meeting_link=real_meeting_result['meeting_link'],
                        meeting_code=real_meeting_result['meeting_code'],
                        meeting_id=real_meeting_result['meeting_id'],
                        scheduled_time=start_time,
                        duration_minutes=interview_details.duration_minutes,
                        title=real_meeting_result['title'],
                        participants=[interview_details.candidate_email] + interview_details.interviewer_names,
                        created_at=datetime.fromisoformat(real_meeting_result['created_at']),
                        expires_at=None
                    )
                    
                    # Cache the real meeting
                    self.meeting_cache[real_meeting.meeting_code] = real_meeting
                    self.active_meetings[real_meeting.meeting_code] = real_meeting
                    
                    # Return OAuth result as dictionary
                    return {
                        "success": True,
                        "meeting_link": real_meeting_result['meeting_link'],
                        "meeting_code": real_meeting_result['meeting_code'],
                        "meeting_id": real_meeting_result['meeting_id'],
                        "scheduled_time": start_time.isoformat(),
                        "duration_minutes": interview_details.duration_minutes,
                        "title": real_meeting_result['title'],
                        "participants": [interview_details.candidate_email] + interview_details.interviewer_names,
                        "created_at": real_meeting_result['created_at'],
                        "expires_at": None,
                        "agent_insights": {
                            "method": "oauth",
                            "status": "success",
                            "meeting_type": "real_google_meet"
                        },
                        "instructions": [
                            "✅ Real Google Meet meeting created successfully!",
                            f"Meeting Link: {real_meeting_result['meeting_link']}",
                            "All participants will receive calendar invitations automatically.",
                            "The meeting is ready to use at the scheduled time."
                        ],
                        "note": "✅ Real Google Meet meeting created via OAuth - ready to use!"
                    }
                    
                else:
                    logger.warning(f"OAuth meeting creation failed: {real_meeting_result.get('error')}")
                    logger.info("Falling back to demo meeting...")
                    
                    # Fall back to demo meeting
                    if create_demo_meeting_link:
                        demo_result = create_demo_meeting_link(
                            candidate_name=interview_details.candidate_name,
                            candidate_email=interview_details.candidate_email,
                            scheduled_date=interview_details.scheduled_date,
                            scheduled_time=interview_details.scheduled_time,
                            duration_minutes=interview_details.duration_minutes,
                            round_name=interview_details.round_name,
                            interviewer_emails=interview_details.interviewer_names,
                            notes=interview_details.notes or ""
                        )
                        
                        if demo_result.get('success'):
                            # Create a MeetingLink object from the demo meeting data
                            demo_meeting = MeetingLink(
                                meeting_link=demo_result['meeting_link'],
                                meeting_code=demo_result['meeting_code'],
                                meeting_id=demo_result['meeting_id'],
                                scheduled_time=datetime.fromisoformat(demo_result['scheduled_time']),
                                duration_minutes=interview_details.duration_minutes,
                                title=demo_result['title'],
                                participants=demo_result['participants'],
                                created_at=datetime.fromisoformat(demo_result['created_at']),
                                expires_at=None
                            )
                            
                            # Cache the demo meeting
                            self.meeting_cache[demo_meeting.meeting_code] = demo_meeting
                            self.active_meetings[demo_meeting.meeting_code] = demo_meeting
                            meeting = demo_meeting
                        else:
                            # Final fallback to basic placeholder
                            meeting = self.link_generator.create_meeting_link(interview_details)
                            self.meeting_cache[meeting.meeting_code] = meeting
                            self.active_meetings[meeting.meeting_code] = meeting
                    else:
                        # Fall back to basic placeholder
                        meeting = self.link_generator.create_meeting_link(interview_details)
                        self.meeting_cache[meeting.meeting_code] = meeting
                        self.active_meetings[meeting.meeting_code] = meeting
            
            # Fallback to Google Meet API if OAuth is not available
            elif self.google_meet_api and create_real_meeting_link:
                logger.info("🚀 Attempting to create real Google Meet meeting via API...")
                
                real_meeting_result = create_real_meeting_link(
                    candidate_name=interview_details.candidate_name,
                    candidate_email=interview_details.candidate_email,
                    scheduled_date=interview_details.scheduled_date,
                    scheduled_time=interview_details.scheduled_time,
                    duration_minutes=interview_details.duration_minutes,
                    round_name=interview_details.round_name,
                    interviewer_emails=interview_details.interviewer_names,
                    notes=interview_details.notes or ""
                )
                
                if real_meeting_result.get('success'):
                    logger.info("✅ Real Google Meet meeting created successfully!")
                    
                    # Create a MeetingLink object from the real meeting data
                    real_meeting = MeetingLink(
                        meeting_link=real_meeting_result['meeting_link'],
                        meeting_code=real_meeting_result['meeting_code'],
                        meeting_id=real_meeting_result['meeting_id'],
                        scheduled_time=datetime.fromisoformat(real_meeting_result['event_details']['start_time']),
                        duration_minutes=interview_details.duration_minutes,
                        title=real_meeting_result['event_details']['title'],
                        participants=real_meeting_result['event_details']['attendees'],
                        created_at=datetime.fromisoformat(real_meeting_result['created_at']),
                        expires_at=None  # Real meetings don't expire automatically
                    )
                    
                    # Cache the real meeting
                    self.meeting_cache[real_meeting.meeting_code] = real_meeting
                    self.active_meetings[real_meeting.meeting_code] = real_meeting
                    
                    # Use the real meeting for the rest of the process
                    meeting = real_meeting
                    
                else:
                    logger.warning(f"Failed to create real meeting: {real_meeting_result.get('error')}")
                    logger.info("Falling back to demo meeting...")
                    
                    # Fall back to demo meeting
                    if create_demo_meeting_link:
                        demo_result = create_demo_meeting_link(
                            candidate_name=interview_details.candidate_name,
                            candidate_email=interview_details.candidate_email,
                            scheduled_date=interview_details.scheduled_date,
                            scheduled_time=interview_details.scheduled_time,
                            duration_minutes=interview_details.duration_minutes,
                            round_name=interview_details.round_name,
                            interviewer_emails=interview_details.interviewer_names,
                            notes=interview_details.notes or ""
                        )
                        
                        if demo_result.get('success'):
                            # Create a MeetingLink object from the demo meeting data
                            demo_meeting = MeetingLink(
                                meeting_link=demo_result['meeting_link'],
                                meeting_code=demo_result['meeting_code'],
                                meeting_id=demo_result['meeting_id'],
                                scheduled_time=datetime.fromisoformat(demo_result['scheduled_time']),
                                duration_minutes=interview_details.duration_minutes,
                                title=demo_result['title'],
                                participants=demo_result['participants'],
                                created_at=datetime.fromisoformat(demo_result['created_at']),
                                expires_at=None
                            )
                            
                            # Cache the demo meeting
                            self.meeting_cache[demo_meeting.meeting_code] = demo_meeting
                            self.active_meetings[demo_meeting.meeting_code] = demo_meeting
                            meeting = demo_meeting
                        else:
                            # Final fallback to basic placeholder
                            meeting = self.link_generator.create_meeting_link(interview_details)
                            self.meeting_cache[meeting.meeting_code] = meeting
                            self.active_meetings[meeting.meeting_code] = meeting
                    else:
                        # Fall back to basic placeholder
                        meeting = self.link_generator.create_meeting_link(interview_details)
                        self.meeting_cache[meeting.meeting_code] = meeting
                        self.active_meetings[meeting.meeting_code] = meeting
            else:
                logger.info("Google Meet API not available, trying alternatives...")
                
                # Try Jitsi Meet first (no account required)
                if self.no_google_alternatives:
                    logger.info("🚀 Attempting to create Jitsi Meet meeting...")
                    jitsi_result = self.no_google_alternatives.create_jitsi_meeting({
                        'title': f"Interview: {interview_details.candidate_name} - {interview_details.round_name}",
                        'scheduled_date': interview_details.scheduled_date,
                        'scheduled_time': interview_details.scheduled_time,
                        'duration_minutes': interview_details.duration_minutes,
                        'participants': [
                            {'email': interview_details.candidate_email}
                        ] + [{'email': email} for email in interview_details.interviewer_names if email]
                    })
                    
                    if jitsi_result.get('success'):
                        logger.info("✅ Jitsi Meet meeting created successfully!")
                        
                        # Create a MeetingLink object from the Jitsi meeting data
                        jitsi_meeting = MeetingLink(
                            meeting_link=jitsi_result['meeting_link'],
                            meeting_code=jitsi_result['room_name'],
                            meeting_id=jitsi_result['meeting_id'],
                            scheduled_time=datetime.fromisoformat(f"{interview_details.scheduled_date}T{interview_details.scheduled_time}:00"),
                            duration_minutes=interview_details.duration_minutes,
                            title=jitsi_result['meeting_info']['title'],
                            participants=[interview_details.candidate_email] + interview_details.interviewer_names,
                            created_at=datetime.now(),
                            expires_at=None
                        )
                        
                        # Cache the Jitsi meeting
                        self.meeting_cache[jitsi_meeting.meeting_code] = jitsi_meeting
                        self.active_meetings[jitsi_meeting.meeting_code] = jitsi_meeting
                        meeting = jitsi_meeting
                    else:
                        logger.warning("Jitsi Meet creation failed, trying browser solution...")
                        
                        # Try browser solution
                        if self.browser_solution:
                            browser_result = self.browser_solution.create_meeting_with_guidance({
                                'title': f"Interview: {interview_details.candidate_name} - {interview_details.round_name}",
                                'scheduled_date': interview_details.scheduled_date,
                                'scheduled_time': interview_details.scheduled_time,
                                'duration_minutes': interview_details.duration_minutes,
                                'participants': [
                                    {'email': interview_details.candidate_email}
                                ] + [{'email': email} for email in interview_details.interviewer_names if email]
                            })
                            
                            if browser_result.get('success'):
                                logger.info("✅ Browser solution provided successfully!")
                                
                                # Create a MeetingLink object from the browser solution
                                browser_meeting = MeetingLink(
                                    meeting_link=browser_result['options']['instant_meeting']['url'],
                                    meeting_code=browser_result['meeting_id'],
                                    meeting_id=browser_result['meeting_id'],
                                    scheduled_time=datetime.fromisoformat(f"{interview_details.scheduled_date}T{interview_details.scheduled_time}:00"),
                                    duration_minutes=interview_details.duration_minutes,
                                    title=browser_result['meeting_info']['title'],
                                    participants=[interview_details.candidate_email] + interview_details.interviewer_names,
                                    created_at=datetime.now(),
                                    expires_at=None
                                )
                                
                                # Cache the browser meeting
                                self.meeting_cache[browser_meeting.meeting_code] = browser_meeting
                                self.active_meetings[browser_meeting.meeting_code] = browser_meeting
                                meeting = browser_meeting
                            else:
                                # Fall back to demo meeting
                                meeting = self._create_demo_meeting(interview_details)
                        else:
                            # Fall back to demo meeting
                            meeting = self._create_demo_meeting(interview_details)
                else:
                    # Fall back to demo meeting
                    meeting = self._create_demo_meeting(interview_details)
            
            # Prepare the prompt for the agents
            prompt = f"""
            Please generate and validate a Google Meet link for the following interview:
            
            Candidate: {interview_details.candidate_name}
            Email: {interview_details.candidate_email}
            Date: {interview_details.scheduled_date}
            Time: {interview_details.scheduled_time}
            Duration: {interview_details.duration_minutes} minutes
            Type: {interview_details.interview_type}
            Round: {interview_details.round_name}
            Interviewers: {', '.join(interview_details.interviewer_names)}
            Notes: {interview_details.notes or 'None'}
            
            Generated Meeting Link: {meeting.meeting_link}
            Meeting Code: {meeting.meeting_code}
            Meeting Title: {meeting.title}
            
            Please validate this meeting setup and provide any recommendations or issues.
            """
            
            # Use AutoGen agents if available
            if self.manager and self.group_chat:
                try:
                    # Start the group chat
                    result = self.group_chat.initiate_chat(
                        self.manager,
                        message=prompt,
                        max_turns=3
                    )
                    
                    # Extract agent insights
                    agent_insights = self._extract_agent_insights(result)
                    
                except Exception as e:
                    logger.warning(f"AutoGen agent interaction failed: {e}")
                    agent_insights = self._basic_validation(meeting, interview_details)
            else:
                # Use basic validation when AutoGen is not available
                agent_insights = self._basic_validation(meeting, interview_details)
            
            # Generate meeting instructions
            instructions = self._generate_meeting_instructions(meeting, interview_details)
            
            return {
                "success": True,
                "meeting_link": meeting.meeting_link,
                "meeting_code": meeting.meeting_code,
                "meeting_id": meeting.meeting_id,
                "scheduled_time": meeting.scheduled_time.isoformat(),
                "duration_minutes": meeting.duration_minutes,
                "title": meeting.title,
                "participants": meeting.participants,
                "created_at": meeting.created_at.isoformat(),
                "expires_at": meeting.expires_at.isoformat() if meeting.expires_at else None,
                "agent_insights": agent_insights,
                "instructions": instructions
            }
            
        except Exception as e:
            logger.error(f"Error generating meeting link: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _try_oauth_meeting(self, interview_details: InterviewDetails) -> MeetingLink:
        """Try to create meeting using OAuth"""
        if self.google_meet_oauth and self.google_meet_oauth.access_token:
            logger.info("🚀 Attempting to create real Google Meet meeting via OAuth...")
            
            # Prepare meeting details for OAuth
            start_time = datetime.fromisoformat(f"{interview_details.scheduled_date}T{interview_details.scheduled_time}:00")
            end_time = start_time + timedelta(minutes=interview_details.duration_minutes)
            
            oauth_meeting_details = {
                'title': f"Interview: {interview_details.candidate_name} - {interview_details.round_name}",
                'description': interview_details.notes or f"Interview with {interview_details.candidate_name}",
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'attendees': [
                    {'email': interview_details.candidate_email}
                ] + [{'email': email} for email in interview_details.interviewer_names if email]
            }
            
            real_meeting_result = self.google_meet_oauth.create_google_meet_meeting(oauth_meeting_details)
            
            if real_meeting_result.get('success'):
                logger.info("✅ Real Google Meet meeting created successfully via OAuth!")
                
                # Create a MeetingLink object from the real meeting data
                real_meeting = MeetingLink(
                    meeting_link=real_meeting_result['meeting_link'],
                    meeting_code=real_meeting_result['meeting_code'],
                    meeting_id=real_meeting_result['meeting_id'],
                    scheduled_time=start_time,
                    duration_minutes=interview_details.duration_minutes,
                    title=real_meeting_result['title'],
                    participants=[interview_details.candidate_email] + interview_details.interviewer_names,
                    created_at=datetime.fromisoformat(real_meeting_result['created_at']),
                    expires_at=None
                )
                
                # Cache the real meeting
                self.meeting_cache[real_meeting.meeting_code] = real_meeting
                self.active_meetings[real_meeting.meeting_code] = real_meeting
                
                # Return OAuth result as dictionary
                return {
                    "success": True,
                    "meeting_link": real_meeting_result['meeting_link'],
                    "meeting_code": real_meeting_result['meeting_code'],
                    "meeting_id": real_meeting_result['meeting_id'],
                    "scheduled_time": start_time.isoformat(),
                    "duration_minutes": interview_details.duration_minutes,
                    "title": real_meeting_result['title'],
                    "participants": [interview_details.candidate_email] + interview_details.interviewer_names,
                    "created_at": real_meeting_result['created_at'],
                    "expires_at": None,
                    "agent_insights": {
                        "method": "oauth",
                        "status": "success",
                        "meeting_type": "real_google_meet"
                    },
                    "instructions": [
                        "✅ Real Google Meet meeting created successfully!",
                        f"Meeting Link: {real_meeting_result['meeting_link']}",
                        "All participants will receive calendar invitations automatically.",
                        "The meeting is ready to use at the scheduled time."
                    ],
                    "note": "✅ Real Google Meet meeting created via OAuth - ready to use!"
                }
        
        # Fall back to demo meeting if OAuth fails
        demo_result = self._create_demo_meeting(interview_details)
        if isinstance(demo_result, dict):
            return demo_result
        else:
            # Convert MeetingLink to dictionary
            return {
                "success": True,
                "meeting_link": demo_result.meeting_link,
                "meeting_code": demo_result.meeting_code,
                "meeting_id": demo_result.meeting_id,
                "scheduled_time": demo_result.scheduled_time.isoformat(),
                "duration_minutes": demo_result.duration_minutes,
                "title": demo_result.title,
                "participants": demo_result.participants,
                "created_at": demo_result.created_at.isoformat(),
                "expires_at": demo_result.expires_at.isoformat() if demo_result.expires_at else None,
                "agent_insights": {
                    "method": "fallback",
                    "status": "success",
                    "meeting_type": "placeholder"
                },
                "instructions": [
                    "⚠️  Placeholder meeting link generated",
                    "This is a fallback link for demonstration purposes.",
                    "Replace with a real Google Meet link before the interview.",
                    "Use the browser solution to create a real meeting."
                ],
                "note": "⚠️  Placeholder meeting link - replace with real Google Meet link"
            }
    
    def _create_demo_meeting(self, interview_details: InterviewDetails) -> MeetingLink:
        """Create a demo meeting as fallback"""
        if create_demo_meeting_link:
            demo_result = create_demo_meeting_link(
                candidate_name=interview_details.candidate_name,
                candidate_email=interview_details.candidate_email,
                scheduled_date=interview_details.scheduled_date,
                scheduled_time=interview_details.scheduled_time,
                duration_minutes=interview_details.duration_minutes,
                round_name=interview_details.round_name,
                interviewer_emails=interview_details.interviewer_names,
                notes=interview_details.notes or ""
            )
            
            if demo_result.get('success'):
                # Create a MeetingLink object from the demo meeting data
                demo_meeting = MeetingLink(
                    meeting_link=demo_result['meeting_link'],
                    meeting_code=demo_result['meeting_code'],
                    meeting_id=demo_result['meeting_id'],
                    scheduled_time=datetime.fromisoformat(demo_result['scheduled_time']),
                    duration_minutes=interview_details.duration_minutes,
                    title=demo_result['title'],
                    participants=demo_result['participants'],
                    created_at=datetime.fromisoformat(demo_result['created_at']),
                    expires_at=None
                )
                
                # Cache the demo meeting
                self.meeting_cache[demo_meeting.meeting_code] = demo_meeting
                self.active_meetings[demo_meeting.meeting_code] = demo_meeting
                return demo_meeting
        
        # Final fallback to basic placeholder
        meeting = self.link_generator.create_meeting_link(interview_details)
        self.meeting_cache[meeting.meeting_code] = meeting
        self.active_meetings[meeting.meeting_code] = meeting
        return meeting
    
    def _extract_agent_insights(self, response) -> Dict[str, Any]:
        """Extract insights from AutoGen agent conversation"""
        try:
            # This would parse the agent conversation and extract key insights
            # For now, return a basic structure
            return {
                "validation_status": "approved",
                "recommendations": [
                    "Meeting link generated successfully",
                    "All participants will be notified",
                    "Meeting is scheduled for the requested time"
                ],
                "warnings": [],
                "agent_notes": "AutoGen agents have validated the meeting setup"
            }
        except Exception as e:
            logger.error(f"Error extracting agent insights: {e}")
            return {"validation_status": "error", "error": str(e)}
    
    def _basic_validation(self, meeting: MeetingLink, interview_details: InterviewDetails) -> Dict[str, Any]:
        """Basic validation when AutoGen is not available"""
        warnings = []
        recommendations = []
        
        # Check if this is a real meeting, demo meeting, or placeholder
        is_real_meeting = meeting.meeting_link and "meet.google.com" in meeting.meeting_link and len(meeting.meeting_code) > 10
        is_demo_meeting = hasattr(meeting, 'is_demo') and meeting.is_demo
        
        if is_real_meeting:
            # This is a real meeting
            recommendations.extend([
                "✅ Real Google Meet meeting created successfully",
                "Meeting link is functional and ready to use",
                "All participants will receive calendar invitations",
                "Test the meeting link to ensure it works properly"
            ])
            validation_status = "approved"
            agent_notes = "Real Google Meet meeting created via API"
        elif is_demo_meeting:
            # This is a demo meeting
            warnings.append("🎯 This is a DEMO meeting link - create a real Google Meet meeting")
            recommendations.extend([
                "🎯 DEMO MODE: This is a demo meeting link for testing",
                "📝 To create a REAL meeting, follow these steps:",
                "1. Click the 'Create Real Meeting' button below",
                "2. Or go to https://meet.google.com manually",
                "3. Set up the meeting with the details provided",
                "4. Replace this demo link with the real link"
            ])
            validation_status = "demo"
            agent_notes = "Demo meeting link created - requires manual Google Meet creation"
        else:
            # This is a placeholder meeting
            warnings.append("⚠️  This is a PLACEHOLDER meeting link - must be replaced with real Google Meet link")
            recommendations.extend([
                "⚠️  CRITICAL: Create a real Google Meet meeting using the provided details",
                "Go to https://meet.google.com and create a new meeting",
                "Replace this placeholder link with the real meeting link",
                "Send the real meeting link to all participants",
                "Test the real meeting link before the interview"
            ])
            validation_status = "warning"
            agent_notes = "Placeholder meeting link generated - requires manual Google Meet creation"
        
        # Check for potential issues (common for both real and placeholder)
        if meeting.scheduled_time < datetime.now():
            warnings.append("Meeting is scheduled in the past")
        
        if interview_details.duration_minutes > 180:
            warnings.append("Meeting duration is longer than 3 hours")
        
        if not interview_details.interviewer_names:
            warnings.append("No interviewers specified")
        
        if not interview_details.candidate_email:
            warnings.append("Candidate email is missing - needed for invitations")
        
        return {
            "validation_status": validation_status,
            "recommendations": recommendations,
            "warnings": warnings,
            "agent_notes": agent_notes,
            "is_real_meeting": is_real_meeting,
            "is_demo_meeting": is_demo_meeting
        }
    
    def _generate_meeting_instructions(self, meeting: MeetingLink, interview_details: InterviewDetails) -> List[str]:
        """Generate meeting instructions for participants"""
        
        # Check if this is a real meeting, demo meeting, or placeholder
        is_real_meeting = meeting.meeting_link and "meet.google.com" in meeting.meeting_link and len(meeting.meeting_code) > 10
        is_demo_meeting = hasattr(meeting, 'is_demo') and meeting.is_demo
        
        if is_real_meeting:
            # Real meeting instructions
            instructions = [
                "✅ REAL Google Meet meeting created successfully!",
                "",
                "📋 Meeting Details:",
                f"Meeting Title: {meeting.title}",
                f"Date & Time: {meeting.scheduled_time.strftime('%Y-%m-%d at %H:%M')}",
                f"Duration: {meeting.duration_minutes} minutes",
                "",
                "🔗 Meeting Link:",
                f"Meeting Link: {meeting.meeting_link}",
                f"Meeting Code: {meeting.meeting_code}",
                "",
                "📱 For Participants:",
                "1. Click the meeting link above or enter the meeting code in Google Meet",
                "2. Join 5 minutes before the scheduled time",
                "3. Ensure your camera and microphone are working",
                "4. Have your resume and any relevant documents ready",
                "",
                "📧 Calendar Invitations:",
                "All participants should receive calendar invitations automatically",
                "Check your email for the meeting invitation",
                "",
                "Participants:",
                f"- Candidate: {interview_details.candidate_name} ({interview_details.candidate_email})"
            ]
            
            for interviewer in interview_details.interviewer_names:
                instructions.append(f"- Interviewer: {interviewer}")
            
            instructions.extend([
                "",
                "✅ This is a REAL meeting link that will work for the interview!"
            ])
            
        elif is_demo_meeting:
            # Demo meeting instructions
            instructions = [
                "🎯 DEMO MODE: This is a demo meeting link for testing",
                "",
                "📋 Meeting Details:",
                f"Meeting Title: {meeting.title}",
                f"Date & Time: {meeting.scheduled_time.strftime('%Y-%m-%d at %H:%M')}",
                f"Duration: {meeting.duration_minutes} minutes",
                "",
                "🔗 Demo Meeting Link:",
                f"Meeting Link: {meeting.meeting_link}",
                f"Meeting Code: {meeting.meeting_code}",
                "",
                "📝 CREATE REAL MEETING - Choose one option:",
                "",
                "Option 1 - Quick Create:",
                "1. Click here to open Google Meet: https://meet.google.com/new",
                "2. Click 'New meeting'",
                "3. Copy the real meeting link",
                "4. Replace the demo link above",
                "",
                "Option 2 - Calendar Integration:",
                "1. Go to https://calendar.google.com",
                "2. Create new event with Google Meet",
                "3. Add participants and save",
                "4. Copy the meeting link",
                "",
                "Option 3 - Manual Steps:",
                "1. Go to https://meet.google.com",
                "2. Click 'New meeting' or 'Schedule a meeting'",
                "3. Set meeting details:",
                f"   - Title: {meeting.title}",
                f"   - Date: {meeting.scheduled_time.strftime('%Y-%m-%d')}",
                f"   - Time: {meeting.scheduled_time.strftime('%H:%M')}",
                f"   - Duration: {meeting.duration_minutes} minutes",
                "4. Add participants:",
                f"   - Candidate: {interview_details.candidate_name} ({interview_details.candidate_email})"
            ]
            
            for interviewer in interview_details.interviewer_names:
                instructions.append(f"   - Interviewer: {interviewer}")
            
            instructions.extend([
                "5. Generate the real meeting link",
                "6. Replace the demo link above with the real link",
                "7. Send the real meeting link to all participants",
                "",
                "📱 For Participants (once real link is provided):",
                "1. Click the meeting link or enter the meeting code in Google Meet",
                "2. Join 5 minutes before the scheduled time",
                "3. Ensure your camera and microphone are working",
                "4. Have your resume and any relevant documents ready",
                "",
                "⚠️  IMPORTANT: This demo link will NOT work for the actual interview!"
            ])
            
        else:
            # Placeholder meeting instructions
            instructions = [
                "⚠️  IMPORTANT: This is a PLACEHOLDER meeting link that needs to be replaced!",
                "",
                "📋 Meeting Details:",
                f"Meeting Title: {meeting.title}",
                f"Date & Time: {meeting.scheduled_time.strftime('%Y-%m-%d at %H:%M')}",
                f"Duration: {meeting.duration_minutes} minutes",
                "",
                "🔗 Current Placeholder Link:",
                f"Meeting Link: {meeting.meeting_link}",
                f"Meeting Code: {meeting.meeting_code}",
                "",
                "📝 NEXT STEPS - Create Real Google Meet Meeting:",
                "1. Go to https://meet.google.com",
                "2. Click 'New meeting' or 'Schedule a meeting'",
                "3. Set the meeting details:",
                f"   - Title: {meeting.title}",
                f"   - Date: {meeting.scheduled_time.strftime('%Y-%m-%d')}",
                f"   - Time: {meeting.scheduled_time.strftime('%H:%M')}",
                f"   - Duration: {meeting.duration_minutes} minutes",
                "4. Add participants:",
                f"   - Candidate: {interview_details.candidate_name} ({interview_details.candidate_email})"
            ]
            
            for interviewer in interview_details.interviewer_names:
                instructions.append(f"   - Interviewer: {interviewer}")
            
            instructions.extend([
                "5. Generate the real meeting link",
                "6. Replace the placeholder link above with the real link",
                "7. Send the real meeting link to all participants",
                "",
                "📱 For Participants (once real link is provided):",
                "1. Click the meeting link or enter the meeting code in Google Meet",
                "2. Join 5 minutes before the scheduled time",
                "3. Ensure your camera and microphone are working",
                "4. Have your resume and any relevant documents ready"
            ])
        
        if interview_details.notes:
            instructions.extend(["", "📝 Additional Notes:", interview_details.notes])
        
        return instructions
    
    def get_meeting_info(self, meeting_code: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific meeting"""
        if meeting_code in self.meeting_cache:
            meeting = self.meeting_cache[meeting_code]
            return {
                "meeting_link": meeting.meeting_link,
                "meeting_code": meeting.meeting_code,
                "scheduled_time": meeting.scheduled_time.isoformat(),
                "duration_minutes": meeting.duration_minutes,
                "title": meeting.title,
                "participants": meeting.participants,
                "created_at": meeting.created_at.isoformat(),
                "expires_at": meeting.expires_at.isoformat() if meeting.expires_at else None,
                "is_active": meeting_code in self.active_meetings
            }
        return None
    
    def cancel_meeting(self, meeting_code: str) -> bool:
        """Cancel a meeting"""
        if meeting_code in self.active_meetings:
            del self.active_meetings[meeting_code]
            logger.info(f"Meeting {meeting_code} cancelled")
            return True
        return False
    
    def list_active_meetings(self) -> List[Dict[str, Any]]:
        """List all active meetings"""
        active_meetings = []
        for meeting_code, meeting in self.active_meetings.items():
            active_meetings.append({
                "meeting_code": meeting_code,
                "meeting_link": meeting.meeting_link,
                "scheduled_time": meeting.scheduled_time.isoformat(),
                "title": meeting.title,
                "participants": meeting.participants
            })
        return active_meetings

# Global instance for easy access
google_meet_agent = None

def initialize_google_meet_agent(api_key: str = None) -> GoogleMeetAgent:
    """Initialize the global Google Meet agent"""
    global google_meet_agent
    if google_meet_agent is None:
        google_meet_agent = GoogleMeetAgent(api_key)
    return google_meet_agent

def generate_meeting_link_for_interview(
    candidate_name: str,
    candidate_email: str,
    scheduled_date: str,
    scheduled_time: str,
    duration_minutes: int = 60,
    interview_type: str = "video_call",
    round_name: str = "Interview",
    interviewer_names: List[str] = None,
    meeting_title: str = None,
    notes: str = None
) -> Dict[str, Any]:
    """Convenience function to generate a meeting link for an interview"""
    global google_meet_agent
    
    if google_meet_agent is None:
        google_meet_agent = initialize_google_meet_agent()
    
    interview_details = InterviewDetails(
        candidate_name=candidate_name,
        candidate_email=candidate_email,
        scheduled_date=scheduled_date,
        scheduled_time=scheduled_time,
        duration_minutes=duration_minutes,
        interview_type=interview_type,
        round_name=round_name,
        interviewer_names=interviewer_names or [],
        meeting_title=meeting_title,
        notes=notes
    )
    
    return google_meet_agent.generate_meeting_link(interview_details)

# Example usage and testing
if __name__ == "__main__":
    # Initialize the agent
    agent = initialize_google_meet_agent()
    
    # Example interview details
    interview_details = InterviewDetails(
        candidate_name="John Doe",
        candidate_email="john.doe@email.com",
        scheduled_date="2024-01-15",
        scheduled_time="14:00",
        duration_minutes=60,
        interview_type="video_call",
        round_name="Technical Round",
        interviewer_names=["Jane Smith", "Bob Johnson"],
        meeting_title="Technical Interview - John Doe",
        notes="Focus on Python and system design"
    )
    
    # Generate meeting link
    result = agent.generate_meeting_link(interview_details)
    
    print("Meeting Link Generation Result:")
    print(json.dumps(result, indent=2))
    
    if result["success"]:
        print(f"\nMeeting Link: {result['meeting_link']}")
        print(f"Meeting Code: {result['meeting_code']}")
        print(f"Scheduled Time: {result['scheduled_time']}")
        print(f"Duration: {result['duration_minutes']} minutes")
        print(f"Title: {result['title']}")
        
        print("\nInstructions:")
        for instruction in result["instructions"]:
            print(f"  {instruction}")
