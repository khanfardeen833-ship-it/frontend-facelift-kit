import logging
import random
import string
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from mysql.connector import connect
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# Email configuration - use environment variables with fallback defaults
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

# Database configuration - use environment variables or fallback
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'root'),
    'database': os.getenv('MYSQL_DATABASE', 'hiring_bot')
}

logger.info(f"Database config: {DB_CONFIG['database']}@{DB_CONFIG['host']}")

def send_email(to_email, subject, body):
    """Send email using SMTP"""
    if not EMAIL_CONFIG['SEND_EMAILS']:
        logger.info(f"Email sending disabled. Would send to {to_email}: {subject}")
        return True
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = f"{EMAIL_CONFIG['FROM_NAME']} <{EMAIL_CONFIG['EMAIL_ADDRESS']}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add body
        msg.attach(MIMEText(body, 'plain'))
        
        # Create SMTP session
        server = smtplib.SMTP(EMAIL_CONFIG['SMTP_SERVER'], EMAIL_CONFIG['SMTP_PORT'])
        server.starttls()
        server.login(EMAIL_CONFIG['EMAIL_ADDRESS'], EMAIL_CONFIG['EMAIL_PASSWORD'])
        
        # Send email
        text = msg.as_string()
        server.sendmail(EMAIL_CONFIG['EMAIL_ADDRESS'], to_email, text)
        server.quit()
        
        logger.info(f"Email sent successfully to {to_email}: {subject}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending email to {to_email}: {e}")
        return False

def reload_email_config():
    """Reload EMAIL_CONFIG from environment variables"""
    global EMAIL_CONFIG
    # Reload environment variables
    load_dotenv()
    EMAIL_CONFIG = {
        'SMTP_SERVER': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
        'SMTP_PORT': int(os.getenv('SMTP_PORT', 587)),
        'EMAIL_ADDRESS': os.getenv('EMAIL_ADDRESS', 'fardeen78754@gmail.com'),
        'EMAIL_PASSWORD': os.getenv('EMAIL_PASSWORD', 'qfadfftaihyrfysu'),
        'USE_TLS': os.getenv('USE_TLS', 'true').lower() == 'true',
        'FROM_NAME': os.getenv('FROM_NAME', 'HR Team - Your Company'),
        'COMPANY_NAME': os.getenv('COMPANY_NAME', 'Your Company Name'),
        'COMPANY_WEBSITE': os.getenv('COMPANY_WEBSITE', 'https://yourcompany.com'),
        'HR_EMAIL': os.getenv('HR_EMAIL', 'snlettings.data@gmail.com'),
        'SEND_EMAILS': os.getenv('SEND_EMAILS', 'true').lower() == 'true'
    }

def get_db_connection():
    """Get database connection"""
    try:
        return connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

