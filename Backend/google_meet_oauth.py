#!/usr/bin/env python3
"""
Google Meet OAuth Integration
Simplified OAuth flow for creating real Google Meet meetings
"""

import os
import json
import webbrowser
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from urllib.parse import urlencode, parse_qs
import http.server
import socketserver
import threading
import time

class GoogleMeetOAuth:
    """Google Meet OAuth integration for creating real meetings"""
    
    def __init__(self, credentials_file: str = "google_oauth_credentials.json"):
        self.credentials_file = credentials_file
        self.credentials = None
        self.access_token = None
        self.refresh_token = None
        self.tokens_file = "google_oauth_tokens.json"
        self.redirect_port = 8080
        self.callback_server = None
        
        # Load credentials
        self.load_credentials()
        
    def load_credentials(self) -> bool:
        """Load OAuth credentials from file"""
        try:
            if os.path.exists(self.credentials_file):
                with open(self.credentials_file, 'r') as f:
                    self.credentials = json.load(f)
                
                # Extract client info
                web_config = self.credentials.get('web', {})
                self.client_id = web_config.get('client_id')
                self.client_secret = web_config.get('client_secret')
                self.redirect_uri = f"http://localhost:{self.redirect_port}/callback"
                
                print("✅ OAuth credentials loaded successfully")
                return True
            else:
                print(f"❌ Credentials file not found: {self.credentials_file}")
                print("💡 Please download your OAuth credentials from Google Developer Console")
                return False
                
        except Exception as e:
            print(f"❌ Failed to load credentials: {e}")
            return False
    
    def load_tokens(self) -> bool:
        """Load saved OAuth tokens"""
        try:
            if os.path.exists(self.tokens_file):
                with open(self.tokens_file, 'r') as f:
                    tokens = json.load(f)
                    self.access_token = tokens.get('access_token')
                    self.refresh_token = tokens.get('refresh_token')
                    
                    # Check if token is expired
                    if self.is_token_expired(tokens):
                        print("🔄 Access token expired, refreshing...")
                        return self.refresh_access_token()
                    
                    print("✅ OAuth tokens loaded successfully")
                    return True
        except Exception as e:
            print(f"❌ Failed to load tokens: {e}")
        return False
    
    def save_tokens(self, tokens: Dict[str, Any]):
        """Save OAuth tokens to file"""
        try:
            with open(self.tokens_file, 'w') as f:
                json.dump(tokens, f, indent=2)
            print("✅ OAuth tokens saved successfully")
        except Exception as e:
            print(f"❌ Failed to save tokens: {e}")
    
    def is_token_expired(self, tokens: Dict[str, Any]) -> bool:
        """Check if access token is expired"""
        expires_at = tokens.get('expires_at')
        if not expires_at:
            return True
        
        try:
            expires_time = datetime.fromisoformat(expires_at)
            return datetime.now() >= expires_time
        except:
            return True
    
    def get_authorization_url(self) -> str:
        """Get Google OAuth authorization URL"""
        if not self.credentials:
            raise Exception("OAuth credentials not loaded")
        
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'https://www.googleapis.com/auth/calendar',
            'response_type': 'code',
            'access_type': 'offline',
            'prompt': 'consent',
            'state': 'hrms_meet_integration'
        }
        
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
        return auth_url
    
    def start_callback_server(self) -> bool:
        """Start local server to receive OAuth callback"""
        try:
            class CallbackHandler(http.server.BaseHTTPRequestHandler):
                def do_GET(self):
                    if self.path.startswith('/callback'):
                        # Extract authorization code
                        query_params = parse_qs(self.path.split('?')[1] if '?' in self.path else '')
                        code = query_params.get('code', [None])[0]
                        state = query_params.get('state', [None])[0]
                        
                        if code and state == 'hrms_meet_integration':
                            # Send success response
                            self.send_response(200)
                            self.send_header('Content-type', 'text/html')
                            self.end_headers()
                            self.wfile.write(b'''
                            <html>
                                <body>
                                    <h1>Authorization Successful!</h1>
                                    <p>You can close this window and return to the application.</p>
                                    <script>setTimeout(() => window.close(), 3000);</script>
                                </body>
                            </html>
                            ''')
                            
                            # Store the code for processing
                            self.server.auth_code = code
                        else:
                            # Send error response
                            self.send_response(400)
                            self.send_header('Content-type', 'text/html')
                            self.end_headers()
                            self.wfile.write(b'''
                            <html>
                                <body>
                                    <h1>Authorization Failed</h1>
                                    <p>Please try again.</p>
                                </body>
                            </html>
                            ''')
                    else:
                        self.send_response(404)
                        self.end_headers()
                
                def log_message(self, format, *args):
                    pass  # Suppress log messages
            
            # Start server
            self.callback_server = socketserver.TCPServer(("", self.redirect_port), CallbackHandler)
            server_thread = threading.Thread(target=self.callback_server.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            
            print(f"✅ Callback server started on port {self.redirect_port}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start callback server: {e}")
            return False
    
    def stop_callback_server(self):
        """Stop the callback server"""
        if self.callback_server:
            self.callback_server.shutdown()
            self.callback_server.server_close()
            print("🔒 Callback server stopped")
    
    def exchange_code_for_tokens(self, authorization_code: str) -> bool:
        """Exchange authorization code for access and refresh tokens"""
        if not self.credentials:
            raise Exception("OAuth credentials not loaded")
        
        token_url = "https://oauth2.googleapis.com/token"
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': authorization_code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }
        
        try:
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            tokens = response.json()
            self.access_token = tokens['access_token']
            self.refresh_token = tokens.get('refresh_token')
            
            # Calculate expiration time
            expires_in = tokens.get('expires_in', 3600)
            expires_at = (datetime.now() + timedelta(seconds=expires_in)).isoformat()
            tokens['expires_at'] = expires_at
            
            # Save tokens
            self.save_tokens(tokens)
            
            print("✅ Successfully obtained OAuth tokens")
            return True
            
        except Exception as e:
            print(f"❌ Failed to exchange code for tokens: {e}")
            return False
    
    def refresh_access_token(self) -> bool:
        """Refresh the access token using refresh token"""
        if not self.refresh_token:
            print("❌ No refresh token available")
            return False
        
        if not self.credentials:
            raise Exception("OAuth credentials not loaded")
        
        token_url = "https://oauth2.googleapis.com/token"
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token'
        }
        
        try:
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            tokens = response.json()
            self.access_token = tokens['access_token']
            
            # Update saved tokens
            expires_in = tokens.get('expires_in', 3600)
            expires_at = (datetime.now() + timedelta(seconds=expires_in)).isoformat()
            
            updated_tokens = {
                'access_token': self.access_token,
                'refresh_token': self.refresh_token,
                'expires_at': expires_at
            }
            
            self.save_tokens(updated_tokens)
            
            print("✅ Access token refreshed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to refresh access token: {e}")
            return False
    
    def create_google_meet_meeting(self, meeting_details: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Google Meet meeting using Google Calendar API"""
        if not self.access_token:
            return {"success": False, "error": "No access token available. Please run OAuth flow first."}
        
        # Create calendar event with Google Meet
        event = {
            'summary': meeting_details.get('title', 'Interview Meeting'),
            'description': meeting_details.get('description', 'Interview session'),
            'start': {
                'dateTime': meeting_details['start_time'],
                'timeZone': 'UTC'
            },
            'end': {
                'dateTime': meeting_details['end_time'],
                'timeZone': 'UTC'
            },
            'attendees': meeting_details.get('attendees', []),
            'guestsCanInviteOthers': True,
            'guestsCanModify': False,
            'guestsCanSeeOtherGuests': True,
            'visibility': 'public',
            'anyoneCanAddSelf': True,
            'conferenceData': {
                'createRequest': {
                    'requestId': f"hrms-meet-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    'conferenceSolutionKey': {
                        'type': 'hangoutsMeet'
                    }
                }
            }
        }
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        url = "https://www.googleapis.com/calendar/v3/calendars/primary/events?conferenceDataVersion=1"
        
        try:
            response = requests.post(url, headers=headers, json=event)
            response.raise_for_status()
            
            event_data = response.json()
            
            # Extract Google Meet link
            conference_data = event_data.get('conferenceData', {})
            entry_points = conference_data.get('entryPoints', [])
            meet_link = entry_points[0].get('uri') if entry_points else None
            
            # Extract meeting code
            meeting_code = None
            if meet_link and 'meet.google.com' in meet_link:
                meeting_code = meet_link.split('/')[-1]
            
            return {
                "success": True,
                "meeting_link": meet_link,
                "meeting_id": event_data['id'],
                "meeting_code": meeting_code,
                "title": event_data['summary'],
                "created_at": datetime.now().isoformat(),
                "event_data": event_data,
                "agent_insights": {
                    "validation_status": "approved",
                    "is_real_meeting": True,
                    "is_demo": False,
                    "agent_notes": "Real Google Meet meeting created via OAuth integration"
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def setup_oauth_flow(self) -> bool:
        """Complete OAuth setup flow"""
        print("🚀 Starting Google OAuth Setup Flow")
        print("=" * 40)
        
        # Check if tokens already exist
        if self.load_tokens():
            print("✅ OAuth already configured and tokens are valid")
            return True
        
        # Check credentials
        if not self.credentials:
            print("❌ OAuth credentials not found")
            print("💡 Please follow the setup guide in GOOGLE_OAUTH_SETUP_GUIDE.md")
            return False
        
        # Start callback server
        if not self.start_callback_server():
            return False
        
        try:
            # Get authorization URL
            auth_url = self.get_authorization_url()
            
            print("📋 Step 1: Authorize the application")
            print(f"Opening browser to: {auth_url}")
            
            # Open browser
            webbrowser.open(auth_url)
            
            print("📋 Step 2: Complete authorization in browser")
            print("Waiting for authorization callback...")
            
            # Wait for callback
            timeout = 300  # 5 minutes
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                if hasattr(self.callback_server, 'auth_code'):
                    auth_code = self.callback_server.auth_code
                    break
                time.sleep(1)
            else:
                print("❌ Authorization timeout")
                return False
            
            print("✅ Authorization code received")
            
            # Exchange code for tokens
            if self.exchange_code_for_tokens(auth_code):
                print("🎉 OAuth setup completed successfully!")
                return True
            else:
                print("❌ Failed to exchange authorization code")
                return False
                
        finally:
            self.stop_callback_server()
    
    def test_meeting_creation(self) -> Dict[str, Any]:
        """Test meeting creation with sample data"""
        print("🧪 Testing Google Meet meeting creation...")
        
        # Sample meeting details
        start_time = datetime.now() + timedelta(hours=1)
        end_time = start_time + timedelta(minutes=60)
        
        meeting_details = {
            'title': 'Test Interview Meeting',
            'description': 'Test meeting created via OAuth integration',
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'attendees': [
                {'email': 'test@example.com'}
            ]
        }
        
        result = self.create_google_meet_meeting(meeting_details)
        
        if result['success']:
            print("✅ Test meeting created successfully!")
            print(f"  Meeting Link: {result['meeting_link']}")
            print(f"  Meeting Code: {result['meeting_code']}")
        else:
            print(f"❌ Test meeting creation failed: {result['error']}")
        
        return result

def main():
    """Main function for OAuth setup and testing"""
    oauth = GoogleMeetOAuth()
    
    # Setup OAuth flow
    if oauth.setup_oauth_flow():
        # Test meeting creation
        oauth.test_meeting_creation()
    else:
        print("❌ OAuth setup failed")
        print("💡 Please check the setup guide: GOOGLE_OAUTH_SETUP_GUIDE.md")

if __name__ == "__main__":
    main()
