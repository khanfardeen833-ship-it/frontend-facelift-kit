#!/usr/bin/env python3
"""
Demo: Dynamic Email Configuration
This script demonstrates how the system now dynamically uses email configuration from config.env
"""

import os
from dotenv import load_dotenv

def demo_dynamic_config():
    """Demonstrate dynamic email configuration"""
    
    print("🎯 Dynamic Email Configuration Demo")
    print("=" * 50)
    
    # Load current configuration
    load_dotenv('config.env')
    
    current_email = os.getenv('EMAIL_ADDRESS')
    current_password = os.getenv('EMAIL_PASSWORD')
    
    print(f"📧 Current HR Email: {current_email}")
    print(f"🔑 Password: {'*' * len(current_password) if current_password else 'Not set'}")
    
    print(f"\n🔄 How to Change HR Email:")
    print(f"1. Open config.env file")
    print(f"2. Update EMAIL_ADDRESS=your_new_hr_email@gmail.com")
    print(f"3. Update EMAIL_PASSWORD=your_new_app_password")
    print(f"4. Update HR_EMAIL=your_new_hr_email@gmail.com")
    print(f"5. Restart the server")
    
    print(f"\n✅ Benefits of Dynamic Configuration:")
    print(f"   • No hardcoded email addresses")
    print(f"   • Easy to change HR email")
    print(f"   • All components use the same email")
    print(f"   • Google Meet uses the configured email")
    print(f"   • Email notifications use the configured email")
    
    print(f"\n📋 Components that use the dynamic email:")
    print(f"   • Email sending (SMTP)")
    print(f"   • Google Meet creation")
    print(f"   • Interview notifications")
    print(f"   • HR notifications")
    print(f"   • All email-related features")
    
    print(f"\n🎉 System is now fully dynamic!")
    print(f"   Just update config.env and restart to change HR email")

if __name__ == "__main__":
    demo_dynamic_config()