def send_interview_notifications(interview_id, schedule_data):
    """Send email notifications for scheduled interview"""
    try:
        conn = get_db_connection()
        if not conn:
            logger.error("Failed to get database connection")
            return
            
        cursor = conn.cursor(dictionary=True)
        
        # Get interview details
        cursor.execute("""
            SELECT 
                isch.*,
                ir.round_name,
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
            logger.error(f"Interview {interview_id} not found")
            return
        
        # Get participants
        cursor.execute("""
            SELECT 
                ip.*,
                i.first_name,
                i.last_name,
                i.email as interviewer_default_email,
                COALESCE(ip.interviewer_email, i.email) as interviewer_email,
                COALESCE(ip.interviewer_name, CONCAT(i.first_name, ' ', i.last_name)) as interviewer_display_name
            FROM interview_participants ip
            LEFT JOIN interviewers i ON ip.interviewer_id = i.id
            WHERE ip.interview_id = %s
        """, (interview_id,))
        participants = cursor.fetchall()
        
        logger.info(f"Found {len(participants)} participants for interview {interview_id}")
        for i, p in enumerate(participants):
            logger.info(f"Participant {i+1}: id={p.get('id')}, interviewer_id={p.get('interviewer_id')}, "
                       f"interviewer_name={p.get('interviewer_name')}, interviewer_email={p.get('interviewer_email')}, "
                       f"display_name={p.get('interviewer_display_name')}")
        
        cursor.close()
        conn.close()
        
        # Generate Google Meet link
        meeting_link = schedule_data.get('meeting_link') or f"https://meet.google.com/{generate_meet_code()}"
        
        # Send email to candidate
        candidate_subject = f"Interview Scheduled - {interview['job_title']}"
        candidate_body = f"""
        Dear {interview['applicant_name']},
        
        Your interview has been scheduled for the position of {interview['job_title']}.
        
        Interview Details:
        - Round: {interview['round_name']}
        - Date: {interview['scheduled_date']}
        - Time: {interview['scheduled_time']}
        - Duration: {interview['duration_minutes']} minutes
        - Type: {interview['interview_type'].replace('_', ' ').title()}
        
        Meeting Link: {meeting_link}
        
        Please join the meeting 5 minutes before the scheduled time.
        
        Best regards,
        HR Team
        """
        
        # Send email to each participant with manager feedback link
        for participant in participants:
            if participant.get('interviewer_email'):
                # Get participant role and format it properly
                participant_role = participant.get('participant_type', 'interviewer')
                role_display = participant_role.replace('_', ' ').title()
                
                # Premium feature: Only generate manager feedback link for selected managers
                feedback_link = ""
                show_feedback_section = participant.get('is_manager_feedback', False)
                
                if show_feedback_section:
                    # Generate manager feedback link - using standalone feedback server
                    import urllib.parse
                    feedback_link = f"http://localhost:3002/?interview_id={interview_id}&candidate_id={interview['candidate_id']}&candidate_name={urllib.parse.quote(interview['applicant_name'])}&candidate_email={urllib.parse.quote(interview['applicant_email'])}&job_title={urllib.parse.quote(interview['job_title'])}&round_name={urllib.parse.quote(interview['round_name'])}"
                
                # Customize email content based on role
                if participant_role == 'observer':
                    role_instruction = "You have been assigned as an observer for this interview. As an observer, you will watch and listen to the interview process but may not actively participate in questioning the candidate."
                    action_instruction = "Please join the meeting 5 minutes before the scheduled time to observe the interview."
                elif participant_role == 'coordinator':
                    role_instruction = "You have been assigned as a coordinator for this interview. As a coordinator, you will help manage the interview process and ensure everything runs smoothly."
                    action_instruction = "Please join the meeting 5 minutes before the scheduled time to coordinate the interview."
                else:  # interviewer (default)
                    role_instruction = "You have been assigned to conduct an interview for the position."
                    action_instruction = "Please join the meeting 5 minutes before the scheduled time to conduct the interview."
                
                interviewer_subject = f"Interview Assignment - {interview['job_title']} (Your Role: {role_display})"
                interviewer_body = f"""
                Dear {participant.get('interviewer_display_name', 'Interviewer')},
                
                ===============================================
                🎯 YOUR ROLE IN THIS INTERVIEW: {role_display.upper()}
                ===============================================
                
                {role_instruction} of {interview['job_title']}.
                
                📋 INTERVIEW DETAILS:
                - Candidate: {interview['applicant_name']}
                - Round: {interview['round_name']}
                - Date: {interview['scheduled_date']}
                - Time: {interview['scheduled_time']}
                - Duration: {interview['duration_minutes']} minutes
                - Type: {interview['interview_type'].replace('_', ' ').title()}
                
                🔗 Meeting Link: {meeting_link}
                
                ⚠️  IMPORTANT: {action_instruction}
{f'''
                ===============================================
                📝 PREMIUM MANAGER FEEDBACK SUBMISSION
                ===============================================
                
                🌟 You have been selected to provide manager feedback for this interview!
                
                After the interview, please submit your feedback using our premium feedback system:
                
                🔗 Feedback Link: {feedback_link}
                
                The premium feedback system includes:
                • Comprehensive rating system (Technical, Communication, Problem Solving, Cultural Fit)
                • Detailed feedback forms with strengths and areas for improvement
                • Hiring recommendation with team fit assessment
                • Salary expectation and start date evaluation
                • Professional feedback that will be visible to the candidate
                
                📱 HOW TO ACCESS FEEDBACK:
                1. Click the feedback link above
                2. The premium feedback form will open in your browser
                3. Complete the 4-step feedback process
                4. Submit your comprehensive assessment
                
                🔧 TROUBLESHOOTING:
                • If the link doesn't work, make sure you're using a modern web browser
                • The feedback form works best in Chrome, Firefox, or Safari
                • If you encounter issues, please contact HR for assistance
                
                Your feedback is crucial for making informed hiring decisions and will help the candidate understand their performance.
                ''' if show_feedback_section else '''
                ===============================================
                📝 INTERVIEW PARTICIPATION
                ===============================================
                
                You are participating in this interview as a {role_display}. 
                Standard interview feedback will be handled through the regular process.
                '''}
                
                Best regards,
                HR Team
                """
                
                # Send email to interviewer
                send_email(participant['interviewer_email'], interviewer_subject, interviewer_body)
                logger.info(f"Interview notification sent to {participant['interviewer_email']} for {participant.get('interviewer_display_name', 'Interviewer')} as {role_display}")
        
        # Send email to candidate
        send_email(interview['applicant_email'], candidate_subject, candidate_body)
        
        # Send email to HR team
        hr_subject = f"Interview Scheduled Notification - {interview['job_title']}"
        hr_body = f"""
        Dear HR Team,
        
        A new interview has been scheduled in the system.
        
        Interview Details:
        - Candidate: {interview['applicant_name']} ({interview['applicant_email']})
        - Position: {interview['job_title']}
        - Round: {interview['round_name']}
        - Date: {interview['scheduled_date']}
        - Time: {interview['scheduled_time']}
        - Duration: {interview['duration_minutes']} minutes
        - Type: {interview['interview_type'].replace('_', ' ').title()}
        
        Meeting Link: {meeting_link}
        
        Participants:
        {chr(10).join([f"- {p.get('interviewer_display_name', 'Unknown')} ({p.get('interviewer_email', '')}) - Role: {p.get('participant_type', 'interviewer').replace('_', ' ').title()}" for p in participants if p.get('interviewer_email')])}
        
        Manager Feedback Links (Premium):
        {chr(10).join([f"- {p.get('interviewer_display_name', 'Unknown')}: http://localhost:3002/?interview_id={interview_id}&candidate_id={interview['candidate_id']}&candidate_name={urllib.parse.quote(interview['applicant_name'])}&candidate_email={urllib.parse.quote(interview['applicant_email'])}&job_title={urllib.parse.quote(interview['job_title'])}&round_name={urllib.parse.quote(interview['round_name'])} ⭐" for p in participants if p.get('interviewer_email') and p.get('is_manager_feedback', False)])}
        
        This is an automated notification for your records.
        
        Best regards,
        Interview Management System
        """
        
        # Send email to HR (using the same email as configured in EMAIL_CONFIG)
        send_email(EMAIL_CONFIG['EMAIL_ADDRESS'], hr_subject, hr_body)
        
    except Exception as e:
        logger.error(f"Error sending interview notifications: {e}")

def generate_meet_code():
    """Generate a random Google Meet code"""
    # Generate a 3-letter + 4-digit code like "abc-defg-hij"
    letters = ''.join(random.choices(string.ascii_lowercase, k=3))
    digits1 = ''.join(random.choices(string.digits, k=4))
    digits2 = ''.join(random.choices(string.digits, k=3))
    return f"{letters}-{digits1}-{digits2}"

def send_interview_update_notifications(interview_id, update_data):
    """Send email notifications for updated interview"""
    try:
        conn = get_db_connection()
        if not conn:
            logger.error("Failed to get database connection")
            return
            
        cursor = conn.cursor(dictionary=True)
        
        # Get interview details
        cursor.execute("""
            SELECT 
                isch.*,
                ir.round_name,
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
            logger.error(f"Interview {interview_id} not found")
            return
        
        # Get participants
        cursor.execute("""
            SELECT 
                ip.*,
                i.first_name,
                i.last_name,
                i.email as interviewer_default_email,
                COALESCE(ip.interviewer_email, i.email) as interviewer_email,
                COALESCE(ip.interviewer_name, CONCAT(i.first_name, ' ', i.last_name)) as interviewer_display_name
            FROM interview_participants ip
            LEFT JOIN interviewers i ON ip.interviewer_id = i.id
            WHERE ip.interview_id = %s
        """, (interview_id,))
        participants = cursor.fetchall()
        
        logger.info(f"Found {len(participants)} participants for interview {interview_id}")
        for i, p in enumerate(participants):
            logger.info(f"Participant {i+1}: id={p.get('id')}, interviewer_id={p.get('interviewer_id')}, "
                       f"interviewer_name={p.get('interviewer_name')}, interviewer_email={p.get('interviewer_email')}, "
                       f"display_name={p.get('interviewer_display_name')}")
        
        cursor.close()
        conn.close()
        
        # Use the updated meeting link from the request data, or generate a new one
        meeting_link = update_data.get('meeting_link') or f"https://meet.google.com/{generate_meet_code()}"
        
        # Send email to candidate
        candidate_subject = f"Interview Updated - {interview['job_title']}"
        candidate_body = f"""
        Dear {interview['applicant_name']},
        
        Your interview details have been updated for the position of {interview['job_title']}.
        
        Updated Interview Details:
        - Round: {interview['round_name']}
        - Date: {update_data.get('scheduled_date', interview['scheduled_date'])}
        - Time: {update_data.get('scheduled_time', interview['scheduled_time'])}
        - Duration: {update_data.get('duration_minutes', interview['duration_minutes'])} minutes
        - Type: {update_data.get('interview_type', interview['interview_type']).replace('_', ' ').title()}
        
        Meeting Link: {meeting_link}
        
        Please join the meeting 5 minutes before the scheduled time.
        
        Best regards,
        HR Team
        """
        
        # Send email to each participant
        for participant in participants:
            if participant.get('interviewer_email'):
                # Get participant role and format it properly
                participant_role = participant.get('participant_type', 'interviewer')
                role_display = participant_role.replace('_', ' ').title()
                
                # Customize email content based on role
                if participant_role == 'observer':
                    role_instruction = "The interview details have been updated. As an observer, you will watch and listen to the interview process but may not actively participate in questioning the candidate."
                    action_instruction = "Please join the meeting 5 minutes before the scheduled time to observe the interview."
                elif participant_role == 'coordinator':
                    role_instruction = "The interview details have been updated. As a coordinator, you will help manage the interview process and ensure everything runs smoothly."
                    action_instruction = "Please join the meeting 5 minutes before the scheduled time to coordinate the interview."
                else:  # interviewer (default)
                    role_instruction = "The interview details have been updated for the position."
                    action_instruction = "Please join the meeting 5 minutes before the scheduled time to conduct the interview."
                
                interviewer_subject = f"Interview Update - {interview['job_title']} (Your Role: {role_display})"
                interviewer_body = f"""
                Dear {participant.get('interviewer_display_name', 'Interviewer')},
                
                ===============================================
                🎯 YOUR ROLE IN THIS INTERVIEW: {role_display.upper()}
                ===============================================
                
                {role_instruction} of {interview['job_title']}.
                
                📋 UPDATED INTERVIEW DETAILS:
                - Candidate: {interview['applicant_name']}
                - Round: {interview['round_name']}
                - Date: {update_data.get('scheduled_date', interview['scheduled_date'])}
                - Time: {update_data.get('scheduled_time', interview['scheduled_time'])}
                - Duration: {update_data.get('duration_minutes', interview['duration_minutes'])} minutes
                - Type: {update_data.get('interview_type', interview['interview_type']).replace('_', ' ').title()}
                
                🔗 Meeting Link: {meeting_link}
                
                ⚠️  IMPORTANT: {action_instruction}
                
                Best regards,
                HR Team
                """
                
                # Send email to interviewer
                send_email(participant['interviewer_email'], interviewer_subject, interviewer_body)
        
        # Send email to candidate
        send_email(interview['applicant_email'], candidate_subject, candidate_body)
        
        # Send email to HR team
        hr_subject = f"Interview Update Notification - {interview['job_title']}"
        hr_body = f"""
        Dear HR Team,
        
        An interview has been updated in the system.
        
        Interview Details:
        - Candidate: {interview['applicant_name']} ({interview['applicant_email']})
        - Position: {interview['job_title']}
        - Round: {interview['round_name']}
        - Date: {update_data.get('scheduled_date', interview['scheduled_date'])}
        - Time: {update_data.get('scheduled_time', interview['scheduled_time'])}
        - Duration: {update_data.get('duration_minutes', interview['duration_minutes'])} minutes
        - Type: {update_data.get('interview_type', interview['interview_type']).replace('_', ' ').title()}
        
        Meeting Link: {meeting_link}
        
        Participants:
        {chr(10).join([f"- {p.get('interviewer_display_name', 'Unknown')} ({p.get('interviewer_email', '')}) - Role: {p.get('participant_type', 'interviewer').replace('_', ' ').title()}" for p in participants if p.get('interviewer_email')])}
        
        This is an automated notification for your records.
        
        Best regards,
        Interview Management System
        """
        
        # Send email to HR (using the same email as configured in EMAIL_CONFIG)
        send_email(EMAIL_CONFIG['EMAIL_ADDRESS'], hr_subject, hr_body)
        
    except Exception as e:
        logger.error(f"Error sending interview update notifications: {e}")

def send_rejection_email(candidate_id, candidate_name, candidate_email, job_title, round_name, feedback_text=None):
    """Send rejection email to candidate"""
    try:
        logger.info(f"Sending rejection email to {candidate_email} for candidate {candidate_id}")
        
        # Create professional rejection email
        subject = f"Application Update - {job_title} Position"
        
        # Professional rejection email body
        body = f"""
Dear {candidate_name},

Thank you for your interest in the {job_title} position and for taking the time to participate in our interview process.

After careful consideration of your application and interview performance, we have decided not to move forward with your candidacy for this particular role at this time.

We appreciate the time and effort you invested in the application process, including your participation in the {round_name}. Your qualifications and experience were impressive, and we encourage you to apply for other opportunities that may be a better fit for your skills and career goals.

{f"Interview Feedback: {feedback_text}" if feedback_text and feedback_text.strip() else ""}

We will keep your information on file and may contact you in the future if a suitable position becomes available.

We wish you the best of luck in your job search and future career endeavors.

Best regards,
HR Team
{EMAIL_CONFIG['COMPANY_NAME']}

---
This is an automated message. Please do not reply to this email.
For any questions, please contact our HR team at {EMAIL_CONFIG['HR_EMAIL']}
        """
        
        # Send the rejection email
        success = send_email(candidate_email, subject, body)
        
        if success:
            logger.info(f"Rejection email sent successfully to {candidate_email}")
            
            # Also send notification to HR team
            hr_subject = f"Candidate Rejected - {candidate_name} ({job_title})"
            hr_body = f"""
Dear HR Team,

A candidate has been rejected during the interview process.

Candidate Details:
- Name: {candidate_name}
- Email: {candidate_email}
- Position: {job_title}
- Rejected at Round: {round_name}
- Feedback: {feedback_text if feedback_text else 'No specific feedback provided'}

The rejection email has been automatically sent to the candidate.

This is an automated notification for your records.

Best regards,
Interview Management System
            """
            
            send_email(EMAIL_CONFIG['HR_EMAIL'], hr_subject, hr_body)
            logger.info(f"HR notification sent for rejected candidate {candidate_name}")
            
        else:
            logger.error(f"Failed to send rejection email to {candidate_email}")
            
        return success
        
    except Exception as e:
        logger.error(f"Error sending rejection email to {candidate_email}: {e}")
        return False
