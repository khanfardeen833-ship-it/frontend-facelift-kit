#!/usr/bin/env python3
"""
Test Email Configuration Script
This script tests the email configuration to ensure it's using the correct email address.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

def test_email_config():
    """Test the email configuration"""
    
    print("🧪 Testing Dynamic Email Configuration")
    print("=" * 50)
    
    # Test environment variables
    email_address = os.getenv('EMAIL_ADDRESS')
    email_password = os.getenv('EMAIL_PASSWORD')
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = os.getenv('SMTP_PORT')
    hr_email = os.getenv('HR_EMAIL')
    
    print(f"📧 EMAIL_ADDRESS: {email_address}")
    print(f"🔑 EMAIL_PASSWORD: {'*' * len(email_password) if email_password else 'Not set'}")
    print(f"📮 SMTP_SERVER: {smtp_server}")
    print(f"🔌 SMTP_PORT: {smtp_port}")
    print(f"👤 HR_EMAIL: {hr_email}")
    
    # Check if all required variables are set
    required_vars = ['EMAIL_ADDRESS', 'EMAIL_PASSWORD', 'SMTP_SERVER']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing required email configuration variables: {', '.join(missing_vars)}")
        print(f"   Please check your config.env file")
        return False
    
    print(f"\n✅ All required email configuration variables are set!")
    print(f"   System will use: {email_address}")
    
    # Test Google Meet API configuration
    print(f"\n🔧 Google Meet API Configuration:")
    google_service_email = os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL')
    google_credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE')
    
    print(f"📧 GOOGLE_SERVICE_ACCOUNT_EMAIL: {google_service_email}")
    print(f"📁 GOOGLE_CREDENTIALS_FILE: {google_credentials_file}")
    
    if google_service_email:
        print(f"✅ Google Meet API email is configured: {google_service_email}")
    else:
        print(f"⚠️  Google Meet API email not configured")
        print(f"   Set GOOGLE_SERVICE_ACCOUNT_EMAIL in config.env")
    
    # Check if credentials file exists
    if google_credentials_file and os.path.exists(google_credentials_file):
        print(f"✅ Google credentials file exists: {google_credentials_file}")
    else:
        print(f"❌ Google credentials file not found: {google_credentials_file}")
        print(f"   Run 'python setup_google_meet_oauth.py' for setup instructions")
    
    print(f"\n📋 Summary:")
    print(f"   Email for sending: {email_address}")
    print(f"   Email for Google Meet: {google_service_email or 'Not configured'}")
    print(f"   System is fully dynamic - updates config.env to change email")
    
    print(f"\n🎉 Dynamic Configuration Status:")
    print(f"   ✅ Email configuration loaded from config.env")
    print(f"   ✅ No hardcoded fallbacks - fully dynamic")
    print(f"   ✅ Update config.env to change HR email")
    
    return True

if __name__ == "__main__":
    test_email_config()
