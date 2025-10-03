#!/usr/bin/env python3
"""
Interview Management API Endpoints
Provides REST API for interview scheduling and management
"""

from flask import Blueprint, jsonify, request
import sqlite3
from datetime import datetime
import json
import os

# Import MySQL connector for cross-database lookups
try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    print("Warning: mysql.connector not available. Some features may not work properly.")

# Create Blueprint
interview_bp = Blueprint('interviews', __name__)

def get_db_connection():
    """Get SQLite database connection"""
    db_path = os.path.join(os.path.dirname(__file__), 'interview_system.db')
    print(f"DEBUG: Connecting to database at: {db_path}")
    print(f"DEBUG: Database exists: {os.path.exists(db_path)}")
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"ERROR: Failed to connect to database: {e}")
        return None

# Get interview rounds for a ticket
@interview_bp.route('/api/interviews/rounds/<ticket_id>', methods=['GET'])
def get_interview_rounds(ticket_id):
    """Get all interview rounds for a specific ticket"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, round_name, round_order, interview_type, 
                   duration_minutes, description, requirements,
                   is_required, can_skip
            FROM interview_rounds
            WHERE ticket_id = ?
            ORDER BY round_order
        """, (ticket_id,))
        
        rounds = []
        for row in cursor.fetchall():
            rounds.append({
                'id': row['id'],
                'round_name': row['round_name'],
                'round_order': row['round_order'],
                'interview_type': row['interview_type'],
                'duration_minutes': row['duration_minutes'],
                'description': row['description'],
                'requirements': row['requirements'],
                'is_required': bool(row['is_required']),
                'can_skip': bool(row['can_skip'])
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'rounds': rounds,
                'total': len(rounds)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Get candidate details by ID
@interview_bp.route('/api/interviews/candidate/<candidate_id>', methods=['GET'])
def get_candidate_details(candidate_id):
    """Get candidate details and interview status"""
    try:
        # REMOVED: Hardcoded override for Fardeen Khan - now fetching real data from database
        
        # URL decode the candidate_id in case it was encoded
        import urllib.parse
        decoded_candidate_id = urllib.parse.unquote(candidate_id)
        
        # Get the ticket_id from query parameters if provided
        from flask import request
        ticket_id_from_query = request.args.get('ticket_id')
        print(f"GET /api/interviews/candidate/{candidate_id} - Starting (decoded: {decoded_candidate_id}, ticket_id: {ticket_id_from_query})")
        
        # Extract the actual database ID from the composite candidate ID
        # The frontend sends IDs like "9bd4f8e1cb-123-0.456" where the middle part is the actual DB ID
        actual_candidate_id = decoded_candidate_id
        if '-' in decoded_candidate_id:
            parts = decoded_candidate_id.split('-')
            if len(parts) >= 2:
                # The second part should be the actual database ID
                actual_candidate_id = parts[1]
                print(f"Extracted actual candidate ID: {actual_candidate_id} from composite ID: {decoded_candidate_id}")
        
        # For other candidate IDs, use the existing logic
        # First try to get candidate from MySQL database (resume applications)
        mysql_conn = None
        if MYSQL_AVAILABLE:
            try:
                mysql_config = {
                    'host': 'localhost',
                    'user': 'root',
                    'password': 'root',
                    'database': 'hiring_bot'
                }
                mysql_conn = mysql.connector.connect(**mysql_config)
                mysql_cursor = mysql_conn.cursor(dictionary=True)
                
                # Look for candidate in resume applications by ID
                mysql_cursor.execute("""
                    SELECT 
                        td1.field_value as applicant_name,
                        td2.field_value as applicant_email,
                        td3.field_value as job_title,
                        t.ticket_id,
                        t.subject as job_title_fallback
                    FROM ticket_details td1
                    INNER JOIN ticket_details td2 ON td1.ticket_id = td2.ticket_id
                    INNER JOIN ticket_details td3 ON td1.ticket_id = td3.ticket_id
                    INNER JOIN tickets t ON td1.ticket_id = t.ticket_id
                    WHERE td1.field_name = 'applicant_name'
                    AND td2.field_name = 'applicant_email'
                    AND td3.field_name = 'job_title'
                    AND td1.id = %s
                """, (actual_candidate_id,))
                
                mysql_candidate = mysql_cursor.fetchone()
                mysql_cursor.close()
                
                if mysql_candidate:
                    # Found candidate in MySQL - use this data
                    candidate = {
                        'id': candidate_id,  # Use the original composite ID from frontend
                        'applicant_name': mysql_candidate['applicant_name'],
                        'applicant_email': mysql_candidate['applicant_email'],
                        'job_title': mysql_candidate['job_title'] or mysql_candidate['job_title_fallback'],
                        'ticket_id': mysql_candidate['ticket_id'],
                        'interview_status': 'not_started',  # Default status
                        'rounds_completed': 0,
                        'total_rounds': 3,  # Default to 3 rounds
                        'final_decision': None,
                        'created_at': None
                    }
                    
                    mysql_conn.close()
                    
                    return jsonify({
                        'success': True,
                        'data': {
                            'candidate': candidate
                        }
                    })
                else:
                    # Candidate not found in MySQL, try to find in metadata files
                    print(f"Candidate {actual_candidate_id} not found in MySQL, checking metadata files...")
                    
                    # Try to find candidate in metadata files with ticket_id filtering
                    import json
                    import glob
                    
                    metadata_files = glob.glob("approved_tickets/*/metadata.json")
                    all_candidates = []
                    
                    for metadata_path in metadata_files:
                        try:
                            with open(metadata_path, 'r', encoding='utf-8', errors='ignore') as f:
                                metadata = json.load(f)
                                
                            if 'resumes' in metadata and len(metadata['resumes']) >= int(actual_candidate_id):
                                if int(actual_candidate_id) <= len(metadata['resumes']):
                                    resume_info = metadata['resumes'][int(actual_candidate_id) - 1]
                                    candidate_name = resume_info.get('applicant_name')
                                    candidate_email = resume_info.get('applicant_email')
                                    ticket_id = metadata.get('ticket_id')
                                    
                                    if candidate_name and candidate_email:
                                        all_candidates.append({
                                            'name': candidate_name,
                                            'email': candidate_email,
                                            'ticket_id': ticket_id,
                                            'metadata_path': metadata_path
                                        })
                                        print(f"Found candidate in metadata: {candidate_name} from ticket {ticket_id}")
                        except Exception as e:
                            print(f"Error reading metadata file {metadata_path}: {e}")
                            continue
                    
                    # Select the correct candidate based on ticket_id if provided
                    selected_candidate = None
                    if all_candidates:
                        if ticket_id_from_query:
                            print(f"Using ticket_id from query parameter: {ticket_id_from_query}")
                            matching_candidates = [c for c in all_candidates if c['ticket_id'] == ticket_id_from_query]
                            if matching_candidates:
                                selected_candidate = matching_candidates[0]
                                print(f"Found matching candidate by ticket_id: {selected_candidate['name']} from ticket {selected_candidate['ticket_id']}")
                            else:
                                print(f"No candidate found for ticket_id {ticket_id_from_query}, using first candidate")
                                selected_candidate = all_candidates[0]
                        else:
                            selected_candidate = all_candidates[0]
                            print(f"No ticket_id provided - using first candidate: {selected_candidate['name']}")
                        
                        if selected_candidate:
                            # Create candidate data from metadata
                            candidate = {
                                'id': candidate_id,
                                'applicant_name': selected_candidate['name'],
                                'applicant_email': selected_candidate['email'],
                                'job_title': 'Position',  # Default job title
                                'ticket_id': selected_candidate['ticket_id'],
                                'interview_status': 'not_started',
                                'rounds_completed': 0,
                                'total_rounds': 3,
                                'final_decision': None,
                                'created_at': None,
                                'from_metadata_only': True
                            }
                            
                            mysql_conn.close()
                            
                            return jsonify({
                                'success': True,
                                'data': {
                                    'candidate': candidate
                                }
                            })
                    
            except Exception as mysql_error:
                print(f"MySQL lookup failed: {mysql_error}")
                if mysql_conn:
                    mysql_conn.close()
        else:
            print("MySQL not available, skipping MySQL lookup")
        
        # Fallback: Try SQLite database (interview system) with name/email matching
        conn = get_db_connection()
        if conn is None:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        cursor = conn.cursor()
        
        # First try to get candidate details from the resumes API to get name/email
        try:
            import requests
            resume_response = requests.get(
                f"http://localhost:5000/api/tickets/24e038ff28/resumes",
                headers={'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789'}
            )
            
            if resume_response.status_code == 200:
                resume_data = resume_response.json()
                resumes = resume_data.get('data', {}).get('resumes', [])
                
                # Find the candidate by ID in the resumes data
                target_candidate = None
                for resume in resumes:
                    if resume.get('id') == int(actual_candidate_id):
                        target_candidate = resume
                        break
                
                if target_candidate:
                    # Use name and email to find the correct candidate in SQLite
                    candidate_name = target_candidate['applicant_name']
                    candidate_email = target_candidate['applicant_email']
                    
                    print(f"Looking for candidate: {candidate_name} ({candidate_email}) in SQLite")
                    
                    # Search in SQLite by name and email instead of ID
                    cursor.execute("""
                        SELECT * FROM candidate_interview_status
                        WHERE candidate_name = ? AND candidate_email = ?
                    """, (candidate_name, candidate_email))
                    
                    candidate_row = cursor.fetchone()
                    
                    if candidate_row:
                        # Found the correct candidate in SQLite
                        candidate = {
                            'id': candidate_id,  # Use the original composite ID from frontend
                            'applicant_name': candidate_row['candidate_name'],
                            'applicant_email': candidate_row['candidate_email'],
                            'job_title': candidate_row['job_title'],
                            'interview_status': candidate_row['interview_status'],
                            'rounds_completed': candidate_row['rounds_completed'],
                            'total_rounds': candidate_row['total_rounds'],
                            'final_decision': candidate_row['final_decision'],
                            'created_at': candidate_row['created_at']
                        }
                        
                        conn.close()
                        
                        return jsonify({
                            'success': True,
                            'data': {
                                'candidate': candidate
                            }
                        })
                    else:
                        # Candidate not found in SQLite, create default data
                        candidate = {
                            'id': candidate_id,  # Use the original composite ID from frontend
                            'applicant_name': candidate_name,
                            'applicant_email': candidate_email,
                            'job_title': 'AI Engineer',  # Default job title
                            'ticket_id': '24e038ff28',
                            'interview_status': 'not_started',
                            'rounds_completed': 0,
                            'total_rounds': 3,
                            'final_decision': None,
                            'created_at': None
                        }
                        
                        conn.close()
                        
                        return jsonify({
                            'success': True,
                            'data': {
                                'candidate': candidate
                            }
                        })
                        
        except Exception as resume_error:
            print(f"Resume API lookup failed: {resume_error}")
        
        # Final fallback: Try SQLite database (interview system) with ID
        cursor.execute("""
            SELECT * FROM candidate_interview_status
            WHERE candidate_id = ?
        """, (candidate_id,))
        
        candidate_row = cursor.fetchone()
        
        if not candidate_row:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Candidate not found in either database'
            }), 404
        
        candidate = {
            'id': candidate_id,  # Use the original composite ID from frontend
            'applicant_name': candidate_row['candidate_name'],
            'applicant_email': candidate_row['candidate_email'],
            'job_title': candidate_row['job_title'],
            'interview_status': candidate_row['interview_status'],
            'rounds_completed': candidate_row['rounds_completed'],
            'total_rounds': candidate_row['total_rounds'],
            'final_decision': candidate_row['final_decision'],
            'created_at': candidate_row['created_at']
        }
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'candidate': candidate
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Get interviews for a candidate
@interview_bp.route('/api/interviews/schedule/<candidate_id>', methods=['GET'])
def get_candidate_interviews(candidate_id):
    """Get all scheduled interviews for a candidate"""
    try:
        # URL decode the candidate_id in case it was encoded
        import urllib.parse
        decoded_candidate_id = urllib.parse.unquote(candidate_id)
        print(f"GET /api/interviews/schedule/{candidate_id} - Starting (decoded: {decoded_candidate_id})")
        
        # Extract the actual database ID from the composite candidate ID
        # The frontend sends IDs like "9bd4f8e1cb-123-0.456" where the middle part is the actual DB ID
        actual_candidate_id = decoded_candidate_id
        if '-' in decoded_candidate_id:
            parts = decoded_candidate_id.split('-')
            if len(parts) >= 2:
                # The second part should be the actual database ID
                actual_candidate_id = parts[1]
                print(f"Extracted actual candidate ID: {actual_candidate_id} from composite ID: {decoded_candidate_id}")
        
        # First get candidate details from MySQL to ensure we have the right person
        candidate_name = None
        candidate_email = None
        
        if MYSQL_AVAILABLE:
            try:
                mysql_config = {
                    'host': 'localhost',
                    'user': 'root',
                    'password': 'root',
                    'database': 'hiring_bot'
                }
                mysql_conn = mysql.connector.connect(**mysql_config)
                mysql_cursor = mysql_conn.cursor(dictionary=True)
                
                # Get candidate details by ID
                mysql_cursor.execute("""
                    SELECT 
                        td1.field_value as applicant_name,
                        td2.field_value as applicant_email
                    FROM ticket_details td1
                    INNER JOIN ticket_details td2 ON td1.ticket_id = td2.ticket_id
                    WHERE td1.field_name = 'applicant_name'
                    AND td2.field_name = 'applicant_email'
                    AND td1.id = %s
                """, (actual_candidate_id,))
                
                mysql_candidate = mysql_cursor.fetchone()
                mysql_cursor.close()
                mysql_conn.close()
                
                if mysql_candidate:
                    candidate_name = mysql_candidate['applicant_name']
                    candidate_email = mysql_candidate['applicant_email']
                    print(f"Found candidate in MySQL: {candidate_name} ({candidate_email})")
                else:
                    print(f"Candidate {candidate_id} not found in MySQL")
                    
            except Exception as mysql_error:
                print(f"MySQL lookup failed: {mysql_error}")
        
        # Now get interviews from SQLite
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if candidate_name and candidate_email:
            # Use strict filtering with name and email
            cursor.execute("""
                SELECT s.*, r.round_name, r.round_order
                FROM interview_schedules s
                LEFT JOIN interview_rounds r ON s.round_id = r.id
                WHERE s.candidate_name = ? AND s.candidate_email = ?
                ORDER BY s.scheduled_date, s.scheduled_time
            """, (candidate_name, candidate_email))
        else:
            # Fallback to ID-based lookup
            cursor.execute("""
                SELECT s.*, r.round_name, r.round_order
                FROM interview_schedules s
                LEFT JOIN interview_rounds r ON s.round_id = r.id
                WHERE s.candidate_id = ?
                ORDER BY s.scheduled_date, s.scheduled_time
            """, (candidate_id,))
        
        interviews = []
        for row in cursor.fetchall():
            interviews.append({
                'id': row['id'],
                'ticket_id': row['ticket_id'],
                'round_id': row['round_id'],
                'round_name': row['round_name'] if row['round_name'] else 'Unknown Round',
                'candidate_id': row['candidate_id'],
                'candidate_name': row['candidate_name'],
                'candidate_email': row['candidate_email'],
                'scheduled_date': row['scheduled_date'],
                'scheduled_time': row['scheduled_time'],
                'duration_minutes': row['duration_minutes'],
                'interview_type': row['interview_type'],
                'meeting_link': row['meeting_link'],
                'location': row['location'],
                'status': row['status'],
                'notes': row['notes'],
                'interviewer_names': row['interviewer_names']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'interviews': interviews,
                'total': len(interviews)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Get feedback for interviews
@interview_bp.route('/api/interviews/feedback/<candidate_id>', methods=['GET'])
def get_interview_feedback(candidate_id):
    """Get feedback for all interviews of a candidate"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get ticket_id from query parameters for proper isolation
        from flask import request
        ticket_id = request.args.get('ticket_id')
        
        if ticket_id:
            cursor.execute("""
                SELECT f.*, r.round_name
                FROM interview_feedback f
                LEFT JOIN interview_rounds r ON f.round_id = r.id
                LEFT JOIN interview_schedules isch ON f.interview_id = isch.id
                WHERE f.candidate_id = ? AND isch.ticket_id = ?
            """, (candidate_id, ticket_id))
        else:
            cursor.execute("""
                SELECT f.*, r.round_name
                FROM interview_feedback f
                LEFT JOIN interview_rounds r ON f.round_id = r.id
                WHERE f.candidate_id = ?
            """, (candidate_id,))
        
        feedback = []
        for row in cursor.fetchall():
            feedback.append({
                'id': row['id'],
                'interview_id': row['interview_id'],
                'round_id': row['round_id'],
                'round_name': row['round_name'] if row['round_name'] else 'Unknown Round',
                'overall_rating': row['overall_rating'],
                'decision': row['decision'],
                'notes': row['notes'],
                'strengths': row['strengths'],
                'areas_of_improvement': row['areas_of_improvement'],
                'submitted_at': row['submitted_at']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'feedback': feedback,
                'total': len(feedback)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Get feedback for a specific candidate (alternative route)
@interview_bp.route('/api/interviews/feedback/candidate/<candidate_id>', methods=['GET'])
def get_candidate_feedback(candidate_id):
    """Get feedback for all interviews of a candidate (alternative route)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get ticket_id from query parameters for proper isolation
        from flask import request
        ticket_id = request.args.get('ticket_id')
        
        if ticket_id:
            cursor.execute("""
                SELECT f.*, r.round_name
                FROM interview_feedback f
                LEFT JOIN interview_rounds r ON f.round_id = r.id
                LEFT JOIN interview_schedules isch ON f.interview_id = isch.id
                WHERE f.candidate_id = ? AND isch.ticket_id = ?
            """, (candidate_id, ticket_id))
        else:
            cursor.execute("""
                SELECT f.*, r.round_name
                FROM interview_feedback f
                LEFT JOIN interview_rounds r ON f.round_id = r.id
                WHERE f.candidate_id = ?
            """, (candidate_id,))
        
        feedback = []
        for row in cursor.fetchall():
            feedback.append({
                'id': row['id'],
                'interview_id': row['interview_id'],
                'round_id': row['round_id'],
                'round_name': row['round_name'] if row['round_name'] else 'Unknown Round',
                'overall_rating': row['overall_rating'],
                'decision': row['decision'],
                'notes': row['notes'],
                'strengths': row['strengths'],
                'areas_of_improvement': row['areas_of_improvement'],
                'submitted_at': row['submitted_at']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'feedback': feedback,
                'total': len(feedback)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Create new interview schedule
@interview_bp.route('/api/interviews/schedule', methods=['POST'])
def create_interview_schedule():
    """Create a new interview schedule"""
    try:
        data = request.get_json()
        
        # Debug: Log the received data
        print(f"DEBUG: Received interview schedule data: {data}")
        print(f"DEBUG: scheduled_date type: {type(data.get('scheduled_date'))}, value: {data.get('scheduled_date')}")
        
        # Convert date format if needed (DD/MM/YYYY to YYYY-MM-DD)
        scheduled_date = data.get('scheduled_date', '')
        if scheduled_date and '/' in scheduled_date:
            try:
                # Handle DD/MM/YYYY format
                day, month, year = scheduled_date.split('/')
                scheduled_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                print(f"DEBUG: Converted date from DD/MM/YYYY to YYYY-MM-DD: {scheduled_date}")
                data['scheduled_date'] = scheduled_date
            except Exception as e:
                print(f"ERROR: Failed to convert date format: {e}")
                return jsonify({
                    'success': False,
                    'error': f'Invalid date format: {scheduled_date}. Expected DD/MM/YYYY or YYYY-MM-DD'
                }), 400
        
        required_fields = ['ticket_id', 'candidate_id', 'candidate_name', 
                          'candidate_email', 'scheduled_date', 'scheduled_time']
        
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO interview_schedules
            (ticket_id, round_id, candidate_id, candidate_name, candidate_email,
             scheduled_date, scheduled_time, duration_minutes, interview_type,
             meeting_link, location, status, notes, interviewer_names, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['ticket_id'],
            data.get('round_id'),
            data['candidate_id'],
            data['candidate_name'],
            data['candidate_email'],
            data['scheduled_date'],
            data['scheduled_time'],
            data.get('duration_minutes', 60),
            data.get('interview_type', 'video_call'),
            data.get('meeting_link'),
            data.get('location'),
            data.get('status', 'scheduled'),
            data.get('notes'),
            data.get('interviewer_names'),
            data.get('created_by', 'system')
        ))
        
        interview_id = cursor.lastrowid
        conn.commit()
        
        # Update candidate status if needed
        cursor.execute("""
            SELECT * FROM candidate_interview_status
            WHERE candidate_id = ?
        """, (data['candidate_id'],))
        
        if not cursor.fetchone():
            # Create candidate status entry
            cursor.execute("""
                INSERT INTO candidate_interview_status
                (ticket_id, candidate_id, candidate_name, candidate_email,
                 job_title, interview_status, rounds_completed, total_rounds)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['ticket_id'],
                data['candidate_id'],
                data['candidate_name'],
                data['candidate_email'],
                data.get('job_title', 'Not Specified'),
                'in_progress',
                0,
                data.get('total_rounds', 1)
            ))
            conn.commit()
        
        conn.close()
        
        # Send email notifications to all participants
        try:
            from interview_email_service import send_interview_notifications
            schedule_data = {
                'meeting_link': data.get('meeting_link'),
                'scheduled_date': data['scheduled_date'],
                'scheduled_time': data['scheduled_time'],
                'duration_minutes': data.get('duration_minutes', 60),
                'interview_type': data.get('interview_type', 'video_call')
            }
            send_interview_notifications(interview_id, schedule_data)
            print(f"DEBUG: Email notifications sent for interview {interview_id}")
        except Exception as email_error:
            print(f"WARNING: Failed to send email notifications: {email_error}")
            # Don't fail the entire request if email sending fails
        
        return jsonify({
            'success': True,
            'data': {
                'interview_id': interview_id,
                'message': 'Interview scheduled successfully'
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Update interview status
@interview_bp.route('/api/interviews/status', methods=['PUT'])
def update_interview_status():
    """Update interview or candidate status"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if 'candidate_id' in data and 'overall_status' in data:
            # Update candidate overall status
            cursor.execute("""
                UPDATE candidate_interview_status
                SET interview_status = ?, final_decision = ?, updated_at = ?
                WHERE candidate_id = ?
            """, (
                data['overall_status'],
                data.get('final_decision'),
                datetime.now().isoformat(),
                data['candidate_id']
            ))
        
        if 'interview_id' in data and 'status' in data:
            # Update specific interview status
            cursor.execute("""
                UPDATE interview_schedules
                SET status = ?, updated_at = ?
                WHERE id = ?
            """, (
                data['status'],
                datetime.now().isoformat(),
                data['interview_id']
            ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Status updated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Submit interview feedback
@interview_bp.route('/api/interviews/feedback', methods=['POST'])
def submit_interview_feedback():
    """Submit feedback for an interview"""
    try:
        data = request.get_json()
        print(f"DEBUG: Received feedback data: {data}")
        
        required_fields = ['candidate_id', 'round_id', 'decision']
        
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        conn = get_db_connection()
        if conn is None:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
            
        cursor = conn.cursor()
        
        # Check if feedback already exists
        cursor.execute("""
            SELECT id FROM interview_feedback
            WHERE candidate_id = ? AND round_id = ?
        """, (data['candidate_id'], data['round_id']))
        
        existing = cursor.fetchone()
        
        # Map frontend fields to backend fields
        # Frontend sends: recommendation_notes, but backend expects: notes
        notes = data.get('recommendation_notes') or data.get('notes', '')
        
        # Find a valid interview_id for this candidate and round
        interview_id = data.get('interview_id', 0)
        if interview_id == 0:
            # Try to find an existing interview for this candidate and round
            cursor.execute("""
                SELECT id FROM interview_schedules
                WHERE candidate_id = ? AND round_id = ?
                LIMIT 1
            """, (data['candidate_id'], data['round_id']))
            
            interview_row = cursor.fetchone()
            if interview_row:
                interview_id = interview_row['id']
                print(f"DEBUG: Found existing interview_id {interview_id} for candidate {data['candidate_id']}, round {data['round_id']}")
            else:
                # Create a dummy interview record if none exists
                cursor.execute("""
                    INSERT INTO interview_schedules
                    (ticket_id, round_id, candidate_id, candidate_name, candidate_email,
                     scheduled_date, scheduled_time, status, created_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    'dummy_ticket',
                    data['round_id'],
                    data['candidate_id'],
                    'Unknown Candidate',
                    'unknown@example.com',
                    '2024-01-01',
                    '12:00:00',
                    'completed',
                    'system'
                ))
                interview_id = cursor.lastrowid
                print(f"DEBUG: Created dummy interview with ID {interview_id} for candidate {data['candidate_id']}, round {data['round_id']}")
        
        if existing:
            # Update existing feedback
            cursor.execute("""
                UPDATE interview_feedback
                SET overall_rating = ?, decision = ?, notes = ?,
                    strengths = ?, areas_of_improvement = ?
                WHERE id = ?
            """, (
                data.get('overall_rating'),
                data['decision'],
                notes,
                data.get('strengths'),
                data.get('areas_of_improvement'),
                existing['id']
            ))
            print(f"DEBUG: Updated existing feedback with ID {existing['id']}")
        else:
            # Insert new feedback
            cursor.execute("""
                INSERT INTO interview_feedback
                (interview_id, candidate_id, round_id, overall_rating,
                 decision, notes, strengths, areas_of_improvement, submitted_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                interview_id,
                data['candidate_id'],
                data['round_id'],
                data.get('overall_rating'),
                data['decision'],
                notes,
                data.get('strengths'),
                data.get('areas_of_improvement'),
                data.get('submitted_by', 'system')
            ))
            print(f"DEBUG: Inserted new feedback for candidate {data['candidate_id']}, round {data['round_id']} with interview_id {interview_id}")
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully'
        })
        
    except Exception as e:
        print(f"ERROR: Failed to submit feedback: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Health check endpoint
@interview_bp.route('/api/interviews/health', methods=['GET'])
def health_check():
    """Health check for interview API"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM interview_schedules")
        count = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'interviews_count': count
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500