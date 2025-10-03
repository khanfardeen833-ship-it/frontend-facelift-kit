#!/usr/bin/env python3
"""
Google Meet OAuth Setup Script
This script helps you set up Google Meet OAuth credentials for your email account.
"""

import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

def setup_google_meet_oauth():
    """Setup Google Meet OAuth credentials"""
    
    print("🔧 Google Meet OAuth Setup")
    print("=" * 50)
    
    # Get email from environment
    email_address = os.getenv('EMAIL_ADDRESS', 'snlettings.data@gmail.com')
    print(f"📧 Email Address: {email_address}")
    
    print("\n📋 To set up Google Meet OAuth, follow these steps:")
    print("\n1. Go to Google Cloud Console:")
    print("   https://console.cloud.google.com/")
    
    print("\n2. Create a new project or select existing project")
    
    print("\n3. Enable Google Calendar API:")
    print("   - Go to 'APIs & Services' > 'Library'")
    print("   - Search for 'Google Calendar API'")
    print("   - Click 'Enable'")
    
    print("\n4. Create OAuth 2.0 credentials:")
    print("   - Go to 'APIs & Services' > 'Credentials'")
    print("   - Click 'Create Credentials' > 'OAuth 2.0 Client IDs'")
    print("   - Application type: 'Desktop application'")
    print("   - Name: 'HRMS Google Meet Integration'")
    print("   - Click 'Create'")
    
    print("\n5. Download the credentials JSON file")
    print("   - Click the download button next to your OAuth client")
    print("   - Save it as 'google_oauth_credentials.json' in the Backend directory")
    
    print("\n6. Update your config.env file with:")
    print(f"   GOOGLE_SERVICE_ACCOUNT_EMAIL={email_address}")
    
    print("\n7. Run the OAuth setup:")
    print("   python google_meet_oauth.py")
    
    print("\n⚠️  Important Notes:")
    print("- The OAuth flow will open a browser window")
    print("- You'll need to sign in with your Google account")
    print("- Grant permissions for Calendar access")
    print("- The system will save the tokens for future use")
    
    print(f"\n✅ Once set up, Google Meet meetings will be created using: {email_address}")
    
    # Check if credentials file exists
    credentials_file = "google_oauth_credentials.json"
    if os.path.exists(credentials_file):
        print(f"\n✅ Found credentials file: {credentials_file}")
        try:
            with open(credentials_file, 'r') as f:
                creds = json.load(f)
                client_id = creds.get('installed', {}).get('client_id', 'Not found')
                print(f"📋 Client ID: {client_id[:20]}...")
        except Exception as e:
            print(f"❌ Error reading credentials file: {e}")
    else:
        print(f"\n❌ Credentials file not found: {credentials_file}")
        print("   Please download and save the OAuth credentials file")
    
    # Check if tokens file exists
    tokens_file = "google_oauth_tokens.json"
    if os.path.exists(tokens_file):
        print(f"✅ Found tokens file: {tokens_file}")
        print("   OAuth setup appears to be complete!")
    else:
        print(f"❌ Tokens file not found: {tokens_file}")
        print("   Run 'python google_meet_oauth.py' to complete setup")

if __name__ == "__main__":
    setup_google_meet_oauth()
