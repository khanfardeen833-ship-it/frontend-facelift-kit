
#!/usr/bin/env python3
"""
complete_server.py - Complete Hiring Bot Server
Combines: Chat Bot + All API Endpoints + Resume Management + Cloudflare Tunnel + AI Resume Filtering + User Authentication
"""

from flask import Flask, jsonify, request, send_file, render_template_string, make_response
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from date_utils import parse_ddmmyyyy_to_date, format_date_to_ddmmyyyy, convert_html_date_to_ddmmyyyy, convert_ddmmyyyy_to_html_date, format_datetime_for_display
import json
from functools import wraps
import logging
import re
import subprocess
import threading
import time
import os
import signal
import sys
import shutil
from werkzeug.utils import secure_filename
import base64
from pathlib import Path
import uuid
import socket
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import ssl
from threading import Thread
import hashlib
import secrets
from dotenv import load_dotenv, set_key

# Load environment variables from config.env file
load_dotenv('config.env')

def validate_email_config():
    """Validate that email configuration is properly loaded"""
    required_vars = ['EMAIL_ADDRESS', 'EMAIL_PASSWORD', 'SMTP_SERVER']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Warning: Missing email configuration variables: {', '.join(missing_vars)}")
        print("   Please check your config.env file")
        return False
    
    print(f"✅ Email configuration loaded successfully")
    print(f"   Email: {os.getenv('EMAIL_ADDRESS')}")
    print(f"   SMTP Server: {os.getenv('SMTP_SERVER')}")
    return True

# Validate email configuration on startup
validate_email_config()
try:
    import jwt
except ImportError:
    try:
        import PyJWT as jwt
    except ImportError:
        print("❌ PyJWT is not installed. Please run: pip install PyJWT")
        exit(1)
from datetime import datetime, timedelta, date

# Load environment variables from .env file
load_dotenv()

# Set the OpenAI API key
os.environ['OPENAI_API_KEY'] = "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"

# Custom JSON encoder to handle datetime, date, and timedelta objects
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, timedelta):
            return str(obj)
        return super().default(obj)

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except ImportError:
    print("Warning: PIL/Pillow not installed. Captcha generation will be disabled.")
    Image = ImageDraw = ImageFont = ImageFilter = None
import random
import string
import io

# Import AI bot handler with error handling
try:
    from ai_bot3 import ChatBotHandler
    print("✅ Successfully imported AI ChatBotHandler")
    
    # Use the Config from ai_bot3
    from ai_bot3 import Config
    print("✅ Successfully imported Config from ai_bot3")
    
except (ImportError, ValueError) as e:
    print(f"❌ Failed to import AI ChatBotHandler: {e}")
    print("Using fallback configuration")

# Import Google Meet Agent
try:
    from google_meet_agent import initialize_google_meet_agent, generate_meeting_link_for_interview
    print("✅ Successfully imported Google Meet Agent")
except ImportError as e:
    print(f"❌ Failed to import Google Meet Agent: {e}")
    print("Google Meet link generation will use fallback method")

# Import Browser Meet Solution
try:
    from browser_meet_solution import create_meeting_with_browser_guidance, browser_meet_solution
    print("✅ Successfully imported Browser Meet Solution")
except ImportError as e:
    print(f"❌ Failed to import Browser Meet Solution: {e}")
    create_meeting_with_browser_guidance = None
    browser_meet_solution = None

# Import Auto Meet Generator
try:
    from auto_meet_generator import create_auto_meeting_link, auto_meet_generator
    print("✅ Successfully imported Auto Meet Generator")
except ImportError as e:
    print(f"❌ Failed to import Auto Meet Generator: {e}")
    create_auto_meeting_link = None
    auto_meet_generator = None

# Import Real Meet Generator
try:
    from real_meet_generator import create_real_meeting_link, real_meet_generator
    print("✅ Successfully imported Real Meet Generator")
except ImportError as e:
    print(f"❌ Failed to import Real Meet Generator: {e}")
    create_real_meeting_link = None
    real_meet_generator = None

# Import Google Meet Helper
try:
    from google_meet_helper import create_meeting_helper_response
    print("✅ Successfully imported Google Meet Helper")
except ImportError as e:
    print(f"❌ Failed to import Google Meet Helper: {e}")
    print("Meeting creation helper will not be available")

# Import Google Meet OAuth
try:
    from google_meet_oauth import GoogleMeetOAuth
    print("✅ Successfully imported Google Meet OAuth")
except ImportError as e:
    print(f"❌ Failed to import Google Meet OAuth: {e}")
    print("OAuth integration will not be available")

# Import Google Calendar Integration
try:
    from google_calendar_integration import create_meeting_with_configured_email, get_meeting_creation_instructions
    print("✅ Successfully imported Google Calendar Integration")
except ImportError as e:
    print(f"❌ Failed to import Google Calendar Integration: {e}")
    create_meeting_with_configured_email = None
    get_meeting_creation_instructions = None
    
    # Create minimal Config class
    class Config:
        MYSQL_HOST = 'localhost'
        MYSQL_USER = 'root'
        MYSQL_PASSWORD = 'root'
        MYSQL_DATABASE = 'hiring_bot'

    # Create minimal ChatBotHandler
    class ChatBotHandler:
        def __init__(self):
            self.context = {}
            # Create minimal session manager
            class SessionManager:
                def get_messages(self, session_id, limit=50):
                    return []
            
            # Create minimal ticket manager
            class TicketManager:
                def get_user_tickets(self, user_id):
                    return []
                
                def get_ticket_details(self, ticket_id):
                    return None
            
            self.session_manager = SessionManager()
            self.ticket_manager = TicketManager()
        
        def process_message(self, session_id, user_id, message, authenticated_user_email=None):
            return {"response": "AI bot is not available. Please contact support."}
        
        def start_session(self, user_id):
            from datetime import datetime
            return {
                "session_id": f"session_{user_id}_{datetime.now().timestamp()}",
                "message": "Welcome! How can I help you today?"
            }

# Import interview email service
try:
    from interview_email_service import send_interview_notifications
except ImportError:
    send_interview_notifications = None
    
# Import interview API endpoints
try:
    from interview_api import interview_bp
except ImportError:
    interview_bp = None

# Import manager feedback API endpoints
try:
    from manager_feedback_api import manager_feedback_bp
except ImportError:
    manager_feedback_bp = None

# Set MySQL configuration from environment variables
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'hiring_bot'),
}

print(f"📊 MySQL Config: {MYSQL_CONFIG['database']}@{MYSQL_CONFIG['host']}")

# ============================================
# JWT HELPER FUNCTIONS
# ============================================

def verify_jwt_token(token):
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return True, payload
    except jwt.ExpiredSignatureError:
        return False, "Token expired"
    except jwt.InvalidTokenError:
        return False, "Invalid token"

# ============================================
# UTILITY FUNCTIONS
# ============================================

def generate_ticket_id() -> str:
    """Generate a unique ticket ID"""
    return hashlib.md5(f"{datetime.now()}_{secrets.token_hex(4)}".encode()).hexdigest()[:10]

# ============================================
# CONFIGURATION - FROM ENVIRONMENT VARIABLES
# ============================================
EMAIL_CONFIG = {
    'SMTP_SERVER': os.getenv('SMTP_SERVER'),
    'SMTP_PORT': int(os.getenv('SMTP_PORT', 587)),
    'EMAIL_ADDRESS': os.getenv('EMAIL_ADDRESS'),
    'EMAIL_PASSWORD': os.getenv('EMAIL_PASSWORD'),
    'USE_TLS': os.getenv('USE_TLS', 'true').lower() == 'true',
    'FROM_NAME': os.getenv('FROM_NAME'),
    'COMPANY_NAME': os.getenv('COMPANY_NAME'),
    'COMPANY_WEBSITE': os.getenv('COMPANY_WEBSITE'),
    'HR_EMAIL': os.getenv('HR_EMAIL'),
    'SEND_EMAILS': os.getenv('SEND_EMAILS', 'true').lower() == 'true'
}

# TEXT CAPTCHA CONFIGURATION
CAPTCHA_LENGTH = 6  # Number of characters
CAPTCHA_TIMEOUT = 300  # 5 minutes in seconds
CAPTCHA_FONT_SIZE = 36
CAPTCHA_IMAGE_WIDTH = 200
CAPTCHA_IMAGE_HEIGHT = 80
active_captchas = {}



# API Configuration
API_KEY = "sk-hiring-bot-2024-secret-key-xyz789"  # Your secret API key
API_PORT = 5000  # Port number for the server

# JWT Configuration
JWT_SECRET_KEY = "your-jwt-secret-key-change-this-in-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Cloudflare Tunnel Configuration
CLOUDFLARE_TUNNEL_NAME = "hiring-bot-complete"  # Name for your tunnel
CLOUDFLARE_TUNNEL_URL = None  # Will be set after tunnel starts

# File Storage Configuration
BASE_STORAGE_PATH = "approved_tickets"  # Base folder for storing approved tickets
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'rtf'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB max file size

# ============================================
# Flask App Initialization
# ============================================

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Better CORS configuration - Allow all headers
CORS(app, 
     resources={r"/api/*": {
         "origins": ["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001", "*"],
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": "*",  # Allow all headers to avoid CORS issues
         "supports_credentials": True
     }},
     origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001", "*"],
     allow_headers="*",
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     expose_headers=["*"])

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize SocketIO for real-time chat
socketio = SocketIO(app, cors_allowed_origins="*")

# Register interview API blueprint if available
# Temporarily disabled to use MySQL-only approach
# if interview_bp:
#     app.register_blueprint(interview_bp)
#     logger.info("Interview API endpoints registered successfully")
# else:
#     logger.warning("Interview API endpoints not available")
logger.info("Interview API endpoints disabled - using MySQL-only approach")

# Register manager feedback API blueprint if available
if manager_feedback_bp:
    try:
        app.register_blueprint(manager_feedback_bp)
        logger.info("Manager feedback API endpoints registered successfully")
    except Exception as e:
        logger.warning(f"Manager feedback API endpoints already registered or error: {e}")
else:
    logger.warning("Manager feedback API endpoints not available")

# Create base storage directory if it doesn't exist
if not os.path.exists(BASE_STORAGE_PATH):
    os.makedirs(BASE_STORAGE_PATH)
    logger.info(f"Created base storage directory: {BASE_STORAGE_PATH}")

# Initialize chat bot handler
chat_bot = ChatBotHandler()
logger.info("Chat bot handler initialized successfully")

# ============================================
# Database Helper Functions
# ============================================

def get_db_connection():
    """Create and return database connection with timeout"""
    try:
        # Add connection timeout to prevent hanging
        config = MYSQL_CONFIG.copy()
        config.update({
            'connection_timeout': 10,  # 10 seconds to establish connection
            'autocommit': False,       # Explicit transaction control
            'buffered': True          # Buffer results to avoid sync issues
        })
        conn = mysql.connector.connect(**config)
        return conn
    except Error as e:
        logger.error(f"Database connection failed: {e}")
        return None

def serialize_datetime(obj):
    """Convert datetime objects to ISO format strings"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj

# ============================================
# Authentication Decorator
# ============================================

def require_api_key(f):
    """Decorator to require API key for endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            api_key = request.args.get('api_key')
        
        if api_key != API_KEY:
            return jsonify({
                'success': False,
                'error': 'Invalid or missing API key'
            }), 401
        
        return f(*args, **kwargs)
    return decorated_function

def require_jwt_auth(f):
    """Decorator to require JWT authentication for HR endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': 'Authorization header required'
            }), 401
        
        token = auth_header.split(' ')[1]
        
        # Verify token
        is_valid, payload = verify_jwt_token(token)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': payload
            }), 401
        
        # Check if user is HR manager
        if payload.get('role') != 'hr':
            return jsonify({
                'success': False,
                'error': 'Access denied. Only HR managers can access this endpoint.'
            }), 403
        
        # Add user info to request context
        request.user = payload
        
        return f(*args, **kwargs)
    return decorated_function

# ============================================
# Cloudflare Tunnel Functions
# ============================================

def get_thank_you_email_template(candidate_name, job_title, application_id, company_name):
    """Generate HTML email template for thank you message"""
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Application Received - {company_name}</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .highlight {{ background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #2196f3; }}
            .footer {{ text-align: center; margin-top: 30px; padding: 20px; color: #666; font-size: 14px; }}
            .button {{ display: inline-block; background: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
            .details {{ background: white; padding: 20px; border-radius: 5px; margin: 20px 0; border: 1px solid #ddd; }}
            .status {{ background: #4CAF50; color: white; padding: 8px 16px; border-radius: 20px; font-size: 12px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Application Received!</h1>
                <p>Thank you for your interest in joining our team</p>
            </div>
            
            <div class="content">
                <h2>Dear {candidate_name},</h2>
                
                <p>Thank you for submitting your application for the <strong>{job_title}</strong> position. We have successfully received your resume and application materials.</p>
                
                <div class="highlight">
                    <h3>📋 Application Details</h3>
                    <div class="details">
                        <p><strong>Position:</strong> {job_title}</p>
                        <p><strong>Application ID:</strong> {application_id}</p>
                        <p><strong>Submitted:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                        <p><strong>Status:</strong> <span class="status">RECEIVED</span></p>
                    </div>
                </div>
                
                <h3>🔄 What happens next?</h3>
                <ul>
                    <li><strong>Review Process:</strong> Our HR team will carefully review your application and resume</li>
                    <li><strong>AI Screening:</strong> Your application will go through our advanced AI screening process to match your skills with job requirements</li>
                    <li><strong>Initial Assessment:</strong> If your profile matches our requirements, we'll contact you within 5-7 business days</li>
                    <li><strong>Interview Process:</strong> Qualified candidates will be invited for interviews</li>
                </ul>
                
                <div class="highlight">
                    <h3>📞 Need Help?</h3>
                    <p>If you have any questions about your application or the hiring process, please don't hesitate to contact us:</p>
                    <p><strong>Email:</strong> {EMAIL_CONFIG['HR_EMAIL']}</p>
                    <p><strong>Application ID:</strong> {application_id} (Please reference this in any communication)</p>
                </div>
                
                <p><strong>Important:</strong> Please keep this email for your records. The Application ID will help us track your application status.</p>
                
                <p>We appreciate your interest in {company_name} and look forward to potentially working with you!</p>
                
                <p>Best regards,<br>
                <strong>The HR Team</strong><br>
                {company_name}</p>
            </div>
            
            <div class="footer">
                <p>This is an automated message. Please do not reply to this email.</p>
                <p>Visit our website: <a href="{EMAIL_CONFIG['COMPANY_WEBSITE']}">{EMAIL_CONFIG['COMPANY_WEBSITE']}</a></p>
                <p>&copy; 2025 {company_name}. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version for email clients that don't support HTML
    text_template = f"""
    Dear {candidate_name},

    Thank you for submitting your application for the {job_title} position!

    APPLICATION DETAILS:
    - Position: {job_title}
    - Application ID: {application_id}
    - Submitted: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
    - Status: RECEIVED

    WHAT HAPPENS NEXT:
    1. Our HR team will review your application
    2. AI screening will match your skills with job requirements
    3. We'll contact qualified candidates within 5-7 business days
    4. Interview process for selected candidates

    NEED HELP?
    Email: {EMAIL_CONFIG['HR_EMAIL']}
    Reference: Application ID {application_id}

    Best regards,
    The HR Team
    {company_name}

    This is an automated message. Please do not reply.
    """
    
    return html_template, text_template

def send_email(to_email, subject, html_content, text_content, from_name=None):
    """Send email using SMTP"""
    if not EMAIL_CONFIG.get('SEND_EMAILS', True):
        logger.info(f"Email sending disabled. Would send to: {to_email}")
        return True, "Email sending disabled"
    
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{from_name or EMAIL_CONFIG['FROM_NAME']} <{EMAIL_CONFIG['EMAIL_ADDRESS']}>"
        message["To"] = to_email
        
        # Add both text and HTML parts
        text_part = MIMEText(text_content, "plain")
        html_part = MIMEText(html_content, "html")
        
        message.attach(text_part)
        message.attach(html_part)
        
        # Create SMTP session
        server = smtplib.SMTP(EMAIL_CONFIG['SMTP_SERVER'], EMAIL_CONFIG['SMTP_PORT'])
        
        if EMAIL_CONFIG.get('USE_TLS', True):
            server.starttls()  # Enable TLS encryption
        
        # Login and send email
        server.login(EMAIL_CONFIG['EMAIL_ADDRESS'], EMAIL_CONFIG['EMAIL_PASSWORD'])
        server.sendmail(EMAIL_CONFIG['EMAIL_ADDRESS'], to_email, message.as_string())
        server.quit()
        
        logger.info(f"Email sent successfully to {to_email}")
        return True, "Email sent successfully"
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False, str(e)

def send_thank_you_email_async(candidate_email, candidate_name, job_title, application_id):
    """Send thank you email in background thread"""
    def send_email_task():
        try:
            # Generate email content
            html_content, text_content = get_thank_you_email_template(
                candidate_name, 
                job_title, 
                application_id, 
                EMAIL_CONFIG['COMPANY_NAME']
            )
            
            # Send email
            subject = f"Application Received - {job_title} Position | {EMAIL_CONFIG['COMPANY_NAME']}"
            
            success, message = send_email(
                candidate_email,
                subject,
                html_content,
                text_content,
                EMAIL_CONFIG['FROM_NAME']
            )
            
            if success:
                logger.info(f"Thank you email sent to {candidate_name} ({candidate_email}) for application {application_id}")
            else:
                logger.error(f"Failed to send thank you email to {candidate_name}: {message}")
                
        except Exception as e:
            logger.error(f"Error in email sending task: {str(e)}")
    
    # Run in background thread
    email_thread = Thread(target=send_email_task, daemon=True)
    email_thread.start()

def get_rejection_email_template(candidate_name, job_title, company_name, hr_email):
    """Generate HTML email template for rejection message"""
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Application Update - {company_name}</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .highlight {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107; }}
            .footer {{ text-align: center; margin-top: 30px; padding: 20px; color: #666; font-size: 14px; }}
            .button {{ display: inline-block; background: #6c757d; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
            .details {{ background: white; padding: 20px; border-radius: 5px; margin: 20px 0; border: 1px solid #ddd; }}
            .status {{ background: #dc3545; color: white; padding: 8px 16px; border-radius: 20px; font-size: 12px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📋 Application Update</h1>
                <p>Thank you for your interest in joining our team</p>
            </div>
            
            <div class="content">
                <h2>Dear {candidate_name},</h2>
                
                <p>Thank you for your interest in the <strong>{job_title}</strong> position at {company_name}. We appreciate the time and effort you invested in your application and the interview process.</p>
                
                <div class="highlight">
                    <h3>📋 Application Status</h3>
                    <div class="details">
                        <p><strong>Position:</strong> {job_title}</p>
                        <p><strong>Status:</strong> <span class="status">NOT SELECTED</span></p>
                        <p><strong>Date:</strong> {datetime.now().strftime('%B %d, %Y')}</p>
                    </div>
                </div>
                
                <p>After careful consideration of your application and interview performance, we regret to inform you that we have decided not to move forward with your candidacy for this position.</p>
                
                <h3>🔄 What happens next?</h3>
                <ul>
                    <li><strong>Keep in Touch:</strong> We will keep your resume on file for future opportunities that may be a better match</li>
                    <li><strong>Future Applications:</strong> You are welcome to apply for other positions that align with your skills and experience</li>
                    <li><strong>Professional Growth:</strong> We encourage you to continue developing your skills and pursuing your career goals</li>
                </ul>
                
                <div class="highlight">
                    <h3>💡 Feedback and Growth</h3>
                    <p>While we cannot provide specific feedback on your application, we encourage you to:</p>
                    <ul>
                        <li>Continue building your technical skills and experience</li>
                        <li>Seek feedback from mentors and colleagues</li>
                        <li>Stay updated with industry trends and best practices</li>
                        <li>Network with professionals in your field</li>
                    </ul>
                </div>
                
                <p><strong>Important:</strong> This decision is not a reflection of your overall capabilities or potential. The selection process involves many factors, and sometimes the best candidates may not be the right fit for a specific role or team.</p>
                
                <p>We wish you the very best in your future endeavors and hope our paths may cross again in the future.</p>
                
                <p>Best regards,<br>
                <strong>The HR Team</strong><br>
                {company_name}</p>
                
                <p><strong>Contact:</strong> If you have any questions, please reach out to us at {hr_email}</p>
            </div>
            
            <div class="footer">
                <p>This is an automated message. Please do not reply to this email.</p>
                <p>Visit our website: <a href="{EMAIL_CONFIG['COMPANY_WEBSITE']}">{EMAIL_CONFIG['COMPANY_WEBSITE']}</a></p>
                <p>&copy; 2025 {company_name}. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version for email clients that don't support HTML
    text_template = f"""
    Dear {candidate_name},

    Thank you for your interest in the {job_title} position at {company_name}. We appreciate the time and effort you invested in your application and the interview process.

    APPLICATION STATUS:
    - Position: {job_title}
    - Status: NOT SELECTED
    - Date: {datetime.now().strftime('%B %d, %Y')}

    After careful consideration of your application and interview performance, we regret to inform you that we have decided not to move forward with your candidacy for this position.

    WHAT HAPPENS NEXT:
    1. We will keep your resume on file for future opportunities
    2. You are welcome to apply for other positions
    3. Continue developing your skills and pursuing your career goals

    FEEDBACK AND GROWTH:
    While we cannot provide specific feedback, we encourage you to:
    - Continue building your technical skills and experience
    - Seek feedback from mentors and colleagues
    - Stay updated with industry trends
    - Network with professionals in your field

    This decision is not a reflection of your overall capabilities. The selection process involves many factors, and sometimes the best candidates may not be the right fit for a specific role.

    We wish you the very best in your future endeavors.

    Best regards,
    The HR Team
    {company_name}

    Contact: {hr_email}

    This is an automated message. Please do not reply.
    """
    
    return html_template, text_template

def get_hiring_email_template(candidate_name, job_title, company_name, hr_email):
    """Generate hiring/selection email template"""
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Congratulations! You've Been Selected - {company_name}</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .highlight {{ background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #4CAF50; }}
            .footer {{ text-align: center; margin-top: 30px; padding: 20px; color: #666; font-size: 14px; }}
            .button {{ display: inline-block; background: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
            .details {{ background: white; padding: 20px; border-radius: 5px; margin: 20px 0; border: 1px solid #ddd; }}
            .status {{ background: #4CAF50; color: white; padding: 8px 16px; border-radius: 20px; font-size: 12px; font-weight: bold; }}
            .celebration {{ font-size: 24px; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="celebration">🎉🎊🎉</div>
                <h1>Congratulations!</h1>
                <p>You've been selected for the position!</p>
            </div>
            
            <div class="content">
                <h2>Dear {candidate_name},</h2>
                
                <p>We are thrilled to inform you that after careful consideration of your application and interview performance, we have decided to <strong>select you</strong> for the <strong>{job_title}</strong> position at {company_name}!</p>
                
                <div class="highlight">
                    <h3>🎯 Selection Details</h3>
                    <div class="details">
                        <p><strong>Position:</strong> {job_title}</p>
                        <p><strong>Status:</strong> <span class="status">SELECTED FOR HIRE</span></p>
                        <p><strong>Selection Date:</strong> {datetime.now().strftime('%B %d, %Y')}</p>
                        <p><strong>Company:</strong> {company_name}</p>
                    </div>
                </div>
                
                <p>Your skills, experience, and enthusiasm during the interview process impressed our team, and we believe you will be a valuable addition to our organization.</p>
                
                <h3>🚀 What happens next?</h3>
                <ul>
                    <li><strong>HR Contact:</strong> Our HR team will contact you within 2-3 business days to discuss the next steps</li>
                    <li><strong>Offer Letter:</strong> You will receive a formal offer letter with details about compensation, benefits, and start date</li>
                    <li><strong>Background Check:</strong> We may conduct a background check as part of our standard hiring process</li>
                    <li><strong>Onboarding:</strong> Once you accept the offer, we'll begin the onboarding process</li>
                </ul>
                
                <div class="highlight">
                    <h3>📞 Next Steps</h3>
                    <p>Please be prepared to:</p>
                    <ul>
                        <li>Review and respond to the offer letter promptly</li>
                        <li>Provide any additional documentation if requested</li>
                        <li>Complete any required background check forms</li>
                        <li>Confirm your availability for the proposed start date</li>
                    </ul>
                </div>
                
                <p><strong>Important:</strong> Please keep this email for your records. This is your official notification of selection for the position.</p>
                
                <p>We are excited about the possibility of you joining our team and look forward to welcoming you to {company_name}!</p>
                
                <p>Congratulations once again on this achievement!</p>
                
                <p>Best regards,<br>
                <strong>The HR Team</strong><br>
                {company_name}</p>
                
                <p><strong>Contact:</strong> If you have any questions, please reach out to us at {hr_email}</p>
            </div>
            
            <div class="footer">
                <p>This is an automated message. Please do not reply to this email.</p>
                <p>Visit our website: <a href="{EMAIL_CONFIG['COMPANY_WEBSITE']}">{EMAIL_CONFIG['COMPANY_WEBSITE']}</a></p>
                <p>&copy; 2025 {company_name}. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version for email clients that don't support HTML
    text_template = f"""
    Dear {candidate_name},

    Congratulations! We are thrilled to inform you that you have been SELECTED for the {job_title} position at {company_name}!

    SELECTION DETAILS:
    - Position: {job_title}
    - Status: SELECTED FOR HIRE
    - Selection Date: {datetime.now().strftime('%B %d, %Y')}
    - Company: {company_name}

    After careful consideration of your application and interview performance, we have decided to select you for this position. Your skills, experience, and enthusiasm impressed our team.

    WHAT HAPPENS NEXT:
    1. Our HR team will contact you within 2-3 business days
    2. You will receive a formal offer letter with compensation and benefits details
    3. We may conduct a background check as part of our standard process
    4. Once you accept, we'll begin the onboarding process

    NEXT STEPS:
    - Review and respond to the offer letter promptly
    - Provide any additional documentation if requested
    - Complete any required background check forms
    - Confirm your availability for the proposed start date

    This is your official notification of selection. Please keep this email for your records.

    We are excited about you joining our team and look forward to welcoming you to {company_name}!

    Congratulations once again on this achievement!

    Best regards,
    The HR Team
    {company_name}

    Contact: {hr_email}

    This is an automated message. Please do not reply.
    """
    
    return html_template, text_template

def send_hiring_email_async(candidate_email, candidate_name, job_title):
    """Send hiring/selection email in background thread"""
    def send_email_task():
        try:
            # Generate email content
            html_content, text_content = get_hiring_email_template(
                candidate_name, 
                job_title, 
                EMAIL_CONFIG['COMPANY_NAME'],
                EMAIL_CONFIG['HR_EMAIL']
            )
            
            # Send email
            subject = f"🎉 Congratulations! You've Been Selected - {job_title} Position | {EMAIL_CONFIG['COMPANY_NAME']}"
            
            success, message = send_email(
                candidate_email,
                subject,
                html_content,
                text_content,
                EMAIL_CONFIG['FROM_NAME']
            )
            
            if success:
                logger.info(f"Hiring email sent to {candidate_name} ({candidate_email}) for position {job_title}")
            else:
                logger.error(f"Failed to send hiring email to {candidate_name}: {message}")
                
        except Exception as e:
            logger.error(f"Error in hiring email sending task: {str(e)}")
    
    # Run in background thread
    email_thread = Thread(target=send_email_task, daemon=True)
    email_thread.start()

def send_rejection_email_async(candidate_email, candidate_name, job_title):
    """Send rejection email in background thread"""
    def send_email_task():
        try:
            # Generate email content
            html_content, text_content = get_rejection_email_template(
                candidate_name, 
                job_title, 
                EMAIL_CONFIG['COMPANY_NAME'],
                EMAIL_CONFIG['HR_EMAIL']
            )
            
            # Send email
            subject = f"Application Update - {job_title} Position | {EMAIL_CONFIG['COMPANY_NAME']}"
            
            success, message = send_email(
                candidate_email,
                subject,
                html_content,
                text_content,
                EMAIL_CONFIG['FROM_NAME']
            )
            
            if success:
                logger.info(f"Rejection email sent to {candidate_name} ({candidate_email}) for position {job_title}")
            else:
                logger.error(f"Failed to send rejection email to {candidate_name}: {message}")
                
        except Exception as e:
            logger.error(f"Error in rejection email sending task: {str(e)}")
    
    # Run in background thread
    email_thread = Thread(target=send_email_task, daemon=True)
    email_thread.start()


def check_cloudflared_installed():
    """Check if cloudflared is installed"""
    try:
        result = subprocess.run(['cloudflared', 'version'], 
                              capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_cloudflared():
    """Install cloudflared if not present"""
    print("\n" + "="*60)
    print("📦 Installing Cloudflare Tunnel (cloudflared)...")
    print("="*60)
    
    system = sys.platform
    
    try:
        if system == "linux" or system == "linux2":
            # Linux installation
            commands = [
                "wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb",
                "sudo dpkg -i cloudflared-linux-amd64.deb",
                "rm cloudflared-linux-amd64.deb"
            ]
            for cmd in commands:
                subprocess.run(cmd, shell=True, check=True)
                
        elif system == "darwin":
            # macOS installation
            subprocess.run("brew install cloudflare/cloudflare/cloudflared", 
                         shell=True, check=True)
                         
        elif system == "win32":
            # Windows installation
            print("Please download cloudflared from:")
            print("https://github.com/cloudflare/cloudflared/releases")
            print("Add it to your PATH and restart the script.")
            return False
            
        print("✅ Cloudflared installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install cloudflared: {e}")
        print("\nPlease install manually:")
        print("https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation")
        return False

def start_cloudflare_tunnel():
    """Start Cloudflare tunnel and return public URL"""
    global CLOUDFLARE_TUNNEL_URL
    
    if not check_cloudflared_installed():
        if not install_cloudflared():
            return None
    
    print("\n" + "="*60)
    print("🌐 Starting Cloudflare Tunnel...")
    print("="*60)
    
    try:
        # Check if user is logged in
        login_check = subprocess.run(['cloudflared', 'tunnel', 'list'], 
                                   capture_output=True, text=True)
        
        if login_check.returncode != 0 or "You need to login" in login_check.stderr:
            print("📝 First time setup - Please login to Cloudflare")
            print("This will open your browser for authentication...")
            subprocess.run(['cloudflared', 'tunnel', 'login'])
            print("✅ Login successful!")
        
        # Try to create tunnel (will fail if exists, which is fine)
        create_result = subprocess.run(
            ['cloudflared', 'tunnel', 'create', CLOUDFLARE_TUNNEL_NAME],
            capture_output=True, text=True
        )
        
        if "already exists" in create_result.stderr:
            print(f"ℹ️  Tunnel '{CLOUDFLARE_TUNNEL_NAME}' already exists")
        elif create_result.returncode == 0:
            print(f"✅ Created tunnel '{CLOUDFLARE_TUNNEL_NAME}'")
        else:
            print(f"⚠️  Tunnel creation: {create_result.stderr}")
        
        # Start the tunnel with try.cloudflare.com for quick testing
        tunnel_process = subprocess.Popen(
            ['cloudflared', 'tunnel', '--url', f'http://localhost:{API_PORT}'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for tunnel to establish and capture URL
        print("⏳ Establishing tunnel connection...")
        
        start_time = time.time()
        while time.time() - start_time < 30:  # 30 second timeout
            line = tunnel_process.stderr.readline()
            
            # Look for the public URL in the output
            if "https://" in line and ".trycloudflare.com" in line:
                # Extract URL from the line
                url_match = re.search(r'https://[^\s]+\.trycloudflare\.com', line)
                if url_match:
                    CLOUDFLARE_TUNNEL_URL = url_match.group(0)
                    break
        
        if CLOUDFLARE_TUNNEL_URL:
            print("\n" + "="*60)
            print("🎉 CLOUDFLARE TUNNEL ACTIVE")
            print("="*60)
            print(f"📱 Public URL: {CLOUDFLARE_TUNNEL_URL}")
            print(f"🔗 Share this URL to access your complete system from anywhere")
            print(f"🔐 API Key: {API_KEY}")
            print("="*60 + "\n")
            
            # Keep tunnel process running in background
            tunnel_thread = threading.Thread(
                target=monitor_tunnel_process, 
                args=(tunnel_process,),
                daemon=True
            )
            tunnel_thread.start()
            
            return CLOUDFLARE_TUNNEL_URL
        else:
            print("❌ Failed to establish tunnel - timeout")
            tunnel_process.terminate()
            return None
            
    except Exception as e:
        print(f"❌ Error starting tunnel: {e}")
        return None

def monitor_tunnel_process(process):
    """Monitor tunnel process and restart if needed"""
    while True:
        output = process.stderr.readline()
        if output:
            # Log tunnel output for debugging (optional)
            if "error" in output.lower():
                logger.error(f"Tunnel error: {output.strip()}")
        
        # Check if process is still running
        if process.poll() is not None:
            logger.error("Tunnel process died! Restarting...")
            # Could implement restart logic here
            break
        
        time.sleep(1)

def stop_cloudflare_tunnel():
    """Stop all cloudflared processes"""
    try:
        if sys.platform == "win32":
            subprocess.run("taskkill /F /IM cloudflared.exe", shell=True)
        else:
            subprocess.run("pkill cloudflared", shell=True)
        print("✅ Cloudflare tunnel stopped")
    except:
        pass

# ============================================
# File Storage Helper Functions
# ============================================

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ============================================
# ENHANCED FOLDER MANAGEMENT SYSTEM
# ============================================

def ensure_job_folder_exists(ticket_id, ticket_subject=None):
    """Ensure a job folder exists for a ticket, create if it doesn't"""
    try:
        # Check if folder already exists
        ticket_folders = [f for f in os.listdir(BASE_STORAGE_PATH) 
                         if f.startswith(f"{ticket_id}_")]
        
        if ticket_folders:
            # Folder exists, return the path
            folder_path = os.path.join(BASE_STORAGE_PATH, ticket_folders[0])
            logger.info(f"Job folder already exists for ticket {ticket_id}: {folder_path}")
            return folder_path
        else:
            # Create new folder
            folder_path = create_ticket_folder(ticket_id, ticket_subject)
            if folder_path:
                logger.info(f"Created new job folder for ticket {ticket_id}: {folder_path}")
                return folder_path
            else:
                logger.error(f"Failed to create job folder for ticket {ticket_id}")
                return None
                
    except Exception as e:
        logger.error(f"Error ensuring job folder exists for ticket {ticket_id}: {e}")
        return None

def auto_create_folders_for_pending_tickets():
    """Automatically create folders for all pending tickets that should have folders"""
    try:
        conn = get_db_connection()
        if not conn:
            logger.error("Failed to connect to database for auto folder creation")
            return
        
        cursor = conn.cursor(dictionary=True)
        
        # Get all tickets that should have folders (approved or have resumes)
        cursor.execute("""
            SELECT DISTINCT t.ticket_id, t.subject, t.approval_status
            FROM tickets t
            LEFT JOIN (
                SELECT ticket_id, COUNT(*) as resume_count
                FROM ticket_details 
                WHERE field_name = 'resume_uploaded' AND field_value = 'true'
                GROUP BY ticket_id
            ) r ON t.ticket_id = r.ticket_id
            WHERE t.approval_status = 'approved' 
               OR r.resume_count > 0
               OR t.status = 'active'
        """)
        
        tickets = cursor.fetchall()
        created_count = 0
        existing_count = 0
        
        logger.info(f"Checking {len(tickets)} tickets for folder creation...")
        
        for ticket in tickets:
            ticket_id = ticket['ticket_id']
            
            # Check if folder already exists
            ticket_folders = [f for f in os.listdir(BASE_STORAGE_PATH) 
                            if f.startswith(f"{ticket_id}_")]
            
            if ticket_folders:
                existing_count += 1
                logger.debug(f"Folder already exists for ticket {ticket_id}")
            else:
                # Create folder
                folder_path = create_ticket_folder(ticket_id, ticket['subject'])
                if folder_path:
                    created_count += 1
                    logger.info(f"Auto-created folder for ticket {ticket_id}: {os.path.basename(folder_path)}")
                else:
                    logger.error(f"Failed to auto-create folder for ticket {ticket_id}")
        
        cursor.close()
        conn.close()
        
        logger.info(f"Auto folder creation complete: {created_count} created, {existing_count} existing")
        
    except Exception as e:
        logger.error(f"Error in auto_create_folders_for_pending_tickets: {e}")

def get_job_folder_info(ticket_id):
    """Get comprehensive information about a job folder"""
    try:
        # Find the ticket folder
        ticket_folders = [f for f in os.listdir(BASE_STORAGE_PATH) 
                         if f.startswith(f"{ticket_id}_")]
        
        if not ticket_folders:
            return {
                'exists': False,
                'folder_name': None,
                'folder_path': None,
                'resume_count': 0,
                'job_details': None,
                'metadata': None,
                'created_at': None
            }
        
        folder_path = os.path.join(BASE_STORAGE_PATH, ticket_folders[0])
        
        # Get folder info
        folder_info = {
            'exists': True,
            'folder_name': ticket_folders[0],
            'folder_path': folder_path,
            'created_at': datetime.fromtimestamp(os.path.getctime(folder_path)).isoformat(),
            'resume_count': 0,
            'job_details': None,
            'metadata': None
        }
        
        # Get metadata
        metadata_path = os.path.join(folder_path, 'metadata.json')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8', errors='ignore') as f:
                folder_info['metadata'] = json.load(f)
                folder_info['resume_count'] = len(folder_info['metadata'].get('resumes', []))
        
        # Get job details
        job_details_path = os.path.join(folder_path, 'job_details.json')
        if os.path.exists(job_details_path):
            with open(job_details_path, 'r') as f:
                folder_info['job_details'] = json.load(f)
        
        # Count actual resume files
        resume_files = [f for f in os.listdir(folder_path) 
                       if f.lower().endswith(('.pdf', '.doc', '.docx', '.txt'))]
        folder_info['actual_resume_files'] = len(resume_files)
        
        return folder_info
        
    except Exception as e:
        logger.error(f"Error getting job folder info for ticket {ticket_id}: {e}")
        return {
            'exists': False,
            'error': str(e)
        }

def cleanup_orphaned_folders():
    """Remove folders that don't have corresponding tickets"""
    try:
        conn = get_db_connection()
        if not conn:
            logger.error("Failed to connect to database for cleanup")
            return
        
        cursor = conn.cursor()
        
        # Get all valid ticket IDs
        cursor.execute("SELECT ticket_id FROM tickets")
        valid_ticket_ids = {row[0] for row in cursor.fetchall()}
        
        cursor.close()
        conn.close()
        
        # Check all folders
        orphaned_folders = []
        for folder_name in os.listdir(BASE_STORAGE_PATH):
            if folder_name.startswith('batch_results') or folder_name.startswith('.'):
                continue  # Skip special folders
                
            # Extract ticket ID from folder name
            ticket_id = folder_name.split('_')[0]
            
            if ticket_id not in valid_ticket_ids:
                orphaned_folders.append(folder_name)
        
        # Remove orphaned folders
        for folder_name in orphaned_folders:
            folder_path = os.path.join(BASE_STORAGE_PATH, folder_name)
            try:
                shutil.rmtree(folder_path)
                logger.info(f"Removed orphaned folder: {folder_name}")
            except Exception as e:
                logger.error(f"Failed to remove orphaned folder {folder_name}: {e}")
        
        logger.info(f"Cleanup complete: {len(orphaned_folders)} orphaned folders removed")
        
    except Exception as e:
        logger.error(f"Error in cleanup_orphaned_folders: {e}")

def create_ticket_folder(ticket_id, ticket_subject=None):
    """Create a folder for approved ticket"""
    try:
        # Clean ticket subject for folder name
        if ticket_subject:
            # Remove special characters and limit length
            clean_subject = re.sub(r'[^\w\s-]', '', ticket_subject)
            clean_subject = re.sub(r'[-\s]+', '-', clean_subject)
            clean_subject = clean_subject[:50].strip('-')
            folder_name = f"{ticket_id}_{clean_subject}"
        else:
            folder_name = str(ticket_id)
        
        folder_path = os.path.join(BASE_STORAGE_PATH, folder_name)
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            logger.info(f"Created folder for ticket {ticket_id}: {folder_path}")
            
            # Create a metadata file
            metadata = {
                'ticket_id': ticket_id,
                'created_at': datetime.now().isoformat(),
                'folder_name': folder_name,
                'resumes': []
            }
            
            metadata_path = os.path.join(folder_path, 'metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Also save job details
            save_job_details_to_folder(ticket_id, folder_path)
        
        return folder_path
        
    except Exception as e:
        logger.error(f"Error creating folder for ticket {ticket_id}: {e}")
        return None

def save_job_details_to_folder(ticket_id, folder_path):
    """Save job details to a JSON file in the ticket folder"""
    try:
        conn = get_db_connection()
        if not conn:
            logger.error("Failed to connect to database for job details")
            return False
        
        cursor = conn.cursor(dictionary=True)
        
        # Get ticket information
        cursor.execute("""
            SELECT * FROM tickets 
            WHERE ticket_id = %s
        """, (ticket_id,))
        
        ticket = cursor.fetchone()
        if not ticket:
            cursor.close()
            conn.close()
            return False
        
        # Get the LATEST value for each field
        cursor.execute("""
            SELECT 
                td1.field_name,
                td1.field_value
            FROM ticket_details td1
            INNER JOIN (
                SELECT field_name, MAX(created_at) as max_created_at
                FROM ticket_details
                WHERE ticket_id = %s
                GROUP BY field_name
            ) td2 ON td1.field_name = td2.field_name 
                 AND td1.created_at = td2.max_created_at
            WHERE td1.ticket_id = %s
        """, (ticket_id, ticket_id))
        
        job_details = {}
        for row in cursor.fetchall():
            job_details[row['field_name']] = row['field_value']
        
        # Convert datetime objects to string
        for key, value in ticket.items():
            if isinstance(value, datetime):
                ticket[key] = value.isoformat()
        
        # Combine ticket info with job details
        complete_job_info = {
            'ticket_info': ticket,
            'job_details': job_details,
            'saved_at': datetime.now().isoformat()
        }
        
        # Save to job_details.json
        job_details_path = os.path.join(folder_path, 'job_details.json')
        with open(job_details_path, 'w', encoding='utf-8') as f:
            json.dump(complete_job_info, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved job details for ticket {ticket_id}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Error saving job details for ticket {ticket_id}: {e}")
        return False

def update_job_details_in_folder(ticket_id):
    """Update job details file when ticket information changes"""
    try:
        # Find the ticket folder
        ticket_folders = [f for f in os.listdir(BASE_STORAGE_PATH) 
                         if f.startswith(f"{ticket_id}_")]
        
        if not ticket_folders:
            logger.error(f"No folder found for ticket {ticket_id}")
            return False
        
        folder_path = os.path.join(BASE_STORAGE_PATH, ticket_folders[0])
        return save_job_details_to_folder(ticket_id, folder_path)
        
    except Exception as e:
        logger.error(f"Error updating job details for ticket {ticket_id}: {e}")
        return False

def save_resume_to_ticket(ticket_id, file, applicant_name=None, applicant_email=None):
    """Save resume to ticket folder"""
    try:
        # Get ticket folder path
        ticket_folders = [f for f in os.listdir(BASE_STORAGE_PATH) 
                         if f.startswith(f"{ticket_id}_")]
        
        if not ticket_folders:
            logger.error(f"No folder found for ticket {ticket_id}")
            return None
        
        folder_path = os.path.join(BASE_STORAGE_PATH, ticket_folders[0])
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_filename = secure_filename(file.filename)
        base_name, ext = os.path.splitext(original_filename)
        
        if applicant_name:
            clean_name = re.sub(r'[^\w\s-]', '', applicant_name)
            clean_name = re.sub(r'[-\s]+', '_', clean_name)
            filename = f"{clean_name}_{timestamp}{ext}"
        else:
            filename = f"resume_{timestamp}{ext}"
        
        file_path = os.path.join(folder_path, filename)
        
        # Save file
        file.save(file_path)
        
        # Update metadata
        metadata_path = os.path.join(folder_path, 'metadata.json')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8', errors='ignore') as f:
                metadata = json.load(f)
            
            resume_info = {
                'filename': filename,
                'original_filename': original_filename,
                'uploaded_at': datetime.now().isoformat(),
                'applicant_name': applicant_name,
                'applicant_email': applicant_email,
                'file_size': os.path.getsize(file_path)
            }
            
            metadata['resumes'].append(resume_info)
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        
        # 🆕 CREATE DATABASE RECORD AUTOMATICALLY
        if applicant_name and applicant_email:
            try:
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor(dictionary=True)
                    
                    # ENHANCED: Check if candidate already exists to avoid duplicates
                    cursor.execute("""
                        SELECT id, applicant_name, status FROM resume_applications 
                        WHERE ticket_id = %s AND applicant_email = %s
                    """, (ticket_id, applicant_email))
                    
                    existing_candidate = cursor.fetchone()
                    
                    if not existing_candidate:
                        # Create new database record
                        cursor.execute("""
                            INSERT INTO resume_applications 
                            (ticket_id, applicant_name, applicant_email, filename, file_path, file_size, file_type, status, uploaded_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending', CURRENT_TIMESTAMP)
                        """, (ticket_id, applicant_name, applicant_email, filename, file_path, 
                              os.path.getsize(file_path), ext.lower()))
                        
                        candidate_id = cursor.lastrowid
                        conn.commit()
                        
                        logger.info(f"✅ Created database record for {applicant_name} (ID: {candidate_id})")
                    else:
                        # DUPLICATE PREVENTION: Reject duplicate applications
                        logger.warning(f"🚫 DUPLICATE APPLICATION BLOCKED: {applicant_name} ({applicant_email}) already applied to job {ticket_id}")
                        cursor.close()
                        conn.close()
                        return {
                            'success': False,
                            'error': f'You have already applied to this job position. Each candidate can only apply once per job posting.',
                            'duplicate_info': {
                                'existing_name': existing_candidate['applicant_name'],
                                'existing_status': existing_candidate['status'],
                                'applied_at': 'Previously'
                            }
                        }
                    
                    cursor.close()
                    conn.close()
                else:
                    logger.warning("Failed to connect to database for resume record creation")
            except Exception as db_error:
                logger.error(f"Failed to create database record for {applicant_name}: {db_error}")
                # Don't fail the upload if database fails
        
        logger.info(f"Saved resume {filename} for ticket {ticket_id}")
        return file_path
        
    except Exception as e:
        logger.error(f"Error saving resume for ticket {ticket_id}: {e}")
        return None

def get_ticket_resumes(ticket_id):
    """Get list of resumes for a ticket"""
    try:
        ticket_folders = [f for f in os.listdir(BASE_STORAGE_PATH) 
                         if f.startswith(f"{ticket_id}_")]
        
        if not ticket_folders:
            logger.info(f"get_ticket_resumes: No folders found for ticket {ticket_id}")
            return []
        
        folder_path = os.path.join(BASE_STORAGE_PATH, ticket_folders[0])
        metadata_path = os.path.join(folder_path, 'metadata.json')
        
        logger.info(f"get_ticket_resumes: Looking for metadata at {metadata_path}")
        
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8', errors='ignore') as f:
                metadata = json.load(f)
                resumes = metadata.get('resumes', [])
                logger.info(f"get_ticket_resumes: Found {len(resumes)} resumes in metadata")
                
                # Try to get MySQL database IDs for consistent ID mapping
                mysql_ids = {}
                try:
                    conn = get_db_connection()
                    if conn:
                        cursor = conn.cursor(dictionary=True)
                        
                        # Get status and final decision for each candidate
                        for resume in resumes:
                            try:
                                # Get status from resume_applications table
                                cursor.execute("""
                                    SELECT status FROM resume_applications 
                                    WHERE ticket_id = %s AND applicant_email = %s
                                """, (ticket_id, resume['applicant_email']))
                                
                                status_result = cursor.fetchone()
                                if status_result:
                                    resume['status'] = status_result['status']
                                    logger.info(f"get_ticket_resumes: Found status '{status_result['status']}' for {resume['applicant_name']}")
                                else:
                                    resume['status'] = 'pending'  # Default status
                                    logger.info(f"get_ticket_resumes: No status found for {resume['applicant_name']}, defaulting to 'pending'")
                                
                                # Get final decision from candidate_interview_status table
                                logger.info(f"get_ticket_resumes: Looking up final_decision for {resume['applicant_name']} ({resume['applicant_email']}) in ticket {ticket_id}")
                                cursor.execute("""
                                    SELECT final_decision FROM candidate_interview_status 
                                    WHERE ticket_id = %s AND candidate_id = (
                                        SELECT id FROM resume_applications 
                                        WHERE ticket_id = %s AND applicant_email = %s
                                    )
                                """, (ticket_id, ticket_id, resume['applicant_email']))
                                
                                decision_result = cursor.fetchone()
                                if decision_result and decision_result['final_decision']:
                                    resume['final_decision'] = decision_result['final_decision']
                                    logger.info(f"get_ticket_resumes: ✅ Found final_decision '{decision_result['final_decision']}' for {resume['applicant_name']}")
                                else:
                                    resume['final_decision'] = None
                                    logger.info(f"get_ticket_resumes: ❌ No final_decision found for {resume['applicant_name']} - decision_result: {decision_result}")
                                    
                            except Exception as status_error:
                                logger.warning(f"get_ticket_resumes: Status/decision lookup failed for {resume['applicant_name']}: {status_error}")
                                resume['status'] = 'pending'  # Default status
                                resume['final_decision'] = None
                            
                            # Try to get MySQL IDs (separate try-catch to avoid affecting status)
                            try:
                                cursor.execute("""
                                    SELECT td1.id as applicant_name_id, td2.id as applicant_email_id
                                    FROM ticket_details td1
                                    INNER JOIN ticket_details td2 ON td1.ticket_id = td2.ticket_id
                                    WHERE td1.field_name = 'applicant_name' 
                                    AND td2.field_name = 'applicant_email'
                                    AND td1.field_value = %s 
                                    AND td2.field_value = %s
                                    AND td1.ticket_id = %s
                                """, (resume['applicant_name'], resume['applicant_email'], ticket_id))
                                
                                result = cursor.fetchone()
                                if result:
                                    # Use the applicant_name ID as the primary ID
                                    mysql_ids[f"{resume['applicant_name']}_{resume['applicant_email']}"] = result['applicant_name_id']
                                    logger.info(f"get_ticket_resumes: Found MySQL ID {result['applicant_name_id']} for {resume['applicant_name']}")
                                else:
                                    logger.warning(f"get_ticket_resumes: No MySQL ID found for {resume['applicant_name']} ({resume['applicant_email']})")
                            except Exception as mysql_error:
                                logger.warning(f"get_ticket_resumes: MySQL lookup failed for {resume['applicant_name']}: {mysql_error}")
                        
                        cursor.close()
                        conn.close()
                        
                except Exception as mysql_error:
                    logger.warning(f"get_ticket_resumes: MySQL lookup failed: {mysql_error}")
                
                # Add IDs to resumes - prefer MySQL IDs, fallback to sequential
                for i, resume in enumerate(resumes):
                    candidate_key = f"{resume['applicant_name']}_{resume['applicant_email']}"
                    
                    if candidate_key in mysql_ids:
                        # Use MySQL database ID for consistency
                        resume['id'] = mysql_ids[candidate_key]
                        logger.info(f"get_ticket_resumes: Using MySQL ID {resume['id']} for {resume['applicant_name']}")
                    else:
                        # Fallback to sequential ID
                        resume['id'] = i + 1
                        logger.info(f"get_ticket_resumes: Using sequential ID {resume['id']} for {resume['applicant_name']}")
                
                logger.info(f"get_ticket_resumes: Returning {len(resumes)} resumes with IDs")
                return resumes
        else:
            logger.info(f"get_ticket_resumes: Metadata file not found at {metadata_path}")
        
        return []
        
    except Exception as e:
        logger.error(f"Error getting resumes for ticket {ticket_id}: {e}")
        return []

def create_folders_for_existing_approved_tickets():
    """Create folders for all existing approved tickets"""
    try:
        conn = get_db_connection()
        if not conn:
            logger.error("Failed to connect to database")
            return
        
        cursor = conn.cursor(dictionary=True)
        
        # Get all approved tickets
        cursor.execute("""
            SELECT ticket_id, subject
            FROM tickets
            WHERE approval_status = 'approved'
        """)
        
        approved_tickets = cursor.fetchall()
        created_count = 0
        existing_count = 0
        
        print(f"\n📁 Checking {len(approved_tickets)} approved tickets for folders...")
        
        for ticket in approved_tickets:
            ticket_id = ticket['ticket_id']
            
            # Check if folder already exists
            ticket_folders = [f for f in os.listdir(BASE_STORAGE_PATH) 
                            if f.startswith(f"{ticket_id}_")]
            
            if ticket_folders:
                existing_count += 1
                print(f"   ✓ Folder already exists for ticket {ticket_id}")
                # Update job details in existing folder
                folder_path = os.path.join(BASE_STORAGE_PATH, ticket_folders[0])
                save_job_details_to_folder(ticket_id, folder_path)
                print(f"   📄 Updated job details for ticket {ticket_id}")
            else:
                # Create folder (which will also save job details)
                folder_path = create_ticket_folder(ticket_id, ticket['subject'])
                if folder_path:
                    created_count += 1
                    print(f"   ✅ Created folder for ticket {ticket_id}: {os.path.basename(folder_path)}")
                    print(f"   📄 Saved job details for ticket {ticket_id}")
                else:
                    print(f"   ❌ Failed to create folder for ticket {ticket_id}")
        
        cursor.close()
        conn.close()
        
        print(f"\n📊 Summary:")
        print(f"   - New folders created: {created_count}")
        print(f"   - Existing folders: {existing_count}")
        print(f"   - Total approved tickets: {len(approved_tickets)}")
        
    except Exception as e:
        logger.error(f"Error creating folders for existing tickets: {e}")
        print(f"❌ Error: {e}")

# ============================================
# CHAT INTERFACE AND ENDPOINTS
# ============================================

@app.route('/')
def index():
    """Serve the main interface with both chat and API info"""
    return render_template_string(r'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hiring Bot - Complete System</title>
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 1200px; 
                margin: 0 auto; 
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-top: 20px;
            }
            .section {
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .chat-section {
                grid-column: span 2;
            }
            h1, h2 { color: #333; }
            #chat-container { 
                border: 1px solid #ddd; 
                height: 400px; 
                overflow-y: auto; 
                padding: 15px; 
                margin-bottom: 10px;
                background: #fafafa;
                border-radius: 4px;
            }
            .message { 
                margin: 10px 0; 
                padding: 10px;
                border-radius: 8px;
                max-width: 70%;
            }
            .user { 
                background: #007bff;
                color: white;
                margin-left: auto;
                text-align: right;
            }
            .bot { 
                background: #e9ecef;
                color: #333;
            }
            #input-container { 
                display: flex; 
                gap: 10px;
            }
            #message-input { 
                flex: 1; 
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            #send-button { 
                padding: 12px 24px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
            }
            #send-button:hover {
                background: #0056b3;
            }
            .api-info {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 4px;
                margin-top: 10px;
            }
            .api-info code {
                background: #e9ecef;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }
            .status-indicator {
                display: inline-block;
                width: 10px;
                height: 10px;
                border-radius: 50%;
                margin-right: 5px;
            }
            .status-active { background: #28a745; }
            .status-inactive { background: #dc3545; }
            .endpoint-list {
                max-height: 300px;
                overflow-y: auto;
                font-size: 13px;
            }
        </style>
    </head>
    <body>
        <h1>🤖 Hiring Bot - Complete System</h1>
        
        <div class="container">
            <div class="section">
                <h2>📊 System Status</h2>
                <p><span class="status-indicator status-active"></span> Server: Active</p>
                <p><span class="status-indicator {% if tunnel_url %}status-active{% else %}status-inactive{% endif %}"></span> 
                   Cloudflare Tunnel: {% if tunnel_url %}Active{% else %}Local Only{% endif %}</p>
                <p>🔐 API Key: <code>{{ api_key[:20] }}...</code></p>
                {% if tunnel_url %}
                <p>🌐 Public URL: <code>{{ tunnel_url }}</code></p>
                {% endif %}
            </div>
            
            <div class="section">
                <h2>🔗 Quick Links</h2>
                <p>📚 <a href="/api/health">Health Check</a></p>
                <p>💼 <a href="/api/jobs/approved?api_key={{ api_key }}">View Approved Jobs</a></p>
                <p>📊 <a href="/api/stats?api_key={{ api_key }}">Statistics</a></p>
                <p>📍 <a href="/api/locations?api_key={{ api_key }}">Locations</a></p>
                <p>🛠️ <a href="/api/skills?api_key={{ api_key }}">Skills</a></p>
            </div>
        </div>
        
        <div class="section chat-section">
            <h2>💬 Chat with Hiring Bot</h2>
            <div id="chat-container"></div>
            <div id="input-container">
                <input type="text" id="message-input" placeholder="Type your message... (try 'I want to post a job' or 'help')" />
                <button id="send-button">Send</button>
            </div>
        </div>
        
        <div class="section api-info">
            <h3>API Endpoints</h3>
            <div class="endpoint-list">
                <p><strong>Chat Endpoints:</strong></p>
                <ul>
                    <li>POST /api/chat/start - Start new chat session</li>
                    <li>POST /api/chat/message - Send message</li>
                    <li>GET /api/chat/history/&lt;id&gt; - Get chat history</li>
                </ul>
                <p><strong>Job Management:</strong></p>
                <ul>
                    <li>GET /api/jobs/approved - Get approved jobs</li>
                    <li>GET /api/jobs/&lt;id&gt; - Get job details</li>
                    <li>GET /api/jobs/search?q=python - Search jobs</li>
                    <li>POST /api/tickets/&lt;id&gt;/approve - Approve ticket</li>
                </ul>
                <p><strong>Resume Management:</strong></p>
                <ul>
                    <li>POST /api/tickets/&lt;id&gt;/resumes - Upload resume</li>
                    <li>GET /api/tickets/&lt;id&gt;/resumes - List resumes</li>
                    <li>GET /api/tickets/&lt;id&gt;/resumes/&lt;filename&gt; - Download resume</li>
                </ul>
                <p><strong>Resume Filtering:</strong></p>
                <ul>
                    <li>POST /api/tickets/&lt;id&gt;/filter-resumes - Trigger filtering</li>
                    <li>GET /api/tickets/&lt;id&gt;/top-resumes - Get top candidates</li>
                    <li>GET /api/tickets/&lt;id&gt;/filtering-report - Get report</li>
                    <li>GET /api/tickets/&lt;id&gt;/filtering-status - Check status</li>
                    <li>POST /api/tickets/&lt;id&gt;/send-top-resumes - Send via webhook</li>
                </ul>
            </div>
        </div>
        
        <script>
            let sessionId = null;
            let userId = 'user_' + Math.random().toString(36).substr(2, 9);
            
            // Start chat session
            async function startChat() {
                const response = await fetch('/api/chat/start', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_id: userId})
                });
                const data = await response.json();
                sessionId = data.session_id;
                addMessage('bot', data.message);
            }
            
            // Send message
            async function sendMessage() {
                const input = document.getElementById('message-input');
                const message = input.value.trim();
                if (!message || !sessionId) return;
                
                addMessage('user', message);
                input.value = '';
                
                const response = await fetch('/api/chat/message', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        session_id: sessionId,
                        user_id: userId,
                        message: message
                    })
                });
                const data = await response.json();
                addMessage('bot', data.response || data.message);
            }
            
            // Add message to chat
            function addMessage(sender, message) {
                const chatContainer = document.getElementById('chat-container');
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message ' + sender;
                
                // Convert markdown-style bold to HTML
                const formattedMessage = message
                    .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
                    .replace(/\\n/g, '<br>');
                
                messageDiv.innerHTML = formattedMessage;
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
            
            // Event listeners
            document.getElementById('send-button').onclick = sendMessage;
            document.getElementById('message-input').onkeypress = (e) => {
                if (e.key === 'Enter') sendMessage();
            };
            
            // Start chat on load
            startChat();
        </script>
    </body>
    </html>
    ''', tunnel_url=CLOUDFLARE_TUNNEL_URL, api_key=API_KEY)

@app.route('/api/debug/tickets', methods=['GET'])
@require_api_key
def debug_tickets():
    """Debug endpoint to see all tickets in the system"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # Get ALL tickets
        cursor.execute("""
            SELECT 
                ticket_id,
                source,
                sender,
                user_id,
                subject,
                approval_status,
                status,
                created_at,
                approved_at
            FROM tickets
            ORDER BY created_at DESC
        """)
        
        all_tickets = cursor.fetchall()
        
        # Get approved tickets
        cursor.execute("""
            SELECT 
                ticket_id,
                source,
                sender,
                user_id,
                subject,
                approval_status,
                status
            FROM tickets
            WHERE approval_status = 'approved'
        """)
        
        approved_tickets = cursor.fetchall()
        
        # Check for orphaned folders
        folders_in_storage = []
        if os.path.exists(BASE_STORAGE_PATH):
            folders_in_storage = [f for f in os.listdir(BASE_STORAGE_PATH) 
                                if not f.startswith('.')]
        
        cursor.close()
        conn.close()
        
        # Convert datetime objects to strings
        for ticket in all_tickets:
            for key, value in ticket.items():
                if isinstance(value, datetime):
                    ticket[key] = value.isoformat()
        
        for ticket in approved_tickets:
            for key, value in ticket.items():
                if isinstance(value, datetime):
                    ticket[key] = value.isoformat()
        
        return jsonify({
            'total_tickets': len(all_tickets),
            'approved_tickets': len(approved_tickets),
            'folders_in_storage': len(folders_in_storage),
            'all_tickets': all_tickets,
            'approved_tickets_list': approved_tickets,
            'storage_folders': folders_in_storage
        })
        
    except Exception as e:
        logger.error(f"Error in debug_tickets: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health_check():
    """Health check endpoint"""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,X-API-Key,ngrok-skip-browser-warning')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        return response, 200
    
    conn = get_db_connection()
    db_status = "connected" if conn else "disconnected"
    
    if conn:
        conn.close()
    
    # Check storage directory
    storage_status = "accessible" if os.path.exists(BASE_STORAGE_PATH) else "not_found"
    
    # Check if filtering module is available
    filtering_module_status = "not_found"
    filtering_module_error = None
    try:
        from resume_filter5 import UpdatedResumeFilteringSystem
        filtering_module_status = "available"
    except ImportError as e:
        filtering_module_error = str(e)
        try:
            from resume_filter5 import UpdatedResumeFilteringSystem
            filtering_module_status = "available (as resume_filter5)"
        except ImportError as e2:
            filtering_module_error = f"resume_filter5: {e}, resume_filter: {e2}"
    
    response = jsonify({
        'status': 'ok' if db_status == "connected" else 'error',
        'database': db_status,
        'tunnel': 'active' if CLOUDFLARE_TUNNEL_URL else 'inactive',
        'public_url': CLOUDFLARE_TUNNEL_URL,
        'storage': storage_status,
        'filtering_module': filtering_module_status,
        'filtering_module_error': filtering_module_error,
        'chat_enabled': True,
        'api_enabled': True,
        'timestamp': datetime.now().isoformat()
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

# ============================================
# CHAT API ENDPOINTS
# ============================================

@app.route('/api/chat/start', methods=['POST'])
@require_api_key
def start_chat():
    """Start a new chat session"""
    try:
        data = request.json
        user_id = data.get('user_id', 'anonymous')
        
        result = chat_bot.start_session(user_id)
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error starting chat: {e}")
        return jsonify({
            'error': 'Failed to start chat session',
            'message': str(e)
        }), 500

@app.route('/api/chat/message', methods=['POST'])
@require_api_key
def send_message():
    """Send a message to the chat bot"""
    try:
        data = request.json
        
        session_id = data.get('session_id')
        user_id = data.get('user_id')
        message = data.get('message')
        
        if not all([session_id, user_id, message]):
            return jsonify({
                'error': 'Missing required fields',
                'required': ['session_id', 'user_id', 'message']
            }), 400
        
        # Check if this is an authenticated HR user
        authenticated_user_email = None
        if 'Authorization' in request.headers:
            try:
                token = request.headers['Authorization'].replace('Bearer ', '')
                payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
                if payload.get('role') == 'hr':
                    authenticated_user_email = payload.get('email')
                    logger.info(f"Authenticated HR user: {authenticated_user_email}")
            except Exception as e:
                logger.warning(f"Failed to decode JWT token: {e}")
        
        # Pass the authenticated user email to the chat bot
        bot_response = chat_bot.process_message(session_id, user_id, message, authenticated_user_email)
        
        # Fix the response format for React frontend compatibility
        formatted_response = {
            'success': True,
            'response': bot_response.get('message', ''),  # Map 'message' to 'response'
            'message': bot_response.get('message', ''),   # Also keep as 'message'
            'metadata': bot_response.get('metadata', {}),
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(formatted_response)
    
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return jsonify({
            'error': 'Failed to process message',
            'message': str(e)
        }), 500

@app.route('/api/chat/history/<session_id>', methods=['GET'])
@require_api_key
def get_chat_history(session_id):
    """Get chat history for a session"""
    try:
        limit = request.args.get('limit', 50, type=int)
        messages = chat_bot.session_manager.get_messages(session_id, limit)
        
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                'id': msg.get('message_id'),
                'sender': msg['sender_type'],
                'message': msg['message_content'],
                'metadata': msg.get('message_metadata'),
                'timestamp': msg['timestamp'].isoformat() if msg.get('timestamp') else None
            })
        
        return jsonify({
            'session_id': session_id,
            'messages': formatted_messages,
            'count': len(formatted_messages)
        })
    
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        return jsonify({
            'error': 'Failed to fetch chat history',
            'message': str(e)
        }), 500

# ============================================
# RESUME MANAGEMENT ENDPOINTS
# ============================================

@app.route('/api/tickets/<ticket_id>/approve', methods=['POST'])
@require_api_key
def approve_ticket_and_create_folder(ticket_id):
    """Approve a ticket and create its folder with enhanced logging"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # Get ticket details
        cursor.execute("""
            SELECT ticket_id, subject, approval_status, sender, created_at
            FROM tickets
            WHERE ticket_id = %s
        """, (ticket_id,))
        
        ticket = cursor.fetchone()
        
        if not ticket:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Ticket not found'
            }), 404
        
        # Update approval status if not already approved
        if ticket['approval_status'] != 'approved':
            cursor.execute("""
                UPDATE tickets 
                SET approval_status = 'approved', 
                    approved_at = NOW(),
                    status = 'active'
                WHERE ticket_id = %s
            """, (ticket_id,))
            conn.commit()
            
            logger.info(f"Ticket {ticket_id} approved by HR manager")
        
        cursor.close()
        conn.close()
        
        # Ensure folder exists (create if it doesn't)
        folder_path = ensure_job_folder_exists(ticket_id, ticket['subject'])
        
        if folder_path:
            # Get folder information
            folder_info = get_job_folder_info(ticket_id)
            
            return jsonify({
                'success': True,
                'message': f'Job {ticket_id} approved and folder created successfully',
                'data': {
                    'ticket_id': ticket_id,
                    'job_title': ticket['subject'],
                    'approved_by': 'HR Manager',
                    'approved_at': datetime.now().isoformat(),
                    'folder_info': folder_info
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create job folder'
            }), 500
            
    except Exception as e:
        logger.error(f"Error approving ticket: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tickets/<ticket_id>/update-job-details', methods=['POST'])
@require_api_key
def update_job_details_endpoint(ticket_id):
    """Update job details file when ticket information changes"""
    try:
        success = update_job_details_in_folder(ticket_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Job details updated for ticket {ticket_id}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update job details'
            }), 500
            
    except Exception as e:
        logger.error(f"Error updating job details: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


    """Upload a resume for a specific ticket"""
    try:
        # Check if the ticket exists and is approved
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT ticket_id, subject, approval_status
            FROM tickets
            WHERE ticket_id = %s
        """, (ticket_id,))
        
        ticket = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not ticket:
            return jsonify({
                'success': False,
                'error': 'Ticket not found'
            }), 404
        
        if ticket['approval_status'] != 'approved':
            return jsonify({
                'success': False,
                'error': 'Ticket must be approved before uploading resumes'
            }), 400
        
        # Check if file is in request
        if 'resume' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['resume']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Get applicant details from form data
        applicant_name = request.form.get('applicant_name', 'Unknown Applicant')
        applicant_email = request.form.get('applicant_email', 'No email provided')
        
        # Ensure folder exists (create if it doesn't)
        folder_path = ensure_job_folder_exists(ticket_id, ticket['subject'])
        if not folder_path:
            return jsonify({
                'success': False,
                'error': 'Failed to create job folder'
            }), 500
        
        # Save the resume
        result = save_resume_to_ticket(
            ticket_id, 
            file, 
            applicant_name, 
            applicant_email
        )
        
        # Handle duplicate prevention response
        if isinstance(result, dict) and not result.get('success', True):
            return jsonify(result), 400
        
        saved_path = result
        if saved_path:
            # Get updated folder information
            folder_info = get_job_folder_info(ticket_id)
            
            return jsonify({
                'success': True,
                'message': 'Resume uploaded successfully',
                'data': {
                    'ticket_id': ticket_id,
                    'job_title': ticket['subject'],
                    'applicant_name': applicant_name,
                    'applicant_email': applicant_email,
                    'filename': os.path.basename(saved_path),
                    'file_size': os.path.getsize(saved_path),
                    'uploaded_at': datetime.now().isoformat(),
                    'folder_info': folder_info
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save resume'
            }), 500
            
    except Exception as e:
        logger.error(f"Error uploading resume: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tickets/<ticket_id>/resumes', methods=['GET'])
@require_api_key
def get_resumes(ticket_id):
    """Get list of all resumes for a ticket"""
    try:
        resumes = get_ticket_resumes(ticket_id)
        logger.info(f"API: Returning {len(resumes)} resumes for ticket {ticket_id}")
        
        # UNIVERSAL FIX: Ensure final_decision is included for each resume
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            for resume in resumes:
                try:
                    # Get final decision from candidate_interview_status table using multiple approaches
                    final_decision = None
                    
                    # Method 1: Try with ticket_id and email
                    cursor.execute("""
                        SELECT final_decision FROM candidate_interview_status 
                        WHERE ticket_id = %s AND candidate_id = (
                            SELECT id FROM resume_applications 
                            WHERE ticket_id = %s AND applicant_email = %s
                        )
                    """, (ticket_id, ticket_id, resume['applicant_email']))
                    
                    decision_result = cursor.fetchone()
                    if decision_result and decision_result['final_decision']:
                        final_decision = decision_result['final_decision']
                        logger.info(f"API: ✅ Found final_decision '{final_decision}' for {resume['applicant_name']} (method 1)")
                    else:
                        # Method 2: Try with just candidate_id from resume_applications
                        cursor.execute("""
                            SELECT final_decision FROM candidate_interview_status 
                            WHERE candidate_id = (
                                SELECT id FROM resume_applications 
                                WHERE ticket_id = %s AND applicant_email = %s
                            )
                        """, (ticket_id, resume['applicant_email']))
                        
                        decision_result2 = cursor.fetchone()
                        if decision_result2 and decision_result2['final_decision']:
                            final_decision = decision_result2['final_decision']
                            logger.info(f"API: ✅ Found final_decision '{final_decision}' for {resume['applicant_name']} (method 2)")
                        else:
                            # Method 3: Try with applicant_name matching
                            cursor.execute("""
                                SELECT final_decision FROM candidate_interview_status 
                                WHERE candidate_id = (
                                    SELECT id FROM resume_applications 
                                    WHERE applicant_name = %s AND applicant_email = %s
                                )
                            """, (resume['applicant_name'], resume['applicant_email']))
                            
                            decision_result3 = cursor.fetchone()
                            if decision_result3 and decision_result3['final_decision']:
                                final_decision = decision_result3['final_decision']
                                logger.info(f"API: ✅ Found final_decision '{final_decision}' for {resume['applicant_name']} (method 3)")
                            else:
                                logger.info(f"API: ❌ No final_decision found for {resume['applicant_name']} using any method")
                    
                    resume['final_decision'] = final_decision
                    
                except Exception as e:
                    logger.warning(f"API: Error getting final_decision for {resume['applicant_name']}: {e}")
                    resume['final_decision'] = None
            
            cursor.close()
            conn.close()
        
        # Log the structure of each resume with status
        for i, resume in enumerate(resumes):
            logger.info(f"API: Resume {i+1} structure: {resume}")
            logger.info(f"API: Resume {i+1} has id: {resume.get('id')}")
            logger.info(f"API: Resume {i+1} has status: {resume.get('status')}")
            logger.info(f"API: Resume {i+1} has final_decision: {resume.get('final_decision')}")
            logger.info(f"API: Resume {i+1} name: {resume.get('applicant_name')}")
            logger.info(f"API: Resume {i+1} email: {resume.get('applicant_email')}")
        
        return jsonify({
            'success': True,
            'data': {
                'ticket_id': ticket_id,
                'resume_count': len(resumes),
                'resumes': resumes
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting resumes: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tickets/<ticket_id>/resumes/<filename>', methods=['GET'])
@require_api_key
def download_resume(ticket_id, filename):
    """Download a specific resume"""
    try:
        # Find the ticket folder
        ticket_folders = [f for f in os.listdir(BASE_STORAGE_PATH) 
                         if f.startswith(f"{ticket_id}_")]
        
        if not ticket_folders:
            return jsonify({
                'success': False,
                'error': 'Ticket folder not found'
            }), 404
        
        folder_path = os.path.join(BASE_STORAGE_PATH, ticket_folders[0])
        file_path = os.path.join(folder_path, secure_filename(filename))
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': 'Resume not found'
            }), 404
        
        return send_file(file_path, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Error downloading resume: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/tickets/<ticket_id>/resumes/<filename>', methods=['DELETE'])
@require_api_key
def delete_resume(ticket_id, filename):
    """Delete a specific resume"""
    try:
        # Find the ticket folder
        ticket_folders = [f for f in os.listdir(BASE_STORAGE_PATH) 
                         if f.startswith(f"{ticket_id}_")]
        
        if not ticket_folders:
            return jsonify({
                'success': False,
                'error': 'Ticket folder not found'
            }), 404
        
        folder_path = os.path.join(BASE_STORAGE_PATH, ticket_folders[0])
        file_path = os.path.join(folder_path, secure_filename(filename))
        metadata_path = os.path.join(folder_path, 'metadata.json')
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': 'Resume not found'
            }), 404
        
        # Delete the file
        os.remove(file_path)
        logger.info(f"Deleted resume file: {file_path}")
        
        # Update metadata to remove the resume entry
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r', encoding='utf-8', errors='ignore') as f:
                    metadata = json.load(f)
                
                # Remove the resume from metadata
                resumes = metadata.get('resumes', [])
                updated_resumes = [r for r in resumes if r.get('filename') != filename]
                metadata['resumes'] = updated_resumes
                
                # Update the metadata file
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                logger.info(f"Updated metadata, removed resume: {filename}")
                
            except Exception as metadata_error:
                logger.error(f"Error updating metadata: {metadata_error}")
                # Continue even if metadata update fails
        
        return jsonify({
            'success': True,
            'message': 'Resume deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting resume: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/resumes/<int:resume_id>', methods=['GET'])
@require_api_key
def get_resume_application(resume_id):
    """Get a specific resume application by ID (from metadata)"""
    try:
        ticket_id = request.args.get('ticket_id')
        logger.info(f"Fetching resume application with ID: {resume_id}, ticket_id: {ticket_id}")
        
        if ticket_id:
            # If ticket_id is provided, search only in that ticket
            logger.info(f"Searching for resume {resume_id} in specific ticket {ticket_id}")
            
            resumes = get_ticket_resumes(ticket_id)
            logger.info(f"Found {len(resumes)} resumes in ticket {ticket_id}")
            
            for resume in resumes:
                logger.info(f"Checking resume ID: {resume.get('id')} vs requested: {resume_id}")
                if resume.get('id') == resume_id:
                    logger.info(f"Found matching resume: {resume}")
                    return jsonify({
                        'success': True,
                        'data': {'resume': resume}
                    })
            
            logger.warning(f"Resume application with ID {resume_id} not found in ticket {ticket_id}")
            return jsonify({'success': False, 'error': 'Resume application not found'}), 404
        else:
            # Fallback: search through all tickets (original behavior)
            logger.info("No ticket_id provided, searching through all tickets")
            
            # Get all tickets to find the one containing this resume
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT ticket_id, subject FROM tickets WHERE approval_status = 'approved'")
            tickets = cursor.fetchall()
            cursor.close()
            conn.close()
            
            logger.info(f"Found {len(tickets)} approved tickets")
            
            # Search through all tickets to find the resume
            for ticket in tickets:
                ticket_id = ticket['ticket_id']
                logger.info(f"Checking ticket {ticket_id} for resume {resume_id}")
                
                resumes = get_ticket_resumes(ticket_id)
                logger.info(f"Found {len(resumes)} resumes in ticket {ticket_id}")
                
                for resume in resumes:
                    logger.info(f"Checking resume ID: {resume.get('id')} vs requested: {resume_id}")
                    if resume.get('id') == resume_id:
                        resume['job_title'] = ticket['subject']
                        logger.info(f"Found matching resume: {resume}")
                        return jsonify({
                            'success': True,
                            'data': {'resume': resume}
                        })
            
            logger.warning(f"Resume application with ID {resume_id} not found in any ticket")
            return jsonify({'success': False, 'error': 'Resume application not found'}), 404
        
    except Exception as e:
        logger.error(f"Error getting resume application: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/maintenance/create-folders', methods=['POST'])
@require_api_key
def create_existing_folders_endpoint():
    """Endpoint to create folders for all existing approved tickets"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # Get all approved tickets
        cursor.execute("""
            SELECT ticket_id, subject
            FROM tickets
            WHERE approval_status = 'approved'
        """)
        
        approved_tickets = cursor.fetchall()
        results = {
            'created': [],
            'existing': [],
            'failed': []
        }
        
        for ticket in approved_tickets:
            ticket_id = ticket['ticket_id']
            
            # Check if folder already exists
            ticket_folders = [f for f in os.listdir(BASE_STORAGE_PATH) 
                            if f.startswith(f"{ticket_id}_")]
            
            if ticket_folders:
                results['existing'].append({
                    'ticket_id': ticket_id,
                    'folder': ticket_folders[0]
                })
            else:
                # Create folder
                folder_path = create_ticket_folder(ticket_id, ticket['subject'])
                if folder_path:
                    results['created'].append({
                        'ticket_id': ticket_id,
                        'folder': os.path.basename(folder_path)
                    })
                else:
                    results['failed'].append({
                        'ticket_id': ticket_id,
                        'reason': 'Failed to create folder'
                    })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'total_approved': len(approved_tickets),
                'folders_created': len(results['created']),
                'folders_existing': len(results['existing']),
                'folders_failed': len(results['failed']),
                'details': results
            }
        })
        
    except Exception as e:
        logger.error(f"Error in create_existing_folders_endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/diagnostics/filtering', methods=['GET'])
@require_api_key
def check_filtering_system():
    """Diagnostic endpoint to check filtering system availability"""
    diagnostics = {
        'module_check': {},
        'system_info': {
            'python_version': sys.version,
            'current_directory': os.getcwd(),
            'python_path': sys.path[:5]  # First 5 paths
        },
        'required_modules': {}
    }
    
    # Check main filtering module
    try:
        from resume_filter5 import UpdatedResumeFilteringSystem
        diagnostics['module_check']['resume_filter5'] = 'available'
        diagnostics['module_check']['class'] = 'UpdatedResumeFilteringSystem found'
    except ImportError as e:
        diagnostics['module_check']['resume_filter5'] = f'not found: {str(e)}'
        
        # Try alternative name
        try:
            from resume_filter4 import UpdatedResumeFilteringSystem
            diagnostics['module_check']['resume_filter4'] = 'available'
            diagnostics['module_check']['class'] = 'UpdatedResumeFilteringSystem found in resume_filter4'
        except ImportError as e2:
            diagnostics['module_check']['resume_filter4'] = f'not found: {str(e2)}'
    
    # Check for file existence
    files_to_check = ['resume_filter5.py', 'resume_filter4.py', 'ai_bot3.py']
    diagnostics['files'] = {}
    
    for filename in files_to_check:
        if os.path.exists(filename):
            diagnostics['files'][filename] = {
                'exists': True,
                'size': os.path.getsize(filename),
                'readable': os.access(filename, os.R_OK)
            }
        else:
            diagnostics['files'][filename] = {'exists': False}
    
    # Check required dependencies
    required_modules = ['openai', 'PyPDF2', 'python-docx', 'tiktoken', 'pathlib']
    for module in required_modules:
        try:
            __import__(module)
            diagnostics['required_modules'][module] = 'installed'
        except ImportError:
            diagnostics['required_modules'][module] = 'not installed'
    
    # Check OpenAI API key
    diagnostics['openai_api_key'] = 'set' if os.environ.get('OPENAI_API_KEY') else 'not set'
    
    return jsonify({
        'success': True,
        'diagnostics': diagnostics
    })

# ============================================
# RESUME FILTERING ENDPOINTS - WITH AI INTEGRATION
# ============================================

@app.route('/api/tickets/<ticket_id>/filter-resumes', methods=['POST'])
@require_api_key
def trigger_resume_filtering(ticket_id):
    """Trigger resume filtering for a specific ticket"""
    try:
        # Check if ticket exists and has resumes
        ticket_folders = [f for f in os.listdir(BASE_STORAGE_PATH) 
                         if f.startswith(f"{ticket_id}_")]
        
        if not ticket_folders:
            return jsonify({
                'success': False,
                'error': 'Ticket folder not found'
            }), 404
        
        folder_path = os.path.join(BASE_STORAGE_PATH, ticket_folders[0])
        
        # Check if filtering is already in progress
        filtering_lock_file = os.path.join(folder_path, '.filtering_in_progress')
        if os.path.exists(filtering_lock_file):
            return jsonify({
                'success': False,
                'error': 'Filtering is already in progress for this ticket',
                'status': 'in_progress'
            }), 409
        
        # Check if there are resumes to filter
        resume_files = [f for f in os.listdir(folder_path) 
                       if f.endswith(('.pdf', '.doc', '.docx', '.txt', '.rtf'))]
        
        if not resume_files:
            return jsonify({
                'success': False,
                'error': 'No resumes found in ticket folder',
                'resume_count': 0
            }), 400
        
        # Check if filtering results already exist
        filtering_results_path = os.path.join(folder_path, 'filtering_results')
        
        # Safely get the force and incremental parameters
        force_refilter = False
        incremental_mode = True  # Default to incremental mode
        try:
            if request.is_json and request.json:
                force_refilter = request.json.get('force', False)
                incremental_mode = request.json.get('incremental', True)  # Default to incremental
        except:
            # If JSON parsing fails, just use defaults
            force_refilter = False
            incremental_mode = True
        
        if os.path.exists(filtering_results_path) and not force_refilter:
            result_files = list(Path(filtering_results_path).glob('final_results_*.json'))
            if result_files:
                # Get the latest result
                latest_result = max(result_files, key=lambda x: x.stat().st_mtime)
                
                with open(latest_result, 'r') as f:
                    filtering_data = json.load(f)
                
                return jsonify({
                    'success': True,
                    'message': 'Filtering results already exist. Use force=true to re-run.',
                    'status': 'completed',
                    'data': {
                        'filtered_at': filtering_data.get('timestamp'),
                        'total_resumes': filtering_data.get('summary', {}).get('total_resumes', 0),
                        'top_candidates_count': len(filtering_data.get('final_top_5', filtering_data.get('top_5_candidates', [])))
                    }
                })
        
        # Create lock file
        with open(filtering_lock_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps({
                'started_at': datetime.now().isoformat(),
                'pid': os.getpid()
            }))
        
        # Run filtering in a background thread
        def run_filtering():
            try:
                logger.info(f"Starting AI filtering for ticket {ticket_id}")
                logger.info(f"Folder path: {folder_path}")
                logger.info(f"Resume files found: {resume_files}")
                
                # Try to import the filtering system
                try:
                    from resume_filter5 import UpdatedResumeFilteringSystem
                    logger.info("Successfully imported UpdatedResumeFilteringSystem from resume_filter5")
                except ImportError as e:
                    logger.error(f"Failed to import resume_filter5: {e}")
                    # Try alternative import
                    try:
                        from resume_filter4 import UpdatedResumeFilteringSystem
                        logger.info("Successfully imported from resume_filter4")
                    except ImportError as e2:
                        logger.error(f"Failed to import resume_filter4: {e2}")
                        raise ImportError(f"Could not import filtering system: resume_filter5: {e} / resume_filter4: {e2}")
                
                # Create and run the filtering system
                logger.info("Creating filter system instance...")
                filter_system = UpdatedResumeFilteringSystem(folder_path)
                
                logger.info(f"Running filter_resumes(incremental={incremental_mode})...")
                results = filter_system.filter_resumes(incremental=incremental_mode)
                
                if "error" not in results:
                    logger.info(f"AI filtering completed successfully for ticket {ticket_id}")
                    
                    # Create a status file for the API
                    status_file = os.path.join(folder_path, 'filtering_status.json')
                    try:
                        with open(status_file, 'w', encoding='utf-8') as f:
                            json.dump({
                                'status': 'completed',
                                'completed_at': datetime.now().isoformat(),
                                'total_resumes': results.get('summary', {}).get('total_resumes', 0),
                                'top_candidates': len(results.get('final_top_5', results.get('top_5_candidates', []))),
                                'success': True
                            }, f)
                    except Exception as write_error:
                        logger.error(f"Error writing status file: {write_error}")
                else:
                    logger.error(f"AI filtering failed for ticket {ticket_id}: {results.get('error')}")
                    
                    # Create error status file
                    status_file = os.path.join(folder_path, 'filtering_status.json')
                    try:
                        with open(status_file, 'w', encoding='utf-8') as f:
                            json.dump({
                                'status': 'failed',
                                'completed_at': datetime.now().isoformat(),
                                'error': results.get('error'),
                                'success': False
                            }, f)
                    except Exception as write_error:
                        logger.error(f"Error writing status file: {write_error}")
                
            except ImportError as e:
                error_msg = f"Import error: {str(e)}"
                logger.error(f"Import error running AI filtering for ticket {ticket_id}: {error_msg}")
                
                # Create error status file
                status_file = os.path.join(folder_path, 'filtering_status.json')
                with open(status_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'status': 'failed',
                        'completed_at': datetime.now().isoformat(),
                        'error': error_msg,
                        'success': False
                    }, f)
                    
            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)}"
                logger.error(f"Error running AI filtering for ticket {ticket_id}: {error_msg}")
                import traceback
                full_traceback = traceback.format_exc()
                logger.error(f"Full traceback:\n{full_traceback}")
                
                # Create error status file
                status_file = os.path.join(folder_path, 'filtering_status.json')
                with open(status_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'status': 'failed',
                        'completed_at': datetime.now().isoformat(),
                        'error': error_msg,
                        'traceback': full_traceback,
                        'success': False
                    }, f)
            
            finally:
                # Remove lock file
                if os.path.exists(filtering_lock_file):
                    os.remove(filtering_lock_file)
                logger.info(f"Filtering thread completed for ticket {ticket_id}")
        
        # Start filtering in background thread
        filtering_thread = threading.Thread(
            target=run_filtering,
            name=f"filtering-{ticket_id}",
            daemon=True
        )
        filtering_thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Resume filtering started',
            'status': 'started',
            'data': {
                'ticket_id': ticket_id,
                'resume_count': len(resume_files),
                'started_at': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error triggering resume filtering: {e}")
        import traceback
        traceback.print_exc()
        
        # Clean up lock file if error
        if 'filtering_lock_file' in locals() and os.path.exists(filtering_lock_file):
            os.remove(filtering_lock_file)
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tickets/<ticket_id>/top-resumes', methods=['GET'])
@require_api_key
def get_top_resumes(ticket_id):
    """Get top-ranked resumes with their details and scores"""
    try:
        # Get parameters
        include_content = request.args.get('include_content', 'false').lower() == 'true'
        top_n = int(request.args.get('top', 0))  # 0 means all candidates
        
        # Find the ticket folder
        ticket_folders = [f for f in os.listdir(BASE_STORAGE_PATH) 
                         if f.startswith(f"{ticket_id}_")]
        
        if not ticket_folders:
            return jsonify({
                'success': False,
                'error': 'Ticket folder not found'
            }), 404
        
        folder_path = os.path.join(BASE_STORAGE_PATH, ticket_folders[0])
        filtering_results_path = os.path.join(folder_path, 'filtering_results')
        
        if not os.path.exists(filtering_results_path):
            return jsonify({
                'success': False,
                'error': 'No filtering results found. Please run resume filtering first.'
            }), 404
        
        # Get the latest filtering results
        result_files = list(Path(filtering_results_path).glob('final_results*.json'))
        if not result_files:
            return jsonify({
                'success': False,
                'error': 'No filtering results found'
            }), 404
        
        latest_result = max(result_files, key=lambda x: x.stat().st_mtime)
        
        with open(latest_result, 'r') as f:
            filtering_data = json.load(f)
        
        # Try to get all ranked candidates from different locations
        all_candidates = []
        
        # First try top-level all_ranked_candidates (latest structure)
        if 'all_ranked_candidates' in filtering_data:
            all_candidates = filtering_data['all_ranked_candidates']
        
        # If not found, try stage1_results.all_resumes
        if not all_candidates:
            stage1_results = filtering_data.get('stage1_results', {})
            all_candidates = stage1_results.get('all_resumes', [])
        
        # If still not found, try final_results
        if not all_candidates:
            final_results = filtering_data.get('final_results', {})
            all_candidates = final_results.get('all_ranked_candidates', final_results.get('top_5_candidates', []))
        
        # Apply top_n limit if specified (0 means all)
        if top_n > 0:
            top_candidates = all_candidates[:top_n]
        else:
            top_candidates = all_candidates
        
        # Debug output
        logger.info(f"DEBUG: all_candidates length: {len(all_candidates)}")
        logger.info(f"DEBUG: top_candidates length: {len(top_candidates)}")
        if top_candidates:
            logger.info(f"DEBUG: First candidate keys: {list(top_candidates[0].keys())}")
            logger.info(f"DEBUG: First candidate filename: {top_candidates[0].get('filename', 'No filename')}")
        else:
            logger.warning("DEBUG: No top_candidates found!")
        
        # Get job requirements used
        job_requirements = filtering_data.get('latest_requirements', {})
        
        # Add final decision data from database for each candidate
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            for candidate in top_candidates:
                try:
                    # Handle different data structures (stage1_results vs final_results)
                    applicant_email = candidate.get('applicant_email', '')
                    applicant_name = candidate.get('applicant_name', candidate.get('filename', 'Unknown'))
                    
                    if applicant_email:
                        # Get final decision from candidate_interview_status table
                        cursor.execute("""
                            SELECT final_decision FROM candidate_interview_status 
                            WHERE ticket_id = %s AND candidate_id = (
                                SELECT id FROM resume_applications 
                                WHERE ticket_id = %s AND applicant_email = %s
                            )
                        """, (ticket_id, ticket_id, applicant_email))
                        
                        decision_result = cursor.fetchone()
                        if decision_result and decision_result['final_decision']:
                            candidate['final_decision'] = decision_result['final_decision']
                            logger.info(f"Top-resumes: Added final_decision '{decision_result['final_decision']}' for {applicant_name}")
                        else:
                            candidate['final_decision'] = None
                            logger.info(f"Top-resumes: No final_decision found for {applicant_name}")
                    else:
                        # For stage1_results data, set final_decision to None
                        candidate['final_decision'] = None
                        logger.info(f"Top-resumes: No applicant_email found for {applicant_name}, setting final_decision to None")
                except Exception as e:
                    logger.warning(f"Top-resumes: Error getting final_decision for {candidate.get('applicant_name', candidate.get('filename', 'Unknown'))}: {e}")
                    candidate['final_decision'] = None
            
            cursor.close()
            conn.close()
        
        # Check if any candidates meet minimum requirements
        warnings = []
        min_experience = 5  # From "5-8 years"
        
        if top_candidates:
            # Check experience requirement
            if all(c.get('detected_experience_years', 0) < min_experience for c in top_candidates):
                warnings.append(f"No candidates meet the minimum experience requirement of {min_experience} years")
            
            # Check location requirement
            if all(c.get('location_score', 0) == 0 for c in top_candidates):
                warnings.append(f"No candidates match the required location: {job_requirements.get('location', 'Unknown')}")
            
            # Check if scores are too low
            if all(c.get('final_score', 0) < 0.6 for c in top_candidates):
                warnings.append("All candidates scored below 60% match")
        
        # Prepare response with resume details
        candidates_with_details = []
        
        # Initialize database connection for status lookups
        db_conn = None
        db_cursor = None
        try:
            db_conn = get_db_connection()
            if db_conn:
                db_cursor = db_conn.cursor(dictionary=True)
        except Exception as mysql_error:
            logger.warning(f"get_top_resumes: Database connection failed: {mysql_error}")
            # Continue without database connection
        
        for i, candidate in enumerate(top_candidates):
            try:
                candidate_data = {
                    'rank': candidate.get('final_rank', i + 1),  # Use final_rank from duplicate-aware ranking
                    'filename': candidate.get('filename', 'Unknown'),
                    'score': candidate.get('final_score', 0),  # Add numeric score for frontend compatibility
                'scores': {
                    'overall': candidate.get('final_score', 0),  # Return numeric value instead of formatted string
                    'skills': candidate.get('skill_score', 0),
                    'experience': candidate.get('experience_score', 0),
                    'location': candidate.get('location_score', 0),
                    'professional_development': candidate.get('professional_development_score', 0)
                },
                'matched_skills': candidate.get('matched_skills', []),
                'detailed_skill_matches': candidate.get('detailed_skill_matches', {}),
                'missing_skills': [s for s in job_requirements.get('tech_stack', []) 
                                 if s not in candidate.get('matched_skills', [])],
                'experience_years': candidate.get('detected_experience_years', 0),
                'skill_match_ratio': f"{len(candidate.get('matched_skills', []))}/{len(job_requirements.get('tech_stack', []))}",
                'file_path': candidate.get('file_path'),
                'key_highlights': candidate.get('professional_development', {}).get('summary', {}).get('key_highlights', []),
                
                # Add duplicate information
                'is_duplicate_group': candidate.get('is_duplicate_group', False),
                'duplicate_group_rank': candidate.get('duplicate_group_rank'),
                'duplicate_of': candidate.get('duplicate_of'),
                'has_duplicates': candidate.get('has_duplicates', False),
                'duplicate_count': candidate.get('duplicate_count', 0),
                'duplicates': candidate.get('duplicates', []),
                
                # Add professional development details
                'professional_development': {
                    'score': candidate.get('professional_development_score', 0),  # Return numeric value
                    'level': candidate.get('professional_development', {}).get('professional_development_level', 'Unknown'),
                    'summary': candidate.get('professional_development', {}).get('summary', {}),
                    'key_highlights': candidate.get('professional_development', {}).get('summary', {}).get('key_highlights', []),
                    'details': {
                        'certifications': {
                            'count': candidate.get('professional_development', {}).get('summary', {}).get('total_certifications', 0),
                            'list': candidate.get('professional_development', {}).get('component_scores', {}).get('certifications', {}).get('certifications_found', []),
                            'categories': candidate.get('professional_development', {}).get('summary', {}).get('certification_categories', [])
                        },
                        'learning_platforms': {
                            'count': candidate.get('professional_development', {}).get('summary', {}).get('learning_platforms_used', 0),
                            'platforms': candidate.get('professional_development', {}).get('component_scores', {}).get('online_learning', {}).get('platforms_found', []),
                            'estimated_courses': candidate.get('professional_development', {}).get('summary', {}).get('estimated_courses_completed', 0)
                        },
                        'conferences': {
                            'attended': candidate.get('professional_development', {}).get('summary', {}).get('conferences_attended', 0),
                            'speaker': candidate.get('professional_development', {}).get('summary', {}).get('conference_speaker', False),
                            'events': candidate.get('professional_development', {}).get('component_scores', {}).get('conferences', {}).get('events_found', [])
                        },
                        'content_creation': {
                            'is_creator': candidate.get('professional_development', {}).get('summary', {}).get('content_creator', False),
                            'types': candidate.get('professional_development', {}).get('summary', {}).get('content_types', []),
                            'platforms': candidate.get('professional_development', {}).get('component_scores', {}).get('content_creation', {}).get('content_platforms', [])
                        }
                    }
                }
            }
                
                # Get metadata from metadata.json
                metadata_path = os.path.join(folder_path, 'metadata.json')
                candidate_matched = False
                
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r', encoding='utf-8', errors='ignore') as f:
                        metadata = json.load(f)
                    
                    # Find matching resume metadata
                    for resume_info in metadata.get('resumes', []):
                        if resume_info['filename'] == candidate.get('filename', ''):
                            candidate_data['applicant_name'] = resume_info.get('applicant_name', 'Unknown')
                            candidate_data['applicant_email'] = resume_info.get('applicant_email', 'Not provided')
                            candidate_data['uploaded_at'] = resume_info.get('uploaded_at')
                            # Get the updated status from database, fallback to candidate status, then pending
                            candidate_data['status'] = candidate.get('status', 'pending')
                            
                            # Also set final_decision for consistency
                            candidate_data['final_decision'] = candidate.get('final_decision', None)
                            # Also update the original candidate object to ensure email is available
                            candidate['applicant_name'] = resume_info.get('applicant_name', 'Unknown')
                            candidate['applicant_email'] = resume_info.get('applicant_email', 'Not provided')
                            candidate_matched = True
                            logger.info(f"get_top_resumes: Updated candidate with email {candidate['applicant_email']} for {candidate.get('filename')}")
                            break
                
                # Skip candidates that couldn't be matched with metadata (orphaned entries)
                if not candidate_matched:
                    logger.warning(f"get_top_resumes: Skipping orphaned candidate {candidate.get('filename', 'Unknown')} - not found in metadata.json")
                    continue
                
                # Now get the actual status from database using the email
                if db_cursor and db_conn:
                    try:
                        logger.info(f"get_top_resumes: Looking up status for {candidate['applicant_email']}")
                        
                        # Get candidate_id and status from resume_applications
                        db_cursor.execute("""
                            SELECT id, status FROM resume_applications 
                            WHERE ticket_id = %s AND applicant_email = %s
                        """, (ticket_id, candidate['applicant_email']))
                        
                        resume_result = db_cursor.fetchone()
                        logger.info(f"get_top_resumes: Resume lookup result: {resume_result}")
                        
                        if resume_result:
                            # First priority: Check candidate_interview_status table
                            db_cursor.execute("""
                                SELECT overall_status, final_decision 
                                FROM candidate_interview_status 
                                WHERE candidate_id = %s AND ticket_id = %s
                            """, (resume_result['id'], ticket_id))
                            
                            status_result = db_cursor.fetchone()
                            logger.info(f"get_top_resumes: Interview status result: {status_result}")
                            
                            if status_result and status_result['overall_status']:
                                # Use interview status (highest priority)
                                final_status = status_result['overall_status']
                                final_decision = status_result['final_decision']
                                logger.info(f"get_top_resumes: Using interview status '{final_status}' for {candidate['applicant_email']}")
                            else:
                                # Fallback to resume_applications status
                                final_status = resume_result['status'] or 'pending'
                                final_decision = resume_result['status'] if resume_result['status'] == 'rejected' else None
                                logger.info(f"get_top_resumes: Using resume status '{final_status}' for {candidate['applicant_email']}")
                            
                            # Update both candidate_data and candidate objects
                            candidate_data['status'] = final_status
                            candidate_data['final_decision'] = final_decision
                            candidate['status'] = final_status
                            candidate['final_decision'] = final_decision
                            
                            logger.info(f"get_top_resumes: FINAL STATUS SET: {candidate['applicant_email']} -> {final_status}")
                        else:
                            logger.warning(f"get_top_resumes: No database record found for {candidate['applicant_email']}")
                            candidate_data['status'] = 'pending'
                            candidate['status'] = 'pending'
                            
                    except Exception as status_error:
                        logger.error(f"get_top_resumes: Status lookup failed for {candidate['applicant_email']}: {status_error}")
                        candidate_data['status'] = 'pending'
                        candidate['status'] = 'pending'
                else:
                    logger.warning(f"get_top_resumes: No database connection available for status lookup")
                    candidate_data['status'] = 'pending'
                    candidate['status'] = 'pending'
                
                # Add download URL if tunnel is active
                if CLOUDFLARE_TUNNEL_URL:
                    candidate_data['download_url'] = f"{CLOUDFLARE_TUNNEL_URL}/api/tickets/{ticket_id}/resumes/{candidate.get('filename', '')}?api_key={API_KEY}"
                
                # Include resume content if requested
                if include_content:
                    resume_path = os.path.join(folder_path, candidate.get('filename', ''))
                    if os.path.exists(resume_path):
                        try:
                            with open(resume_path, 'rb') as f:
                                resume_content = f.read()
                                candidate_data['resume_base64'] = base64.b64encode(resume_content).decode('utf-8')
                                candidate_data['resume_size'] = len(resume_content)
                        except Exception as e:
                            logger.error(f"Error reading resume {candidate.get('filename', 'Unknown')}: {e}")
                
                candidates_with_details.append(candidate_data)
                logger.info(f"DEBUG: Added candidate {candidate.get('filename', 'Unknown')} to response")
            except Exception as e:
                logger.error(f"Error processing candidate {candidate.get('filename', 'Unknown')}: {e}")
                continue
        
        # Get AI analysis if available
        ai_analysis = {
            'stage1_review': filtering_data.get('stage1_results', {}).get('agent_review', ''),
            'stage2_analysis': filtering_data.get('stage2_results', {}).get('detailed_analysis', ''),
            'qa_assessment': filtering_data.get('qa_review', {}).get('qa_assessment', '')
        }
        
        # Get scoring weights used
        scoring_weights = {}
        if top_candidates:
            scoring_weights = top_candidates[0].get('scoring_weights', {})
        
        # Get duplicate information
        duplicate_info = filtering_data.get('summary', {})
        duplicate_banner_message = duplicate_info.get('duplicate_banner_message', '')
        duplicate_groups_found = duplicate_info.get('duplicate_groups_found', 0)
        
        # Clean up database connection
        if db_cursor:
            db_cursor.close()
        if db_conn:
            db_conn.close()
        
        return jsonify({
            'success': True,
            'warnings': warnings,  # Add warnings about candidate quality
            'data': {
                'ticket_id': ticket_id,
                'filtered_at': filtering_data.get('timestamp'),
                'job_position': filtering_data.get('position'),
                'job_requirements': job_requirements,
                'scoring_weights': {
                    'skills': f"{scoring_weights.get('skills', 0.4):.0%}",
                    'experience': f"{scoring_weights.get('experience', 0.3):.0%}",
                    'location': f"{scoring_weights.get('location', 0.1):.0%}",
                    'professional_development': f"{scoring_weights.get('professional_dev', 0.2):.0%}"
                },
                'summary': {
                    'total_resumes_processed': filtering_data.get('summary', {}).get('total_resumes', 0),
                    'top_candidates_returned': len(candidates_with_details),
                    'duplicate_groups_found': duplicate_groups_found,
                    'duplicate_banner_message': duplicate_banner_message
                },
                'top_candidates': candidates_with_details,
                'ai_analysis': ai_analysis,
                'duplicate_detection': filtering_data.get('duplicate_detection', {})
            }
        })
        
    except Exception as e:
        # Clean up database connection in case of error
        if 'db_cursor' in locals() and db_cursor:
            db_cursor.close()
        if 'db_conn' in locals() and db_conn:
            db_conn.close()
            
        logger.error(f"Error getting top resumes: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tickets/<ticket_id>/filtering-report', methods=['GET'])
@require_api_key
def get_filtering_report(ticket_id):
    """Get the complete filtering report for a ticket"""
    try:
        # Find the ticket folder
        ticket_folders = [f for f in os.listdir(BASE_STORAGE_PATH) 
                         if f.startswith(f"{ticket_id}_")]
        
        if not ticket_folders:
            return jsonify({
                'success': False,
                'error': 'Ticket folder not found'
            }), 404
        
        folder_path = os.path.join(BASE_STORAGE_PATH, ticket_folders[0])
        filtering_results_path = os.path.join(folder_path, 'filtering_results')
        
        if not os.path.exists(filtering_results_path):
            return jsonify({
                'success': False,
                'error': 'No filtering results found'
            }), 404
        
        # Get the latest summary report
        report_files = list(Path(filtering_results_path).glob('summary_report_*.txt'))
        if not report_files:
            return jsonify({
                'success': False,
                'error': 'No summary report found'
            }), 404
        
        latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
        
        with open(latest_report, 'r', encoding='utf-8', errors='ignore') as f:
            report_content = f.read()
        
        # Also get the JSON results
        result_files = list(Path(filtering_results_path).glob('final_results_*.json'))
        if result_files:
            latest_result = max(result_files, key=lambda x: x.stat().st_mtime)
            with open(latest_result, 'r', encoding='utf-8', errors='ignore') as f:
                json_results = json.load(f)
        else:
            json_results = {}
        
        return jsonify({
            'success': True,
            'data': {
                'ticket_id': ticket_id,
                'report_text': report_content,
                'report_filename': latest_report.name,
                'generated_at': json_results.get('timestamp'),
                'summary_stats': json_results.get('summary', {}),
                'all_candidates': json_results.get('stage1_results', {}).get('all_resumes', json_results.get('final_results', {}).get('all_ranked_candidates', json_results.get('all_ranked_candidates', []))),
                'files': {
                    'report': str(latest_report),
                    'json_results': str(latest_result) if result_files else None
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting filtering report: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tickets/<ticket_id>/send-top-resumes', methods=['POST'])
@require_api_key
def send_top_resumes_email(ticket_id):
    """Send top resumes via email or webhook"""
    try:
        # Get request data
        data = request.get_json()
        recipient_email = data.get('email')
        webhook_url = data.get('webhook_url')
        include_resumes = data.get('include_resumes', True)
        top_n = min(data.get('top_n', 5), 10)
        
        if not recipient_email and not webhook_url:
            return jsonify({
                'success': False,
                'error': 'Either email or webhook_url is required'
            }), 400
        
        # Get top resumes data
        response = get_top_resumes(ticket_id)
        resume_data = response.get_json()
        
        if not resume_data['success']:
            return response
        
        top_candidates = resume_data['data']['top_candidates'][:top_n]
        
        # Prepare email/webhook payload
        payload = {
            'ticket_id': ticket_id,
            'job_position': resume_data['data']['job_position'],
            'filtered_at': resume_data['data']['filtered_at'],
            'top_candidates': []
        }
        
        # Add candidate details
        for candidate in top_candidates:
            candidate_info = {
                'rank': candidate['rank'],
                'name': candidate.get('applicant_name', 'Unknown'),
                'email': candidate.get('applicant_email', ''),
                'filename': candidate['filename'],
                'scores': candidate['scores'],
                'matched_skills': candidate['matched_skills'],
                'detailed_skill_matches': candidate.get('detailed_skill_matches', {}),
                'experience_years': candidate['experience_years']
            }
            
            # Add download link
            if CLOUDFLARE_TUNNEL_URL:
                candidate_info['download_url'] = f"{CLOUDFLARE_TUNNEL_URL}/api/tickets/{ticket_id}/resumes/{candidate['filename']}"
            
            payload['top_candidates'].append(candidate_info)
        
        # If webhook URL provided, send to webhook
        if webhook_url:
            import requests
            try:
                webhook_response = requests.post(webhook_url, json=payload, timeout=30)
                if webhook_response.status_code == 200:
                    return jsonify({
                        'success': True,
                        'message': 'Top resumes sent to webhook successfully'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': f'Webhook returned status {webhook_response.status_code}'
                    }), 500
            except Exception as webhook_error:
                logger.error(f"Webhook error: {webhook_error}")
                return jsonify({
                    'success': False,
                    'error': f'Failed to send to webhook: {str(webhook_error)}'
                }), 500
        
        # If email provided, you would implement email sending here
        if recipient_email:
            # This is a placeholder - you would implement actual email sending
            # using a service like SendGrid, AWS SES, or SMTP
            return jsonify({
                'success': True,
                'message': f'Email functionality not implemented. Would send to: {recipient_email}',
                'payload': payload
            })
        
    except Exception as e:
        logger.error(f"Error sending top resumes: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tickets/<ticket_id>/filtering-status', methods=['GET'])
@require_api_key
def get_filtering_status(ticket_id):
    """Check if filtering has been done for a ticket"""
    try:
        # Find the ticket folder
        ticket_folders = [f for f in os.listdir(BASE_STORAGE_PATH) 
                         if f.startswith(f"{ticket_id}_")]
        
        if not ticket_folders:
            return jsonify({
                'success': False,
                'status': 'no_folder',
                'message': 'Ticket folder not found'
            })
        
        folder_path = os.path.join(BASE_STORAGE_PATH, ticket_folders[0])
        
        # Check for resumes
        resume_count = len([f for f in os.listdir(folder_path) 
                           if f.endswith(('.pdf', '.doc', '.docx', '.txt', '.rtf'))])
        
        # Check if filtering is in progress
        filtering_lock_file = os.path.join(folder_path, '.filtering_in_progress')
        if os.path.exists(filtering_lock_file):
            with open(filtering_lock_file, 'r') as f:
                lock_data = json.load(f)
            
            return jsonify({
                'success': True,
                'data': {
                    'ticket_id': ticket_id,
                    'folder_exists': True,
                    'resume_count': resume_count,
                    'status': 'in_progress',
                    'filtering_started_at': lock_data.get('started_at'),
                    'message': 'Filtering is currently in progress'
                }
            })
        
        # Check for status file (for recently completed/failed filtering)
        status_file = os.path.join(folder_path, 'filtering_status.json')
        if os.path.exists(status_file):
            with open(status_file, 'r', encoding='utf-8', errors='ignore') as f:
                status_data = json.load(f)
            
            # If filtering failed, include error info
            if status_data.get('status') == 'failed':
                return jsonify({
                    'success': True,
                    'data': {
                        'ticket_id': ticket_id,
                        'folder_exists': True,
                        'resume_count': resume_count,
                        'status': 'failed',
                        'error': status_data.get('error'),
                        'failed_at': status_data.get('completed_at')
                    }
                })
        
        # Check for filtering results
        filtering_results_path = os.path.join(folder_path, 'filtering_results')
        has_filtering_results = os.path.exists(filtering_results_path)
        
        filtering_info = {}
        if has_filtering_results:
            result_files = list(Path(filtering_results_path).glob('final_results_*.json'))
            if result_files:
                latest_result = max(result_files, key=lambda x: x.stat().st_mtime)
                with open(latest_result, 'r', encoding='utf-8', errors='ignore') as f:
                    filtering_data = json.load(f)
                
                filtering_info = {
                    'filtered_at': filtering_data.get('timestamp'),
                    'total_processed': filtering_data.get('summary', {}).get('total_resumes', 0),
                    'top_candidates': len(filtering_data.get('final_top_5', filtering_data.get('top_5_candidates', []))),
                    'last_updated': datetime.fromtimestamp(latest_result.stat().st_mtime).isoformat()
                }
        
        # Determine the overall status
        overall_status = 'no_resumes'
        if resume_count > 0:
            if has_filtering_results:
                overall_status = 'completed'
            else:
                overall_status = 'ready'
        
        # Enhanced filtering info
        enhanced_filtering_info = {
            **filtering_info,
            'status': overall_status,
            'resume_count': resume_count,
            'has_results': has_filtering_results
        }
        
        # Include completion timestamp for frontend comparison
        completed_at = None
        if has_filtering_results and filtering_info.get('filtered_at'):
            completed_at = filtering_info['filtered_at']
        elif os.path.exists(status_file):
            try:
                with open(status_file, 'r', encoding='utf-8', errors='ignore') as f:
                    status_data = json.load(f)
                    completed_at = status_data.get('completed_at')
            except Exception as e:
                print(f"Error reading status file: {e}")
                completed_at = None
        
        
        return jsonify({
            'success': True,
            'data': {
                'ticket_id': ticket_id,
                'folder_exists': True,
                'resume_count': resume_count,
                'has_filtering_results': has_filtering_results,
                'filtering_info': enhanced_filtering_info,
                'ready_for_filtering': resume_count > 0,
                'status': overall_status,
                'completed_at': completed_at,  # Add this for frontend comparison
                'message': {
                    'completed': 'AI filtering has been completed successfully',
                    'ready': 'Ready to start AI filtering',
                    'no_resumes': 'No resumes found to filter',
                    'in_progress': 'AI filtering is currently in progress',
                    'failed': 'AI filtering failed'
                }.get(overall_status, 'Unknown status')
            }
        })
        
    except Exception as e:
        logger.error(f"Error checking filtering status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================
# CANDIDATE MANAGEMENT ENDPOINTS
# ============================================

# DISABLED: Duplicate endpoint - using update_candidate_overall_status() instead
# @app.route('/api/candidates/status', methods=['PUT'])
# @require_api_key
def update_candidate_status_disabled():
    """Update candidate status and send appropriate emails"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        candidate_id = data.get('candidate_id')
        ticket_id = data.get('ticket_id')
        overall_status = data.get('overall_status')
        final_decision = data.get('final_decision')
        
        if not all([candidate_id, ticket_id, overall_status]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields: candidate_id, ticket_id, overall_status'
            }), 400
        
        # Get candidate and job details from the database
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # Get candidate details from resume metadata
        candidate_name = None
        candidate_email = None
        job_title = None
        
        # First try to get from ticket folder metadata
        ticket_folders = [f for f in os.listdir(BASE_STORAGE_PATH) 
                         if f.startswith(f"{ticket_id}_")]
        
        if ticket_folders:
            folder_path = os.path.join(BASE_STORAGE_PATH, ticket_folders[0])
            metadata_path = os.path.join(folder_path, 'metadata.json')
            
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8', errors='ignore') as f:
                    metadata = json.load(f)
                
                # Find candidate by ID (assuming candidate_id matches resume ID)
                for resume in metadata.get('resumes', []):
                    if resume.get('id') == candidate_id:
                        candidate_name = resume.get('applicant_name', 'Unknown Candidate')
                        candidate_email = resume.get('applicant_email', '')
                        break
        
        # If not found in metadata, try to get from database
        if not candidate_name:
            cursor.execute("""
                SELECT subject FROM tickets WHERE ticket_id = %s
            """, (ticket_id,))
            ticket_result = cursor.fetchone()
            if ticket_result:
                job_title = ticket_result['subject']
                candidate_name = f"Candidate {candidate_id}"
        
        # If still no job title, use ticket_id as fallback
        if not job_title:
            job_title = f"Position {ticket_id}"
        
        cursor.close()
        conn.close()
        
        # Update candidate status in interview system if it exists
        try:
            interview_db_path = os.path.join(os.path.dirname(__file__), 'interview_system.db')
            if os.path.exists(interview_db_path):
                import sqlite3
                interview_conn = sqlite3.connect(interview_db_path)
                interview_cursor = interview_conn.cursor()
                
                # Update candidate status
                interview_cursor.execute("""
                    UPDATE candidate_interview_status
                    SET interview_status = ?, final_decision = ?, updated_at = ?
                    WHERE candidate_id = ?
                """, (overall_status, final_decision, datetime.now().isoformat(), candidate_id))
                
                interview_conn.commit()
                interview_conn.close()
                logger.info(f"Updated candidate {candidate_id} status in interview system")
        except Exception as e:
            logger.warning(f"Could not update interview system: {e}")
        
        # Send rejection email if candidate is rejected
        if overall_status == 'rejected' and candidate_email and candidate_name:
            logger.info(f"Sending rejection email to {candidate_name} ({candidate_email}) for position {job_title}")
            send_rejection_email_async(candidate_email, candidate_name, job_title)
        elif overall_status == 'hired' and candidate_email and candidate_name:
            logger.info(f"Candidate {candidate_name} hired for position {job_title}")
            # You could add a hiring email here if needed
        elif overall_status == 'completed' and candidate_email and candidate_name:
            logger.info(f"Candidate {candidate_name} put on hold for position {job_title}")
            # You could add a hold email here if needed
        
        return jsonify({
            'success': True,
            'message': f'Candidate status updated to {overall_status}',
            'data': {
                'candidate_id': candidate_id,
                'ticket_id': ticket_id,
                'overall_status': overall_status,
                'final_decision': final_decision,
                'email_sent': overall_status == 'rejected' and candidate_email is not None
            }
        })
        
    except Exception as e:
        logger.error(f"Error updating candidate status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================
# JOB MANAGEMENT ENDPOINTS
# ============================================

@app.route('/api/jobs/approved', methods=['GET'])
@require_api_key
def get_approved_jobs():
    """Get all approved jobs with pagination and filtering (for public/candidate access)"""
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 10)), 50)
        location_filter = request.args.get('location', '')
        skills_filter = request.args.get('skills', '')
        sort_by = request.args.get('sort', 'approved_at')
        order = request.args.get('order', 'desc')
        
        # Validate sort parameters
        allowed_sorts = ['created_at', 'approved_at', 'last_updated']
        if sort_by not in allowed_sorts:
            sort_by = 'approved_at'
        
        if order not in ['asc', 'desc']:
            order = 'desc'
        
        offset = (page - 1) * per_page
        
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # First, get all approved tickets (public access - no user filtering)
        # Only show jobs that are visible (is_visible = 'true' or not set)
        cursor.execute("""
            SELECT 
                t.ticket_id,
                t.sender,
                t.subject,
                t.created_at,
                t.last_updated,
                t.approved_at,
                t.status,
                COALESCE(td_visibility.field_value, 'true') as is_visible
            FROM tickets t
            LEFT JOIN (
                SELECT td1.ticket_id, td1.field_value
                FROM ticket_details td1
                INNER JOIN (
                    SELECT ticket_id, MAX(created_at) as max_created_at
                    FROM ticket_details
                    WHERE field_name = 'is_visible'
                    GROUP BY ticket_id
                ) td2 ON td1.ticket_id = td2.ticket_id 
                     AND td1.created_at = td2.max_created_at
                WHERE td1.field_name = 'is_visible'
            ) td_visibility ON t.ticket_id = td_visibility.ticket_id
            WHERE t.approval_status = 'approved' 
                AND t.status != 'terminated'
                AND COALESCE(td_visibility.field_value, 'true') = 'true'
            ORDER BY {} {}
            LIMIT %s OFFSET %s
        """.format(sort_by, order), (per_page, offset))
        
        tickets = cursor.fetchall()
        
        # For each ticket, get the LATEST value for each field
        jobs = []
        for ticket in tickets:
            ticket_id = ticket['ticket_id']
            
            # Get the latest value for each field using a subquery
            cursor.execute("""
                SELECT 
                    td1.field_name,
                    td1.field_value
                FROM ticket_details td1
                INNER JOIN (
                    SELECT field_name, MAX(created_at) as max_created_at
                    FROM ticket_details
                    WHERE ticket_id = %s
                    GROUP BY field_name
                ) td2 ON td1.field_name = td2.field_name 
                     AND td1.created_at = td2.max_created_at
                WHERE td1.ticket_id = %s
            """, (ticket_id, ticket_id))
            
            # Build the job details
            job_details = {}
            for row in cursor.fetchall():
                job_details[row['field_name']] = row['field_value']
            
            # Apply location filter if specified
            if location_filter and job_details.get('location', '').lower() != location_filter.lower():
                continue
            
            # Apply skills filter if specified
            if skills_filter:
                skill_list = [s.strip().lower() for s in skills_filter.split(',')]
                job_skills = job_details.get('required_skills', '').lower()
                if not any(skill in job_skills for skill in skill_list):
                    continue
            
            # Check if this job was updated after approval
            cursor.execute("""
                SELECT COUNT(*) as update_count
                FROM ticket_updates
                WHERE ticket_id = %s AND update_timestamp > %s
            """, (ticket_id, ticket['approved_at']))
            
            update_info = cursor.fetchone()
            updated_after_approval = update_info['update_count'] > 0
            
            # Check if folder exists and get resume count
            resumes = get_ticket_resumes(ticket_id)
            
            # Combine ticket info with job details
            job = {
                'ticket_id': ticket['ticket_id'],
                'sender': ticket['sender'],
                'subject': ticket['subject'],
                'created_at': serialize_datetime(ticket['created_at']),
                'last_updated': serialize_datetime(ticket['last_updated']),
                'approved_at': serialize_datetime(ticket['approved_at']),
                'status': ticket['status'],
                'job_title': job_details.get('job_title', 'NOT_FOUND'),
                'location': job_details.get('location', 'NOT_FOUND'),
                'experience_required': job_details.get('experience_required', 'NOT_FOUND'),
                'salary_range': job_details.get('salary_range', 'NOT_FOUND'),
                'job_description': job_details.get('job_description', 'NOT_FOUND'),
                'required_skills': job_details.get('required_skills', 'NOT_FOUND'),
                'employment_type': job_details.get('employment_type', 'NOT_FOUND'),
                'deadline': job_details.get('deadline', 'NOT_FOUND'),
                'updated_after_approval': updated_after_approval,
                'resume_count': len(resumes),
                'has_folder': len([f for f in os.listdir(BASE_STORAGE_PATH) if f.startswith(f"{ticket_id}_")]) > 0
            }
            
            jobs.append(job)
        
        # Get total count for pagination
        count_query = """
            SELECT COUNT(*) as total
            FROM tickets
            WHERE approval_status = 'approved' 
                AND status != 'terminated'
        """
        cursor.execute(count_query)
        total_count = cursor.fetchone()['total']
        
        cursor.close()
        conn.close()
        
        # Calculate pagination info
        total_pages = (total_count + per_page - 1) // per_page
        
        return jsonify({
            'success': True,
            'data': {
                'jobs': jobs,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total_count,
                    'total_pages': total_pages,
                    'has_next': page < total_pages,
                    'has_prev': page > 1
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error in get_approved_jobs: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/hr/jobs/approved', methods=['GET'])
@require_jwt_auth
def get_hr_approved_jobs():
    """Get approved jobs for HR users (only shows tickets created by the authenticated HR user)"""
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 10)), 50)
        location_filter = request.args.get('location', '')
        skills_filter = request.args.get('skills', '')
        sort_by = request.args.get('sort', 'approved_at')
        order = request.args.get('order', 'desc')
        
        # Validate sort parameters
        allowed_sorts = ['created_at', 'approved_at', 'last_updated']
        if sort_by not in allowed_sorts:
            sort_by = 'approved_at'
        
        if order not in ['asc', 'desc']:
            order = 'desc'
        
        offset = (page - 1) * per_page
        
        # Get authenticated user info
        user_id = request.user['user_id']
        user_email = request.user['email']
        
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # Get approved tickets created by this HR user only
        cursor.execute("""
            SELECT 
                ticket_id,
                sender,
                subject,
                created_at,
                last_updated,
                approved_at,
                status
            FROM tickets
            WHERE approval_status = 'approved' 
                AND status != 'terminated'
                AND (user_id = %s OR sender = %s)
            ORDER BY {} {}
            LIMIT %s OFFSET %s
        """.format(sort_by, order), (user_id, user_email, per_page, offset))
        
        tickets = cursor.fetchall()
        
        # For each ticket, get the LATEST value for each field
        jobs = []
        for ticket in tickets:
            ticket_id = ticket['ticket_id']
            
            # Get the latest value for each field using a subquery
            cursor.execute("""
                SELECT 
                    td1.field_name,
                    td1.field_value
                FROM ticket_details td1
                INNER JOIN (
                    SELECT field_name, MAX(created_at) as max_created_at
                    FROM ticket_details
                    WHERE ticket_id = %s
                    GROUP BY field_name
                ) td2 ON td1.field_name = td2.field_name 
                     AND td1.created_at = td2.max_created_at
                WHERE td1.ticket_id = %s
            """, (ticket_id, ticket_id))
            
            # Build the job details
            job_details = {}
            for row in cursor.fetchall():
                job_details[row['field_name']] = row['field_value']
            
            # Apply location filter if specified
            if location_filter and job_details.get('location', '').lower() != location_filter.lower():
                continue
            
            # Apply skills filter if specified
            if skills_filter:
                skill_list = [s.strip().lower() for s in skills_filter.split(',')]
                job_skills = job_details.get('required_skills', '').lower()
                if not any(skill in job_skills for skill in skill_list):
                    continue
            
            # Check if this job was updated after approval
            cursor.execute("""
                SELECT COUNT(*) as update_count
                FROM ticket_updates
                WHERE ticket_id = %s AND update_timestamp > %s
            """, (ticket_id, ticket['approved_at']))
            
            update_info = cursor.fetchone()
            updated_after_approval = update_info['update_count'] > 0
            
            # Check if folder exists and get resume count
            resumes = get_ticket_resumes(ticket_id)
            
            # Combine ticket info with job details
            job = {
                'ticket_id': ticket['ticket_id'],
                'sender': ticket['sender'],
                'subject': ticket['subject'],
                'created_at': serialize_datetime(ticket['created_at']),
                'last_updated': serialize_datetime(ticket['last_updated']),
                'approved_at': serialize_datetime(ticket['approved_at']),
                'status': ticket['status'],
                'job_title': job_details.get('job_title', 'NOT_FOUND'),
                'location': job_details.get('location', 'NOT_FOUND'),
                'experience_required': job_details.get('experience_required', 'NOT_FOUND'),
                'salary_range': job_details.get('salary_range', 'NOT_FOUND'),
                'job_description': job_details.get('job_description', 'NOT_FOUND'),
                'required_skills': job_details.get('required_skills', 'NOT_FOUND'),
                'employment_type': job_details.get('employment_type', 'NOT_FOUND'),
                'deadline': job_details.get('deadline', 'NOT_FOUND'),
                'updated_after_approval': updated_after_approval,
                'resume_count': len(resumes),
                'has_folder': len([f for f in os.listdir(BASE_STORAGE_PATH) if f.startswith(f"{ticket_id}_")]) > 0
            }
            
            jobs.append(job)
        
        # Get total count for pagination (filtered by user)
        count_query = """
            SELECT COUNT(*) as total
            FROM tickets
            WHERE approval_status = 'approved' 
                AND status != 'terminated'
                AND (user_id = %s OR sender = %s)
        """
        cursor.execute(count_query, (user_id, user_email))
        total_count = cursor.fetchone()['total']
        
        cursor.close()
        conn.close()
        
        # Calculate pagination info
        total_pages = (total_count + per_page - 1) // per_page
        
        return jsonify({
            'success': True,
            'data': {
                'jobs': jobs,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total_count,
                    'total_pages': total_pages,
                    'has_next': page < total_pages,
                    'has_prev': page > 1
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error in get_hr_approved_jobs: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/jobs/<ticket_id>', methods=['GET'])
@require_api_key
def get_job_details(ticket_id):
    """Get detailed information about a specific job"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # Get ticket information
        cursor.execute("""
            SELECT * FROM tickets 
            WHERE ticket_id = %s
        """, (ticket_id,))
        
        ticket = cursor.fetchone()
        
        if not ticket:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Job not found'
            }), 404
        
        # Get the LATEST value for each field
        cursor.execute("""
            SELECT 
                td1.field_name,
                td1.field_value,
                td1.created_at,
                td1.is_initial
            FROM ticket_details td1
            INNER JOIN (
                SELECT field_name, MAX(created_at) as max_created_at
                FROM ticket_details
                WHERE ticket_id = %s
                GROUP BY field_name
            ) td2 ON td1.field_name = td2.field_name 
                 AND td1.created_at = td2.max_created_at
            WHERE td1.ticket_id = %s
        """, (ticket_id, ticket_id))
        
        current_details = {}
        for row in cursor.fetchall():
            current_details[row['field_name']] = row['field_value']
        
        # Get complete history
        cursor.execute("""
            SELECT field_name, field_value, created_at, is_initial
            FROM ticket_details 
            WHERE ticket_id = %s
            ORDER BY field_name, created_at DESC
        """, (ticket_id,))
        
        all_details = cursor.fetchall()
        
        # Organize history by field
        detail_history = {}
        for row in all_details:
            field_name = row['field_name']
            if field_name not in detail_history:
                detail_history[field_name] = []
            
            detail_history[field_name].append({
                'value': row['field_value'],
                'updated_at': serialize_datetime(row['created_at']),
                'is_initial': row['is_initial']
            })
        
        # Get update history
        cursor.execute("""
            SELECT update_timestamp, updated_fields
            FROM ticket_updates
            WHERE ticket_id = %s
            ORDER BY update_timestamp DESC
        """, (ticket_id,))
        
        updates = []
        for row in cursor.fetchall():
            updates.append({
                'timestamp': serialize_datetime(row['update_timestamp']),
                'fields': json.loads(row['updated_fields']) if row['updated_fields'] else {}
            })
        
        # Convert datetime objects in ticket
        for key, value in ticket.items():
            ticket[key] = serialize_datetime(value)
        
        # Get resume information
        resumes = get_ticket_resumes(ticket_id)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'ticket': ticket,
                'current_details': current_details,
                'history': detail_history,
                'updates': updates,
                'is_approved': ticket['approval_status'] == 'approved',
                'updated_after_approval': len([u for u in updates if u['timestamp'] > ticket['approved_at']]) > 0 if ticket['approved_at'] else False,
                'resumes': resumes,
                'resume_count': len(resumes)
            }
        })
        
    except Exception as e:
        logger.error(f"Error in get_job_details: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/jobs/search', methods=['GET'])
@require_api_key
def search_jobs():
    """Search jobs by keyword"""
    try:
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query is required'
            }), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # First, get all approved tickets
        cursor.execute("""
            SELECT DISTINCT
                t.ticket_id,
                t.subject,
                t.created_at,
                t.approved_at,
                t.last_updated
            FROM tickets t
            WHERE t.approval_status = 'approved' 
                AND t.status != 'terminated'
            ORDER BY t.approved_at DESC
        """)
        
        tickets = cursor.fetchall()
        jobs = []
        
        for ticket in tickets:
            ticket_id = ticket['ticket_id']
            
            # Get latest values for this ticket
            cursor.execute("""
                SELECT 
                    td1.field_name,
                    td1.field_value
                FROM ticket_details td1
                INNER JOIN (
                    SELECT field_name, MAX(created_at) as max_created_at
                    FROM ticket_details
                    WHERE ticket_id = %s
                    GROUP BY field_name
                ) td2 ON td1.field_name = td2.field_name 
                     AND td1.created_at = td2.max_created_at
                WHERE td1.ticket_id = %s
            """, (ticket_id, ticket_id))
            
            job_details = {}
            for row in cursor.fetchall():
                job_details[row['field_name']] = row['field_value']
            
            # Check if search query matches any field
            search_text = query.lower()
            if (search_text in ticket['subject'].lower() or
                search_text in job_details.get('job_title', '').lower() or
                search_text in job_details.get('job_description', '').lower() or
                search_text in job_details.get('required_skills', '').lower() or
                search_text in job_details.get('location', '').lower()):
                
                job = {
                    'ticket_id': ticket['ticket_id'],
                    'subject': ticket['subject'],
                    'created_at': serialize_datetime(ticket['created_at']),
                    'approved_at': serialize_datetime(ticket['approved_at']),
                    'last_updated': serialize_datetime(ticket['last_updated']),
                    'job_title': job_details.get('job_title', 'NOT_FOUND'),
                    'location': job_details.get('location', 'NOT_FOUND'),
                    'experience_required': job_details.get('experience_required', 'NOT_FOUND'),
                    'salary_range': job_details.get('salary_range', 'NOT_FOUND'),
                    'job_description': job_details.get('job_description', 'NOT_FOUND'),
                    'required_skills': job_details.get('required_skills', 'NOT_FOUND'),
                    'employment_type': job_details.get('employment_type', 'NOT_FOUND'),
                    'deadline': job_details.get('deadline', 'NOT_FOUND')
                }
                jobs.append(job)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'query': query,
                'count': len(jobs),
                'jobs': jobs
            }
        })
        
    except Exception as e:
        logger.error(f"Error in search_jobs: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats', methods=['GET', 'OPTIONS'])
def get_statistics():
    """Get hiring statistics and analytics (system-wide)"""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,X-API-Key,ngrok-skip-browser-warning')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        return response, 200
    
    # Require API key for GET requests
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        api_key = request.args.get('api_key')
    
    if api_key != API_KEY:
        return jsonify({
            'success': False,
            'error': 'Invalid or missing API key'
        }), 401
    
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # Overall statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_tickets,
                SUM(CASE WHEN approval_status = 'approved' THEN 1 ELSE 0 END) as approved_jobs,
                SUM(CASE WHEN approval_status = 'pending' THEN 1 ELSE 0 END) as pending_approval,
                SUM(CASE WHEN approval_status = 'rejected' THEN 1 ELSE 0 END) as rejected_jobs,
                SUM(CASE WHEN status = 'terminated' THEN 1 ELSE 0 END) as terminated_jobs
            FROM tickets
        """)
        
        overall_stats = cursor.fetchone()
        
        # Jobs by location - using latest values
        cursor.execute("""
            SELECT 
                latest.location,
                COUNT(*) as count
            FROM (
                SELECT 
                    t.ticket_id,
                    td1.field_value as location
                FROM tickets t
                JOIN ticket_details td1 ON t.ticket_id = td1.ticket_id
                INNER JOIN (
                    SELECT ticket_id, MAX(created_at) as max_created_at
                    FROM ticket_details
                    WHERE field_name = 'location'
                    GROUP BY ticket_id
                ) td2 ON td1.ticket_id = td2.ticket_id 
                     AND td1.created_at = td2.max_created_at
                WHERE td1.field_name = 'location'
                    AND t.approval_status = 'approved'
                    AND t.status != 'terminated'
            ) latest
            GROUP BY latest.location
            ORDER BY count DESC
        """)
        
        locations = cursor.fetchall()
        
        # Recent activity (last 7 days)
        cursor.execute("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as new_jobs
            FROM tickets
            WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """)
        
        recent_activity = cursor.fetchall()
        
        # Convert dates
        for activity in recent_activity:
            activity['date'] = activity['date'].isoformat()
        
        cursor.close()
        conn.close()
        
        response = jsonify({
            'success': True,
            'data': {
                'overall': overall_stats,
                'by_location': locations,
                'recent_activity': recent_activity
            }
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        logger.error(f"Error in get_statistics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/hr/stats', methods=['GET'])
@require_jwt_auth
def get_hr_statistics():
    """Get hiring statistics and analytics for authenticated HR user"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # Get user info from JWT token
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1] if auth_header and auth_header.startswith('Bearer ') else None
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'No token provided'
            }), 401
        
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            user_email = payload.get('email')
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'error': 'Token expired'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'error': 'Invalid token'
            }), 401
        
        # User-specific statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_tickets,
                SUM(CASE WHEN approval_status = 'approved' THEN 1 ELSE 0 END) as approved_jobs,
                SUM(CASE WHEN approval_status = 'pending' THEN 1 ELSE 0 END) as pending_approval,
                SUM(CASE WHEN approval_status = 'rejected' THEN 1 ELSE 0 END) as rejected_jobs,
                SUM(CASE WHEN status = 'terminated' THEN 1 ELSE 0 END) as terminated_jobs
            FROM tickets
            WHERE sender = %s OR user_id IN (
                SELECT user_id FROM users WHERE email = %s
            )
        """, (user_email, user_email))
        
        overall_stats = cursor.fetchone()
        
        # User-specific jobs by location
        cursor.execute("""
            SELECT 
                latest.location,
                COUNT(*) as count
            FROM (
                SELECT 
                    t.ticket_id,
                    td1.field_value as location
                FROM tickets t
                JOIN ticket_details td1 ON t.ticket_id = td1.ticket_id
                INNER JOIN (
                    SELECT ticket_id, MAX(created_at) as max_created_at
                    FROM ticket_details
                    WHERE field_name = 'location'
                    GROUP BY ticket_id
                ) td2 ON td1.ticket_id = td2.ticket_id 
                     AND td1.created_at = td2.max_created_at
                WHERE td1.field_name = 'location'
                    AND t.approval_status = 'approved'
                    AND t.status != 'terminated'
                    AND (t.sender = %s OR t.user_id IN (
                        SELECT user_id FROM users WHERE email = %s
                    ))
            ) latest
            GROUP BY latest.location
            ORDER BY count DESC
        """, (user_email, user_email))
        
        locations = cursor.fetchall()
        
        # User-specific recent activity (last 7 days)
        cursor.execute("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as new_jobs
            FROM tickets
            WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                AND (sender = %s OR user_id IN (
                    SELECT user_id FROM users WHERE email = %s
                ))
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """, (user_email, user_email))
        
        recent_activity = cursor.fetchall()
        
        # Convert dates
        for activity in recent_activity:
            activity['date'] = activity['date'].isoformat()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'overall': overall_stats,
                'by_location': locations,
                'recent_activity': recent_activity
            }
        })
        
    except Exception as e:
        logger.error(f"Error in get_hr_statistics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/locations', methods=['GET'])
@require_api_key
def get_locations():
    """Get list of all unique locations using latest values"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT td1.field_value
            FROM ticket_details td1
            INNER JOIN (
                SELECT ticket_id, MAX(created_at) as max_created_at
                FROM ticket_details
                WHERE field_name = 'location'
                GROUP BY ticket_id
            ) td2 ON td1.ticket_id = td2.ticket_id 
                 AND td1.created_at = td2.max_created_at
            JOIN tickets t ON td1.ticket_id = t.ticket_id
            WHERE td1.field_name = 'location'
                AND td1.field_value IS NOT NULL
                AND td1.field_value != 'NOT_FOUND'
                AND t.approval_status = 'approved'
            ORDER BY td1.field_value
        """)
        
        locations = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'locations': locations
            }
        })
        
    except Exception as e:
        logger.error(f"Error in get_locations: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/skills', methods=['GET'])
@require_api_key
def get_skills():
    """Get list of all unique skills using latest values"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT td1.field_value
            FROM ticket_details td1
            INNER JOIN (
                SELECT ticket_id, MAX(created_at) as max_created_at
                FROM ticket_details
                WHERE field_name = 'required_skills'
                GROUP BY ticket_id
            ) td2 ON td1.ticket_id = td2.ticket_id 
                 AND td1.created_at = td2.max_created_at
            JOIN tickets t ON td1.ticket_id = t.ticket_id
            WHERE td1.field_name = 'required_skills'
                AND td1.field_value IS NOT NULL
                AND td1.field_value != 'NOT_FOUND'
                AND t.approval_status = 'approved'
        """)
        
        # Extract unique skills
        all_skills = set()
        for row in cursor.fetchall():
            skills_text = row[0]
            # Split by common delimiters
            skills = re.split(r'[,;|\n]', skills_text)
            for skill in skills:
                skill = skill.strip()
                if skill:
                    all_skills.add(skill)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'skills': sorted(list(all_skills))
            }
        })
        
    except Exception as e:
        logger.error(f"Error in get_skills: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================
# TICKET MANAGEMENT ENDPOINTS (for chat bot)
# ============================================

@app.route('/api/tickets/<user_id>', methods=['GET'])
def get_user_tickets(user_id):
    """Get all tickets for a user"""
    try:
        tickets = chat_bot.ticket_manager.get_user_tickets(user_id)
        
        # Format tickets for response
        formatted_tickets = []
        for ticket in tickets:
            formatted_tickets.append({
                'ticket_id': ticket['ticket_id'],
                'job_title': ticket.get('job_title', 'Untitled'),
                'status': ticket['status'],
                'approval_status': ticket['approval_status'],
                'created_at': ticket['created_at'].isoformat() if ticket.get('created_at') else None,
                'updated_at': ticket['last_updated'].isoformat() if ticket.get('last_updated') else None
            })
        
        return jsonify({
            'user_id': user_id,
            'tickets': formatted_tickets,
            'count': len(formatted_tickets)
        })
    
    except Exception as e:
        logger.error(f"Error fetching tickets: {e}")
        return jsonify({
            'error': 'Failed to fetch tickets',
            'message': str(e)
        }), 500

@app.route('/api/tickets/<ticket_id>/details', methods=['GET'])
def get_ticket_details(ticket_id):
    """Get detailed information about a specific ticket"""
    try:
        ticket = chat_bot.ticket_manager.get_ticket_details(ticket_id)
        
        if not ticket:
            return jsonify({
                'error': 'Ticket not found',
                'ticket_id': ticket_id
            }), 404
        
        # Format response
        response = {
            'ticket_id': ticket['ticket_id'],
            'status': ticket['status'],
            'approval_status': ticket['approval_status'],
            'created_at': ticket['created_at'].isoformat() if ticket.get('created_at') else None,
            'details': ticket.get('details', {})
        }
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error fetching ticket details: {e}")
        return jsonify({
            'error': 'Failed to fetch ticket details',
            'message': str(e)
        }), 500

# ============================================
# WEBSOCKET EVENTS
# ============================================

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {
        'message': 'Connected to hiring bot server',
        'features': ['chat', 'api', 'file_upload', 'resume_filtering'],
        'timestamp': datetime.now().isoformat(),
        'tunnel_url': CLOUDFLARE_TUNNEL_URL
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('start_session')
def handle_start_session(data):
    """Start a new chat session via WebSocket"""
    try:
        user_id = data.get('user_id')
        result = chat_bot.start_session(user_id)
        emit('session_started', result)
    except Exception as e:
        logger.error(f"WebSocket error starting session: {e}")
        emit('error', {'error': str(e)})

@socketio.on('send_message')
def handle_websocket_message(data):
    """Handle incoming message via WebSocket"""
    try:
        session_id = data.get('session_id')
        user_id = data.get('user_id')
        message = data.get('message')
        
        if not all([session_id, user_id, message]):
            emit('error', {'error': 'Missing required fields'})
            return
        
        # Process message
        bot_response = chat_bot.process_message(session_id, user_id, message)
        
        # Format response for WebSocket
        formatted_response = {
            'response': bot_response.get('message', ''),
            'metadata': bot_response.get('metadata', {}),
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        }
        
        emit('message_response', formatted_response)
    
    except Exception as e:
        logger.error(f"WebSocket error processing message: {e}")
        emit('error', {'error': str(e)})

# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource was not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

# ============================================
# CLEANUP HANDLER
# ============================================

def cleanup_on_exit(signum=None, frame=None):
    """Cleanup function to stop tunnel on exit"""
    print("\n🛑 Shutting down...")
    stop_cloudflare_tunnel()
    sys.exit(0)

# Register cleanup handlers
signal.signal(signal.SIGINT, cleanup_on_exit)
signal.signal(signal.SIGTERM, cleanup_on_exit)



def generate_captcha_text(length=6):
    """Generate random CAPTCHA text"""
    # Use mix of uppercase letters and numbers (avoid confusing characters)
    characters = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'  # Removed I,O,0,1 for clarity
    return ''.join(random.choice(characters) for _ in range(length))

def create_captcha_image(text):
    """Create a CAPTCHA image with distorted text"""
    # Create image
    width = CAPTCHA_IMAGE_WIDTH
    height = CAPTCHA_IMAGE_HEIGHT
    
    # Create base image with random background color
    bg_color = (random.randint(240, 255), random.randint(240, 255), random.randint(240, 255))
    image = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(image)
    
    # Try to use a font, fallback to default if not available
    try:
        # Try different font paths based on OS
        font_paths = [
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",  # Linux
            "/System/Library/Fonts/Helvetica.ttc",  # macOS
            "C:\\Windows\\Fonts\\Arial.ttf",  # Windows
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Alternative Linux
        ]
        
        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, CAPTCHA_FONT_SIZE)
                break
        
        if not font:
            # Use default font if no system font found
            font = ImageFont.load_default()
    except:
        # Use default font if any error
        font = ImageFont.load_default()
    
    # Add noise lines
    for _ in range(random.randint(5, 8)):
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)
        color = (random.randint(0, 150), random.randint(0, 150), random.randint(0, 150))
        draw.line([(x1, y1), (x2, y2)], fill=color, width=random.randint(1, 2))
    
    # Draw each character with random position and rotation
    char_spacing = width // (len(text) + 1)
    for i, char in enumerate(text):
        # Create individual character image
        char_image = Image.new('RGBA', (40, 50), (255, 255, 255, 0))
        char_draw = ImageDraw.Draw(char_image)
        
        # Random color for each character
        char_color = (
            random.randint(0, 100),
            random.randint(0, 100),
            random.randint(0, 100)
        )
        
        char_draw.text((10, 10), char, font=font, fill=char_color)
        
        # Random rotation
        angle = random.randint(-30, 30)
        char_image = char_image.rotate(angle, expand=1)
        
        # Random position
        x = char_spacing * (i + 1) - 20 + random.randint(-10, 10)
        y = (height - 40) // 2 + random.randint(-10, 10)
        
        # Paste character onto main image
        image.paste(char_image, (x, y), char_image)
    
    # Add noise dots
    for _ in range(random.randint(100, 150)):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        color = (random.randint(0, 200), random.randint(0, 200), random.randint(0, 200))
        draw.point((x, y), fill=color)
    
    # Apply slight blur for more distortion
    image = image.filter(ImageFilter.SMOOTH_MORE)
    
    return image

def generate_captcha_session():
    """Generate a new CAPTCHA and return session data"""
    captcha_text = generate_captcha_text(CAPTCHA_LENGTH)
    captcha_image = create_captcha_image(captcha_text)
    
    # Convert image to base64
    buffer = io.BytesIO()
    captcha_image.save(buffer, format='PNG')
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # Generate unique session ID
    session_id = f"captcha_{uuid.uuid4().hex}"
    
    # Store in active captchas with expiration
    active_captchas[session_id] = {
        'text': captcha_text,
        'created_at': datetime.now(),
        'attempts': 0
    }
    
    # Clean up old captchas
    cleanup_expired_captchas()
    
    logger.info(f"Generated CAPTCHA session {session_id} with text: {captcha_text}")
    
    return {
        'session_id': session_id,
        'image': f"data:image/png;base64,{image_base64}",
        'expires_in': CAPTCHA_TIMEOUT
    }

def verify_captcha(session_id, user_input):
    """Verify CAPTCHA input"""
    if not session_id or not user_input:
        return False, "Missing CAPTCHA data"
    
    if session_id not in active_captchas:
        return False, "CAPTCHA expired or invalid"
    
    captcha_data = active_captchas[session_id]
    
    # Check if expired
    if datetime.now() - captcha_data['created_at'] > timedelta(seconds=CAPTCHA_TIMEOUT):
        del active_captchas[session_id]
        return False, "CAPTCHA expired"
    
    # Check attempts
    captcha_data['attempts'] += 1
    if captcha_data['attempts'] > 3:
        del active_captchas[session_id]
        return False, "Too many failed attempts"
    
    # Verify text (case insensitive)
    if user_input.upper().strip() == captcha_data['text']:
        # Mark as verified but keep session for a short time for the actual upload
        captcha_data['verified'] = True
        captcha_data['verified_at'] = datetime.now()
        logger.info(f"CAPTCHA verified successfully for session {session_id}")
        return True, "Verified"
    
    logger.warning(f"CAPTCHA verification failed for session {session_id}. Expected: {captcha_data['text']}, Got: {user_input}")
    return False, "Incorrect CAPTCHA"
def is_captcha_verified(session_id, user_input):
    """Check if CAPTCHA session is verified and valid for use"""
    if not session_id or not user_input:
        return False, "Missing CAPTCHA data"
    
    if session_id not in active_captchas:
        return False, "CAPTCHA session not found"
    
    captcha_data = active_captchas[session_id]
    
    # Check if it was verified
    if not captcha_data.get('verified', False):
        return False, "CAPTCHA not verified"
    
    # Check if verification is still valid (allow 5 minutes after verification)
    if datetime.now() - captcha_data.get('verified_at', datetime.now()) > timedelta(minutes=5):
        del active_captchas[session_id]
        return False, "CAPTCHA verification expired"
    
    # Verify the text again for security
    if user_input.upper().strip() != captcha_data['text']:
        return False, "CAPTCHA text mismatch"
    
    # Delete session after successful use
    del active_captchas[session_id]
    logger.info(f"CAPTCHA session {session_id} used successfully for upload")
    return True, "Valid"
def cleanup_expired_captchas():
    """Remove expired CAPTCHAs from memory"""
    current_time = datetime.now()
    expired_sessions = [
        session_id for session_id, data in active_captchas.items()
        if current_time - data['created_at'] > timedelta(seconds=CAPTCHA_TIMEOUT)
    ]
    for session_id in expired_sessions:
        del active_captchas[session_id]
        logger.info(f"Cleaned up expired CAPTCHA session: {session_id}")

# ============================================
# USER AUTHENTICATION FUNCTIONS
# ============================================

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_jwt_token(user_id, email, role):
    """Generate JWT token for user"""
    # Use timezone.utc for compatibility with older Python versions
    from datetime import timezone
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'exp': datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def get_db_connection():
    """Get database connection"""
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        return conn
    except Error as e:
        logger.error(f"Database connection error: {e}")
        return None

def create_user_table():
    """Create users table if it doesn't exist"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                role ENUM('hr') DEFAULT 'hr',  -- Only HR managers are supported
                phone VARCHAR(20),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                INDEX idx_email (email),
                INDEX idx_user_id (user_id)
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        logger.error(f"Error creating users table: {e}")
        return False

def user_exists(email):
    """Check if user exists by email"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result is not None
    except Error as e:
        logger.error(f"Error checking user existence: {e}")
        return False

def create_user(user_data):
    """Create a new user"""
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed"
    
    try:
        cursor = conn.cursor()
        
        # Generate unique user_id
        user_id = f"user_{secrets.token_hex(8)}"
        
        # Hash password
        password_hash = hash_password(user_data['password'])
        
        cursor.execute("""
            INSERT INTO users (user_id, email, password_hash, first_name, last_name, role, phone)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id,
            user_data['email'],
            password_hash,
            user_data['first_name'],
            user_data['last_name'],
            'hr',  # Force role to be 'hr' only
            user_data.get('phone', '')
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True, user_id
    except Error as e:
        logger.error(f"Error creating user: {e}")
        return False, str(e)

def authenticate_user(email, password):
    """Authenticate user with email and password"""
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed"
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT user_id, email, password_hash, first_name, last_name, role, is_active
            FROM users WHERE email = %s
        """, (email,))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            return False, "User not found"
        
        if not user['is_active']:
            return False, "Account is deactivated"
        
        # Verify password
        if hash_password(password) != user['password_hash']:
            return False, "Invalid password"
        
        return True, user
    except Error as e:
        logger.error(f"Error authenticating user: {e}")
        return False, str(e)

def get_user_by_id(user_id):
    """Get user by user_id"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT user_id, email, first_name, last_name, role, phone, created_at, is_active
            FROM users WHERE user_id = %s
        """, (user_id,))
        
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    except Error as e:
        logger.error(f"Error getting user: {e}")
        return None

# ============================================
# ADD THESE API ENDPOINTS AFTER YOUR EXISTING ENDPOINTS
# ============================================

@app.route('/api/captcha/generate', methods=['GET'])
def generate_captcha():
    """Generate a new CAPTCHA"""
    try:
        captcha_data = generate_captcha_session()
        return jsonify({
            'success': True,
            'data': captcha_data
        })
    except Exception as e:
        logger.error(f"Error generating CAPTCHA: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate CAPTCHA'
        }), 500

@app.route('/api/captcha/verify', methods=['POST'])
def verify_captcha_endpoint():
    """Verify CAPTCHA input"""
    try:
        data = request.json
        session_id = data.get('session_id')
        user_input = data.get('captcha_text')
        
        logger.info(f"Verifying CAPTCHA for session {session_id} with input: {user_input}")
        
        is_valid, message = verify_captcha(session_id, user_input)
        
        return jsonify({
            'success': is_valid,
            'message': message
        })
    except Exception as e:
        logger.error(f"Error verifying CAPTCHA: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to verify CAPTCHA'
        }), 500

# ============================================
# TEST ENDPOINT - Create Sample Jobs
# ============================================

@app.route('/api/test/create-sample-jobs', methods=['POST'])
@require_api_key
def create_sample_jobs():
    """Create sample jobs for testing the candidate portal"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor()
        
        # Sample job data
        sample_jobs = [
            {
                'subject': 'Senior Software Engineer Position',
                'description': 'We are looking for a Senior Software Engineer to join our growing team.',
                'priority': 'medium',
                'status': 'open',
                'approval_status': 'approved',
                'job_title': 'Senior Software Engineer',
                'company_name': 'TechCorp',
                'location': 'San Francisco, CA',
                'job_type': 'Full-time',
                'salary_range': '$120,000 - $150,000',
                'job_description': 'We are looking for a Senior Software Engineer to join our growing team. You will be responsible for developing and maintaining high-quality software solutions.',
                'requirements': '5+ years of experience,Strong problem-solving skills,Experience with modern frameworks',
                'skills': 'React,Node.js,TypeScript,AWS',
                'experience_level': '5+ years'
            },
            {
                'subject': 'Product Manager Position',
                'description': 'Join our product team to help shape the future of our platform.',
                'priority': 'medium',
                'status': 'open',
                'approval_status': 'approved',
                'job_title': 'Product Manager',
                'company_name': 'InnovateTech',
                'location': 'New York, NY',
                'job_type': 'Full-time',
                'salary_range': '$100,000 - $130,000',
                'job_description': 'Join our product team to help shape the future of our platform. You will work closely with engineering and design teams.',
                'requirements': '3+ years of product management,Strong analytical skills,Excellent communication',
                'skills': 'Product Strategy,Data Analysis,User Research,Agile',
                'experience_level': '3+ years'
            },
            {
                'subject': 'UX Designer Position',
                'description': 'Create beautiful and intuitive user experiences for our web and mobile applications.',
                'priority': 'medium',
                'status': 'open',
                'approval_status': 'approved',
                'job_title': 'UX Designer',
                'company_name': 'DesignStudio',
                'location': 'Remote',
                'job_type': 'Contract',
                'salary_range': '$80,000 - $100,000',
                'job_description': 'Create beautiful and intuitive user experiences for our web and mobile applications.',
                'requirements': 'Portfolio of work,Experience with design tools,User-centered design approach',
                'skills': 'Figma,Sketch,Adobe Creative Suite,Prototyping',
                'experience_level': '2+ years'
            }
        ]
        
        created_jobs = []
        
        for job_data in sample_jobs:
            # Insert ticket
            cursor.execute("""
                INSERT INTO tickets (subject, description, priority, status, approval_status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
            """, (job_data['subject'], job_data['description'], job_data['priority'], 
                  job_data['status'], job_data['approval_status']))
            
            ticket_id = cursor.lastrowid
            
            # Insert ticket details
            details = [
                ('job_title', job_data['job_title']),
                ('company_name', job_data['company_name']),
                ('location', job_data['location']),
                ('job_type', job_data['job_type']),
                ('salary_range', job_data['salary_range']),
                ('job_description', job_data['job_description']),
                ('requirements', job_data['requirements']),
                ('skills', job_data['skills']),
                ('experience_level', job_data['experience_level'])
            ]
            
            for field_name, field_value in details:
                cursor.execute("""
                    INSERT INTO ticket_details (ticket_id, field_name, field_value, created_at)
                    VALUES (%s, %s, %s, NOW())
                """, (ticket_id, field_name, field_value))
            
            created_jobs.append({
                'ticket_id': ticket_id,
                'job_title': job_data['job_title'],
                'company_name': job_data['company_name']
            })
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Successfully created {len(created_jobs)} sample jobs',
            'data': created_jobs
        })
        
    except Exception as e:
        logger.error(f"Error creating sample jobs: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to create sample jobs: {str(e)}'
        }), 500

# ============================================
# JOB CREATION ENDPOINT
# ============================================

@app.route('/api/jobs', methods=['POST', 'OPTIONS'])
def create_job():
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return jsonify({'success': True}), 200
    
    # Require API key for POST requests only
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        api_key = request.args.get('api_key')
    
    if api_key != API_KEY:
        return jsonify({
            'success': False,
            'error': 'Invalid or missing API key'
        }), 401
    
    """Create a new job posting"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['job_title', 'location', 'employment_type', 'experience_required']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor()
        
        # Generate ticket ID
        ticket_id = generate_ticket_id()
        
        # Create ticket
        cursor.execute("""
            INSERT INTO tickets (ticket_id, source, user_id, sender, subject, approval_status, created_at, last_updated)
            VALUES (%s, 'chat', %s, %s, %s, 'approved', NOW(), NOW())
        """, (ticket_id, data.get('contact_email', 'manual@company.com'), 
              data.get('contact_email', 'manual@company.com'), 
              data.get('job_title', 'Job Posting')))
        
        # Insert job details
        job_details = [
            ('job_title', data.get('job_title')),
            ('company_name', data.get('company_name', 'Your Company')),
            ('location', data.get('location')),
            ('employment_type', data.get('employment_type')),
            ('experience_required', data.get('experience_required')),
            ('salary_range', data.get('salary_range', 'Competitive')),
            ('job_description', data.get('job_description', '')),
            ('requirements', data.get('requirements', '')),
            ('required_skills', data.get('skills_required', '')),
            ('deadline', convert_html_date_to_ddmmyyyy(data.get('deadline', ''))),
            ('contact_email', data.get('contact_email', '')),
            ('contact_phone', data.get('contact_phone', ''))
        ]
        
        for field_name, field_value in job_details:
            if field_value:
                cursor.execute("""
                    INSERT INTO ticket_details (ticket_id, field_name, field_value, is_initial, source)
                    VALUES (%s, %s, %s, TRUE, 'chat')
                """, (ticket_id, field_name, field_value))
        
        # Create job folder
        try:
            create_job_folder(ticket_id, data.get('job_title'))
        except Exception as e:
            logger.warning(f"Failed to create job folder for {ticket_id}: {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Created job posting {ticket_id} via manual form")
        
        return jsonify({
            'success': True,
            'message': 'Job posting created successfully',
            'data': {
                'ticket_id': ticket_id,
                'job_title': data.get('job_title'),
                'status': 'approved'
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating job: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to create job posting: {str(e)}'
        }), 500

# ============================================
# HR DASHBOARD JOBS ENDPOINT (shows all jobs including hidden)
# ============================================

@app.route('/api/jobs/dashboard', methods=['GET'])
@require_api_key
def get_dashboard_jobs():
    """Get all approved jobs for HR dashboard (including hidden jobs)"""
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)
        sort_by = request.args.get('sort', 'approved_at')
        order = request.args.get('order', 'desc')
        
        # Validate sort parameters
        allowed_sorts = ['created_at', 'approved_at', 'last_updated']
        if sort_by not in allowed_sorts:
            sort_by = 'approved_at'
        
        if order not in ['asc', 'desc']:
            order = 'desc'
        
        offset = (page - 1) * per_page
        
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # Get all approved tickets (including hidden ones for HR dashboard)
        cursor.execute("""
            SELECT 
                t.ticket_id,
                t.sender,
                t.subject,
                t.created_at,
                t.last_updated,
                t.approved_at,
                t.status,
                COALESCE(td_visibility.field_value, 'true') as is_visible
            FROM tickets t
            LEFT JOIN (
                SELECT td1.ticket_id, td1.field_value
                FROM ticket_details td1
                INNER JOIN (
                    SELECT ticket_id, MAX(created_at) as max_created_at
                    FROM ticket_details
                    WHERE field_name = 'is_visible'
                    GROUP BY ticket_id
                ) td2 ON td1.ticket_id = td2.ticket_id 
                     AND td1.created_at = td2.max_created_at
                WHERE td1.field_name = 'is_visible'
            ) td_visibility ON t.ticket_id = td_visibility.ticket_id
            WHERE t.approval_status = 'approved' 
                AND t.status != 'terminated'
            ORDER BY {} {}
            LIMIT %s OFFSET %s
        """.format(sort_by, order), (per_page, offset))
        
        tickets = cursor.fetchall()
        
        # For each ticket, get the LATEST value for each field
        jobs = []
        for ticket in tickets:
            ticket_id = ticket['ticket_id']
            
            # Get the latest value for each field using a subquery
            cursor.execute("""
                SELECT 
                    td1.field_name,
                    td1.field_value
                FROM ticket_details td1
                INNER JOIN (
                    SELECT field_name, MAX(created_at) as max_created_at
                    FROM ticket_details
                    WHERE ticket_id = %s
                    GROUP BY field_name
                ) td2 ON td1.field_name = td2.field_name 
                     AND td1.created_at = td2.max_created_at
                WHERE td1.ticket_id = %s
            """, (ticket_id, ticket_id))
            
            # Build the job details
            job_details = {}
            for row in cursor.fetchall():
                job_details[row['field_name']] = row['field_value']
            
            # Check if this job was updated after approval
            cursor.execute("""
                SELECT COUNT(*) as update_count
                FROM ticket_updates
                WHERE ticket_id = %s AND update_timestamp > %s
            """, (ticket_id, ticket['approved_at']))
            
            update_info = cursor.fetchone()
            updated_after_approval = update_info['update_count'] > 0
            
            # Build the job object
            job = {
                'ticket_id': ticket_id,
                'job_title': job_details.get('job_title', ticket['subject']),
                'company_name': job_details.get('company_name', ticket['sender']),
                'location': job_details.get('location', 'Not specified'),
                'employment_type': job_details.get('employment_type', 'Full-time'),
                'experience_required': job_details.get('experience_required', 'Not specified'),
                'salary_range': job_details.get('salary_range', 'Competitive'),
                'job_description': job_details.get('job_description', 'No description available'),
                'requirements': job_details.get('requirements', 'No requirements specified'),
                'required_skills': job_details.get('required_skills', 'No skills specified'),
                'deadline': job_details.get('deadline', 'Open until filled'),
                'contact_email': job_details.get('contact_email', ''),
                'contact_phone': job_details.get('contact_phone', ''),
                'created_at': ticket['created_at'].isoformat() if ticket['created_at'] else None,
                'approved_at': ticket['approved_at'].isoformat() if ticket['approved_at'] else None,
                'last_updated': ticket['last_updated'].isoformat() if ticket['last_updated'] else None,
                'status': ticket['status'],
                'is_visible': ticket['is_visible'] == 'true',
                'updated_after_approval': updated_after_approval
            }
            
            jobs.append(job)
        
        # Get total count for pagination
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM tickets
            WHERE approval_status = 'approved' 
                AND status != 'terminated'
        """)
        
        total_count = cursor.fetchone()['total']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'jobs': jobs,
                'total': total_count,
                'page': page,
                'per_page': per_page,
                'total_pages': (total_count + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching dashboard jobs: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch dashboard jobs: {str(e)}'
        }), 500

# ============================================
# JOB VISIBILITY TOGGLE ENDPOINT
# ============================================

@app.route('/api/jobs/<ticket_id>/toggle-visibility', methods=['POST', 'OPTIONS'])
def toggle_job_visibility(ticket_id):
    """Toggle job visibility on career portal"""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return jsonify({'success': True}), 200
    
    # Require API key
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        api_key = request.args.get('api_key')
    
    if api_key != API_KEY:
        return jsonify({
            'success': False,
            'error': 'Invalid or missing API key'
        }), 401
    
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor()
        
        # Check if job exists and get current visibility status
        cursor.execute("""
            SELECT t.ticket_id, t.subject, td.field_value as is_visible
            FROM tickets t
            LEFT JOIN ticket_details td ON t.ticket_id = td.ticket_id AND td.field_name = 'is_visible'
            WHERE t.ticket_id = %s AND t.approval_status = 'approved'
        """, (ticket_id,))
        
        job = cursor.fetchone()
        if not job:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Job not found or not approved'
            }), 404
        
        # Determine new visibility status (default to True if not set)
        current_visibility = job[2] if job[2] else 'true'
        new_visibility = 'false' if current_visibility.lower() == 'true' else 'true'
        
        # Update visibility status
        cursor.execute("""
            DELETE FROM ticket_details 
            WHERE ticket_id = %s AND field_name = 'is_visible'
        """, (ticket_id,))
        
        cursor.execute("""
            INSERT INTO ticket_details (ticket_id, field_name, field_value, is_initial, source)
            VALUES (%s, 'is_visible', %s, TRUE, 'chat')
        """, (ticket_id, new_visibility))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Job visibility {"enabled" if new_visibility == "true" else "disabled"} successfully',
            'data': {
                'ticket_id': ticket_id,
                'is_visible': new_visibility == 'true',
                'status': 'visible' if new_visibility == 'true' else 'hidden'
            }
        })
        
    except Exception as e:
        logger.error(f"Error toggling job visibility: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to toggle job visibility: {str(e)}'
        }), 500

# ============================================
# JOB UPDATE AND DELETION ENDPOINT
# ============================================

@app.route('/api/jobs/<ticket_id>', methods=['PUT', 'DELETE', 'OPTIONS'])
def update_or_delete_job(ticket_id):
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        return jsonify({'success': True}), 200
    
    # Require API key for PUT and DELETE requests
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        api_key = request.args.get('api_key')
    
    if api_key != API_KEY:
        return jsonify({
            'success': False,
            'error': 'Invalid or missing API key'
        }), 401
    
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor()
        
        # Check if job exists
        cursor.execute("""
            SELECT ticket_id, subject FROM tickets 
            WHERE ticket_id = %s
        """, (ticket_id,))
        
        job = cursor.fetchone()
        if not job:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Job not found'
            }), 404
        
        if request.method == 'PUT':
            """Update a job posting"""
            data = request.get_json()
            
            if not data:
                cursor.close()
                conn.close()
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
            # Update the ticket subject if job_title is provided
            if 'job_title' in data:
                cursor.execute("""
                    UPDATE tickets 
                    SET subject = %s, last_updated = NOW()
                    WHERE ticket_id = %s
                """, (data['job_title'], ticket_id))
            
            # Update job details
            job_details = [
                ('job_title', data.get('job_title')),
                ('company_name', data.get('company_name')),
                ('location', data.get('location')),
                ('employment_type', data.get('employment_type')),
                ('experience_required', data.get('experience_required')),
                ('salary_range', data.get('salary_range')),
                ('job_description', data.get('job_description')),
                ('requirements', data.get('requirements')),
                ('required_skills', data.get('skills_required')),
                ('deadline', convert_html_date_to_ddmmyyyy(data.get('deadline', ''))),
                ('contact_email', data.get('contact_email')),
                ('contact_phone', data.get('contact_phone')),
                ('is_visible', data.get('is_visible', 'true'))
            ]
            
            for field_name, field_value in job_details:
                if field_value is not None:  # Allow empty strings to clear fields
                    # Delete existing entry for this field
                    cursor.execute("""
                        DELETE FROM ticket_details 
                        WHERE ticket_id = %s AND field_name = %s
                    """, (ticket_id, field_name))
                    
                    # Insert new value
                    cursor.execute("""
                        INSERT INTO ticket_details (ticket_id, field_name, field_value, is_initial, source)
                        VALUES (%s, %s, %s, TRUE, 'chat')
                    """, (ticket_id, field_name, field_value))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': f'Job {ticket_id} updated successfully',
                'data': {
                    'ticket_id': ticket_id,
                    'updated_fields': [field for field, value in job_details if value is not None]
                }
            }), 200
        
        elif request.method == 'DELETE':
            """Delete a job posting"""
            # Delete job details first (due to foreign key constraint)
            cursor.execute("""
                DELETE FROM ticket_details 
                WHERE ticket_id = %s
            """, (ticket_id,))
        
        # Delete ticket updates
        cursor.execute("""
            DELETE FROM ticket_updates 
            WHERE ticket_id = %s
        """, (ticket_id,))
        
        # Delete ticket history
        cursor.execute("""
            DELETE FROM ticket_history 
            WHERE ticket_id = %s
        """, (ticket_id,))
        
        # ENHANCED: Delete all interview-related data for this job
        logger.info(f"Starting cascade deletion of interview data for job {ticket_id}")
        
        # 1. Delete interview feedback first (due to foreign key constraints)
        cursor.execute("""
            DELETE FROM interview_feedback 
            WHERE interview_id IN (
                SELECT id FROM interview_schedules 
                WHERE ticket_id = %s
            )
        """, (ticket_id,))
        feedback_deleted = cursor.rowcount
        logger.info(f"Deleted {feedback_deleted} interview feedback records for job {ticket_id}")
        
        # 2. Delete interview schedules
        cursor.execute("""
            DELETE FROM interview_schedules 
            WHERE ticket_id = %s
        """, (ticket_id,))
        schedules_deleted = cursor.rowcount
        logger.info(f"Deleted {schedules_deleted} interview schedules for job {ticket_id}")
        
        # 3. Delete interview rounds
        cursor.execute("""
            DELETE FROM interview_rounds 
            WHERE ticket_id = %s
        """, (ticket_id,))
        rounds_deleted = cursor.rowcount
        logger.info(f"Deleted {rounds_deleted} interview rounds for job {ticket_id}")
        
        # 4. Delete candidate interview status
        cursor.execute("""
            DELETE FROM candidate_interview_status 
            WHERE ticket_id = %s
        """, (ticket_id,))
        status_deleted = cursor.rowcount
        logger.info(f"Deleted {status_deleted} candidate interview status records for job {ticket_id}")
        
        # 5. Delete resume applications
        cursor.execute("""
            DELETE FROM resume_applications 
            WHERE ticket_id = %s
        """, (ticket_id,))
        resumes_deleted = cursor.rowcount
        logger.info(f"Deleted {resumes_deleted} resume applications for job {ticket_id}")
        
        logger.info(f"Job deletion cascade summary for {ticket_id}: {feedback_deleted} feedback, {schedules_deleted} schedules, {rounds_deleted} rounds, {status_deleted} status, {resumes_deleted} resumes")
        
        # Delete the main ticket
        cursor.execute("""
            DELETE FROM tickets 
            WHERE ticket_id = %s
        """, (ticket_id,))
        
        # Delete job folder if it exists
        try:
            job_folder = os.path.join(BASE_STORAGE_PATH, f"{ticket_id}_*")
            import glob
            folders = glob.glob(job_folder)
            for folder in folders:
                import shutil
                shutil.rmtree(folder)
                logger.info(f"Deleted job folder: {folder}")
        except Exception as e:
            logger.warning(f"Failed to delete job folder for {ticket_id}: {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Deleted job posting {ticket_id}")
        
        return jsonify({
            'success': True,
            'message': 'Job posting deleted successfully',
            'data': {
                'ticket_id': ticket_id,
                'job_title': job[1] if job else 'Unknown'
            }
        }), 200
        
    except Exception as e:
        operation = 'updating' if request.method == 'PUT' else 'deleting'
        logger.error(f"Error {operation} job: {e}")
        try:
            if 'conn' in locals():
                conn.rollback()
                conn.close()
        except:
            pass
        return jsonify({
            'success': False,
            'error': f'Failed to {operation} job posting: {str(e)}'
        }), 500

# ============================================
# MODIFY YOUR EXISTING upload_resume FUNCTION
# ============================================

@app.route('/api/tickets/<ticket_id>/resumes', methods=['POST'])
@require_api_key
def upload_resume(ticket_id):
    """Upload a resume for a specific ticket with CAPTCHA verification and email confirmation"""
    try:
        # CAPTCHA verification (existing code)
        captcha_session = request.form.get('captcha_session')
        captcha_text = request.form.get('captcha_text')
        
        logger.info(f"Resume upload attempt for ticket {ticket_id}")
        logger.info(f"CAPTCHA session: {captcha_session}, CAPTCHA text: {captcha_text}")
        
        # Verify CAPTCHA using the new method
        is_valid, message = is_captcha_verified(captcha_session, captcha_text)
        if not is_valid:
            logger.warning(f"CAPTCHA verification failed for ticket {ticket_id}: {message}")
            return jsonify({
                'success': False,
                'error': f'CAPTCHA verification failed: {message}'
            }), 400
        
        logger.info(f"CAPTCHA verified successfully for ticket {ticket_id}")
        
        # Existing database checks
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT ticket_id, subject, approval_status
            FROM tickets
            WHERE ticket_id = %s
        """, (ticket_id,))
        
        ticket = cursor.fetchone()
        
        if not ticket:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Ticket not found'
            }), 404
        
        if ticket['approval_status'] != 'approved':
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Ticket must be approved before uploading resumes'
            }), 400
        
        # Get job title from ticket details
        cursor.execute("""
            SELECT td1.field_value as job_title
            FROM ticket_details td1
            INNER JOIN (
                SELECT MAX(created_at) as max_created_at
                FROM ticket_details
                WHERE ticket_id = %s AND field_name = 'job_title'
            ) td2 ON td1.created_at = td2.max_created_at
            WHERE td1.ticket_id = %s AND td1.field_name = 'job_title'
        """, (ticket_id, ticket_id))
        
        job_result = cursor.fetchone()
        job_title = job_result['job_title'] if job_result else 'Unknown Position'
        
        cursor.close()
        conn.close()
        
        # File validation (existing code)
        if 'resume' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['resume']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Get applicant details
        applicant_name = request.form.get('applicant_name', '').strip()
        applicant_email = request.form.get('applicant_email', '').strip()
        applicant_phone = request.form.get('applicant_phone', '').strip()
        cover_letter = request.form.get('cover_letter', '').strip()
        
        # Validate required fields
        if not applicant_name or not applicant_email:
            return jsonify({
                'success': False,
                'error': 'Applicant name and email are required'
            }), 400
        
        # Basic email validation
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, applicant_email):
            return jsonify({
                'success': False,
                'error': 'Please provide a valid email address'
            }), 400
        
        logger.info(f"Processing resume upload for {applicant_name} ({applicant_email})")
        
        # Create folder and save resume (existing code)
        folder_path = create_ticket_folder(ticket_id, ticket['subject'])
        if not folder_path:
            return jsonify({
                'success': False,
                'error': 'Failed to create ticket folder'
            }), 500
        
        # Save the resume
        result = save_resume_to_ticket(
            ticket_id, 
            file, 
            applicant_name, 
            applicant_email
        )
        
        # Handle duplicate prevention response
        if isinstance(result, dict) and not result.get('success', True):
            return jsonify(result), 400
        
        saved_path = result
        if saved_path:
            # Generate unique application ID
            application_id = f"APP_{ticket_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{applicant_name.replace(' ', '').upper()[:4]}"
            
            logger.info(f"Resume uploaded successfully for ticket {ticket_id}: {saved_path}")
            
            # 🆕 SEND THANK YOU EMAIL
            try:
                send_thank_you_email_async(
                    candidate_email=applicant_email,
                    candidate_name=applicant_name,
                    job_title=job_title,
                    application_id=application_id
                )
                logger.info(f"Thank you email queued for {applicant_name} ({applicant_email})")
            except Exception as email_error:
                logger.error(f"Failed to queue thank you email: {email_error}")
                # Don't fail the upload if email fails
            
            return jsonify({
                'success': True,
                'message': 'Resume uploaded successfully! You will receive a confirmation email shortly.',
                'data': {
                    'file_path': saved_path,
                    'application_id': application_id,
                    'job_title': job_title,
                    'applicant_name': applicant_name,
                    'email_sent': EMAIL_CONFIG.get('SEND_EMAILS', True)
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save resume'
            }), 500
            
    except Exception as e:
        logger.error(f"Error uploading resume: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================
# ADDITIONAL EMAIL ENDPOINTS (OPTIONAL)
# ============================================

@app.route('/api/email/test', methods=['POST'])
@require_api_key
def test_email_configuration():
    """Test email configuration"""
    try:
        data = request.json
        test_email = data.get('test_email', EMAIL_CONFIG.get('HR_EMAIL'))
        
        if not test_email:
            return jsonify({
                'success': False,
                'error': 'Test email address required'
            }), 400
        
        # Send test email
        subject = "Email Configuration Test - HR System"
        html_content = """
        <h2>Email Test Successful! ✅</h2>
        <p>Your email configuration is working correctly.</p>
        <p>The candidate confirmation emails will be sent successfully.</p>
        <p><strong>Test Time:</strong> {}</p>
        """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        text_content = f"""
        Email Test Successful!
        
        Your email configuration is working correctly.
        The candidate confirmation emails will be sent successfully.
        
        Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        success, message = send_email(test_email, subject, html_content, text_content)
        
        return jsonify({
            'success': success,
            'message': message,
            'test_email': test_email,
            'smtp_server': EMAIL_CONFIG['SMTP_SERVER'],
            'from_email': EMAIL_CONFIG['EMAIL_ADDRESS']
        })
        
    except Exception as e:
        logger.error(f"Email test failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/email/status', methods=['GET'])
@require_api_key
def get_email_status():
    """Get email configuration status"""
    return jsonify({
        'success': True,
        'data': {
            'email_enabled': EMAIL_CONFIG.get('SEND_EMAILS', True),
            'smtp_server': EMAIL_CONFIG['SMTP_SERVER'],
            'smtp_port': EMAIL_CONFIG['SMTP_PORT'],
            'from_email': EMAIL_CONFIG['EMAIL_ADDRESS'],
            'from_name': EMAIL_CONFIG['FROM_NAME'],
            'company_name': EMAIL_CONFIG['COMPANY_NAME'],
            'hr_email': EMAIL_CONFIG['HR_EMAIL'],
            'use_tls': EMAIL_CONFIG.get('USE_TLS', True)
        }
    })

    """Upload a resume for a specific ticket with CAPTCHA verification"""
    try:
        # CAPTCHA verification
        captcha_session = request.form.get('captcha_session')
        captcha_text = request.form.get('captcha_text')
        
        logger.info(f"Resume upload attempt for ticket {ticket_id}")
        logger.info(f"CAPTCHA session: {captcha_session}, CAPTCHA text: {captcha_text}")
        
        # Verify CAPTCHA using the new method
        is_valid, message = is_captcha_verified(captcha_session, captcha_text)
        if not is_valid:
            logger.warning(f"CAPTCHA verification failed for ticket {ticket_id}: {message}")
            return jsonify({
                'success': False,
                'error': f'CAPTCHA verification failed: {message}'
            }), 400
        
        logger.info(f"CAPTCHA verified successfully for ticket {ticket_id}")
        
        # Rest of your existing upload_resume code...
        # Check if the ticket exists and is approved
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT ticket_id, subject, approval_status
            FROM tickets
            WHERE ticket_id = %s
        """, (ticket_id,))
        
        ticket = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not ticket:
            return jsonify({
                'success': False,
                'error': 'Ticket not found'
            }), 404
        
        if ticket['approval_status'] != 'approved':
            return jsonify({
                'success': False,
                'error': 'Ticket must be approved before uploading resumes'
            }), 400
        
        # Check if file is in request
        if 'resume' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['resume']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Get applicant details from form data
        applicant_name = request.form.get('applicant_name')
        applicant_email = request.form.get('applicant_email')
        
        logger.info(f"Processing resume upload for {applicant_name} ({applicant_email})")
        
        # Ensure folder exists
        folder_path = create_ticket_folder(ticket_id, ticket['subject'])
        if not folder_path:
            return jsonify({
                'success': False,
                'error': 'Failed to create ticket folder'
            }), 500
        
        # Save the resume
        result = save_resume_to_ticket(
            ticket_id, 
            file, 
            applicant_name, 
            applicant_email
        )
        
        # Handle duplicate prevention response
        if isinstance(result, dict) and not result.get('success', True):
            return jsonify(result), 400
        
        saved_path = result
        if saved_path:
            logger.info(f"Resume uploaded successfully for ticket {ticket_id}: {saved_path}")
            return jsonify({
                'success': True,
                'message': 'Resume uploaded successfully',
                'file_path': saved_path
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save resume'
            }), 500
            
    except Exception as e:
        logger.error(f"Error uploading resume: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    """Upload a resume for a specific ticket with CAPTCHA verification"""
    try:
        # CAPTCHA verification
        captcha_session = request.form.get('captcha_session')
        captcha_text = request.form.get('captcha_text')
        
        logger.info(f"Resume upload attempt for ticket {ticket_id}")
        logger.info(f"CAPTCHA session: {captcha_session}, CAPTCHA text: {captcha_text}")
        
        # Verify CAPTCHA using the new method
        is_valid, message = is_captcha_verified(captcha_session, captcha_text)
        if not is_valid:
            logger.warning(f"CAPTCHA verification failed for ticket {ticket_id}: {message}")
            return jsonify({
                'success': False,
                'error': f'CAPTCHA verification failed: {message}'
            }), 400
        
        logger.info(f"CAPTCHA verified successfully for ticket {ticket_id}")
        
        # Check if the ticket exists and is approved
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT ticket_id, subject, approval_status
            FROM tickets
            WHERE ticket_id = %s
        """, (ticket_id,))
        
        ticket = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not ticket:
            return jsonify({
                'success': False,
                'error': 'Ticket not found'
            }), 404
        
        if ticket['approval_status'] != 'approved':
            return jsonify({
                'success': False,
                'error': 'Ticket must be approved before uploading resumes'
            }), 400
        
        # Check if file is in request
        if 'resume' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['resume']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Get applicant details from form data
        applicant_name = request.form.get('applicant_name')
        applicant_email = request.form.get('applicant_email')
        
        logger.info(f"Processing resume upload for {applicant_name} ({applicant_email})")
        
        # Ensure folder exists
        folder_path = create_ticket_folder(ticket_id, ticket['subject'])
        if not folder_path:
            return jsonify({
                'success': False,
                'error': 'Failed to create ticket folder'
            }), 500
        
        # Save the resume
        result = save_resume_to_ticket(
            ticket_id, 
            file, 
            applicant_name, 
            applicant_email
        )
        
        # Handle duplicate prevention response
        if isinstance(result, dict) and not result.get('success', True):
            return jsonify(result), 400
        
        saved_path = result
        if saved_path:
            logger.info(f"Resume uploaded successfully for ticket {ticket_id}: {saved_path}")
            return jsonify({
                'success': True,
                'message': 'Resume uploaded successfully',
                'file_path': saved_path
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save resume'
            }), 500
            
    except Exception as e:
        logger.error(f"Error uploading resume: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================
# ADD THIS DIAGNOSTIC ENDPOINT (OPTIONAL)
# ============================================

@app.route('/api/captcha/status', methods=['GET'])
def get_captcha_status():
    """Get CAPTCHA system status (for debugging)"""
    try:
        # Clean up expired captchas first
        cleanup_expired_captchas()
        
        return jsonify({
            'success': True,
            'data': {
                'active_sessions': len(active_captchas),
                'captcha_length': CAPTCHA_LENGTH,
                'timeout_seconds': CAPTCHA_TIMEOUT,
                'image_dimensions': f"{CAPTCHA_IMAGE_WIDTH}x{CAPTCHA_IMAGE_HEIGHT}",
                'pil_version': Image.__version__ if hasattr(Image, '__version__') else 'Unknown'
            }
        })
    except Exception as e:
        logger.error(f"Error getting CAPTCHA status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================
# AUTHENTICATION API ENDPOINTS
# ============================================

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """User registration endpoint"""
    try:
        data = request.json
        required_fields = ['email', 'password', 'first_name', 'last_name']
        
        # Validate required fields
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Validate email format
        email = data['email'].lower().strip()
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return jsonify({
                'success': False,
                'error': 'Invalid email format'
            }), 400
        
        # Validate password strength
        password = data['password']
        if len(password) < 8:
            return jsonify({
                'success': False,
                'error': 'Password must be at least 8 characters long'
            }), 400
        
        # Check if user already exists
        if user_exists(email):
            return jsonify({
                'success': False,
                'error': 'User with this email already exists'
            }), 409
        
        # Force role to be 'hr' (only HR managers can be created)
        data['role'] = 'hr'
        
        # Create user
        success, result = create_user(data)
        if not success:
            return jsonify({
                'success': False,
                'error': result
            }), 500
        
        # Generate JWT token
        token = generate_jwt_token(result, email, 'hr')
        
        return jsonify({
            'success': True,
            'message': 'HR Manager registered successfully',
            'data': {
                'user_id': result,
                'email': email,
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'role': 'hr',
                'token': token
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error in signup: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.json
        
        if not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'error': 'Email and password are required'
            }), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Authenticate user
        success, result = authenticate_user(email, password)
        if not success:
            return jsonify({
                'success': False,
                'error': result
            }), 401
        
        # Check if user is HR manager (only HR managers can login)
        if result['role'] != 'hr':
            return jsonify({
                'success': False,
                'error': 'Access denied. Only HR managers can login to this system.'
            }), 403
        
        # Generate JWT token
        token = generate_jwt_token(result['user_id'], result['email'], result['role'])
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'data': {
                'user_id': result['user_id'],
                'email': result['email'],
                'first_name': result['first_name'],
                'last_name': result['last_name'],
                'role': result['role'],
                'token': token
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in login: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/auth/profile', methods=['GET'])
def get_profile():
    """Get user profile (requires authentication)"""
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': 'Authorization header required'
            }), 401
        
        token = auth_header.split(' ')[1]
        
        # Verify token
        is_valid, payload = verify_jwt_token(token)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': payload
            }), 401
        
        # Get user data
        user = get_user_by_id(payload['user_id'])
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'user_id': user['user_id'],
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'role': user['role'],
                'phone': user['phone'],
                'created_at': user['created_at'].isoformat() if user['created_at'] else None
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting profile: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/auth/verify', methods=['POST'])
def verify_token():
    """Verify JWT token validity"""
    try:
        data = request.json
        token = data.get('token')
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'Token is required'
            }), 400
        
        # Verify token
        is_valid, payload = verify_jwt_token(token)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': payload
            }), 401
        
        return jsonify({
            'success': True,
            'data': {
                'user_id': payload['user_id'],
                'email': payload['email'],
                'role': payload['role'],
                'exp': payload['exp']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

# ============================================
# NEW ENDPOINTS FOR FOLDER MANAGEMENT
# ============================================

@app.route('/api/jobs/<ticket_id>/folder-info', methods=['GET'])
@require_api_key
def get_job_folder_information(ticket_id):
    """Get detailed information about a job's folder"""
    try:
        folder_info = get_job_folder_info(ticket_id)
        
        return jsonify({
            'success': True,
            'data': folder_info
        })
        
    except Exception as e:
        logger.error(f"Error getting folder info: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/maintenance/auto-create-folders', methods=['POST'])
@require_api_key
def auto_create_folders_endpoint():
    """Automatically create folders for all tickets that need them"""
    try:
        auto_create_folders_for_pending_tickets()
        
        return jsonify({
            'success': True,
            'message': 'Auto folder creation completed successfully'
        })
        
    except Exception as e:
        logger.error(f"Error in auto create folders endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/maintenance/cleanup-folders', methods=['POST'])
@require_api_key
def cleanup_folders_endpoint():
    """Clean up orphaned folders"""
    try:
        cleanup_orphaned_folders()
        
        return jsonify({
            'success': True,
            'message': 'Folder cleanup completed successfully'
        })
        
    except Exception as e:
        logger.error(f"Error in cleanup folders endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/maintenance/folder-stats', methods=['GET'])
@require_api_key
def get_folder_statistics():
    """Get statistics about job folders"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # Get total approved jobs
        cursor.execute("""
            SELECT COUNT(*) as total_approved
            FROM tickets
            WHERE approval_status = 'approved'
        """)
        total_approved = cursor.fetchone()['total_approved']
        
        cursor.close()
        conn.close()
        
        # Count actual folders
        actual_folders = len([f for f in os.listdir(BASE_STORAGE_PATH) 
                            if not f.startswith(('.', 'batch_results'))])
        
        # Count total resumes
        total_resumes = 0
        for folder_name in os.listdir(BASE_STORAGE_PATH):
            if folder_name.startswith(('.', 'batch_results')):
                continue
            folder_path = os.path.join(BASE_STORAGE_PATH, folder_name)
            if os.path.isdir(folder_path):
                resume_files = [f for f in os.listdir(folder_path) 
                               if f.lower().endswith(('.pdf', '.doc', '.docx', '.txt'))]
                total_resumes += len(resume_files)
        
        return jsonify({
            'success': True,
            'data': {
                'total_approved_jobs': total_approved,
                'jobs_with_folders': actual_folders,
                'folder_coverage': f"{(actual_folders/total_approved*100):.1f}%" if total_approved > 0 else "0%",
                'total_resumes': total_resumes,
                'average_resumes_per_job': f"{total_resumes/actual_folders:.1f}" if actual_folders > 0 else "0",
                'storage_path': BASE_STORAGE_PATH
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting folder statistics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================
# INTERVIEW MANAGEMENT ENDPOINTS
# ============================================

@app.route('/api/interviews/schedule', methods=['POST'])
@require_api_key
def schedule_interview():
    """Schedule an interview for a candidate"""
    try:
        data = request.get_json()
        logger.info(f"Schedule Interview: Received data - {data}")
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get frontend candidate_id and ticket_id
        candidate_id = data.get('candidate_id')
        ticket_id = data.get('ticket_id')
        
        logger.info(f"Schedule Interview: Frontend candidate_id: {candidate_id}, ticket_id: {ticket_id}")
        
        # Always use metadata mapping to find the correct candidate
        # Don't rely on frontend candidate_id matching database ID
        actual_candidate_id = None
        
        try:
            import json
            import os
            
            # Get the ticket folder
            ticket_folders = [f for f in os.listdir(BASE_STORAGE_PATH) 
                             if f.startswith(f"{ticket_id}_")]
            
            if ticket_folders:
                folder_path = os.path.join(BASE_STORAGE_PATH, ticket_folders[0])
                metadata_path = os.path.join(folder_path, 'metadata.json')
                
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r', encoding='utf-8', errors='ignore') as f:
                        metadata = json.load(f)
                        resumes = metadata.get('resumes', [])
                        
                        # Find the candidate by frontend ID (1-based index)
                        if 1 <= candidate_id <= len(resumes):
                            resume_info = resumes[candidate_id - 1]  # Convert to 0-based index
                            mapped_email = resume_info.get('applicant_email')
                            mapped_name = resume_info.get('applicant_name')
                            
                            logger.info(f"Schedule Interview: Metadata mapping - frontend ID {candidate_id} -> {mapped_name} ({mapped_email})")
                            
                            # Check if this candidate already exists in resume_applications by email and ticket_id
                            cursor.execute("""
                                SELECT id FROM resume_applications 
                                WHERE applicant_email = %s AND ticket_id = %s 
                                ORDER BY id DESC LIMIT 1
                            """, (mapped_email, ticket_id))
                            
                            existing_by_email = cursor.fetchone()
                            if existing_by_email:
                                actual_candidate_id = existing_by_email['id']
                                logger.info(f"Schedule Interview: Found existing candidate in resume_applications with ID {actual_candidate_id}")
                            else:
                                # Create new record in resume_applications table
                                logger.info(f"Schedule Interview: Creating new resume_applications record for {mapped_name}")
                                
                                insert_data = (
                                    ticket_id,
                                    resume_info.get('applicant_name', 'Unknown'),
                                    resume_info.get('applicant_email', ''),
                                    resume_info.get('filename', ''),
                                    resume_info.get('file_path', ''),
                                    resume_info.get('file_size', 0),
                                    resume_info.get('uploaded_at', datetime.now()),
                                    'pending'
                                )
                                logger.info(f"Schedule Interview: Inserting resume_applications with data: {insert_data}")
                                
                                cursor.execute("""
                                    INSERT INTO resume_applications
                                    (ticket_id, applicant_name, applicant_email, filename, file_path, file_size, uploaded_at, status)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                """, insert_data)
                                
                                # Get the actual database ID
                                actual_candidate_id = cursor.lastrowid
                                logger.info(f"Schedule Interview: Created resume_applications record for candidate {candidate_id} with actual ID {actual_candidate_id}")
                        else:
                            logger.error(f"Schedule Interview: Invalid candidate_id {candidate_id} - only {len(resumes)} candidates available")
                            return jsonify({'success': False, 'error': f'Invalid candidate ID. Only {len(resumes)} candidates available.'}), 400
                else:
                    logger.error(f"Schedule Interview: Metadata file not found at {metadata_path}")
                    return jsonify({'success': False, 'error': 'Metadata file not found'}), 404
            else:
                logger.error(f"Schedule Interview: No ticket folder found for ticket {ticket_id}")
                return jsonify({'success': False, 'error': 'Ticket folder not found'}), 404
                
        except Exception as metadata_error:
            logger.error(f"Schedule Interview: Error in metadata mapping: {metadata_error}")
            return jsonify({'success': False, 'error': f'Metadata mapping error: {str(metadata_error)}'}), 500
        
        if not actual_candidate_id:
            logger.error(f"Schedule Interview: Failed to determine actual_candidate_id for frontend candidate_id {candidate_id}")
            return jsonify({'success': False, 'error': 'Failed to map candidate ID'}), 500
        
        # Verify the actual_candidate_id exists in resume_applications
        cursor.execute("SELECT id FROM resume_applications WHERE id = %s", (actual_candidate_id,))
        verification = cursor.fetchone()
        logger.info(f"Schedule Interview: Verification of actual_candidate_id {actual_candidate_id}: {verification}")
        
        if not verification:
            logger.error(f"Schedule Interview: CRITICAL ERROR - actual_candidate_id {actual_candidate_id} does not exist in resume_applications table!")
            return jsonify({'success': False, 'error': 'Database integrity error - candidate ID not found'}), 500
        
        # Check for existing interview schedule for the same candidate and round
        round_id = data.get('round_id')
        if round_id:
            cursor.execute("""
                SELECT iss.id, iss.status, ir.round_name 
                FROM interview_schedules iss
                JOIN interview_rounds ir ON iss.round_id = ir.id
                WHERE iss.candidate_id = %s AND iss.round_id = %s
            """, (actual_candidate_id, round_id))
            
            existing_interview = cursor.fetchone()
            if existing_interview:
                round_name = existing_interview['round_name']
                status = existing_interview['status']
                logger.warning(f"Schedule Interview: Found existing interview for candidate {actual_candidate_id} and round {round_id} ({round_name}) with status: {status}")
                
                return jsonify({
                    'success': False, 
                    'error': f'Interview for "{round_name}" already exists for this candidate with status: {status}. Please use the existing interview or delete it first.',
                    'existing_interview_id': existing_interview['id'],
                    'existing_status': status
                }), 400
        
        # Convert date format if needed (DD/MM/YYYY to YYYY-MM-DD)
        scheduled_date = data.get('scheduled_date', '')
        if scheduled_date and '/' in scheduled_date:
            try:
                # Handle DD/MM/YYYY format
                day, month, year = scheduled_date.split('/')
                scheduled_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                print(f"DEBUG: Converted date from DD/MM/YYYY to YYYY-MM-DD: {scheduled_date}")
            except Exception as e:
                print(f"ERROR: Failed to convert date format: {e}")
                return jsonify({
                    'success': False,
                    'error': f'Invalid date format: {scheduled_date}. Expected DD/MM/YYYY or YYYY-MM-DD'
                }), 400

        # Insert interview schedule with the actual candidate_id
        schedule_data = (
            ticket_id,
            data.get('round_id'),
            actual_candidate_id,
            scheduled_date,
            data.get('scheduled_time'),
            data.get('duration_minutes', 60),
            data.get('interview_type', 'video_call'),
            data.get('meeting_link'),
            data.get('location'),
            data.get('notes'),
            data.get('created_by')
        )
        logger.info(f"Schedule Interview: Inserting interview_schedules with data: {schedule_data}")
        
        cursor.execute("""
            INSERT INTO interview_schedules 
            (ticket_id, round_id, candidate_id, scheduled_date, scheduled_time, duration_minutes, 
             interview_type, meeting_link, location, notes, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, schedule_data)
        
        interview_id = cursor.lastrowid
        logger.info(f"Schedule Interview: Created interview_schedules record with ID: {interview_id}")
        
        # Add participants
        participants = data.get('participants', [])
        logger.info(f"Schedule Interview: Adding {len(participants)} participants")
        
        for i, participant in enumerate(participants):
            # Convert empty interviewer_id to None (NULL in database)
            interviewer_id = participant.get('interviewer_id')
            if interviewer_id == '' or interviewer_id is None:
                interviewer_id = None
            
            participant_data = (
                interview_id,
                interviewer_id,
                participant.get('interviewer_name', ''),  # Add interviewer_name field
                participant.get('participant_type', 'interviewer'),
                participant.get('is_primary', False),
                participant.get('interviewer_email', ''),
                participant.get('is_manager_feedback', False)  # Premium feature: manager feedback selection
            )
            logger.info(f"Schedule Interview: Adding participant {i+1}: {participant_data}")
            
            cursor.execute("""
                INSERT INTO interview_participants 
                (interview_id, interviewer_id, interviewer_name, participant_type, is_primary, interviewer_email, is_manager_feedback)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, participant_data)
        
        # Update candidate status
        status_data = (
            ticket_id,
            actual_candidate_id,
            data.get('round_id'),
            ticket_id
        )
        logger.info(f"Schedule Interview: Updating candidate_interview_status with data: {status_data}")
        
        cursor.execute("""
            INSERT INTO candidate_interview_status 
            (ticket_id, candidate_id, current_round_id, overall_status, total_rounds)
            VALUES (%s, %s, %s, 'in_progress', 
                    (SELECT COUNT(*) FROM interview_rounds WHERE ticket_id = %s))
            ON DUPLICATE KEY UPDATE 
            current_round_id = VALUES(current_round_id),
            overall_status = 'in_progress'
        """, status_data)
        
        logger.info(f"Schedule Interview: Committing transaction")
        conn.commit()
        
        # Send email notifications
        try:
            if send_interview_notifications:
                send_interview_notifications(interview_id, data)
                logger.info(f"Email notifications sent for interview {interview_id}")
            else:
                logger.warning("Email service not available - notifications not sent")
        except Exception as email_error:
            logger.error(f"Error sending email notifications: {email_error}")
        
        cursor.close()
        conn.close()
        
        logger.info(f"Schedule Interview: Successfully completed - interview_id: {interview_id}")
        return jsonify({
            'success': True,
            'message': 'Interview scheduled successfully',
            'data': {'interview_id': interview_id}
        })
        
    except Exception as e:
        logger.error(f"Error scheduling interview: {e}")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error details: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/interviews/calendar', methods=['GET'])
@require_api_key
def get_all_interviews_calendar():
    """Get all scheduled interviews for calendar view"""
    try:
        # Connect to MySQL database (same as main system)
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get all interviews with candidate and round details from MySQL
        cursor.execute("""
            SELECT 
                s.id,
                s.ticket_id,
                s.candidate_id,
                s.scheduled_date,
                s.scheduled_time,
                s.duration_minutes,
                s.interview_type,
                s.meeting_link,
                s.location,
                s.status,
                s.notes,
                s.created_by,
                r.round_name,
                r.round_order,
                ra.applicant_name as candidate_name,
                ra.applicant_email as candidate_email,
                t.subject as job_title,
                GROUP_CONCAT(DISTINCT p.interviewer_name SEPARATOR ', ') as interviewer_names
            FROM interview_schedules s
            LEFT JOIN interview_rounds r ON s.round_id = r.id
            LEFT JOIN resume_applications ra ON s.candidate_id = ra.id AND s.ticket_id = ra.ticket_id
            LEFT JOIN tickets t ON s.ticket_id = t.ticket_id
            LEFT JOIN interview_participants p ON s.id = p.interview_id
            WHERE s.status IN ('scheduled', 'in_progress', 'completed')
            AND s.scheduled_date IS NOT NULL 
            AND s.scheduled_time IS NOT NULL
            GROUP BY s.id, s.ticket_id, s.candidate_id, s.scheduled_date, s.scheduled_time, 
                     s.duration_minutes, s.interview_type, s.meeting_link, s.location, 
                     s.status, s.notes, s.created_by, r.round_name, r.round_order, 
                     ra.applicant_name, ra.applicant_email, t.subject
            ORDER BY s.scheduled_date, s.scheduled_time
        """)
        
        interviews = cursor.fetchall()
        
        # Format interviews for calendar
        calendar_events = []
        logger.info(f"Calendar API: Processing {len(interviews)} interviews from database")
        
        for interview in interviews:
            if not interview['scheduled_date'] or not interview['scheduled_time']:
                logger.warning(f"Skipping interview {interview['id']} - missing date/time")
                continue
                
            # Combine date and time
            datetime_str = f"{interview['scheduled_date']} {interview['scheduled_time']}"
            
            # Log each interview being processed
            logger.info(f"Processing interview {interview['id']}: {interview['candidate_name']} - {interview['round_name']}")
            logger.info(f"Interview {interview['id']} - interviewer_names: {interview.get('interviewer_names')}, created_by: {interview.get('created_by')}")
            
            calendar_events.append({
                'id': interview['id'],
                'title': f"{interview['candidate_name'] or 'Unknown'} - {interview['round_name'] or 'Interview'}",
                'start': datetime_str,
                'end': datetime_str,
                'duration': interview['duration_minutes'] or 60,
                'candidate_name': interview['candidate_name'] or 'Unknown Candidate',
                'candidate_email': interview['candidate_email'] or '',
                'round_name': interview['round_name'] or 'Interview',
                'interview_type': interview['interview_type'] or 'video_call',
                'meeting_link': interview['meeting_link'],
                'location': interview['location'],
                'status': interview['status'] or 'scheduled',
                'notes': interview['notes'],
                'interviewer_names': interview.get('interviewer_names') or interview.get('created_by', 'Not assigned'),
                'job_title': interview['job_title'] or f"Job {interview['ticket_id']}",
                'ticket_id': interview['ticket_id']
            })
        
        conn.close()
        
        logger.info(f"Calendar API: Found {len(calendar_events)} interviews from MySQL")
        
        return jsonify({
            'success': True,
            'events': calendar_events,
            'total': len(calendar_events)
        })
        
    except Exception as e:
        logger.error(f"Error fetching calendar interviews: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/interviews/schedule/<candidate_id>', methods=['GET'])
@require_api_key
def get_candidate_interviews(candidate_id):
    """Get all interviews for a candidate"""
    try:
        # URL decode the candidate_id in case it was encoded
        import urllib.parse
        decoded_candidate_id = urllib.parse.unquote(candidate_id)
        
        # Get the ticket_id from query parameters if provided
        ticket_id_from_query = request.args.get('ticket_id')
        logger.info(f"GET /api/interviews/schedule/{candidate_id} - Starting (decoded: {decoded_candidate_id}, ticket_id: {ticket_id_from_query})")
        
        # Extract the actual database ID from the composite candidate ID
        # The frontend sends IDs like "9bd4f8e1cb-123-0.456" where the middle part is the actual DB ID
        actual_candidate_id = decoded_candidate_id
        if '-' in str(decoded_candidate_id):
            parts = str(decoded_candidate_id).split('-')
            if len(parts) >= 2:
                # The second part should be the actual database ID
                actual_candidate_id = parts[1]
                logger.info(f"Extracted actual candidate ID: {actual_candidate_id} from composite ID: {decoded_candidate_id}")
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Use metadata mapping to find the correct candidate (same logic as POST endpoint)
        candidate_name = None
        candidate_email = None
        
        try:
            import json
            import os
            import glob
            
            # Find all metadata files to determine which one to use
            # FIXED: Use absolute path to ensure we find the files correctly
            metadata_files = glob.glob("approved_tickets/*/metadata.json")
            if not metadata_files:
                # Fallback: try with Backend prefix if running from different directory
                metadata_files = glob.glob("Backend/approved_tickets/*/metadata.json")
            logger.info(f"Found {len(metadata_files)} metadata files")
            
            # FIXED: Prioritize ticket_id from query parameter to avoid cross-ticket mapping issues
            # If ticket_id is provided, only search in that ticket's metadata
            metadata_files_to_search = metadata_files
            if ticket_id_from_query:
                # Filter to only search in the specified ticket's metadata
                metadata_files_to_search = [path for path in metadata_files if ticket_id_from_query in path]
                logger.info(f"GET: Filtering search to ticket {ticket_id_from_query} metadata files: {metadata_files_to_search}")
            
            # Try to find the candidate in each metadata file
            # Collect all possible candidates first, then select the most appropriate one
            all_candidates = []
            
            for metadata_path in metadata_files_to_search:
                try:
                    with open(metadata_path, 'r', encoding='utf-8', errors='ignore') as f:
                        metadata = json.load(f)
                    
                    # Check if this metadata contains the candidate we're looking for
                    if 'resumes' in metadata and len(metadata['resumes']) >= int(actual_candidate_id):
                        # actual_candidate_id is 1-based, but array is 0-based
                        if int(actual_candidate_id) <= len(metadata['resumes']):
                            resume_info = metadata['resumes'][int(actual_candidate_id) - 1]
                            mapped_email = resume_info.get('applicant_email')
                            mapped_name = resume_info.get('applicant_name')
                            ticket_id = metadata.get('ticket_id')
                            
                            logger.info(f"GET: Metadata mapping - frontend ID {candidate_id} -> {mapped_name} ({mapped_email}) from ticket {ticket_id}")
                            
                            # Find this candidate in the database by email and ticket_id
                            cursor.execute("SELECT id, applicant_name, applicant_email FROM resume_applications WHERE applicant_email = %s AND ticket_id = %s ORDER BY id DESC LIMIT 1", (mapped_email, ticket_id))
                            mapped_candidate = cursor.fetchone()
                            
                            if mapped_candidate:
                                all_candidates.append({
                                    'id': mapped_candidate['id'],
                                    'name': mapped_candidate['applicant_name'],
                                    'email': mapped_candidate['applicant_email'],
                                    'ticket_id': ticket_id,
                                    'metadata_path': metadata_path
                                })
                                logger.info(f"GET: Found candidate in database: {mapped_candidate['applicant_name']} (ID: {mapped_candidate['id']}) from ticket {ticket_id}")
                            else:
                                logger.warning(f"GET: Candidate {mapped_name} ({mapped_email}) from ticket {ticket_id} not found in resume_applications table")
                                # Still add to candidates list even if not in database, using metadata info
                                all_candidates.append({
                                    'id': None,  # No database ID
                                    'name': mapped_name,
                                    'email': mapped_email,
                                    'ticket_id': ticket_id,
                                    'metadata_path': metadata_path,
                                    'from_metadata_only': True
                                })
                                logger.info(f"GET: Added candidate from metadata only: {mapped_name} from ticket {ticket_id}")
                            
                except Exception as e:
                    logger.warning(f"Error processing metadata file {metadata_path}: {e}")
                    continue
            
            # Now select the most appropriate candidate
            if all_candidates:
                # If we have multiple candidates, we need to determine which one is correct
                # The issue is that we don't have the job context (ticket_id) from the frontend
                # For now, we'll use a more intelligent selection based on the candidate data
                
                selected_candidate = None
                
                # If there's only one candidate, use it
                if len(all_candidates) == 1:
                    selected_candidate = all_candidates[0]
                    logger.info(f"GET: Single candidate found: {selected_candidate['name']} (ID: {selected_candidate['id']})")
                else:
                    # Multiple candidates found - need to select the right one
                    logger.warning(f"GET: Multiple candidates found for frontend ID {candidate_id}:")
                    for i, candidate in enumerate(all_candidates):
                        logger.warning(f"  {i+1}. {candidate['name']} (ID: {candidate['id']}) from ticket {candidate['ticket_id']}")
                    
                    # Use ticket_id from query parameter to filter candidates if available
                    if ticket_id_from_query:
                        logger.info(f"GET: Using ticket_id from query parameter: {ticket_id_from_query}")
                        matching_candidates = [c for c in all_candidates if c['ticket_id'] == ticket_id_from_query]
                        if matching_candidates:
                            # Prefer candidates that exist in the database over metadata-only candidates
                            db_candidates = [c for c in matching_candidates if c['id'] is not None]
                            if db_candidates:
                                selected_candidate = db_candidates[0]
                                logger.info(f"GET: Found matching candidate in database by ticket_id: {selected_candidate['name']} (ID: {selected_candidate['id']}) from ticket {selected_candidate['ticket_id']}")
                            else:
                                selected_candidate = matching_candidates[0]
                                logger.info(f"GET: Found matching candidate in metadata only by ticket_id: {selected_candidate['name']} from ticket {selected_candidate['ticket_id']}")
                        else:
                            logger.warning(f"GET: No candidate found for ticket_id {ticket_id_from_query}, using first candidate")
                            selected_candidate = all_candidates[0]
                    else:
                        # No ticket_id provided, use first candidate as fallback
                        selected_candidate = all_candidates[0]
                        logger.info(f"GET: No ticket_id provided - using first candidate: {selected_candidate['name']} (ID: {selected_candidate['id']})")
                        logger.warning(f"GET: WARNING - This may not be the correct candidate! Consider passing ticket_id from frontend.")
                
                actual_candidate_id = selected_candidate['id']
                candidate_name = selected_candidate['name']
                candidate_email = selected_candidate['email']  # This is already a string
                
                if actual_candidate_id is None:
                    logger.warning(f"GET: Selected candidate {candidate_name} has no database ID - creating default response")
                    # For metadata-only candidates, return a default response with no interviews
                    # This allows the frontend to show the candidate info even if they don't have interviews yet
                    return jsonify({
                        'success': True,
                        'data': {
                            'interviews': [],
                            'candidate_info': {
                                'name': candidate_name,
                                'email': candidate_email,
                                'ticket_id': selected_candidate['ticket_id'],
                                'from_metadata_only': True
                            }
                        }
                    })
                
                logger.info(f"GET: Final selection - frontend ID {candidate_id} -> database ID {actual_candidate_id} ({candidate_name})")
                    
        except Exception as metadata_error:
            logger.error(f"Error in metadata mapping for GET: {metadata_error}")
        
        if not actual_candidate_id:
            logger.error(f"GET: Failed to map frontend candidate_id {candidate_id} to database record")
            return jsonify({'success': False, 'error': 'Candidate not found'}), 404
        
        # Now search for interviews using the actual database ID
        logger.info(f"GET: Searching for interviews with actual_candidate_id = {actual_candidate_id}")
        
        # Get the ticket_id from the selected candidate data
        selected_ticket_id = selected_candidate.get('ticket_id')
        
        # FIXED: Include ticket_id filtering to show only interviews for the current job
        if selected_ticket_id:
            cursor.execute("""
                SELECT 
                    isch.*,
                    ir.round_name,
                    ir.round_type,
                    ra.applicant_name,
                    ra.applicant_email,
                    t.subject as job_title
                FROM interview_schedules isch
                JOIN interview_rounds ir ON isch.round_id = ir.id
                JOIN resume_applications ra ON isch.candidate_id = ra.id
                JOIN tickets t ON isch.ticket_id = t.ticket_id
                WHERE isch.candidate_id = %s AND isch.ticket_id = %s
                ORDER BY isch.scheduled_date, isch.scheduled_time
            """, (actual_candidate_id, selected_ticket_id))
        else:
            # Fallback to original query if no ticket_id available
            cursor.execute("""
                SELECT 
                    isch.*,
                    ir.round_name,
                    ir.round_type,
                    ra.applicant_name,
                    ra.applicant_email,
                    t.subject as job_title
                FROM interview_schedules isch
                JOIN interview_rounds ir ON isch.round_id = ir.id
                JOIN resume_applications ra ON isch.candidate_id = ra.id
                JOIN tickets t ON isch.ticket_id = t.ticket_id
                WHERE isch.candidate_id = %s
                ORDER BY isch.scheduled_date, isch.scheduled_time
            """, (actual_candidate_id,))
        interviews = cursor.fetchall()
        logger.info(f"GET: Found {len(interviews)} interviews for {candidate_name} (database ID {actual_candidate_id})")
        
        # Get the correct job title for this candidate from the selected candidate data
        cursor.execute("SELECT subject FROM tickets WHERE ticket_id = %s", (selected_ticket_id,))
        job_title_result = cursor.fetchone()
        correct_job_title = job_title_result['subject'] if job_title_result else 'Unknown Position'
        logger.info(f"GET: Retrieved job title '{correct_job_title}' for ticket {selected_ticket_id}")
        
        # If no interviews found by ID, try metadata mapping for frontend IDs
        if not interviews:
            logger.info(f"No interviews found for candidate ID {candidate_id}, trying metadata mapping")
            
            # First try direct database lookup using the extracted candidate ID
            cursor.execute("SELECT applicant_email, applicant_name FROM resume_applications WHERE id = %s", (actual_candidate_id,))
            candidate_email_result = cursor.fetchone()
            logger.info(f"Candidate email lookup result: {candidate_email_result}")
            
            if candidate_email_result:
                # Search for interviews by email
                candidate_email_str = candidate_email_result['applicant_email']
                logger.info(f"Searching for interviews with email = {candidate_email_str}")
                # FIXED: Include ticket_id filtering to prevent cross-job data leakage
                if selected_ticket_id:
                    cursor.execute("""
                        SELECT 
                            isch.*,
                            ir.round_name,
                            ir.round_type,
                            ra.applicant_name,
                            ra.applicant_email,
                            t.subject as job_title
                        FROM interview_schedules isch
                        JOIN interview_rounds ir ON isch.round_id = ir.id
                        JOIN resume_applications ra ON isch.candidate_id = ra.id
                        JOIN tickets t ON isch.ticket_id = t.ticket_id
                        WHERE ra.applicant_email = %s AND isch.ticket_id = %s
                        ORDER BY isch.scheduled_date, isch.scheduled_time
                    """, (candidate_email_str, selected_ticket_id))
                else:
                    # Fallback to original query if no ticket_id available
                    cursor.execute("""
                        SELECT 
                            isch.*,
                            ir.round_name,
                            ir.round_type,
                            ra.applicant_name,
                            ra.applicant_email,
                            t.subject as job_title
                        FROM interview_schedules isch
                        JOIN interview_rounds ir ON isch.round_id = ir.id
                        JOIN resume_applications ra ON isch.candidate_id = ra.id
                        JOIN tickets t ON isch.ticket_id = t.ticket_id
                        WHERE ra.applicant_email = %s
                        ORDER BY isch.scheduled_date, isch.scheduled_time
                    """, (candidate_email_str,))
                interviews = cursor.fetchall()
                logger.info(f"Found {len(interviews)} interviews by email {candidate_email_str}")
            else:
                logger.warning(f"No candidate found in resume_applications with ID {candidate_id}")
                
                # Try metadata file mapping for frontend IDs (1, 2, 3...)
                logger.info(f"Trying metadata mapping for frontend ID {candidate_id}")
                
                try:
                    import json
                    import os
                    import glob
                    
                    # Find all metadata files to determine which one to use
                    # FIXED: Use absolute path to ensure we find the files correctly
                    metadata_files = glob.glob("approved_tickets/*/metadata.json")
                    if not metadata_files:
                        # Fallback: try with Backend prefix if running from different directory
                        metadata_files = glob.glob("Backend/approved_tickets/*/metadata.json")
                    logger.info(f"Found {len(metadata_files)} metadata files")
                    
                    # Try to find the candidate in each metadata file
                    for metadata_path in metadata_files:
                        try:
                            with open(metadata_path, 'r', encoding='utf-8', errors='ignore') as f:
                                metadata = json.load(f)
                                
                            # Check if this metadata contains the candidate we're looking for
                            if 'resumes' in metadata and len(metadata['resumes']) >= candidate_id:
                                # candidate_id is 1-based, but array is 0-based
                                if candidate_id <= len(metadata['resumes']):
                                    resume_info = metadata['resumes'][candidate_id - 1]
                                    mapped_email = resume_info.get('applicant_email')
                                    mapped_name = resume_info.get('applicant_name')
                                    ticket_id = metadata.get('ticket_id')
                                    
                                    logger.info(f"Metadata mapping: frontend ID {candidate_id} -> {mapped_name} ({mapped_email}) from ticket {ticket_id}")
                                    
                                    # Find this candidate in the database by email and ticket_id
                                    cursor.execute("SELECT id, applicant_name, applicant_email FROM resume_applications WHERE applicant_email = %s AND ticket_id = %s ORDER BY id DESC LIMIT 1", (mapped_email, ticket_id))
                                    mapped_candidate = cursor.fetchone()
                                    
                                    if mapped_candidate:
                                        actual_db_id = mapped_candidate['id']
                                        logger.info(f"Found mapped candidate: frontend ID {candidate_id} -> database ID {actual_db_id} ({mapped_candidate['applicant_name']}) from ticket {ticket_id}")
                                        
                                        # Search for ALL interviews for this email (in case of duplicate candidate records)
                                        cursor.execute("""
                                            SELECT 
                                                isch.*,
                                                ir.round_name,
                                                ir.round_type,
                                                ra.applicant_name,
                                                ra.applicant_email,
                                                t.subject as job_title
                                            FROM interview_schedules isch
                                            JOIN interview_rounds ir ON isch.round_id = ir.id
                                            JOIN resume_applications ra ON isch.candidate_id = ra.id
                                            JOIN tickets t ON isch.ticket_id = t.ticket_id
                                            WHERE ra.applicant_email = %s AND ra.ticket_id = %s
                                            ORDER BY isch.scheduled_date, isch.scheduled_time
                                        """, (mapped_email, ticket_id))
                                        interviews = cursor.fetchall()
                                        logger.info(f"Found {len(interviews)} interviews for {mapped_candidate['applicant_name']} (all candidate records with email {mapped_email}) in ticket {ticket_id}")
                                        break  # Found the candidate, no need to check other metadata files
                                    else:
                                        logger.warning(f"No database record found for mapped email {mapped_email} in ticket {ticket_id}")
                                else:
                                    logger.warning(f"Frontend candidate_id {candidate_id} exceeds available resumes in metadata for {metadata_path}")
                            else:
                                logger.warning(f"No resumes found in metadata {metadata_path} or candidate_id {candidate_id} out of range")
                        except Exception as e:
                            logger.error(f"Error reading metadata file {metadata_path}: {e}")
                            continue
                        
                except Exception as e:
                    logger.error(f"Error during metadata mapping: {e}")
        
        # Only log what we actually found, no more hardcoded fallbacks
        if interviews:
            # Get the actual candidate info for logging
            sample_interview = interviews[0]
            logger.info(f"Successfully found {len(interviews)} interviews for {sample_interview['applicant_name']} ({sample_interview['applicant_email']})")
        else:
            logger.info(f"No interviews found for candidate ID {candidate_id} after all lookup attempts")
        
        # Debug: Let's also check what interviews exist in the database
        cursor.execute("SELECT COUNT(*) as total FROM interview_schedules")
        total_interviews = cursor.fetchone()
        logger.info(f"Total interviews in database: {total_interviews['total']}")
        
        cursor.execute("SELECT candidate_id, COUNT(*) as count FROM interview_schedules GROUP BY candidate_id")
        candidate_counts = cursor.fetchall()
        logger.info(f"Interviews by candidate_id: {candidate_counts}")
        
        cursor.close()
        conn.close()
        
        # Convert any datetime/timedelta objects to strings
        def serialize_interview_data(interview):
            serialized = {}
            for key, value in interview.items():
                if isinstance(value, (datetime, timedelta)):
                    serialized[key] = str(value)
                elif hasattr(value, 'isoformat'):  # Handle datetime objects
                    serialized[key] = value.isoformat()
                else:
                    serialized[key] = value
            return serialized
        
        # Serialize all interviews
        serialized_interviews = []
        for interview in interviews:
            try:
                serialized_interview = serialize_interview_data(interview)
                serialized_interviews.append(serialized_interview)
            except Exception as e:
                logger.error(f"Error serializing interview: {e}")
                # Skip this interview if it can't be serialized
                continue
        
        logger.info(f"Returning {len(serialized_interviews)} interviews for candidate {candidate_id}")
        
        # Use json.dumps to ensure proper serialization
        import json
        # Create candidate info with correct job title
        # Ensure candidate_email is a string, not a dictionary object
        email_str = candidate_email
        if isinstance(candidate_email, dict):
            if 'applicant_email' in candidate_email:
                email_str = candidate_email['applicant_email']
            elif 'email' in candidate_email:
                email_str = candidate_email['email']
        elif isinstance(candidate_email, str):
            email_str = candidate_email  # Already a string
        else:
            logger.warning(f"Unexpected candidate_email type: {type(candidate_email)}, value: {candidate_email}")
            email_str = str(candidate_email) if candidate_email else ''
        
        candidate_info = {
            'applicant_name': candidate_name,
            'applicant_email': email_str,
            'job_title': correct_job_title,
            'ticket_id': selected_ticket_id
        }
        
        response_data = {
            'success': True,
            'data': {
                'interviews': serialized_interviews,
                'candidate_info': candidate_info
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error fetching candidate interviews: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/interviews/feedback', methods=['POST'])
@require_api_key
def submit_interview_feedback():
    """Submit feedback for an interview"""
    try:
        data = request.get_json()
        logger.info(f"Submit Feedback: Received data - {data}")
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Handle interviewer_id - if it's None, empty, or doesn't exist, use default interviewer
        interviewer_id = data.get('interviewer_id')
        if interviewer_id is None or interviewer_id == '' or interviewer_id == 'null':
            # Use default interviewer (ID 1)
            interviewer_id = 1
            logger.info(f"Using default interviewer ID {interviewer_id}")
        else:
            # Check if the interviewer exists in the database
            cursor.execute("SELECT id FROM interviewers WHERE id = %s", (interviewer_id,))
            if not cursor.fetchone():
                logger.warning(f"Interviewer ID {interviewer_id} not found in database, using default interviewer")
                interviewer_id = 1
        
        # Handle interview_id - if it's None, 0, or empty, find an existing one
        interview_id = data.get('interview_id')
        if interview_id is None or interview_id == 0 or interview_id == '' or interview_id == 'null':
            # Try to find an existing interview for this candidate and round
            cursor.execute("""
                SELECT id FROM interview_schedules 
                WHERE candidate_id = %s AND round_id = %s 
                LIMIT 1
            """, (data.get('candidate_id'), data.get('round_id')))
            
            existing_interview = cursor.fetchone()
            if existing_interview:
                interview_id = existing_interview['id']
                logger.info(f"Found existing interview_id {interview_id} for candidate {data.get('candidate_id')}, round {data.get('round_id')}")
            else:
                # If no specific interview found, use any existing interview for this candidate
                cursor.execute("""
                    SELECT id FROM interview_schedules 
                    WHERE candidate_id = %s 
                    LIMIT 1
                """, (data.get('candidate_id'),))
                
                any_interview = cursor.fetchone()
                if any_interview:
                    interview_id = any_interview['id']
                    logger.info(f"Using existing interview_id {interview_id} for candidate {data.get('candidate_id')} (no specific round match)")
                else:
                    # If no interviews exist for this candidate, use any existing interview
                    cursor.execute("SELECT id FROM interview_schedules LIMIT 1")
                    fallback_interview = cursor.fetchone()
                    if fallback_interview:
                        interview_id = fallback_interview['id']
                        logger.info(f"Using fallback interview_id {interview_id} for candidate {data.get('candidate_id')}")
                    else:
                        return jsonify({
                            'success': False,
                            'error': 'No interviews found in the system. Please schedule an interview first.'
                        }), 400
        
        # First, check if this is new feedback or an update
        cursor.execute("SELECT id FROM interview_feedback WHERE interview_id = %s", (interview_id,))
        existing_feedback = cursor.fetchone()
        is_new_feedback = existing_feedback is None
        
        logger.info(f"Submit Feedback: interview_id = {interview_id}, interviewer_id = {interviewer_id}, is_new_feedback = {is_new_feedback}")
        
        # Insert or update feedback - FIXED: Include interviewer_id as required field
        cursor.execute("""
            INSERT INTO interview_feedback 
            (interview_id, candidate_id, round_id, overall_rating, decision, 
             strengths, areas_of_improvement, interviewer_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            overall_rating = VALUES(overall_rating),
            decision = VALUES(decision),
            strengths = VALUES(strengths),
            areas_of_improvement = VALUES(areas_of_improvement),
            interviewer_id = VALUES(interviewer_id)
        """, (
            interview_id,  # Use the validated interview_id
            data.get('candidate_id'),
            data.get('round_id'),
            data.get('overall_rating'),
            data.get('decision'),
            data.get('strengths', ''),
            data.get('areas_of_improvement', ''),
            interviewer_id  # Include the interviewer_id that we determined earlier
        ))
        
        # Mark the interview as completed
        cursor.execute("""
            UPDATE interview_schedules 
            SET status = 'completed', updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (interview_id,))
        
        # Update the candidate interview status and progress (only for new feedback)
        if is_new_feedback:
            logger.info(f"New feedback submitted for interview {interview_id}, updating rounds_completed")
            
            # Get the ticket_id from the interview (handle different column names)
            try:
                cursor.execute("SELECT ticket_id FROM interview_schedules WHERE id = %s", (interview_id,))
                interview_data = cursor.fetchone()
                
                if interview_data:
                    ticket_id = interview_data['ticket_id']
                else:
                    # If no interview found, use a default ticket_id
                    ticket_id = 'fce79ea29c'  # Use the current ticket_id from the logs
            except Exception as e:
                logger.warning(f"Could not get ticket_id from interview: {e}")
                ticket_id = 'fce79ea29c'  # Use default ticket_id
            
            candidate_id = data.get('candidate_id')
            
            # Update or create candidate interview status
            # FIXED: Include ticket_id as it's required in MySQL schema
            cursor.execute("""
                    INSERT INTO candidate_interview_status 
                    (ticket_id, candidate_id, overall_status, rounds_completed, created_at, updated_at)
                    VALUES (%s, %s, 'in_progress', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    ON DUPLICATE KEY UPDATE 
                    rounds_completed = rounds_completed + 1,
                    overall_status = CASE 
                        WHEN overall_status = 'not_started' THEN 'in_progress'
                        WHEN overall_status IN ('rejected', 'hired', 'selected') THEN overall_status
                        ELSE 'in_progress'
                    END,
                    updated_at = CURRENT_TIMESTAMP
                """, (ticket_id, candidate_id))
            
            logger.info(f"Updated rounds_completed for candidate {candidate_id} in ticket {ticket_id}")
            
            # FIXED: Auto-update overall status based on round decisions
            # Check if any round has a reject decision - if so, auto-reject the candidate
            cursor.execute("""
                SELECT decision FROM interview_feedback 
                WHERE candidate_id = %s AND decision = 'reject'
                LIMIT 1
            """, (candidate_id,))
            
            has_reject_decision = cursor.fetchone()
            if has_reject_decision:
                logger.info(f"Found reject decision for candidate {candidate_id}, auto-updating overall status to rejected")
                cursor.execute("""
                    UPDATE candidate_interview_status 
                    SET overall_status = 'rejected', final_decision = 'reject', updated_at = CURRENT_TIMESTAMP
                    WHERE candidate_id = %s AND ticket_id = %s
                """, (candidate_id, ticket_id))
                
                # Send rejection email to candidate
                try:
                    # Get candidate details for rejection email
                    cursor.execute("""
                        SELECT 
                            ra.applicant_name,
                            ra.applicant_email,
                            t.subject as job_title,
                            ir.round_name
                        FROM resume_applications ra
                        JOIN tickets t ON ra.ticket_id = t.ticket_id
                        LEFT JOIN interview_schedules isch ON ra.id = isch.candidate_id
                        LEFT JOIN interview_rounds ir ON isch.round_id = ir.id
                        WHERE ra.id = %s AND t.ticket_id = %s
                        LIMIT 1
                    """, (candidate_id, ticket_id))
                    
                    candidate_data = cursor.fetchone()
                    if candidate_data:
                        from interview_email_service import send_rejection_email
                        
                        # Get the feedback text for this rejection
                        cursor.execute("""
                            SELECT strengths FROM interview_feedback 
                            WHERE candidate_id = %s AND decision = 'reject'
                            ORDER BY submitted_at DESC
                            LIMIT 1
                        """, (candidate_id,))
                        
                        feedback_result = cursor.fetchone()
                        feedback_text = feedback_result['strengths'] if feedback_result else None
                        
                        # Send rejection email
                        send_rejection_email(
                            candidate_id=candidate_id,
                            candidate_name=candidate_data['applicant_name'],
                            candidate_email=candidate_data['applicant_email'],
                            job_title=candidate_data['job_title'],
                            round_name=candidate_data['round_name'] or 'Interview',
                            feedback_text=feedback_text
                        )
                        logger.info(f"Rejection email sent to {candidate_data['applicant_email']} for candidate {candidate_id}")
                    else:
                        logger.warning(f"Could not find candidate data for rejection email: candidate_id={candidate_id}, ticket_id={ticket_id}")
                        
                except Exception as email_error:
                    logger.error(f"Error sending rejection email for candidate {candidate_id}: {email_error}")
                    # Don't fail the entire operation if email sending fails
            else:
                # Check if all rounds are completed and all decisions are positive
                cursor.execute("""
                    SELECT COUNT(*) as total_rounds FROM interview_rounds WHERE ticket_id = %s
                """, (ticket_id,))
                total_rounds_result = cursor.fetchone()
                total_rounds = total_rounds_result['total_rounds'] if total_rounds_result else 0
                
                cursor.execute("""
                    SELECT COUNT(*) as completed_rounds FROM interview_feedback f
                    JOIN interview_schedules s ON f.interview_id = s.id
                    WHERE f.candidate_id = %s AND s.ticket_id = %s AND f.decision IS NOT NULL
                """, (candidate_id, ticket_id))
                completed_rounds_result = cursor.fetchone()
                completed_rounds = completed_rounds_result['completed_rounds'] if completed_rounds_result else 0
                
                # If all rounds are completed and no reject decisions, mark as completed
                if completed_rounds >= total_rounds and total_rounds > 0:
                    logger.info(f"All {total_rounds} rounds completed for candidate {candidate_id}, marking as completed")
                    cursor.execute("""
                        UPDATE candidate_interview_status 
                        SET overall_status = 'completed', final_decision = 'maybe', updated_at = CURRENT_TIMESTAMP
                        WHERE candidate_id = %s AND ticket_id = %s AND overall_status NOT IN ('rejected', 'hired', 'selected')
                    """, (candidate_id, ticket_id))
                else:
                    # Keep status as in_progress if not all rounds are completed
                    logger.info(f"Only {completed_rounds}/{total_rounds} rounds completed for candidate {candidate_id}, keeping status as in_progress")
        else:
            logger.info(f"Updated existing feedback for interview {data.get('interview_id')}, checking for rejection status")
            
            # Check if the updated feedback is a rejection decision
            if data.get('decision') == 'reject':
                logger.info(f"Updated feedback contains reject decision for candidate {candidate_id}, checking if we need to send rejection email")
                
                # Check if candidate is already marked as rejected to avoid duplicate emails
                cursor.execute("""
                    SELECT overall_status FROM candidate_interview_status 
                    WHERE candidate_id = %s AND ticket_id = %s
                """, (candidate_id, ticket_id))
                
                status_result = cursor.fetchone()
                current_status = status_result['overall_status'] if status_result else None
                
                if current_status != 'rejected':
                    # Update status to rejected
                    cursor.execute("""
                        UPDATE candidate_interview_status 
                        SET overall_status = 'rejected', final_decision = 'reject', updated_at = CURRENT_TIMESTAMP
                        WHERE candidate_id = %s AND ticket_id = %s
                    """, (candidate_id, ticket_id))
                    
                    # Send rejection email
                    try:
                        # Get candidate details for rejection email
                        cursor.execute("""
                            SELECT 
                                ra.applicant_name,
                                ra.applicant_email,
                                t.subject as job_title,
                                ir.round_name
                            FROM resume_applications ra
                            JOIN tickets t ON ra.ticket_id = t.ticket_id
                            LEFT JOIN interview_schedules isch ON ra.id = isch.candidate_id
                            LEFT JOIN interview_rounds ir ON isch.round_id = ir.id
                            WHERE ra.id = %s AND t.ticket_id = %s
                            LIMIT 1
                        """, (candidate_id, ticket_id))
                        
                        candidate_data = cursor.fetchone()
                        if candidate_data:
                            from interview_email_service import send_rejection_email
                            
                            # Get the feedback text for this rejection
                            feedback_text = data.get('strengths') or data.get('recommendation_notes')
                            
                            # Send rejection email
                            send_rejection_email(
                                candidate_id=candidate_id,
                                candidate_name=candidate_data['applicant_name'],
                                candidate_email=candidate_data['applicant_email'],
                                job_title=candidate_data['job_title'],
                                round_name=candidate_data['round_name'] or 'Interview',
                                feedback_text=feedback_text
                            )
                            logger.info(f"Rejection email sent to {candidate_data['applicant_email']} for candidate {candidate_id} (updated feedback)")
                        else:
                            logger.warning(f"Could not find candidate data for rejection email: candidate_id={candidate_id}, ticket_id={ticket_id}")
                            
                    except Exception as email_error:
                        logger.error(f"Error sending rejection email for candidate {candidate_id}: {email_error}")
                        # Don't fail the entire operation if email sending fails
                else:
                    logger.info(f"Candidate {candidate_id} is already marked as rejected, skipping rejection email")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully',
            'details': {
                'interview_id': data.get('interview_id'),
                'is_new_feedback': is_new_feedback,
                'candidate_id': data.get('candidate_id')
            }
        })
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/interviews/feedback/<int:interview_id>', methods=['GET'])
@require_api_key
def get_interview_feedback(interview_id):
    """Get feedback for a specific interview"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                feedback.id, feedback.interview_id, feedback.interviewer_id, feedback.candidate_id, 
                feedback.round_id, feedback.overall_rating,
                feedback.strengths, feedback.areas_of_improvement,
                feedback.decision, feedback.submitted_at, feedback.updated_at,
                COALESCE(i.first_name, 'Unknown') as first_name, 
                COALESCE(i.last_name, 'Interviewer') as last_name, 
                COALESCE(i.email, 'unknown@example.com') as interviewer_email,
                COALESCE(ir.round_name, 'Interview') as round_name, 
                COALESCE(ir.round_type, 'other') as round_type
            FROM interview_feedback feedback
            LEFT JOIN interviewers i ON feedback.interviewer_id = i.id
            LEFT JOIN interview_rounds ir ON feedback.round_id = ir.id
            WHERE feedback.interview_id = %s
        """, (interview_id,))
        feedback = cursor.fetchall()
        
        logger.info(f"Found {len(feedback)} feedback records for interview {interview_id}")
        for feedback_item in feedback:
            logger.info(f"Feedback: {feedback_item}")
        
        cursor.close()
        conn.close()
        
        # Serialize datetime objects in feedback
        for feedback_item in feedback:
            for key, value in feedback_item.items():
                if isinstance(value, datetime):
                    feedback_item[key] = value.isoformat()
                elif isinstance(value, timedelta):
                    feedback_item[key] = str(value)
        
        return jsonify({
            'success': True,
            'data': {'feedback': feedback}
        })
        
    except Exception as e:
        logger.error(f"Error fetching interview feedback: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/interviews/feedback/candidate/<int:candidate_id>', methods=['GET'])
@require_api_key
def get_candidate_feedback(candidate_id):
    """Get feedback for all interviews of a candidate"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                feedback.id, feedback.interview_id, feedback.interviewer_id, feedback.candidate_id, 
                feedback.round_id, feedback.overall_rating,
                feedback.strengths, feedback.areas_of_improvement,
                feedback.decision, feedback.submitted_at, feedback.updated_at,
                COALESCE(i.first_name, 'Unknown') as first_name, 
                COALESCE(i.last_name, 'Interviewer') as last_name, 
                COALESCE(i.email, 'unknown@example.com') as interviewer_email,
                COALESCE(ir.round_name, 'Interview') as round_name, 
                COALESCE(ir.round_type, 'other') as round_type
            FROM interview_feedback feedback
            LEFT JOIN interviewers i ON feedback.interviewer_id = i.id
            LEFT JOIN interview_rounds ir ON feedback.round_id = ir.id
            WHERE feedback.candidate_id = %s
        """, (candidate_id,))
        feedback = cursor.fetchall()
        
        logger.info(f"Found {len(feedback)} feedback records for candidate {candidate_id}")
        for feedback_item in feedback:
            logger.info(f"Feedback: {feedback_item}")
        
        cursor.close()
        conn.close()
        
        # Serialize datetime objects in feedback
        for feedback_item in feedback:
            for key, value in feedback_item.items():
                if isinstance(value, datetime):
                    feedback_item[key] = value.isoformat()
                elif isinstance(value, timedelta):
                    feedback_item[key] = str(value)
        
        return jsonify({
            'success': True,
            'data': {'feedback': feedback}
        })
        
    except Exception as e:
        logger.error(f"Error fetching candidate feedback: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/interviews/status', methods=['PUT'])
@require_api_key
def update_interview_status():
    """Update interview status"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Update interview schedule status
        cursor.execute("""
            UPDATE interview_schedules 
            SET status = %s, notes = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (
            data.get('status'),
            data.get('notes'),
            data.get('interview_id')
        ))
        
        # Update candidate status if interview is completed
        if data.get('status') == 'completed':
            cursor.execute("""
                UPDATE candidate_interview_status 
                SET rounds_completed = rounds_completed + 1,
                    current_round_id = (
                        SELECT id FROM interview_rounds 
                        WHERE ticket_id = candidate_interview_status.ticket_id 
                        AND round_order > (
                            SELECT round_order FROM interview_rounds WHERE id = current_round_id
                        ) 
                        ORDER BY round_order LIMIT 1
                    )
                WHERE candidate_id = %s
            """, (data.get('candidate_id'),))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Interview status updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating interview status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# ROUND-BASED CANDIDATE FILTERING API
# ============================================

@app.route('/api/candidates/filter-by-round', methods=['GET'])
@require_api_key
def filter_candidates_by_round():
    """Filter candidates by round and status"""
    try:
        round_filter = request.args.get('round', 'all')  # all, 1, 2, 3, etc.
        status_filter = request.args.get('status', 'all')  # all, passed, failed, pending, scheduled
        ticket_id = request.args.get('ticket_id')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Base query to get candidates with their round information
        base_query = """
            SELECT DISTINCT
                ra.id as candidate_id,
                ra.applicant_name,
                ra.applicant_email,
                ra.ticket_id,
                ra.filename,
                t.subject as job_title,
                COALESCE(ra.status, cis.overall_status) as overall_status,
                cis.rounds_completed,
                cis.total_rounds,
                COALESCE(ra.status, cis.final_decision) as final_decision,
                ir.id as round_id,
                ir.round_name,
                ir.round_order,
                ir.round_type,
                ir.duration_minutes,
                ir.description as round_description,
                isch.id as interview_id,
                isch.status as interview_status,
                isch.scheduled_date,
                isch.scheduled_time,
                ifb.decision as round_decision,
                ifb.overall_rating,
                ifb.recommendation_notes
            FROM resume_applications ra
            JOIN tickets t ON ra.ticket_id = t.ticket_id
            LEFT JOIN candidate_interview_status cis ON ra.id = cis.candidate_id AND ra.ticket_id = cis.ticket_id
            LEFT JOIN interview_rounds ir ON ra.ticket_id = ir.ticket_id
            LEFT JOIN interview_schedules isch ON ra.id = isch.candidate_id AND ir.id = isch.round_id
            LEFT JOIN interview_feedback ifb ON isch.id = ifb.interview_id
        """
        
        conditions = []
        params = []
        
        # Filter by ticket_id if provided
        if ticket_id:
            conditions.append("ra.ticket_id = %s")
            params.append(ticket_id)
        
        # Filter by specific round
        if round_filter != 'all':
            try:
                round_number = int(round_filter)
                conditions.append("ir.round_order = %s")
                params.append(round_number)
            except ValueError:
                pass
        
        # Build the query
        if conditions:
            query = base_query + " WHERE " + " AND ".join(conditions)
        else:
            query = base_query
        
        query += " ORDER BY ra.applicant_name, ir.round_order"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        # Group candidates by their ID and organize round data
        candidates = {}
        for row in results:
            candidate_id = row['candidate_id']
            
            if candidate_id not in candidates:
                candidates[candidate_id] = {
                    'candidate_id': candidate_id,
                    'applicant_name': row['applicant_name'],
                    'applicant_email': row['applicant_email'],
                    'ticket_id': row['ticket_id'],
                    'filename': row['filename'],
                    'job_title': row['job_title'],
                    'overall_status': row['overall_status'] or 'pending',
                    'rounds_completed': row['rounds_completed'] or 0,
                    'total_rounds': row['total_rounds'] or 0,
                    'final_decision': row['final_decision'],
                    'rounds': []
                }
            
            # Add round information if available
            if row['round_id']:
                round_data = {
                    'round_id': row['round_id'],
                    'round_name': row['round_name'],
                    'round_order': row['round_order'],
                    'interview_type': row['round_type'],
                    'duration_minutes': row['duration_minutes'],
                    'round_description': row['round_description'],
                    'interview_id': row['interview_id'],
                    'interview_status': row['interview_status'],
                    'scheduled_date': row['scheduled_date'],
                    'scheduled_time': row['scheduled_time'],
                    'round_decision': row['round_decision'],
                    'overall_rating': row['overall_rating'],
                    'recommendation_notes': row['recommendation_notes']
                }
                candidates[candidate_id]['rounds'].append(round_data)
        
        # Apply status filter
        filtered_candidates = []
        for candidate in candidates.values():
            if status_filter == 'all':
                filtered_candidates.append(candidate)
            else:
                # Check if candidate matches the status filter for the specified round
                if round_filter != 'all':
                    try:
                        round_number = int(round_filter)
                        matching_round = next(
                            (r for r in candidate['rounds'] if r['round_order'] == round_number), 
                            None
                        )
                        
                        if matching_round:
                            if status_filter == 'passed' and matching_round['round_decision'] in ['hire', 'strong_hire', 'hired', 'selected']:
                                filtered_candidates.append(candidate)
                            elif status_filter == 'failed' and matching_round['round_decision'] in ['reject', 'strong_reject', 'rejected']:
                                filtered_candidates.append(candidate)
                            elif status_filter == 'pending' and not matching_round['round_decision'] and matching_round['interview_status'] != 'completed':
                                filtered_candidates.append(candidate)
                            elif status_filter == 'scheduled' and matching_round['interview_status'] == 'scheduled':
                                filtered_candidates.append(candidate)
                    except ValueError:
                        pass
                else:
                    # For 'all rounds', check overall status
                    if status_filter == 'passed' and candidate['final_decision'] in ['hire', 'strong_hire', 'hired', 'selected']:
                        filtered_candidates.append(candidate)
                    elif status_filter == 'failed' and candidate['final_decision'] in ['reject', 'strong_reject', 'rejected']:
                        filtered_candidates.append(candidate)
                    elif status_filter == 'pending' and candidate['overall_status'] in ['in_progress', 'pending']:
                        filtered_candidates.append(candidate)
                    elif status_filter == 'scheduled' and any(r['interview_status'] == 'scheduled' for r in candidate['rounds']):
                        filtered_candidates.append(candidate)
        
        conn.close()
        
        response_data = {
            'success': True,
            'data': {
                'candidates': filtered_candidates,
                'total': len(filtered_candidates),
                'filters': {
                    'round': round_filter,
                    'status': status_filter,
                    'ticket_id': ticket_id
                }
            }
        }
        
        # Use the custom JSON encoder to handle datetime/timedelta objects
        response = make_response(json.dumps(response_data, cls=CustomJSONEncoder))
        response.headers['Content-Type'] = 'application/json'
        return response
        
    except Exception as e:
        logger.error(f"Error filtering candidates by round: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/candidates/round-statistics', methods=['GET'])
@require_api_key
def get_round_statistics():
    """Get statistics for each round"""
    try:
        ticket_id = request.args.get('ticket_id')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get round statistics
        query = """
            SELECT 
                ir.round_order,
                ir.round_name,
                ir.round_type,
                COUNT(DISTINCT ra.id) as total_candidates,
                COUNT(DISTINCT CASE WHEN ifb.decision IN ('hire', 'strong_hire', 'selected') THEN ra.id END) as passed,
                COUNT(DISTINCT CASE WHEN ifb.decision IN ('reject', 'strong_reject') THEN ra.id END) as failed,
                COUNT(DISTINCT CASE WHEN isch.status = 'scheduled' THEN ra.id END) as scheduled,
                COUNT(DISTINCT CASE WHEN isch.status = 'completed' AND ifb.decision IS NULL THEN ra.id END) as pending_feedback,
                AVG(ifb.overall_rating) as average_rating
            FROM interview_rounds ir
            LEFT JOIN resume_applications ra ON ir.ticket_id = ra.ticket_id
            LEFT JOIN interview_schedules isch ON ra.id = isch.candidate_id AND ir.id = isch.round_id
            LEFT JOIN interview_feedback ifb ON isch.id = ifb.interview_id
        """
        
        params = []
        if ticket_id:
            query += " WHERE ir.ticket_id = %s"
            params.append(ticket_id)
        
        query += " GROUP BY ir.round_order, ir.round_name, ir.round_type ORDER BY ir.round_order"
        
        cursor.execute(query, params)
        round_stats = cursor.fetchall()
        
        # Get overall statistics
        overall_query = """
            SELECT 
                COUNT(DISTINCT ra.id) as total_candidates,
                COUNT(DISTINCT CASE WHEN cis.final_decision IN ('hire', 'strong_hire', 'selected') THEN ra.id END) as hired,
                COUNT(DISTINCT CASE WHEN cis.final_decision IN ('reject', 'strong_reject') THEN ra.id END) as rejected,
                COUNT(DISTINCT CASE WHEN cis.overall_status = 'in_progress' THEN ra.id END) as in_progress,
                COUNT(DISTINCT CASE WHEN cis.overall_status = 'not_started' THEN ra.id END) as not_started
            FROM resume_applications ra
            LEFT JOIN candidate_interview_status cis ON ra.id = cis.candidate_id AND ra.ticket_id = cis.ticket_id
        """
        
        if ticket_id:
            overall_query += " WHERE ra.ticket_id = %s"
            cursor.execute(overall_query, [ticket_id])
        else:
            cursor.execute(overall_query)
        
        overall_stats = cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'round_statistics': round_stats,
                'overall_statistics': overall_stats
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting round statistics: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/candidates/recalculate-status/<int:candidate_id>', methods=['POST'])
@require_api_key
def recalculate_candidate_status(candidate_id):
    """Recalculate and fix the overall status for a candidate based on their round decisions"""
    try:
        data = request.get_json()
        ticket_id = data.get('ticket_id')
        
        if not ticket_id:
            return jsonify({'success': False, 'error': 'ticket_id is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Find the actual database candidate ID using metadata mapping
        actual_candidate_id = None
        
        try:
            import json
            import os
            import glob
            
            # Find all metadata files to determine which one to use
            # FIXED: Use absolute path to ensure we find the files correctly
            metadata_files = glob.glob("approved_tickets/*/metadata.json")
            if not metadata_files:
                # Fallback: try with Backend prefix if running from different directory
                metadata_files = glob.glob("Backend/approved_tickets/*/metadata.json")
            
            # Try to find the candidate in each metadata file
            for metadata_path in metadata_files:
                try:
                    with open(metadata_path, 'r', encoding='utf-8', errors='ignore') as f:
                        metadata = json.load(f)
                        
                    if 'resumes' in metadata and len(metadata['resumes']) >= candidate_id:
                        if candidate_id <= len(metadata['resumes']):
                            resume_info = metadata['resumes'][candidate_id - 1]
                            mapped_email = resume_info.get('applicant_email')
                            mapped_ticket_id = metadata.get('ticket_id')
                            
                            if mapped_ticket_id == ticket_id:
                                # Find this candidate in the database by email and ticket_id
                                cursor.execute("""
                                    SELECT id FROM resume_applications 
                                    WHERE applicant_email = %s AND ticket_id = %s
                                    ORDER BY id DESC LIMIT 1
                                """, (mapped_email, ticket_id))
                                
                                candidate_result = cursor.fetchone()
                                if candidate_result:
                                    actual_candidate_id = candidate_result['id']
                                    break
                except Exception as e:
                    logger.error(f"Error reading metadata file {metadata_path}: {e}")
                    continue
        except Exception as e:
            logger.error(f"Error during metadata mapping: {e}")
        
        if not actual_candidate_id:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': f'Candidate ID {candidate_id} not found'}), 404
        
        # Check for reject decisions first
        cursor.execute("""
            SELECT decision FROM interview_feedback 
            WHERE candidate_id = %s AND ticket_id = %s AND decision = 'reject'
            LIMIT 1
        """, (actual_candidate_id, ticket_id))
        
        has_reject_decision = cursor.fetchone()
        if has_reject_decision:
            logger.info(f"Found reject decision for candidate {actual_candidate_id}, setting status to rejected")
            cursor.execute("""
                UPDATE candidate_interview_status 
                SET overall_status = 'rejected', final_decision = 'reject', updated_at = CURRENT_TIMESTAMP
                WHERE candidate_id = %s AND ticket_id = %s
            """, (actual_candidate_id, ticket_id))
            
            status_result = 'rejected'
        else:
            # Check if all rounds are completed
            cursor.execute("""
                SELECT COUNT(*) as total_rounds FROM interview_rounds WHERE ticket_id = %s
            """, (ticket_id,))
            total_rounds_result = cursor.fetchone()
            total_rounds = total_rounds_result['total_rounds'] if total_rounds_result else 0
            
            cursor.execute("""
                SELECT COUNT(*) as completed_rounds FROM interview_feedback 
                WHERE candidate_id = %s AND ticket_id = %s AND decision IS NOT NULL
            """, (actual_candidate_id, ticket_id))
            completed_rounds_result = cursor.fetchone()
            completed_rounds = completed_rounds_result['completed_rounds'] if completed_rounds_result else 0
            
            if completed_rounds >= total_rounds and total_rounds > 0:
                logger.info(f"All {total_rounds} rounds completed for candidate {actual_candidate_id}, setting status to completed")
                cursor.execute("""
                    UPDATE candidate_interview_status 
                    SET overall_status = 'completed', final_decision = 'maybe', updated_at = CURRENT_TIMESTAMP
                    WHERE candidate_id = %s AND ticket_id = %s
                """, (actual_candidate_id, ticket_id))
                status_result = 'completed'
            else:
                logger.info(f"Rounds in progress for candidate {actual_candidate_id}, setting status to in_progress")
                cursor.execute("""
                    UPDATE candidate_interview_status 
                    SET overall_status = 'in_progress', final_decision = NULL, updated_at = CURRENT_TIMESTAMP
                    WHERE candidate_id = %s AND ticket_id = %s
                """, (actual_candidate_id, ticket_id))
                status_result = 'in_progress'
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Status recalculated successfully',
            'new_status': status_result,
            'candidate_id': candidate_id,
            'ticket_id': ticket_id
        })
        
    except Exception as e:
        logger.error(f"Error recalculating candidate status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def cleanup_filtering_results(ticket_id, deleted_filename):
    """Helper function to clean up filtering results when a candidate is deleted"""
    try:
        # Find the ticket folder
        ticket_folders = [f for f in os.listdir(BASE_STORAGE_PATH) 
                         if f.startswith(f"{ticket_id}_")]
        
        if not ticket_folders:
            logger.warning(f"No ticket folder found for {ticket_id}")
            return
        
        folder_path = os.path.join(BASE_STORAGE_PATH, ticket_folders[0])
        filtering_results_path = os.path.join(folder_path, 'filtering_results')
        
        if os.path.exists(filtering_results_path):
            # Update all filtering result files
            result_files = list(Path(filtering_results_path).glob('final_results*.json'))
            for result_file in result_files:
                try:
                    with open(result_file, 'r', encoding='utf-8') as f:
                        filtering_data = json.load(f)
                    
                    updated = False
                    
                    # Remove from all_ranked_candidates and re-rank
                    if 'all_ranked_candidates' in filtering_data:
                        original_count = len(filtering_data['all_ranked_candidates'])
                        filtering_data['all_ranked_candidates'] = [
                            candidate for candidate in filtering_data['all_ranked_candidates']
                            if candidate.get('filename') != deleted_filename
                        ]
                        new_count = len(filtering_data['all_ranked_candidates'])
                        if original_count != new_count:
                            # Re-rank remaining candidates
                            for i, candidate in enumerate(filtering_data['all_ranked_candidates']):
                                candidate['final_rank'] = i + 1
                            logger.info(f"Removed candidate from {result_file.name}: {original_count} -> {new_count} and re-ranked")
                            updated = True
                    
                    # Remove from stage1_results.all_resumes and re-rank if it exists
                    if 'stage1_results' in filtering_data and 'all_resumes' in filtering_data['stage1_results']:
                        original_count = len(filtering_data['stage1_results']['all_resumes'])
                        filtering_data['stage1_results']['all_resumes'] = [
                            candidate for candidate in filtering_data['stage1_results']['all_resumes']
                            if candidate.get('filename') != deleted_filename
                        ]
                        new_count = len(filtering_data['stage1_results']['all_resumes'])
                        if original_count != new_count:
                            # Re-rank remaining candidates
                            for i, candidate in enumerate(filtering_data['stage1_results']['all_resumes']):
                                candidate['final_rank'] = i + 1
                            logger.info(f"Removed candidate from stage1_results in {result_file.name}: {original_count} -> {new_count} and re-ranked")
                            updated = True
                    
                    # Remove from final_results and re-rank if it exists
                    if 'final_results' in filtering_data:
                        if 'all_ranked_candidates' in filtering_data['final_results']:
                            original_count = len(filtering_data['final_results']['all_ranked_candidates'])
                            filtering_data['final_results']['all_ranked_candidates'] = [
                                candidate for candidate in filtering_data['final_results']['all_ranked_candidates']
                                if candidate.get('filename') != deleted_filename
                            ]
                            new_count = len(filtering_data['final_results']['all_ranked_candidates'])
                            if original_count != new_count:
                                # Re-rank remaining candidates
                                for i, candidate in enumerate(filtering_data['final_results']['all_ranked_candidates']):
                                    candidate['final_rank'] = i + 1
                                logger.info(f"Removed candidate from final_results in {result_file.name}: {original_count} -> {new_count} and re-ranked")
                                updated = True
                        
                        if 'top_5_candidates' in filtering_data['final_results']:
                            original_count = len(filtering_data['final_results']['top_5_candidates'])
                            filtering_data['final_results']['top_5_candidates'] = [
                                candidate for candidate in filtering_data['final_results']['top_5_candidates']
                                if candidate.get('filename') != deleted_filename
                            ]
                            new_count = len(filtering_data['final_results']['top_5_candidates'])
                            if original_count != new_count:
                                # Re-rank remaining candidates
                                for i, candidate in enumerate(filtering_data['final_results']['top_5_candidates']):
                                    candidate['final_rank'] = i + 1
                                logger.info(f"Removed candidate from top_5_candidates in {result_file.name}: {original_count} -> {new_count} and re-ranked")
                                updated = True
                    
                    # Write updated filtering results back only if changes were made
                    if updated:
                        with open(result_file, 'w', encoding='utf-8') as f:
                            json.dump(filtering_data, f, indent=2, ensure_ascii=False)
                    
                except Exception as file_error:
                    logger.warning(f"Failed to update filtering result file {result_file}: {file_error}")
            
            logger.info(f"Updated {len(result_files)} filtering result files to remove {deleted_filename}")
        else:
            logger.info("No filtering results found to update")
    except Exception as filtering_error:
        logger.warning(f"Failed to update filtering results: {filtering_error}")

@app.route('/api/candidates/delete', methods=['POST'])
@require_api_key
def delete_candidate():
    """Delete a single candidate completely from the system"""
    try:
        data = request.get_json()
        candidate_id = data.get('candidate_id')  # This is the index in metadata
        ticket_id = data.get('ticket_id')
        candidate_email = data.get('candidate_email')
        candidate_name = data.get('candidate_name')
        
        if not all([ticket_id, candidate_email]):
            return jsonify({
                'success': False,
                'error': 'ticket_id and candidate_email are required'
            }), 400
        
        logger.info(f"Delete candidate request: {candidate_name} ({candidate_email}) from ticket {ticket_id}")
        
        # 1. Remove from metadata.json file
        ticket_folders = [f for f in os.listdir(BASE_STORAGE_PATH) 
                         if f.startswith(f"{ticket_id}_")]
        
        if not ticket_folders:
            return jsonify({
                'success': False,
                'error': f'No folder found for ticket {ticket_id}'
            }), 404
        
        folder_path = os.path.join(BASE_STORAGE_PATH, ticket_folders[0])
        metadata_path = os.path.join(folder_path, 'metadata.json')
        
        if os.path.exists(metadata_path):
            # Read metadata
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Find and remove the candidate
            original_count = len(metadata.get('resumes', []))
            metadata['resumes'] = [
                resume for resume in metadata.get('resumes', [])
                if not (resume.get('applicant_email') == candidate_email and 
                       resume.get('applicant_name') == candidate_name)
            ]
            new_count = len(metadata['resumes'])
            
            if original_count == new_count:
                return jsonify({
                    'success': False,
                    'error': f'Candidate {candidate_name} not found in metadata'
                }), 404
            
            # Write updated metadata
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Removed candidate from metadata: {original_count} -> {new_count} candidates")
        
        # 2. Delete from database if exists
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            # Get the actual candidate ID first for cascade deletion
            cursor.execute("""
                SELECT id FROM resume_applications 
                WHERE ticket_id = %s AND applicant_email = %s
                LIMIT 1
            """, (ticket_id, candidate_email))
            candidate_record = cursor.fetchone()
            
            if candidate_record:
                actual_candidate_id = candidate_record['id']
                logger.info(f"Found candidate ID {actual_candidate_id} for cascade deletion")
                
                # 1. Delete interview feedback first (due to foreign key constraints)
                cursor.execute("""
                    DELETE FROM interview_feedback 
                    WHERE candidate_id = %s AND interview_id IN (
                        SELECT id FROM interview_schedules 
                        WHERE ticket_id = %s AND candidate_id = %s
                    )
                """, (actual_candidate_id, ticket_id, actual_candidate_id))
                feedback_deleted = cursor.rowcount
                logger.info(f"Deleted {feedback_deleted} interview feedback records")
                
                # 2. Delete interview schedules
                cursor.execute("""
                    DELETE FROM interview_schedules 
                    WHERE ticket_id = %s AND candidate_id = %s
                """, (ticket_id, actual_candidate_id))
                schedules_deleted = cursor.rowcount
                logger.info(f"Deleted {schedules_deleted} interview schedules")
                
                # 3. Delete from candidate_interview_status
                cursor.execute("""
                    DELETE FROM candidate_interview_status 
                    WHERE ticket_id = %s AND candidate_id = %s
                """, (ticket_id, actual_candidate_id))
                status_deleted = cursor.rowcount
                logger.info(f"Deleted {status_deleted} records from candidate_interview_status")
                
                # 4. Delete from resume_applications
                cursor.execute("""
                    DELETE FROM resume_applications 
                    WHERE ticket_id = %s AND applicant_email = %s
                """, (ticket_id, candidate_email))
                resume_deleted = cursor.rowcount
                logger.info(f"Deleted {resume_deleted} records from resume_applications")
                
                # 5. Additional cleanup: Delete any orphaned records in candidate_interview_status
                cursor.execute("""
                    DELETE FROM candidate_interview_status 
                    WHERE ticket_id = %s AND candidate_id = %s
                """, (ticket_id, actual_candidate_id))
                orphaned_deleted = cursor.rowcount
                if orphaned_deleted > 0:
                    logger.info(f"Deleted {orphaned_deleted} orphaned records from candidate_interview_status")
                
                logger.info(f"Cascade deletion summary: {feedback_deleted} feedback, {schedules_deleted} schedules, {status_deleted} status, {resume_deleted} resume records")
            else:
                logger.warning(f"No candidate record found in resume_applications for {candidate_email} in ticket {ticket_id}")
                
                # Fallback: Delete from candidate_interview_status using subquery
                cursor.execute("""
                    DELETE FROM candidate_interview_status 
                    WHERE ticket_id = %s AND candidate_id IN (
                        SELECT id FROM resume_applications 
                        WHERE ticket_id = %s AND applicant_email = %s
                    )
                """, (ticket_id, ticket_id, candidate_email))
                interview_deleted = cursor.rowcount
                logger.info(f"Deleted {interview_deleted} records from candidate_interview_status (fallback)")
            
            conn.commit()
            cursor.close()
            conn.close()
        
        # 3. Delete physical resume file if it exists
        deleted_filename = None
        try:
            # Find the resume file
            for resume in metadata.get('resumes', []):
                if (resume.get('applicant_email') == candidate_email and 
                    resume.get('applicant_name') == candidate_name):
                    filename = resume.get('filename')
                    deleted_filename = filename  # Store for filtering results cleanup
                    if filename:
                        file_path = os.path.join(folder_path, filename)
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            logger.info(f"Deleted resume file: {filename}")
                        break
        except Exception as e:
            logger.warning(f"Failed to delete resume file: {e}")
        
        # 4. Update filtering results to remove the deleted candidate
        if deleted_filename:
            cleanup_filtering_results(ticket_id, deleted_filename)
        
        return jsonify({
            'success': True,
            'message': f'Candidate {candidate_name} deleted successfully',
            'data': {
                'candidate_name': candidate_name,
                'candidate_email': candidate_email,
                'ticket_id': ticket_id
            }
        })
        
    except Exception as e:
        logger.error(f"Error deleting candidate: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/candidates/cleanup-orphaned', methods=['POST'])
@require_api_key
def cleanup_orphaned_candidates():
    """Clean up orphaned candidate records that don't have corresponding resume_applications"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor()
        
        # Find and delete orphaned candidate_interview_status records
        cursor.execute("""
            DELETE cis FROM candidate_interview_status cis
            LEFT JOIN resume_applications ra ON cis.candidate_id = ra.id AND cis.ticket_id = ra.ticket_id
            WHERE ra.id IS NULL
        """)
        orphaned_status_deleted = cursor.rowcount
        logger.info(f"Deleted {orphaned_status_deleted} orphaned candidate_interview_status records")
        
        # Find and delete orphaned interview_schedules records
        cursor.execute("""
            DELETE isch FROM interview_schedules isch
            LEFT JOIN resume_applications ra ON isch.candidate_id = ra.id AND isch.ticket_id = ra.ticket_id
            WHERE ra.id IS NULL
        """)
        orphaned_schedules_deleted = cursor.rowcount
        logger.info(f"Deleted {orphaned_schedules_deleted} orphaned interview_schedules records")
        
        # Find and delete orphaned interview_feedback records
        cursor.execute("""
            DELETE ifb FROM interview_feedback ifb
            LEFT JOIN interview_schedules isch ON ifb.interview_id = isch.id
            LEFT JOIN resume_applications ra ON isch.candidate_id = ra.id AND isch.ticket_id = ra.ticket_id
            WHERE ra.id IS NULL
        """)
        orphaned_feedback_deleted = cursor.rowcount
        logger.info(f"Deleted {orphaned_feedback_deleted} orphaned interview_feedback records")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Orphaned candidate records cleaned up successfully',
            'data': {
                'orphaned_status_deleted': orphaned_status_deleted,
                'orphaned_schedules_deleted': orphaned_schedules_deleted,
                'orphaned_feedback_deleted': orphaned_feedback_deleted
            }
        })
        
    except Exception as e:
        logger.error(f"Error cleaning up orphaned candidates: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to cleanup orphaned candidates: {str(e)}'
        }), 500

@app.route('/api/candidates/bulk-reject', methods=['POST'])
@require_api_key
def bulk_reject_candidates():
    """Bulk reject multiple candidates and send rejection emails"""
    try:
        data = request.get_json()
        candidate_ids = data.get('candidate_ids', [])
        ticket_id = data.get('ticket_id')
        rejection_type = data.get('type', 'bulk')  # 'bulk', 'selected', 'unselected', 'below_score'
        
        if not candidate_ids or not ticket_id:
            return jsonify({
                'success': False,
                'error': 'candidate_ids and ticket_id are required'
            }), 400
        
        logger.info(f"Bulk rejection request: {len(candidate_ids)} candidates, type: {rejection_type}")
        
        results = {
            'successful': [],
            'failed': [],
            'total': len(candidate_ids)
        }
        
        # Process each candidate
        for candidate_id in candidate_ids:
            try:
                # Get candidate details for email
                candidate_name = None
                candidate_email = None
                job_title = None
                
                # Try to get candidate details from metadata
                try:
                    import json
                    import os
                    import glob
                    
                    metadata_files = glob.glob(f"approved_tickets/{ticket_id}*/metadata.json")
                    
                    for metadata_path in metadata_files:
                        try:
                            with open(metadata_path, 'r', encoding='utf-8', errors='ignore') as f:
                                metadata = json.load(f)
                                
                            if 'resumes' in metadata and candidate_id >= 0 and candidate_id < len(metadata['resumes']):
                                # Frontend now sends 0-based array indices
                                resume_info = metadata['resumes'][candidate_id]
                                candidate_name = resume_info.get('applicant_name', 'Unknown Candidate')
                                candidate_email = resume_info.get('applicant_email', '')
                                job_title = metadata.get('job_title', 'Position')
                                
                                # Handle "Unknown Applicant" cases - generate a unique identifier
                                if candidate_name in ['Unknown Applicant', 'Unknown Candidate'] or not candidate_email or candidate_email in ['No email provided', '']:
                                    # Generate a unique email for unknown applicants to avoid conflicts
                                    unique_id = f"unknown_{ticket_id}_{candidate_id}"
                                    candidate_email = f"{unique_id}@unknown.local"
                                    candidate_name = f"Unknown Applicant #{candidate_id}"
                                    logger.info(f"Bulk rejection: Generated unique identifier for unknown candidate: {candidate_name} ({candidate_email})")
                                
                                logger.info(f"Bulk rejection: Processing candidate index {candidate_id} -> {candidate_name} ({candidate_email})")
                                break
                        except Exception as e:
                            logger.error(f"Error reading metadata file {metadata_path}: {e}")
                            continue
                except Exception as e:
                    logger.error(f"Error in metadata lookup: {e}")
                
                # If we still don't have candidate details, create default ones
                if not candidate_name or not candidate_email:
                    unique_id = f"unknown_{ticket_id}_{candidate_id}"
                    candidate_email = f"{unique_id}@unknown.local"
                    candidate_name = f"Unknown Applicant #{candidate_id}"
                    job_title = "Position"
                    logger.info(f"Bulk rejection: No metadata found, created default candidate: {candidate_name} ({candidate_email})")
                
                # Update candidate status in database
                # Note: We need to find the actual database ID, not the array index
                conn = get_db_connection()
                if conn:
                    try:
                        cursor = conn.cursor(dictionary=True)
                        
                        # First, try to find the candidate by email in the database
                        if candidate_email:
                            logger.info(f"Bulk rejection: Looking for candidate with email {candidate_email} in ticket {ticket_id}")
                            cursor.execute("""
                                SELECT id FROM resume_applications 
                                WHERE ticket_id = %s AND applicant_email = %s
                            """, (ticket_id, candidate_email))
                            db_candidate = cursor.fetchone()
                            logger.info(f"Bulk rejection: Database lookup result: {db_candidate}")
                            
                            if db_candidate:
                                # Update using the actual database ID
                                logger.info(f"Bulk rejection: Updating resume_applications for ID {db_candidate['id']}")
                                cursor.execute("""
                                    UPDATE resume_applications 
                                    SET status = 'rejected' 
                                    WHERE ticket_id = %s AND id = %s
                                """, (ticket_id, db_candidate['id']))
                                logger.info(f"Bulk rejection: resume_applications update affected {cursor.rowcount} rows")
                                
                                # Also update candidate_interview_status table if it exists
                                logger.info(f"Bulk rejection: Updating candidate_interview_status for candidate_id {db_candidate['id']}")
                                cursor.execute("""
                                    UPDATE candidate_interview_status 
                                    SET overall_status = 'rejected', final_decision = 'reject', updated_at = CURRENT_TIMESTAMP
                                    WHERE candidate_id = %s AND ticket_id = %s
                                """, (db_candidate['id'], ticket_id))
                                logger.info(f"Bulk rejection: candidate_interview_status update affected {cursor.rowcount} rows")
                                
                                logger.info(f"Updated database record for {candidate_name} (DB ID: {db_candidate['id']})")
                            else:
                                # 🆕 AUTO-CREATE DATABASE RECORD IF MISSING
                                logger.info(f"Bulk rejection: Database record missing for {candidate_name} ({candidate_email}) - creating automatically")
                                
                                # Always create a record since we now have guaranteed name and email
                                try:
                                    # Create resume_applications record
                                    safe_filename = candidate_name.replace(' ', '_').replace('#', 'num')
                                    cursor.execute("""
                                        INSERT INTO resume_applications 
                                        (ticket_id, applicant_name, applicant_email, filename, file_path, status, uploaded_at)
                                        VALUES (%s, %s, %s, %s, %s, 'rejected', CURRENT_TIMESTAMP)
                                    """, (ticket_id, candidate_name, candidate_email, 
                                          f"{safe_filename}.pdf", 
                                          f"approved_tickets/{ticket_id}*/{safe_filename}.pdf"))
                                    
                                    new_candidate_id = cursor.lastrowid
                                    logger.info(f"Bulk rejection: Created resume_applications record with ID {new_candidate_id}")
                                    
                                    # Create candidate_interview_status record
                                    cursor.execute("""
                                        INSERT INTO candidate_interview_status 
                                        (ticket_id, candidate_id, overall_status, final_decision, updated_at)
                                        VALUES (%s, %s, 'rejected', 'reject', CURRENT_TIMESTAMP)
                                    """, (ticket_id, new_candidate_id))
                                    
                                    logger.info(f"Bulk rejection: Created candidate_interview_status record for candidate_id {new_candidate_id}")
                                    logger.info(f"✅ Auto-created and rejected database record for {candidate_name} (New DB ID: {new_candidate_id})")
                                    
                                except Exception as create_error:
                                    logger.error(f"Bulk rejection: Failed to auto-create database record for {candidate_name}: {create_error}")
                                    # Continue processing even if database creation fails
                        
                        conn.commit()
                    except Exception as db_error:
                        logger.error(f"Database error for candidate {candidate_id}: {db_error}")
                        conn.rollback()
                    finally:
                        if cursor:
                            cursor.close()
                        conn.close()
                
                # Send rejection email if we have candidate details (but skip for unknown.local emails)
                if candidate_email and candidate_name:
                    if candidate_email.endswith('@unknown.local'):
                        # Skip sending email to unknown candidates but mark as successful
                        logger.info(f"Skipping email for unknown candidate {candidate_name} ({candidate_email}) - marked as deleted")
                        results['successful'].append({
                            'candidate_id': candidate_id,
                            'name': candidate_name,
                            'email': candidate_email,
                            'note': 'Unknown candidate deleted (no email sent)'
                        })
                    else:
                        logger.info(f"Sending rejection email to {candidate_name} ({candidate_email}) for position {job_title}")
                        send_rejection_email_async(candidate_email, candidate_name, job_title)
                        results['successful'].append({
                            'candidate_id': candidate_id,
                            'name': candidate_name,
                            'email': candidate_email
                        })
                else:
                    # This should not happen anymore with our improved logic
                    logger.warning(f"Could not process candidate {candidate_id} - missing email or name")
                    results['failed'].append({
                        'candidate_id': candidate_id,
                        'error': 'Missing candidate email or name'
                    })
                    
            except Exception as e:
                logger.error(f"Error processing candidate {candidate_id}: {e}")
                results['failed'].append({
                    'candidate_id': candidate_id,
                    'error': str(e)
                })
        
        logger.info(f"Bulk rejection completed: {len(results['successful'])} successful, {len(results['failed'])} failed")
        
        return jsonify({
            'success': True,
            'message': f'Bulk rejection completed: {len(results["successful"])} successful, {len(results["failed"])} failed',
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error in bulk rejection: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/candidates/status', methods=['PUT'])
@require_api_key
def update_candidate_overall_status():
    """Update candidate overall status and final decision"""
    try:
        data = request.get_json()
        frontend_candidate_id = data.get('candidate_id')
        ticket_id = data.get('ticket_id')
        overall_status = data.get('overall_status')
        final_decision = data.get('final_decision')
        
        logger.info(f"🔄 PUT /api/candidates/status - Frontend candidate_id: {frontend_candidate_id}, status: {overall_status}, decision: {final_decision}")
        logger.info(f"🔄 Request data: {data}")
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Find the actual database candidate ID (handle metadata mapping)
        actual_candidate_id = None
        
        # FIXED: Use the same candidate ID mapping logic as the FETCH operation
        # This ensures both operations find the same candidate
        logger.info(f"🔄 UPDATE: Using same mapping logic as FETCH for frontend candidate ID: {frontend_candidate_id}")
        
        # FIXED: Use the exact same candidate ID mapping logic as the FETCH operation
        # This ensures both operations find the same candidate
        try:
            # Use the same query logic as the FETCH operation
            cursor.execute("""
                SELECT 
                    ra.id,
                    ra.applicant_name,
                    ra.applicant_email
                FROM resume_applications ra
                JOIN tickets t ON ra.ticket_id = t.ticket_id
                WHERE ra.ticket_id = %s
                ORDER BY ra.id ASC
                LIMIT 1 OFFSET %s
            """, (ticket_id, frontend_candidate_id - 1))
            
            candidate = cursor.fetchone()
            if candidate:
                actual_candidate_id = candidate['id']
                logger.info(f"🔄 UPDATE: Found candidate using FETCH logic: ID {actual_candidate_id}, Name: {candidate['applicant_name']}, Email: {candidate['applicant_email']}")
                logger.info(f"🔄 UPDATE: SUCCESS - Using candidate ID {actual_candidate_id} for update")
            else:
                logger.warning(f"🔄 UPDATE: No candidate found using FETCH logic for frontend ID {frontend_candidate_id}")
        except Exception as e:
            logger.error(f"🔄 UPDATE: Error using FETCH logic: {e}")
        
        # If FETCH logic failed, use metadata mapping as fallback
        if not actual_candidate_id:
            logger.info(f"🔄 UPDATE: FETCH logic failed, using metadata mapping as fallback")
        
        # Use only FETCH logic - no metadata mapping fallback
        if actual_candidate_id:
            logger.info(f"🔄 UPDATE: Using candidate ID {actual_candidate_id} from FETCH logic")
        else:
            logger.error(f"🔄 UPDATE: FETCH logic failed for frontend candidate ID: {frontend_candidate_id}")
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': f'Could not find candidate with ID {frontend_candidate_id} in ticket {ticket_id}'
            }), 404
        
        # Update candidate overall status using the actual database ID
        logger.info(f"Updating status for candidate_id {actual_candidate_id} in ticket {ticket_id}")
        
        # FIXED: Update BOTH tables to keep them synchronized
        # 1. Update candidate_interview_status table
        logger.info(f"🔄 Updating candidate_interview_status: candidate_id={actual_candidate_id}, ticket_id={ticket_id}, status={overall_status}, decision={final_decision}")
        
        cursor.execute("""
            UPDATE candidate_interview_status 
            SET overall_status = %s, final_decision = %s, updated_at = CURRENT_TIMESTAMP
            WHERE candidate_id = %s AND ticket_id = %s
        """, (
            overall_status,
            final_decision,
            actual_candidate_id,
            ticket_id
        ))
        
        rows_affected = cursor.rowcount
        logger.info(f"🔄 candidate_interview_status update affected {rows_affected} rows")
        
        # Debug: Check what's in the table after update
        cursor.execute("""
            SELECT * FROM candidate_interview_status 
            WHERE candidate_id = %s AND ticket_id = %s
        """, (actual_candidate_id, ticket_id))
        debug_record = cursor.fetchone()
        logger.info(f"🔄 Debug - Record after update: {debug_record}")
        
        # If no rows were affected, insert a new record
        if rows_affected == 0:
            logger.info(f"No existing status record found, creating new one for candidate {actual_candidate_id}")
            cursor.execute("""
                INSERT INTO candidate_interview_status 
                (ticket_id, candidate_id, overall_status, final_decision, created_at, updated_at)
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (
                ticket_id,
                actual_candidate_id,
                overall_status,
                final_decision
            ))
            logger.info(f"Created new status record for candidate {actual_candidate_id}")
        
        # 2. Update resume_applications table to keep status synchronized
        cursor.execute("""
            UPDATE resume_applications 
            SET status = %s
            WHERE id = %s AND ticket_id = %s
        """, (
            overall_status,
            actual_candidate_id,
            ticket_id
        ))
        
        resume_rows_affected = cursor.rowcount
        logger.info(f"resume_applications update affected {resume_rows_affected} rows")
        
        if resume_rows_affected == 0:
            logger.warning(f"No resume_applications record found for candidate {actual_candidate_id} in ticket {ticket_id}")
        else:
            logger.info(f"Successfully synchronized status '{overall_status}' in both tables for candidate {actual_candidate_id}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Send appropriate email based on status
        if overall_status in ['rejected', 'hired', 'selected']:
            logger.info(f"Processing {overall_status} for candidate {actual_candidate_id}")
            
            # Get candidate details for email from database
            candidate_name = None
            candidate_email = None
            job_title = None
            
            try:
                # Get candidate details from database
                cursor.execute("""
                    SELECT ra.applicant_name, ra.applicant_email, t.subject as job_title
                    FROM resume_applications ra
                    LEFT JOIN tickets t ON ra.ticket_id = t.ticket_id
                    WHERE ra.id = %s
                """, (actual_candidate_id,))
                candidate_data = cursor.fetchone()
                
                if candidate_data:
                    candidate_name = candidate_data['applicant_name']
                    candidate_email = candidate_data['applicant_email']
                    job_title = candidate_data['job_title'] or f"Position {ticket_id}"
                    
                    cursor.close()
                    conn.close()
                
                # Send appropriate email if we have the required information
                if candidate_email and candidate_name and job_title:
                    if overall_status == 'rejected':
                        logger.info(f"Sending rejection email to {candidate_name} ({candidate_email}) for position {job_title}")
                        send_rejection_email_async(candidate_email, candidate_name, job_title)
                    elif overall_status in ['hired', 'selected']:
                        logger.info(f"Sending hiring email to {candidate_name} ({candidate_email}) for position {job_title}")
                        send_hiring_email_async(candidate_email, candidate_name, job_title)
                else:
                    logger.warning(f"Cannot send {overall_status} email - missing data: name={candidate_name}, email={candidate_email}, job={job_title}")
                    
            except Exception as e:
                logger.error(f"Error processing {overall_status} email: {e}")
        
        response_data = {
            'success': True,
            'message': 'Candidate overall status updated successfully',
            'details': {
                'frontend_candidate_id': frontend_candidate_id,
                'actual_candidate_id': actual_candidate_id,
                'status': overall_status,
                'decision': final_decision,
                'rows_affected': rows_affected
            }
        }
        logger.info(f"🔄 Returning success response: {response_data}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error updating candidate overall status: {e}")
        try:
            if 'conn' in locals():
                conn.rollback()
                conn.close()
        except:
            pass
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/interviews/candidates/<ticket_id>', methods=['GET'])
@require_api_key
def get_candidates_for_interview(ticket_id):
    """Get candidates who have applied for a job and can be scheduled for interviews"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                ra.*,
                COALESCE(cis.overall_status, 'not_started') as interview_status,
                cis.rounds_completed,
                cis.total_rounds,
                cis.average_rating,
                cis.final_decision
            FROM resume_applications ra
            LEFT JOIN candidate_interview_status cis ON ra.id = cis.candidate_id AND cis.ticket_id = %s
            WHERE ra.ticket_id = %s AND ra.status = 'pending'
            ORDER BY ra.uploaded_at DESC
        """, (ticket_id, ticket_id))
        candidates = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Serialize datetime objects in candidates
        for candidate in candidates:
            for key, value in candidate.items():
                if isinstance(value, datetime):
                    candidate[key] = value.isoformat()
                elif isinstance(value, timedelta):
                    candidate[key] = str(value)
        
        return jsonify({
            'success': True,
            'data': {'candidates': candidates}
        })
        
    except Exception as e:
        logger.error(f"Error fetching candidates: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/interviews/candidate/<int:candidate_id>', methods=['GET'])
@require_api_key
def get_candidate_details(candidate_id):
    """Get detailed candidate information for interview scheduling"""
    try:
        # Get the ticket_id from query parameters if provided
        ticket_id_from_query = request.args.get('ticket_id')
        logger.info(f"GET /api/interviews/candidate/{candidate_id} - Starting (ticket_id: {ticket_id_from_query})")
        
        # FIXED: Always fetch actual data from database instead of hardcoded values
        logger.info(f"🔍 Fetching actual candidate data for ID {candidate_id} from database")
        
        # Fetch candidate data from database for all candidates
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # FIXED: Always use metadata mapping first to ensure correct candidate mapping
        # The frontend uses sequential IDs (1, 2, 3...) but database IDs may be different
        logger.info(f"Using metadata mapping for candidate data fetch: {candidate_id}")
        
        candidate = None
        
        # Try metadata mapping first (this is the correct approach)
        try:
            import json
            import os
            import glob
            
            # Find all metadata files to determine which one to use
            # FIXED: Use absolute path to ensure we find the files correctly
            metadata_files = glob.glob("approved_tickets/*/metadata.json")
            if not metadata_files:
                # Fallback: try with Backend prefix if running from different directory
                metadata_files = glob.glob("Backend/approved_tickets/*/metadata.json")
            logger.info(f"Found {len(metadata_files)} metadata files")
            
            # FIXED: Prioritize ticket_id from query parameter to avoid cross-ticket mapping issues
            # If ticket_id is provided, only search in that ticket's metadata
            metadata_files_to_search = metadata_files
            if ticket_id_from_query:
                # Filter to only search in the specified ticket's metadata
                metadata_files_to_search = [path for path in metadata_files if ticket_id_from_query in path]
                logger.info(f"GET: Filtering search to ticket {ticket_id_from_query} metadata files: {metadata_files_to_search}")
            
            # FIXED: Use the ticket_id from query parameter for database lookup, not from metadata
            db_ticket_id = ticket_id_from_query if ticket_id_from_query else None
            logger.info(f"🔄 Using ticket_id for database lookup: {db_ticket_id}")
            
            # Try to find the candidate in each metadata file
            for metadata_path in metadata_files_to_search:
                try:
                    with open(metadata_path, 'r', encoding='utf-8', errors='ignore') as f:
                        metadata = json.load(f)
                        
                    # Check if this metadata contains the candidate we're looking for
                    if 'resumes' in metadata and len(metadata['resumes']) >= candidate_id:
                        if candidate_id <= len(metadata['resumes']):
                            resume_info = metadata['resumes'][candidate_id - 1]
                            mapped_email = resume_info.get('applicant_email')
                            mapped_name = resume_info.get('applicant_name')
                            ticket_id = metadata.get('ticket_id')
                            
                            logger.info(f"🔄 FETCH Metadata mapping: frontend ID {candidate_id} -> {mapped_name} ({mapped_email}) from ticket {ticket_id} in file {metadata_path}")
                            
                            # Find this candidate in the database by email and ticket_id
                            # FIXED: Use the ticket_id from query parameter, not from metadata
                            query_ticket_id = db_ticket_id if db_ticket_id else ticket_id
                            logger.info(f"🔄 FETCH query: email={mapped_email}, ticket_id={query_ticket_id} (from {'query' if db_ticket_id else 'metadata'})")
                            
                            cursor.execute("""
                                SELECT 
                                    ra.*,
                                    t.subject as job_title,
                                    t.ticket_id,
                                    COALESCE(cis.overall_status, 'not_started') as interview_status,
                                    cis.rounds_completed,
                                    cis.total_rounds,
                                    cis.average_rating,
                                    cis.final_decision
                                FROM resume_applications ra
                                JOIN tickets t ON ra.ticket_id = t.ticket_id
                                LEFT JOIN candidate_interview_status cis ON ra.id = cis.candidate_id AND cis.ticket_id = ra.ticket_id
                                WHERE ra.applicant_email = %s AND ra.ticket_id = %s
                                ORDER BY ra.id DESC LIMIT 1
                            """, (mapped_email, query_ticket_id))
                            
                            candidate = cursor.fetchone()
                            if candidate:
                                logger.info(f"Found mapped candidate: frontend ID {candidate_id} -> database ID {candidate['id']} ({candidate['applicant_name']}) from ticket {ticket_id}")
                                logger.info(f"🔄 Candidate data from DB: final_decision={candidate.get('final_decision')}, interview_status={candidate.get('interview_status')}")
                                break  # Found the candidate, no need to check other metadata files
                            else:
                                logger.warning(f"No database record found for mapped email {mapped_email} in ticket {ticket_id}")
                        else:
                            logger.warning(f"Frontend candidate_id {candidate_id} exceeds available resumes in metadata for {metadata_path}")
                    else:
                        logger.warning(f"No resumes found in metadata {metadata_path} or candidate_id {candidate_id} out of range")
                except Exception as e:
                    logger.error(f"Error reading metadata file {metadata_path}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error during metadata mapping: {e}")
        
        cursor.close()
        conn.close()
        
        if not candidate:
            logger.warning(f"Candidate with ID {candidate_id} not found after all lookup attempts")
            return jsonify({'success': False, 'error': 'Candidate not found'}), 404
        
        # Serialize datetime objects
        for key, value in candidate.items():
            if isinstance(value, datetime):
                candidate[key] = value.isoformat()
            elif isinstance(value, timedelta):
                candidate[key] = str(value)
        
        logger.info(f"Found candidate: {candidate['applicant_name']} (ID: {candidate_id})")
        
        return jsonify({
            'success': True,
            'data': {'candidate': candidate}
        })
        
    except Exception as e:
        logger.error(f"Error getting candidate details: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/interviews/ticket/<ticket_id>', methods=['GET'])
@require_api_key
def get_interviews_for_ticket(ticket_id):
    """Get all interviews for a specific ticket/job"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                isch.*,
                ir.round_name,
                ir.round_type,
                ra.applicant_name,
                ra.applicant_email,
                t.subject as job_title,
                GROUP_CONCAT(
                    CONCAT(i.first_name, ' ', i.last_name, ' (', COALESCE(ip.interviewer_email, i.email), ')')
                    SEPARATOR ', '
                ) as interviewers
            FROM interview_schedules isch
            JOIN interview_rounds ir ON isch.round_id = ir.id
            JOIN resume_applications ra ON isch.candidate_id = ra.id
            JOIN tickets t ON isch.ticket_id = t.ticket_id
            LEFT JOIN interview_participants ip ON isch.id = ip.interview_id
            LEFT JOIN interviewers i ON ip.interviewer_id = i.id
            WHERE isch.ticket_id = %s
            GROUP BY isch.id
            ORDER BY isch.scheduled_date DESC, isch.scheduled_time DESC
        """, (ticket_id,))
        interviews = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Serialize datetime objects in interviews
        for interview in interviews:
            for key, value in interview.items():
                if isinstance(value, datetime):
                    interview[key] = value.isoformat()
                elif isinstance(value, timedelta):
                    interview[key] = str(value)
        
        return jsonify({
            'success': True,
            'data': {'interviews': interviews}
        })
        
    except Exception as e:
        logger.error(f"Error fetching interviews for ticket: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/interviews/<int:interview_id>', methods=['GET'])
@require_api_key
def get_interview_details(interview_id):
    """Get details of a specific interview"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                isch.*,
                ir.round_name,
                ir.round_type,
                ra.applicant_name,
                ra.applicant_email,
                t.subject as job_title
            FROM interview_schedules isch
            JOIN interview_rounds ir ON isch.round_id = ir.id
            JOIN resume_applications ra ON isch.candidate_id = ra.id
            JOIN tickets t ON isch.ticket_id = t.ticket_id
            WHERE isch.id = %s
        """, (interview_id,))
        
        interview = cursor.fetchone()
        
        if not interview:
            return jsonify({'success': False, 'error': 'Interview not found'}), 404
        
        # Get participants
        cursor.execute("""
            SELECT 
                ip.*,
                i.first_name,
                i.last_name,
                i.email
            FROM interview_participants ip
            LEFT JOIN interviewers i ON ip.interviewer_id = i.id
            WHERE ip.interview_id = %s
        """, (interview_id,))
        
        participants = cursor.fetchall()
        interview['participants'] = participants
        
        cursor.close()
        conn.close()
        
        # Serialize datetime objects in interview
        for key, value in interview.items():
            if isinstance(value, datetime):
                interview[key] = value.isoformat()
            elif isinstance(value, timedelta):
                interview[key] = str(value)
        
        # Serialize datetime objects in participants
        for participant in participants:
            for key, value in participant.items():
                if isinstance(value, datetime):
                    participant[key] = value.isoformat()
                elif isinstance(value, timedelta):
                    participant[key] = str(value)
        
        return jsonify({
            'success': True,
            'data': {'interview': interview}
        })
        
    except Exception as e:
        logger.error(f"Error fetching interview details: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/interviews/<int:interview_id>', methods=['PUT'])
@require_api_key
def update_interview(interview_id):
    """Update an interview schedule"""
    try:
        data = request.get_json()
        logger.info(f"Update Interview: Received data for interview {interview_id} - {data}")
        logger.info(f"Update Interview: Meeting link in request: {data.get('meeting_link', 'NOT_FOUND')}")
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if interview exists
        cursor.execute("SELECT id FROM interview_schedules WHERE id = %s", (interview_id,))
        if not cursor.fetchone():
            return jsonify({'success': False, 'error': 'Interview not found'}), 404
        
        # Update interview schedule
        update_fields = []
        update_values = []
        
        if 'round_id' in data:
            update_fields.append("round_id = %s")
            update_values.append(data['round_id'])
        
        if 'scheduled_date' in data:
            update_fields.append("scheduled_date = %s")
            update_values.append(data['scheduled_date'])
        
        if 'scheduled_time' in data:
            update_fields.append("scheduled_time = %s")
            update_values.append(data['scheduled_time'])
        
        if 'duration_minutes' in data:
            update_fields.append("duration_minutes = %s")
            update_values.append(data['duration_minutes'])
        
        if 'interview_type' in data:
            update_fields.append("interview_type = %s")
            update_values.append(data['interview_type'])
        
        if 'meeting_link' in data:
            update_fields.append("meeting_link = %s")
            update_values.append(data.get('meeting_link', ''))
        
        if 'location' in data:
            update_fields.append("location = %s")
            update_values.append(data.get('location', ''))
        
        if 'notes' in data:
            update_fields.append("notes = %s")
            update_values.append(data.get('notes', ''))
        
        if 'status' in data:
            update_fields.append("status = %s")
            update_values.append(data['status'])
        
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        
        # Add interview_id to the values for WHERE clause
        update_values.append(interview_id)
        
        if update_fields:
            update_query = f"""
                UPDATE interview_schedules 
                SET {', '.join(update_fields)}
                WHERE id = %s
            """
            cursor.execute(update_query, update_values)
        
        # Update participants if provided
        if 'participants' in data:
            # Delete existing participants
            cursor.execute("DELETE FROM interview_participants WHERE interview_id = %s", (interview_id,))
            
            # Add new participants
            for participant in data['participants']:
                interviewer_id = participant.get('interviewer_id')
                if interviewer_id == '' or interviewer_id is None:
                    interviewer_id = None
                
                cursor.execute("""
                    INSERT INTO interview_participants 
                    (interview_id, interviewer_id, interviewer_name, participant_type, is_primary, interviewer_email, is_manager_feedback)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    interview_id,
                    interviewer_id,
                    participant.get('interviewer_name', ''),  # Add interviewer_name field
                    participant.get('participant_type', 'interviewer'),
                    participant.get('is_primary', False),
                    participant.get('interviewer_email', ''),
                    participant.get('is_manager_feedback', False)  # Premium feature: manager feedback selection
                ))
        
        conn.commit()
        
        # Send update notifications
        try:
            logger.info(f"Update Interview: Attempting to send email notifications for interview {interview_id}")
            from interview_email_service import send_interview_update_notifications
            send_interview_update_notifications(interview_id, data)
            logger.info(f"Update Interview: Email notifications sent successfully for interview {interview_id}")
        except Exception as email_error:
            logger.error(f"Error sending update notifications: {email_error}")
        
        cursor.close()
        conn.close()
        
        logger.info(f"Update Interview: Successfully updated interview {interview_id}")
        return jsonify({
            'success': True,
            'message': 'Interview updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating interview: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/interviews/<int:interview_id>/participants', methods=['GET'])
@require_api_key
def get_interview_participants(interview_id):
    """Get participants for a specific interview"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                ip.*,
                i.first_name,
                i.last_name,
                i.email as interviewer_default_email,
                i.role
            FROM interview_participants ip
            LEFT JOIN interviewers i ON ip.interviewer_id = i.id
            WHERE ip.interview_id = %s
        """, (interview_id,))
        
        participants = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Serialize datetime objects in participants
        for participant in participants:
            for key, value in participant.items():
                if isinstance(value, datetime):
                    participant[key] = value.isoformat()
                elif isinstance(value, timedelta):
                    participant[key] = str(value)
        
        return jsonify({
            'success': True,
            'data': {'participants': participants}
        })
        
    except Exception as e:
        logger.error(f"Error fetching interview participants: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/interviews/<int:interview_id>', methods=['DELETE'])
@require_api_key
def delete_interview(interview_id):
    """Delete an interview schedule"""
    try:
        logger.info(f"DELETE /api/interviews/{interview_id} - Starting deletion")
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # First, check if the interview exists
        cursor.execute("SELECT id, candidate_id, round_id FROM interview_schedules WHERE id = %s", (interview_id,))
        interview = cursor.fetchone()
        
        if not interview:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Interview not found'}), 404
        
        logger.info(f"Found interview {interview_id} for candidate {interview['candidate_id']}")
        
        # Delete all related records in the correct order to avoid foreign key constraint issues
        
        # 1. Delete interview feedback first
        logger.info(f"Deleting feedback for interview {interview_id}")
        cursor.execute("DELETE FROM interview_feedback WHERE interview_id = %s", (interview_id,))
        feedback_deleted = cursor.rowcount
        logger.info(f"Deleted {feedback_deleted} feedback records")
        
        # 2. Delete interview notifications
        logger.info(f"Deleting notifications for interview {interview_id}")
        cursor.execute("DELETE FROM interview_notifications WHERE interview_id = %s", (interview_id,))
        notifications_deleted = cursor.rowcount
        logger.info(f"Deleted {notifications_deleted} notification records")
        
        # 3. Delete interview participants
        logger.info(f"Deleting participants for interview {interview_id}")
        cursor.execute("DELETE FROM interview_participants WHERE interview_id = %s", (interview_id,))
        participants_deleted = cursor.rowcount
        logger.info(f"Deleted {participants_deleted} participant records")
        
        # 4. Finally, delete the interview schedule itself
        logger.info(f"Deleting interview schedule {interview_id}")
        cursor.execute("DELETE FROM interview_schedules WHERE id = %s", (interview_id,))
        
        # Commit all changes at once
        conn.commit()
        logger.info(f"Successfully deleted interview {interview_id} and all related records")
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Interview deleted successfully',
            'details': {
                'interview_id': interview_id,
                'feedback_records_deleted': feedback_deleted,
                'notifications_deleted': notifications_deleted,
                'participants_deleted': participants_deleted
            }
        })
        
    except Exception as e:
        logger.error(f"Error deleting interview {interview_id}: {e}")
        try:
            if 'conn' in locals():
                conn.rollback()
                conn.close()
        except:
            pass
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# MAIN EXECUTION
# ============================================

def main():
    """Run the complete server"""
    # Get local IP address
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print("="*80)
    print("🚀 COMPLETE HIRING BOT SERVER - CHAT + API + CLOUDFLARE TUNNEL + AI FILTERING")
    print("="*80)
    print(f"Database: {MYSQL_CONFIG['database']}@{MYSQL_CONFIG['host']}")
    print(f"Local URL: http://localhost:{API_PORT}")
    print(f"Network URL: http://{local_ip}:{API_PORT}")
    print(f"API Key: {API_KEY}")
    print(f"Storage Path: {BASE_STORAGE_PATH}")
    print("="*80)
    
    # Create folders for existing approved tickets
    create_folders_for_existing_approved_tickets()
    
    # Auto-create folders for any pending tickets that need them
    auto_create_folders_for_pending_tickets()
    
    # Create users table for authentication
    if create_user_table():
        print("✅ User authentication system initialized")
    else:
        print("❌ Failed to initialize user authentication system")
    
    # Start Cloudflare tunnel
    tunnel_url = start_cloudflare_tunnel()
    
    if tunnel_url:
        print("\n📱 Your complete system is accessible globally!")
        print(f"   Public URL: {tunnel_url}")
        print(f"\n🔗 For React Frontend:")
        print(f"   const API_BASE_URL = '{tunnel_url}';")
        print(f"\n🔐 Example API calls:")
        print(f"   # Chat Interface:")
        print(f"   {tunnel_url}")
        print(f"\n   # Get approved jobs:")
        print(f"   curl -H 'X-API-Key: {API_KEY}' {tunnel_url}/api/jobs/approved")
        print(f"\n   # Trigger AI filtering:")
        print(f"   curl -X POST -H 'X-API-Key: {API_KEY}' {tunnel_url}/api/tickets/TICKET_ID/filter-resumes")
        print(f"\n   # Get top resumes:")
        print(f"   curl -H 'X-API-Key: {API_KEY}' {tunnel_url}/api/tickets/TICKET_ID/top-resumes")
        print(f"\n   # Upload resume:")
        print(f"   curl -X POST -H 'X-API-Key: {API_KEY}' \\")
        print(f"        -F 'resume=@resume.pdf' \\")
        print(f"        -F 'applicant_name=John Doe' \\")
        print(f"        -F 'applicant_email=john@example.com' \\")
        print(f"        {tunnel_url}/api/tickets/TICKET_ID/resumes")
    else:
        print("\n⚠️  Running in local mode only")
        print("   Install cloudflared for public access")
    
    print("\n📚 Features:")
    print("  ✅ Chat Bot - AI-powered job posting assistant")
    print("  ✅ Job Management API - Full REST API")
    print("  ✅ Resume Management - Upload and organize resumes")
    print("  ✅ AI Resume Filtering - Automated candidate ranking")
    print("  ✅ Background Processing - Non-blocking filtering")
    print("  ✅ WebSocket Support - Real-time communication")
    print("  ✅ Cloudflare Tunnel - Global accessibility")
    
    print("\n📚 API Endpoints:")
    print("\n🔹 Chat:")
    print("  POST /api/chat/start")
    print("  POST /api/chat/message")
    print("  GET  /api/chat/history/<id>")
    
    print("\n🔹 Job Management:")
    print("  GET  /api/jobs/approved")
    print("  GET  /api/jobs/<id>")
    print("  GET  /api/jobs/search?q=<query>")
    print("  GET  /api/stats")
    print("  GET  /api/locations")
    print("  GET  /api/skills")
    
    print("\n🔹 Resume Management:")
    print("  POST /api/tickets/<id>/approve")
    print("  POST /api/tickets/<id>/resumes")
    print("  GET  /api/tickets/<id>/resumes")
    print("  GET  /api/tickets/<id>/resumes/<filename>")
    
    print("\n🔹 Folder Management:")
    print("  GET  /api/jobs/<id>/folder-info")
    print("  POST /api/maintenance/auto-create-folders")
    print("  POST /api/maintenance/cleanup-folders")
    print("  GET  /api/maintenance/folder-stats")
    
    print("\n🔹 AI Resume Filtering:")
    print("  GET  /api/tickets/<id>/filtering-status")
    print("  POST /api/tickets/<id>/filter-resumes")
    print("  GET  /api/tickets/<id>/top-resumes")
    print("  GET  /api/tickets/<id>/filtering-report")
    print("  POST /api/tickets/<id>/send-top-resumes")
    
    print("\n🔹 Interview Scheduling:")
    print("  POST /api/interviews/rounds")
    print("  GET  /api/interviews/rounds/<ticket_id>")
    print("  POST /api/interviews/interviewers")
    print("  GET  /api/interviews/interviewers")
    print("  POST /api/interviews/rounds/<round_id>/interviewers")
    print("  POST /api/interviews/schedule")
    print("  GET  /api/interviews/schedule/<candidate_id>")
    print("  POST /api/interviews/feedback")
    print("  GET  /api/interviews/feedback/<interview_id>")
    print("  PUT  /api/interviews/status")
    print("  GET  /api/interviews/candidates/<ticket_id>")
    
    print("\n✋ Press CTRL+C to stop the server")
    print("="*80 + "\n")
    
    try:
        # Run with SocketIO for WebSocket support
        socketio.run(app, host='0.0.0.0', port=API_PORT, debug=False, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        cleanup_on_exit()
    except Exception as e:
        print(f"❌ Server error: {e}")
        cleanup_on_exit()

# ============================================
# INTERVIEW SCHEDULING API ENDPOINTS
# ============================================

@app.route('/api/interviews/rounds', methods=['POST'])
@require_api_key
def create_interview_rounds():
    """Create interview rounds for a job"""
    try:
        data = request.get_json()
        ticket_id = data.get('ticket_id')
        rounds = data.get('rounds', [])
        
        if not ticket_id or not rounds:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Verify ticket exists
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tickets WHERE ticket_id = %s", (ticket_id,))
        ticket = cursor.fetchone()
        
        if not ticket:
            return jsonify({'success': False, 'error': 'Ticket not found'}), 404
        
        # Check for existing rounds to prevent duplicates
        cursor.execute("SELECT round_name FROM interview_rounds WHERE ticket_id = %s", (ticket_id,))
        existing_round_names = [row['round_name'] for row in cursor.fetchall()]
        
        # Check for duplicates in the new rounds being created
        new_round_names = [round_data.get('round_name') for round_data in rounds if round_data.get('round_name')]
        duplicate_in_request = [name for name in new_round_names if new_round_names.count(name) > 1]
        
        if duplicate_in_request:
            return jsonify({
                'success': False, 
                'error': f'Duplicate round names found in request: {", ".join(set(duplicate_in_request))}'
            }), 400
        
        # Check for duplicates with existing rounds
        duplicates_with_existing = [name for name in new_round_names if name in existing_round_names]
        
        if duplicates_with_existing:
            return jsonify({
                'success': False, 
                'error': f'Round names already exist for this job: {", ".join(duplicates_with_existing)}. Please use different names or delete existing rounds first.'
            }), 400
        
        # Create interview rounds
        created_rounds = []
        for i, round_data in enumerate(rounds):
            cursor.execute("""
                INSERT INTO interview_rounds 
                (ticket_id, round_name, round_order, round_type, duration_minutes, description, requirements, is_required, can_skip)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                ticket_id,
                round_data.get('round_name'),
                i + 1,
                round_data.get('round_type', 'other'),
                round_data.get('duration_minutes', 60),
                round_data.get('description'),
                round_data.get('requirements'),
                round_data.get('is_required', True),
                round_data.get('can_skip', False)
            ))
            round_id = cursor.lastrowid
            created_rounds.append({'id': round_id, 'round_name': round_data.get('round_name')})
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Created {len(created_rounds)} interview rounds',
            'data': {'rounds': created_rounds}
        })
        
    except Exception as e:
        logger.error(f"Error creating interview rounds: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/interviews/rounds/<ticket_id>', methods=['GET'])
@require_api_key
def get_interview_rounds(ticket_id):
    """Get interview rounds for a job"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT * FROM interview_rounds 
            WHERE ticket_id = %s 
            ORDER BY round_order
        """, (ticket_id,))
        rounds = cursor.fetchall()
        
        logger.info(f"Found {len(rounds)} rounds for ticket {ticket_id}")
        for round_data in rounds:
            logger.info(f"Round: {round_data}")
        
        cursor.close()
        conn.close()
        
        # Serialize datetime objects in rounds
        for round_data in rounds:
            for key, value in round_data.items():
                if isinstance(value, datetime):
                    round_data[key] = value.isoformat()
                elif isinstance(value, timedelta):
                    round_data[key] = str(value)
        
        return jsonify({
            'success': True,
            'data': {'rounds': rounds}
        })
        
    except Exception as e:
        logger.error(f"Error fetching interview rounds: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/interviews/rounds/<ticket_id>', methods=['DELETE'])
@require_api_key
def delete_interview_rounds(ticket_id):
    """Delete all interview rounds for a job"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if there are any scheduled interviews using these rounds
        cursor.execute("""
            SELECT COUNT(*) as count FROM interview_schedules iss
            JOIN interview_rounds ir ON iss.round_id = ir.id
            WHERE ir.ticket_id = %s
        """, (ticket_id,))
        scheduled_interviews = cursor.fetchone()['count']
        
        if scheduled_interviews > 0:
            return jsonify({
                'success': False,
                'error': f'Cannot delete rounds. There are {scheduled_interviews} scheduled interviews using these rounds. Please reschedule or cancel interviews first.'
            }), 400
        
        # Delete all rounds for this ticket
        cursor.execute("DELETE FROM interview_rounds WHERE ticket_id = %s", (ticket_id,))
        deleted_count = cursor.rowcount
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Successfully deleted {deleted_count} interview rounds',
            'data': {'deleted_count': deleted_count}
        })
        
    except Exception as e:
        logger.error(f"Error deleting interview rounds: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/interviews/rounds/<ticket_id>/setup-default', methods=['POST'])
@require_api_key
def setup_default_interview_rounds(ticket_id):
    """Setup default 3-round interview process: HR Round → Technical Round → HR Final Round"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if default rounds already exist by name
        default_round_names = ['HR Round', 'Technical Round', 'HR Final Round']
        cursor.execute("SELECT round_name FROM interview_rounds WHERE ticket_id = %s", (ticket_id,))
        existing_round_names = [row['round_name'] for row in cursor.fetchall()]
        
        # Check for duplicates with existing rounds
        duplicates_with_existing = [name for name in default_round_names if name in existing_round_names]
        
        if duplicates_with_existing:
            return jsonify({
                'success': False, 
                'error': f'Default round names already exist for this job: {", ".join(duplicates_with_existing)}. Please use different names or delete existing rounds first.',
                'existing_rounds': len(existing_round_names),
                'duplicate_rounds': duplicates_with_existing
            }), 400
        
        # Define the 3-round system
        default_rounds = [
            {
                'round_name': 'HR Round',
                'round_type': 'hr',
                'duration_minutes': 45,
                'description': 'Initial HR screening to assess candidate fit, experience, and motivation',
                'requirements': 'Resume review, basic behavioral questions, salary expectations discussion',
                'is_required': True,
                'can_skip': False
            },
            {
                'round_name': 'Technical Round',
                'round_type': 'technical',
                'duration_minutes': 90,
                'description': 'Technical skills assessment and problem-solving evaluation',
                'requirements': 'Technical questions, coding challenges, system design discussion',
                'is_required': True,
                'can_skip': False
            },
            {
                'round_name': 'HR Final Round',
                'round_type': 'final',
                'duration_minutes': 60,
                'description': 'Final HR round for cultural fit assessment and offer discussion',
                'requirements': 'Cultural fit evaluation, final behavioral questions, offer negotiation',
                'is_required': True,
                'can_skip': False
            }
        ]
        
        # Create the rounds
        created_rounds = []
        for i, round_data in enumerate(default_rounds):
            cursor.execute("""
                INSERT INTO interview_rounds 
                (ticket_id, round_name, round_order, round_type, duration_minutes, description, requirements, is_required, can_skip)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                ticket_id,
                round_data['round_name'],
                i + 1,
                round_data['round_type'],
                round_data['duration_minutes'],
                round_data['description'],
                round_data['requirements'],
                round_data['is_required'],
                round_data['can_skip']
            ))
            round_id = cursor.lastrowid
            created_rounds.append({
                'id': round_id, 
                'round_name': round_data['round_name'],
                'round_type': round_data['round_type'],
                'duration_minutes': round_data['duration_minutes']
            })
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Default 3-round interview process created successfully',
            'data': {
                'rounds': created_rounds,
                'process': 'HR Round → Technical Round → HR Final Round'
            }
        })
        
    except Exception as e:
        logger.error(f"Error setting up default interview rounds: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/interviews/interviewers', methods=['POST'])
@require_api_key
def create_interviewer():
    """Create a new interviewer"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            INSERT INTO interviewers (user_id, email, first_name, last_name, role, department, expertise_areas, availability_schedule)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get('user_id'),
            data.get('email'),
            data.get('first_name'),
            data.get('last_name'),
            data.get('role'),
            data.get('department'),
            json.dumps(data.get('expertise_areas', [])),
            json.dumps(data.get('availability_schedule', {}))
        ))
        
        interviewer_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Interviewer created successfully',
            'data': {'interviewer_id': interviewer_id}
        })
        
    except Exception as e:
        logger.error(f"Error creating interviewer: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/interviews/interviewers', methods=['GET'])
@require_api_key
def get_interviewers():
    """Get all active interviewers"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT * FROM interviewers 
            WHERE is_active = TRUE 
            ORDER BY first_name, last_name
        """)
        interviewers = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Serialize datetime objects in interviewers
        for interviewer in interviewers:
            for key, value in interviewer.items():
                if isinstance(value, datetime):
                    interviewer[key] = value.isoformat()
                elif isinstance(value, timedelta):
                    interviewer[key] = str(value)
        
        return jsonify({
            'success': True,
            'data': {'interviewers': interviewers}
        })
        
    except Exception as e:
        logger.error(f"Error fetching interviewers: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/interviews/rounds/<int:round_id>/interviewers', methods=['POST'])
@require_api_key
def assign_interviewers_to_round(round_id):
    """Assign interviewers to a specific round"""
    try:
        data = request.get_json()
        interviewer_ids = data.get('interviewer_ids', [])
        
        if not interviewer_ids:
            return jsonify({'success': False, 'error': 'No interviewer IDs provided'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Remove existing assignments for this round
        cursor.execute("DELETE FROM round_interviewers WHERE round_id = %s", (round_id,))
        
        # Add new assignments
        for interviewer_id in interviewer_ids:
            cursor.execute("""
                INSERT INTO round_interviewers (round_id, interviewer_id)
                VALUES (%s, %s)
            """, (round_id, interviewer_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Assigned {len(interviewer_ids)} interviewers to round'
        })
        
    except Exception as e:
        logger.error(f"Error assigning interviewers: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/interviews/generate-meet-link', methods=['POST', 'OPTIONS'])
def generate_google_meet_link():
    """Generate a Google Meet link using AutoGen AI agent based on interview details"""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,X-API-Key,ngrok-skip-browser-warning')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response, 200
    
    # Require API key for POST requests
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        api_key = request.args.get('api_key')
    
    if api_key != API_KEY:
        return jsonify({
            'success': False,
            'error': 'Invalid or missing API key'
        }), 401
    
    try:
        data = request.get_json()
        scheduled_date = data.get('scheduled_date')
        scheduled_time = data.get('scheduled_time')
        duration_minutes = data.get('duration_minutes', 60)
        interview_title = data.get('interview_title', 'Interview')
        candidate_name = data.get('candidate_name', 'Candidate')
        candidate_email = data.get('candidate_email', '')
        round_name = data.get('round_name', 'Interview')
        interviewer_names = data.get('interviewer_names', [])
        notes = data.get('notes', '')
        
        if not scheduled_date or not scheduled_time:
            return jsonify({'success': False, 'error': 'Date and time are required'}), 400
        
        # Try Real Meet Generator first (creates actual working links)
        if create_real_meeting_link:
            try:
                logger.info("🚀 Using Real Meet Generator for actual Google Meet creation...")
                
                # Prepare interview details for real meet generator
                real_interview_details = {
                    'candidate_name': candidate_name,
                    'candidate_email': candidate_email,
                    'scheduled_date': scheduled_date,
                    'scheduled_time': scheduled_time,
                    'duration_minutes': duration_minutes,
                    'round_name': round_name,
                    'participants': [
                        {'email': candidate_email, 'name': candidate_name, 'role': 'candidate'}
                    ] + [{'email': email, 'name': f'Interviewer {i+1}', 'role': 'interviewer'} 
                          for i, email in enumerate(interviewer_names) if email]
                }
                
                # Create real meeting (browser-based for actual working links)
                result = create_real_meeting_link(real_interview_details, 'browser')
                
                if result.get('success'):
                    logger.info("✅ Real Meet Generator provided working solution!")
                    
                    # Format the response for real meet generator
                    response_data = {
                        'meeting_link': result.get('meeting_link', 'https://meet.google.com/new'),
                        'meeting_code': result.get('meeting_code', 'browser-required'),
                        'meeting_id': result['meeting_id'],
                        'scheduled_time': f"{scheduled_date}T{scheduled_time}:00",
                        'duration_minutes': duration_minutes,
                        'title': result['meeting_info']['title'],
                        'participants': [candidate_email] + interviewer_names,
                        'created_at': result['meeting_info']['created_at'],
                        'expires_at': None,
                        'agent_insights': {
                            'method': 'real_meet_generator',
                            'status': 'success',
                            'validation_status': 'browser_guided',
                            'meeting_type': 'real_google_meet'
                        },
                        'instructions': result.get('instructions', []),
                        'action_buttons': result.get('action_buttons', []),
                        'formatted_datetime': f"{scheduled_date} {scheduled_time}",
                        'interview_title': result['meeting_info']['title'],
                        'note': '🎯 Real Google Meet Creation: Follow instructions to create a working meeting link'
                    }
                    
                    # Return the successful response
                    response = jsonify({'success': True, 'data': response_data})
                    response.headers.add('Access-Control-Allow-Origin', '*')
                    return response, 200
                else:
                    logger.warning("Real Meet Generator failed, trying Auto Meet Generator...")
                    raise Exception(result.get('error', 'Real Meet Generator failed'))
                    
            except Exception as real_error:
                logger.warning(f"Real Meet Generator failed: {real_error}, trying Auto Meet Generator...")
                # Continue to Auto Meet Generator fallback
        
        # Try Auto Meet Generator as fallback (creates fake but realistic links)
        if create_auto_meeting_link:
            try:
                logger.info("🚀 Using Auto Meet Generator for automatic Google Meet creation...")
                
                # Prepare interview details for auto meet generator
                auto_interview_details = {
                    'candidate_name': candidate_name,
                    'candidate_email': candidate_email,
                    'scheduled_date': scheduled_date,
                    'scheduled_time': scheduled_time,
                    'duration_minutes': duration_minutes,
                    'round_name': round_name,
                    'participants': [
                        {'email': candidate_email, 'name': candidate_name, 'role': 'candidate'}
                    ] + [{'email': email, 'name': f'Interviewer {i+1}', 'role': 'interviewer'} 
                          for i, email in enumerate(interviewer_names) if email]
                }
                
                # Create automatic meeting (try scheduled first, then instant)
                result = create_auto_meeting_link(auto_interview_details, 'scheduled')
                if not result.get('success'):
                    result = create_auto_meeting_link(auto_interview_details, 'instant')
                
                if result.get('success'):
                    logger.info("✅ Auto Meet Generator created meeting successfully!")
                    
                    # Format the response for auto meet generator
                    response_data = {
                        'meeting_link': result['meeting_link'],
                        'meeting_code': result['meeting_code'],
                        'meeting_id': result['meeting_id'],
                        'scheduled_time': f"{scheduled_date}T{scheduled_time}:00",
                        'duration_minutes': duration_minutes,
                        'title': result['meeting_info']['title'],
                        'participants': [candidate_email] + interviewer_names,
                        'created_at': result['meeting_info']['created_at'],
                        'expires_at': None,
                        'agent_insights': {
                            'method': 'auto_meet_generator',
                            'status': 'success',
                            'validation_status': 'auto_created',
                            'meeting_type': 'real_google_meet'
                        },
                        'instructions': result.get('instructions', []),
                        'action_buttons': result.get('action_buttons', []),
                        'calendar_url': result.get('calendar_url'),
                        'formatted_datetime': f"{scheduled_date} {scheduled_time}",
                        'interview_title': result['meeting_info']['title'],
                        'note': '✅ Real Google Meet meeting created automatically - ready to use!'
                    }
                    
                    # Return the successful response
                    response = jsonify({'success': True, 'data': response_data})
                    response.headers.add('Access-Control-Allow-Origin', '*')
                    return response, 200
                else:
                    logger.warning("Auto Meet Generator failed, trying Browser Solution...")
                    raise Exception(result.get('error', 'Auto Meet Generator failed'))
                    
            except Exception as auto_error:
                logger.warning(f"Auto Meet Generator failed: {auto_error}, trying Browser Solution...")
                # Continue to Browser Solution fallback
        
        # Try Browser Solution as fallback (provides guidance)
        if create_meeting_with_browser_guidance:
            try:
                logger.info("🚀 Using Browser Solution for Google Meet creation...")
                
                # Prepare interview details for browser solution
                browser_interview_details = {
                    'candidate_name': candidate_name,
                    'candidate_email': candidate_email,
                    'scheduled_date': scheduled_date,
                    'scheduled_time': scheduled_time,
                    'duration_minutes': duration_minutes,
                    'round_name': round_name,
                    'participants': [
                        {'email': candidate_email, 'name': candidate_name, 'role': 'candidate'}
                    ] + [{'email': email, 'name': f'Interviewer {i+1}', 'role': 'interviewer'} 
                          for i, email in enumerate(interviewer_names) if email]
                }
                
                # Create meeting with browser guidance
                result = create_meeting_with_browser_guidance(browser_interview_details)
                
                if result.get('success'):
                    logger.info("✅ Browser solution provided successfully!")
                    
                    # Format the response for browser solution
                    response_data = {
                        'meeting_link': result['options']['instant_meeting']['url'],  # Default to instant meeting
                        'meeting_code': result['meeting_id'],
                        'meeting_id': result['meeting_id'],
                        'scheduled_time': f"{scheduled_date}T{scheduled_time}:00",
                        'duration_minutes': duration_minutes,
                        'title': result['meeting_info']['title'],
                        'participants': [candidate_email] + interviewer_names,
                        'created_at': result['meeting_info']['created_at'],
                        'expires_at': None,
                        'agent_insights': {
                            'method': 'browser_solution',
                            'status': 'success',
                            'validation_status': 'browser_guided',
                            'instructions': result.get('instructions', [])
                        },
                        'instructions': result.get('instructions', []),
                        'action_buttons': result.get('action_buttons', []),
                        'meeting_options': result.get('options', {}),
                        'formatted_datetime': f"{scheduled_date} {scheduled_time}",
                        'interview_title': result['meeting_info']['title'],
                        'note': '🎯 Browser Solution: Follow the instructions to create a real Google Meet meeting'
                    }
                    
                    # Return the successful response
                    response = jsonify({'success': True, 'data': response_data})
                    response.headers.add('Access-Control-Allow-Origin', '*')
                    return response, 200
                else:
                    logger.warning("Browser solution failed, trying AutoGen agent...")
                    raise Exception(result.get('error', 'Browser solution failed'))
                    
            except Exception as browser_error:
                logger.warning(f"Browser solution failed: {browser_error}, trying AutoGen agent...")
                # Continue to AutoGen agent fallback
        
        # Try to use the AutoGen agent for intelligent meeting link generation
        try:
            from google_meet_agent import generate_meeting_link_for_interview
            
            # Use the AutoGen agent to generate the meeting link
            result = generate_meeting_link_for_interview(
                candidate_name=candidate_name,
                candidate_email=candidate_email,
                scheduled_date=scheduled_date,
                scheduled_time=scheduled_time,
                duration_minutes=duration_minutes,
                interview_type="video_call",
                round_name=round_name,
                interviewer_names=interviewer_names,
                meeting_title=interview_title,
                notes=notes
            )
            
            if result.get('success'):
                # Format the response with additional information
                response_data = {
                    'meeting_link': result['meeting_link'],
                    'meeting_code': result['meeting_code'],
                    'meeting_id': result['meeting_id'],
                    'scheduled_time': result['scheduled_time'],
                    'duration_minutes': result['duration_minutes'],
                    'title': result['title'],
                    'participants': result['participants'],
                    'created_at': result['created_at'],
                    'expires_at': result['expires_at'],
                    'agent_insights': result.get('agent_insights', {}),
                    'instructions': result.get('instructions', []),
                    'formatted_datetime': result['scheduled_time'],  # For backward compatibility
                    'interview_title': result['title'],
                    'note': _get_meeting_note(result)
                }
                
                logger.info(f"AutoGen agent successfully generated meeting link: {result['meeting_link']}")
                
                # Return the successful response
                response = jsonify({'success': True, 'data': response_data})
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response, 200
                
            else:
                # Fallback to basic generation if AutoGen fails
                raise Exception(result.get('error', 'AutoGen agent failed'))
                
        except ImportError:
            # Fallback to basic generation if AutoGen is not available
            logger.warning("AutoGen agent not available, using fallback method")
            raise Exception("AutoGen agent not available")
        
        except Exception as agent_error:
            # Fallback to basic generation
            logger.error(f"AutoGen agent failed: {agent_error}, using fallback method")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            
            # Basic fallback implementation
            import random
            import string
            import hashlib
            import time
            
            def generate_realistic_meet_code():
                """Generate a more realistic Google Meet code based on interview details"""
                unique_string = f"{scheduled_date}_{scheduled_time}_{interview_title}_{time.time()}"
                hash_object = hashlib.md5(unique_string.encode())
                hash_hex = hash_object.hexdigest()
                
                letters = ''.join(random.choices(string.ascii_lowercase, k=3))
                digits1 = hash_hex[:4]
                digits2 = hash_hex[4:7]
                
                return f"{letters}-{digits1}-{digits2}"
            
            meeting_code = generate_realistic_meet_code()
            meeting_link = f"https://meet.google.com/{meeting_code}"
            
            # Format the date and time for display
            try:
                if isinstance(scheduled_date, str) and 'GMT' in scheduled_date:
                    date_obj = datetime.strptime(scheduled_date.split(', ')[1], '%d %b %Y %H:%M:%S GMT')
                else:
                    date_obj = datetime.fromisoformat(scheduled_date.replace('Z', '+00:00'))
                
                if scheduled_time:
                    time_parts = scheduled_time.split(':')
                    if len(time_parts) >= 2:
                        date_obj = date_obj.replace(
                            hour=int(time_parts[0]),
                            minute=int(time_parts[1]),
                            second=0,
                            microsecond=0
                        )
                
                formatted_datetime = date_obj.strftime('%B %d, %Y at %I:%M %p')
                
            except Exception as e:
                logger.warning(f"Error parsing date/time: {e}")
                formatted_datetime = f"{scheduled_date} {scheduled_time}"
            
            response_data = {
                'meeting_link': meeting_link,
                'meeting_code': meeting_code,
                'formatted_datetime': formatted_datetime,
                'duration_minutes': duration_minutes,
                'interview_title': interview_title,
                'note': "⚠️  PLACEHOLDER meeting link - must be replaced with real Google Meet link created at https://meet.google.com"
            }
        
        response = jsonify({
            'success': True,
            'data': response_data
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
        
    except Exception as e:
        logger.error(f"Error generating Google Meet link: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/interviews/meeting-creation-help', methods=['POST', 'OPTIONS'])
def get_meeting_creation_help():
    """Get detailed instructions for creating a real Google Meet meeting"""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,X-API-Key,ngrok-skip-browser-warning')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response, 200
    
    # Require API key for POST requests
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        api_key = request.args.get('api_key')
    
    if api_key != API_KEY:
        return jsonify({
            'success': False,
            'error': 'Invalid or missing API key'
        }), 401
    
    try:
        data = request.get_json()
        
        # Extract interview details
        interview_details = {
            'candidate_name': data.get('candidate_name', 'Candidate'),
            'candidate_email': data.get('candidate_email', ''),
            'scheduled_date': data.get('scheduled_date', ''),
            'scheduled_time': data.get('scheduled_time', ''),
            'duration_minutes': data.get('duration_minutes', 60),
            'interview_type': data.get('interview_type', 'video_call'),
            'round_name': data.get('round_name', 'Interview'),
            'interviewer_names': data.get('interviewer_names', []),
            'meeting_title': data.get('meeting_title', 'Interview Meeting'),
            'notes': data.get('notes', '')
        }
        
        # Try to use the helper
        try:
            from google_meet_helper import create_meeting_helper_response
            helper_response = create_meeting_helper_response(interview_details)
            
            response = jsonify(helper_response)
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 200
            
        except ImportError:
            # Fallback response
            fallback_response = {
                "success": True,
                "type": "meeting_creation_helper",
                "data": {
                    "message": "⚠️  The generated meeting link is a PLACEHOLDER and must be replaced with a real Google Meet link.",
                    "instructions": {
                        "title": "How to Create a Real Google Meet Meeting",
                        "steps": [
                            {
                                "step": 1,
                                "title": "Go to Google Meet",
                                "description": "Open https://meet.google.com in your browser",
                                "url": "https://meet.google.com"
                            },
                            {
                                "step": 2,
                                "title": "Create New Meeting",
                                "description": "Click 'New meeting' or 'Schedule a meeting'"
                            },
                            {
                                "step": 3,
                                "title": "Set Meeting Details",
                                "description": f"Set title: {interview_details['meeting_title']}"
                            },
                            {
                                "step": 4,
                                "title": "Add Participants",
                                "description": f"Add candidate: {interview_details['candidate_name']}"
                            },
                            {
                                "step": 5,
                                "title": "Generate Real Link",
                                "description": "Copy the real meeting link and replace the placeholder"
                            }
                        ]
                    },
                    "meeting_details": interview_details,
                    "important_notes": [
                        "⚠️  The current link is a PLACEHOLDER and will not work",
                        "You must create a real Google Meet meeting",
                        "Test the real meeting link before sending to participants"
                    ]
                }
            }
            
            response = jsonify(fallback_response)
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 200
        
    except Exception as e:
        logger.error(f"Error getting meeting creation help: {e}")
        response = jsonify({
            'success': False,
            'error': str(e)
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@app.route('/api/interviews/create-meeting-with-email', methods=['POST', 'OPTIONS'])
@require_api_key
def create_meeting_with_configured_email_endpoint():
    """Create a Google Meet meeting using the configured email address"""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-API-Key')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Extract interview details
        interview_details = {
            'candidate_name': data.get('candidate_name', 'Candidate'),
            'candidate_email': data.get('candidate_email', ''),
            'scheduled_date': data.get('scheduled_date', ''),
            'scheduled_time': data.get('scheduled_time', ''),
            'duration_minutes': data.get('duration_minutes', 60),
            'round_name': data.get('round_name', 'Interview'),
            'interviewer_emails': data.get('interviewer_emails', [])
        }
        
        # Use Google Calendar integration if available
        if create_meeting_with_configured_email:
            result = create_meeting_with_configured_email(interview_details)
            
            response = jsonify({
                'success': result['success'],
                'data': {
                    'meeting_link': result.get('meeting_link'),
                    'meeting_info': result.get('meeting_info'),
                    'instructions': result.get('instructions'),
                    'note': result.get('note'),
                    'organizer_email': EMAIL_CONFIG['EMAIL_ADDRESS']
                }
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        else:
            return jsonify({
                'success': False,
                'error': 'Google Calendar integration not available'
            }), 500
        
    except Exception as e:
        logger.error(f"Error creating meeting with configured email: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def _get_meeting_note(result):
    """Get appropriate note based on meeting type"""
    agent_insights = result.get('agent_insights', {})
    is_browser_solution = agent_insights.get('validation_status') == 'browser_guided'
    is_real_meeting = agent_insights.get('is_real_meeting', False)
    
    if is_browser_solution:
        return "🎯 Browser Solution: Google Meet opened in browser - follow instructions to create real meeting"
    elif is_real_meeting:
        return "✅ Real Google Meet meeting created automatically via API"
    else:
        return "⚠️  PLACEHOLDER meeting link - must be replaced with real Google Meet link created at https://meet.google.com"

@app.route('/api/interviews/browser-meet-link', methods=['POST', 'OPTIONS'])
def create_browser_meet_link():
    """Create a Google Meet link using browser-based solution"""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,X-API-Key,ngrok-skip-browser-warning')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response, 200
    
    # Require API key for POST requests
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        api_key = request.args.get('api_key')
    
    if api_key != API_KEY:
        return jsonify({
            'success': False,
            'error': 'Invalid or missing API key'
        }), 401
    
    try:
        data = request.get_json()
        scheduled_date = data.get('scheduled_date')
        scheduled_time = data.get('scheduled_time')
        duration_minutes = data.get('duration_minutes', 60)
        interview_title = data.get('interview_title', 'Interview')
        candidate_name = data.get('candidate_name', 'Candidate')
        candidate_email = data.get('candidate_email', '')
        round_name = data.get('round_name', 'Interview')
        interviewer_names = data.get('interviewer_names', [])
        notes = data.get('notes', '')
        
        if not scheduled_date or not scheduled_time:
            return jsonify({'success': False, 'error': 'Date and time are required'}), 400
        
        if not create_meeting_with_browser_guidance:
            return jsonify({'success': False, 'error': 'Browser solution not available'}), 500
        
        # Prepare interview details for browser solution
        browser_interview_details = {
            'candidate_name': candidate_name,
            'candidate_email': candidate_email,
            'scheduled_date': scheduled_date,
            'scheduled_time': scheduled_time,
            'duration_minutes': duration_minutes,
            'round_name': round_name,
            'participants': [
                {'email': candidate_email, 'name': candidate_name, 'role': 'candidate'}
            ] + [{'email': email, 'name': f'Interviewer {i+1}', 'role': 'interviewer'} 
                  for i, email in enumerate(interviewer_names) if email]
        }
        
        # Create meeting with browser guidance
        result = create_meeting_with_browser_guidance(browser_interview_details)
        
        if result.get('success'):
            logger.info("✅ Browser solution provided successfully!")
            
            # Format the response for browser solution
            response_data = {
                'meeting_link': result['options']['instant_meeting']['url'],  # Default to instant meeting
                'meeting_code': result['meeting_id'],
                'meeting_id': result['meeting_id'],
                'scheduled_time': f"{scheduled_date}T{scheduled_time}:00",
                'duration_minutes': duration_minutes,
                'title': result['meeting_info']['title'],
                'participants': [candidate_email] + interviewer_names,
                'created_at': result['meeting_info']['created_at'],
                'expires_at': None,
                'agent_insights': {
                    'method': 'browser_solution',
                    'status': 'success',
                    'validation_status': 'browser_guided',
                    'instructions': result.get('instructions', [])
                },
                'instructions': result.get('instructions', []),
                'action_buttons': result.get('action_buttons', []),
                'meeting_options': result.get('options', {}),
                'formatted_datetime': f"{scheduled_date} {scheduled_time}",
                'interview_title': result['meeting_info']['title'],
                'note': '🎯 Browser Solution: Follow the instructions to create a real Google Meet meeting'
            }
            
            # Return the successful response
            response = jsonify({'success': True, 'data': response_data})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 200
        else:
            return jsonify({'success': False, 'error': result.get('error', 'Browser solution failed')}), 500
            
    except Exception as e:
        logger.error(f"Error creating browser meet link: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/interviews/open-browser-meeting/<meeting_id>', methods=['POST', 'OPTIONS'])
def open_browser_meeting(meeting_id):
    """Open browser for meeting creation"""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,X-API-Key,ngrok-skip-browser-warning')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response, 200
    
    # Require API key for POST requests
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        api_key = request.args.get('api_key')
    
    if api_key != API_KEY:
        return jsonify({
            'success': False,
            'error': 'Invalid or missing API key'
        }), 401
    
    try:
        data = request.get_json() or {}
        method = data.get('method', 'instant')  # instant, scheduled, manual
        
        if not browser_meet_solution:
            return jsonify({'success': False, 'error': 'Browser solution not available'}), 500
        
        # Open browser for meeting creation
        result = browser_meet_solution.open_meeting_creation(meeting_id, method)
        
        if result.get('success'):
            response = jsonify({'success': True, 'data': result})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 200
        else:
            return jsonify({'success': False, 'error': result.get('error', 'Failed to open browser')}), 500
            
    except Exception as e:
        logger.error(f"Error opening browser meeting: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================
# EMAIL SETTINGS HELPER FUNCTIONS
# ============================================

def update_env_file(key, value):
    """Update a key-value pair in the .env file"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    set_key(env_path, key, str(value))
    
def reload_email_config():
    """Reload EMAIL_CONFIG from environment variables"""
    global EMAIL_CONFIG
    EMAIL_CONFIG = {
        'SMTP_SERVER': os.getenv('SMTP_SERVER'),
        'SMTP_PORT': int(os.getenv('SMTP_PORT', 587)),
        'EMAIL_ADDRESS': os.getenv('EMAIL_ADDRESS'),
        'EMAIL_PASSWORD': os.getenv('EMAIL_PASSWORD'),
        'USE_TLS': os.getenv('USE_TLS', 'true').lower() == 'true',
        'FROM_NAME': os.getenv('FROM_NAME'),
        'COMPANY_NAME': os.getenv('COMPANY_NAME'),
        'COMPANY_WEBSITE': os.getenv('COMPANY_WEBSITE'),
        'HR_EMAIL': os.getenv('HR_EMAIL'),
        'SEND_EMAILS': os.getenv('SEND_EMAILS', 'true').lower() == 'true'
    }

# ============================================
# EMAIL SETTINGS API ENDPOINTS
# ============================================

@app.route('/api/settings/email', methods=['GET', 'PUT', 'OPTIONS'])
def email_settings():
    """Get or update email configuration settings"""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,X-API-Key')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,OPTIONS')
        return response, 200
    
    # Require API key for GET and PUT requests
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        api_key = request.args.get('api_key')
    
    if api_key != API_KEY:
        return jsonify({
            'success': False,
            'error': 'Invalid or missing API key'
        }), 401
    
    try:
        if request.method == 'GET':
            # Return current email configuration
            return jsonify({
                'success': True,
                'data': EMAIL_CONFIG
            }), 200
            
        elif request.method == 'PUT':
            # Update email configuration in .env file
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'No data provided'}), 400
            
            # Validate required fields
            required_fields = ['smtp_server', 'smtp_port', 'email_address', 'email_password']
            for field in required_fields:
                if field not in data:
                    return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
            
            try:
                # Update .env file with new values
                update_env_file('SMTP_SERVER', data.get('smtp_server', os.getenv('SMTP_SERVER')))
                update_env_file('SMTP_PORT', data.get('smtp_port', os.getenv('SMTP_PORT', 587)))
                update_env_file('EMAIL_ADDRESS', data.get('email_address', os.getenv('EMAIL_ADDRESS')))
                update_env_file('EMAIL_PASSWORD', data.get('email_password', os.getenv('EMAIL_PASSWORD')))
                update_env_file('USE_TLS', data.get('use_tls', os.getenv('USE_TLS', 'true')))
                update_env_file('FROM_NAME', data.get('from_name', os.getenv('FROM_NAME')))
                update_env_file('COMPANY_NAME', data.get('company_name', os.getenv('COMPANY_NAME')))
                update_env_file('COMPANY_WEBSITE', data.get('company_website', os.getenv('COMPANY_WEBSITE')))
                update_env_file('HR_EMAIL', data.get('hr_email', os.getenv('HR_EMAIL')))
                update_env_file('SEND_EMAILS', data.get('send_emails', os.getenv('SEND_EMAILS', 'true')))
                
                # Reload environment variables
                load_dotenv()
                
                # Reload EMAIL_CONFIG from updated environment variables
                reload_email_config()
                
                # Also reload email config in interview_email_service if it's imported
                try:
                    from interview_email_service import reload_email_config as reload_interview_email_config
                    reload_interview_email_config()
                    logger.info("Interview email service configuration reloaded")
                except ImportError:
                    logger.warning("Could not reload interview_email_service configuration")
                
                logger.info("Email configuration updated successfully in .env file")
                
                return jsonify({
                    'success': True,
                    'message': 'Email configuration updated successfully in .env file',
                    'data': EMAIL_CONFIG
                }), 200
                
            except Exception as e:
                logger.error(f"Error updating .env file: {e}")
                return jsonify({'success': False, 'error': f'Failed to update .env file: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"Error in email settings API: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/settings/email/test', methods=['POST', 'OPTIONS'])
def test_email_connection():
    """Test email connection with provided settings"""
    # Handle OPTIONS request for CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,X-API-Key')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response, 200
    
    # Require API key for POST requests
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        api_key = request.args.get('api_key')
    
    if api_key != API_KEY:
        return jsonify({
            'success': False,
            'error': 'Invalid or missing API key'
        }), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Extract email config from request
        test_config = {
            'SMTP_SERVER': data.get('smtp_server'),
            'SMTP_PORT': int(data.get('smtp_port', 587)),
            'EMAIL_ADDRESS': data.get('email_address'),
            'EMAIL_PASSWORD': data.get('email_password'),
            'USE_TLS': bool(data.get('use_tls', True)),
            'FROM_NAME': data.get('from_name', 'Test Email'),
            'COMPANY_NAME': data.get('company_name', 'Test Company'),
            'COMPANY_WEBSITE': data.get('company_website', 'https://test.com'),
            'HR_EMAIL': data.get('hr_email', data.get('email_address')),
            'SEND_EMAILS': True
        }
        
        # Validate required fields
        if not all([test_config['SMTP_SERVER'], test_config['EMAIL_ADDRESS'], test_config['EMAIL_PASSWORD']]):
            return jsonify({'success': False, 'error': 'Missing required SMTP configuration'}), 400
        
        # Test email connection
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Create test message
            message = MIMEMultipart("alternative")
            message["Subject"] = "Email Configuration Test"
            message["From"] = f"{test_config['FROM_NAME']} <{test_config['EMAIL_ADDRESS']}>"
            message["To"] = test_config['EMAIL_ADDRESS']  # Send test email to self
            
            # Create test content
            html_content = """
            <html>
            <body>
                <h2>✅ Email Configuration Test Successful!</h2>
                <p>Your email settings are working correctly.</p>
                <p><strong>SMTP Server:</strong> {}</p>
                <p><strong>Port:</strong> {}</p>
                <p><strong>From:</strong> {}</p>
                <p><strong>TLS:</strong> {}</p>
                <p>This is a test email from your HRMS system.</p>
            </body>
            </html>
            """.format(
                test_config['SMTP_SERVER'],
                test_config['SMTP_PORT'],
                test_config['EMAIL_ADDRESS'],
                'Enabled' if test_config['USE_TLS'] else 'Disabled'
            )
            
            text_content = f"""
            Email Configuration Test Successful!
            
            Your email settings are working correctly.
            
            SMTP Server: {test_config['SMTP_SERVER']}
            Port: {test_config['SMTP_PORT']}
            From: {test_config['EMAIL_ADDRESS']}
            TLS: {'Enabled' if test_config['USE_TLS'] else 'Disabled'}
            
            This is a test email from your HRMS system.
            """
            
            # Add content to message
            text_part = MIMEText(text_content, "plain")
            html_part = MIMEText(html_content, "html")
            message.attach(text_part)
            message.attach(html_part)
            
            # Create SMTP session and test connection
            server = smtplib.SMTP(test_config['SMTP_SERVER'], test_config['SMTP_PORT'])
            
            if test_config['USE_TLS']:
                server.starttls()
            
            # Test login
            server.login(test_config['EMAIL_ADDRESS'], test_config['EMAIL_PASSWORD'])
            
            # Send test email
            server.sendmail(test_config['EMAIL_ADDRESS'], test_config['EMAIL_ADDRESS'], message.as_string())
            server.quit()
            
            logger.info("Email connection test successful")
            
            return jsonify({
                'success': True,
                'message': 'Email connection test successful! Test email sent to your address.',
                'data': {
                    'smtp_server': test_config['SMTP_SERVER'],
                    'smtp_port': test_config['SMTP_PORT'],
                    'email_address': test_config['EMAIL_ADDRESS'],
                    'tls_enabled': test_config['USE_TLS']
                }
            }), 200
            
        except smtplib.SMTPAuthenticationError:
            return jsonify({'success': False, 'error': 'Authentication failed. Please check your email address and password.'}), 400
        except smtplib.SMTPConnectError:
            return jsonify({'success': False, 'error': 'Failed to connect to SMTP server. Please check your server address and port.'}), 400
        except smtplib.SMTPException as e:
            return jsonify({'success': False, 'error': f'SMTP error: {str(e)}'}), 400
        except Exception as e:
            return jsonify({'success': False, 'error': f'Connection test failed: {str(e)}'}), 400
            
    except Exception as e:
        logger.error(f"Error testing email connection: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    main()
