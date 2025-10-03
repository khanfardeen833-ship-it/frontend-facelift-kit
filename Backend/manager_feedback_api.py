#!/usr/bin/env python3
"""
Manager Feedback API
Handles manager feedback submission and retrieval for interviews
"""

from flask import Blueprint, jsonify, request
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import json
import os
import logging

logger = logging.getLogger(__name__)

# MySQL configuration - import from main server
try:
    from server import MYSQL_CONFIG
except ImportError:
    # Fallback configuration if server import fails
    MYSQL_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'root',
        'database': 'hiring_bot'
    }

# Create Blueprint
manager_feedback_bp = Blueprint('manager_feedback', __name__)

def get_db_connection():
    """Get MySQL database connection"""
    try:
        config = MYSQL_CONFIG.copy()
        config.update({
            'autocommit': True,
            'connect_timeout': 10,
            'buffered': True
        })
        conn = mysql.connector.connect(**config)
        return conn
    except Error as e:
        logger.error(f"Failed to connect to MySQL database: {e}")
        return None

def create_manager_feedback_table():
    """Create manager feedback table if it doesn't exist"""
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS manager_feedback (
                id INT AUTO_INCREMENT PRIMARY KEY,
                interview_id INT,
                candidate_id VARCHAR(255),
                candidate_name VARCHAR(255),
                candidate_email VARCHAR(255),
                job_title VARCHAR(255),
                round_name VARCHAR(255),
                
                -- Overall Assessment
                overall_rating INT,
                decision VARCHAR(50),
                
                -- Detailed Ratings
                technical_skills INT,
                communication_skills INT,
                problem_solving INT,
                cultural_fit INT,
                leadership_potential INT,
                
                -- Feedback Text
                strengths TEXT,
                areas_for_improvement TEXT,
                detailed_feedback TEXT,
                recommendation TEXT,
                
                -- Additional Info
                would_hire_again BOOLEAN,
                team_fit VARCHAR(50),
                salary_expectation VARCHAR(50),
                start_date VARCHAR(50),
                
                -- Metadata
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                submitted_by VARCHAR(100),
                feedback_token VARCHAR(255) UNIQUE,
                
                INDEX idx_candidate_id (candidate_id),
                INDEX idx_interview_id (interview_id),
                INDEX idx_submitted_at (submitted_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Check if columns exist and add them if they don't
        cursor.execute("SHOW COLUMNS FROM manager_feedback")
        columns = [column[0] for column in cursor.fetchall()]
        
        if 'job_title' not in columns:
            cursor.execute("ALTER TABLE manager_feedback ADD COLUMN job_title VARCHAR(255)")
            logger.info("Added job_title column to manager_feedback table")
        
        if 'round_name' not in columns:
            cursor.execute("ALTER TABLE manager_feedback ADD COLUMN round_name VARCHAR(255)")
            logger.info("Added round_name column to manager_feedback table")
        
        conn.commit()
        logger.info("Manager feedback table created successfully in MySQL")
        return True
        
    except Exception as e:
        logger.error(f"Error creating manager feedback table: {e}")
        return False
    finally:
        conn.close()

# Initialize table on import
create_manager_feedback_table()

@manager_feedback_bp.route('/api/manager-feedback', methods=['POST'])
def submit_manager_feedback():
    """Submit manager feedback for an interview"""
    try:
        data = request.get_json()
        logger.info(f"Received manager feedback: {data}")
        
        # Validate required fields
        required_fields = ['candidate_id', 'candidate_name', 'candidate_email', 'overall_rating', 'decision']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor()
        
        # Generate unique feedback token
        import uuid
        feedback_token = str(uuid.uuid4())
        
        # Insert manager feedback
        cursor.execute("""
                INSERT INTO manager_feedback (
                    interview_id, candidate_id, candidate_name, candidate_email,
                    job_title, round_name, overall_rating, decision,
                    technical_skills, communication_skills, problem_solving,
                    cultural_fit, leadership_potential, strengths,
                    areas_for_improvement, detailed_feedback, recommendation,
                    would_hire_again, team_fit, salary_expectation, start_date,
                    submitted_by, feedback_token
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data.get('interview_id'),
                data['candidate_id'],
                data['candidate_name'],
                data['candidate_email'],
                data.get('job_title'),
                data.get('round_name'),
                data['overall_rating'],
                data['decision'],
                data.get('technical_skills'),
                data.get('communication_skills'),
                data.get('problem_solving'),
                data.get('cultural_fit'),
                data.get('leadership_potential'),
                data.get('strengths'),
                data.get('areas_for_improvement'),
                data.get('detailed_feedback'),
                data.get('recommendation'),
                data.get('would_hire_again', True),
                data.get('team_fit'),
                data.get('salary_expectation'),
                data.get('start_date'),
                data.get('submitted_by', 'manager'),
                feedback_token
            ))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        
        # Update interview status if needed
        if data.get('interview_id'):
            cursor.execute("""
                UPDATE interview_schedules
                SET status = 'completed', updated_at = %s
                WHERE id = %s
            """, (datetime.now().isoformat(), data['interview_id']))
            conn.commit()
        
        # Check if this is a rejection decision and handle immediate rejection
        if data.get('decision') == 'reject':
            logger.info(f"Manager feedback contains reject decision for candidate {data['candidate_id']}, processing immediate rejection")
            
            try:
                # Update candidate interview status to rejected
                cursor.execute("""
                    UPDATE candidate_interview_status 
                    SET overall_status = 'rejected', final_decision = 'reject', updated_at = CURRENT_TIMESTAMP
                    WHERE candidate_id = %s
                """, (data['candidate_id'],))
                conn.commit()
                
                # Send rejection email
                from interview_email_service import send_rejection_email
                
                send_rejection_email(
                    candidate_id=data['candidate_id'],
                    candidate_name=data['candidate_name'],
                    candidate_email=data['candidate_email'],
                    job_title=data.get('job_title', 'Position'),
                    round_name=data.get('round_name', 'Interview'),
                    feedback_text=data.get('detailed_feedback') or data.get('recommendation')
                )
                logger.info(f"Rejection email sent to {data['candidate_email']} for candidate {data['candidate_id']} (manager feedback)")
                
            except Exception as rejection_error:
                logger.error(f"Error processing immediate rejection for candidate {data['candidate_id']}: {rejection_error}")
                # Don't fail the entire operation if rejection processing fails
        
        conn.close()
        
        logger.info(f"Manager feedback submitted successfully with ID: {feedback_id}")
        
        return jsonify({
            'success': True,
            'data': {
                'feedback_id': feedback_id,
                'feedback_token': feedback_token,
                'message': 'Manager feedback submitted successfully'
            }
        })
        
    except Exception as e:
        logger.error(f"Error submitting manager feedback: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@manager_feedback_bp.route('/api/manager-feedback/<candidate_id>', methods=['GET'])
def get_manager_feedback(candidate_id):
    """Get manager feedback for a candidate"""
    try:
        logger.info(f"Getting manager feedback for candidate_id: {candidate_id}")
        
        # Use the same connection method as the main server
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor()
        logger.info("Database connection established")
        
        # Get all feedback for the candidate
        cursor.execute("""
            SELECT id, interview_id, candidate_id, candidate_name, candidate_email, 
                   job_title, round_name, overall_rating, decision, technical_skills,
                   communication_skills, problem_solving, cultural_fit, leadership_potential,
                   strengths, areas_for_improvement, detailed_feedback, recommendation,
                   would_hire_again, team_fit, salary_expectation, start_date,
                   submitted_at, submitted_by, feedback_token
            FROM manager_feedback
            WHERE candidate_id = %s
            ORDER BY submitted_at DESC
        """, (candidate_id,))
        
        rows = cursor.fetchall()
        logger.info(f"Found {len(rows)} rows for candidate {candidate_id}")
        
        feedback_list = []
        for row in rows:
            feedback_list.append({
                'id': row[0],
                'interview_id': row[1],
                'candidate_id': row[2],
                'candidate_name': row[3],
                'candidate_email': row[4],
                'job_title': row[5],
                'round_name': row[6],
                'overall_rating': row[7],
                'decision': row[8],
                'technical_skills': row[9],
                'communication_skills': row[10],
                'problem_solving': row[11],
                'cultural_fit': row[12],
                'leadership_potential': row[13],
                'strengths': row[14],
                'areas_for_improvement': row[15],
                'detailed_feedback': row[16],
                'recommendation': row[17],
                'would_hire_again': bool(row[18]) if row[18] is not None else None,
                'team_fit': row[19],
                'salary_expectation': row[20],
                'start_date': row[21],
                'submitted_at': str(row[22]) if row[22] else None,
                'submitted_by': row[23],
                'feedback_token': row[24]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'feedback': feedback_list,
                'total': len(feedback_list)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting manager feedback: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@manager_feedback_bp.route('/api/manager-feedback/token/<feedback_token>', methods=['GET'])
def get_feedback_by_token(feedback_token):
    """Get manager feedback by token (for public access)"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM manager_feedback
            WHERE feedback_token = ?
        """, (feedback_token,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({
                'success': False,
                'error': 'Feedback not found'
            }), 404
        
        feedback = {
            'id': row['id'],
            'interview_id': row['interview_id'],
            'candidate_id': row['candidate_id'],
            'candidate_name': row['candidate_name'],
            'candidate_email': row['candidate_email'],
            'job_title': row['job_title'],
            'round_name': row['round_name'],
            'overall_rating': row['overall_rating'],
            'decision': row['decision'],
            'technical_skills': row['technical_skills'],
            'communication_skills': row['communication_skills'],
            'problem_solving': row['problem_solving'],
            'cultural_fit': row['cultural_fit'],
            'leadership_potential': row['leadership_potential'],
            'strengths': row['strengths'],
            'areas_for_improvement': row['areas_for_improvement'],
            'detailed_feedback': row['detailed_feedback'],
            'recommendation': row['recommendation'],
            'would_hire_again': bool(row['would_hire_again']),
            'team_fit': row['team_fit'],
            'salary_expectation': row['salary_expectation'],
            'start_date': row['start_date'],
            'submitted_at': row['submitted_at'],
            'submitted_by': row['submitted_by'],
            'feedback_token': row['feedback_token']
        }
        
        return jsonify({
            'success': True,
            'data': {
                'feedback': feedback
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting feedback by token: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@manager_feedback_bp.route('/api/manager-feedback/<feedback_id>', methods=['PUT'])
def update_manager_feedback(feedback_id):
    """Update manager feedback"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor()
        
        # Build dynamic update query
        update_fields = []
        update_values = []
        
        allowed_fields = [
            'overall_rating', 'decision', 'technical_skills', 'communication_skills',
            'problem_solving', 'cultural_fit', 'leadership_potential', 'strengths',
            'areas_for_improvement', 'detailed_feedback', 'recommendation',
            'would_hire_again', 'team_fit', 'salary_expectation', 'start_date'
        ]
        
        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = ?")
                update_values.append(data[field])
        
        if not update_fields:
            return jsonify({
                'success': False,
                'error': 'No valid fields to update'
            }), 400
        
        update_values.append(datetime.now().isoformat())  # updated_at
        update_values.append(feedback_id)
        
        query = f"""
            UPDATE manager_feedback
            SET {', '.join(update_fields)}, updated_at = ?
            WHERE id = ?
        """
        
        cursor.execute(query, update_values)
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Manager feedback updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating manager feedback: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@manager_feedback_bp.route('/api/manager-feedback/<feedback_id>', methods=['DELETE'])
def delete_manager_feedback(feedback_id):
    """Delete manager feedback"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM manager_feedback WHERE id = ?", (feedback_id,))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Feedback not found'
            }), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Manager feedback deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting manager feedback: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@manager_feedback_bp.route('/api/manager-feedback/stats', methods=['GET'])
def get_feedback_stats():
    """Get manager feedback statistics"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'success': False,
                'error': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor()
        
        # Get total feedback count
        cursor.execute("SELECT COUNT(*) as total FROM manager_feedback")
        total_feedback = cursor.fetchone()['total']
        
        # Get feedback by decision
        cursor.execute("""
            SELECT decision, COUNT(*) as count
            FROM manager_feedback
            GROUP BY decision
        """)
        decision_stats = {row['decision']: row['count'] for row in cursor.fetchall()}
        
        # Get average ratings
        cursor.execute("""
            SELECT 
                AVG(overall_rating) as avg_overall,
                AVG(technical_skills) as avg_technical,
                AVG(communication_skills) as avg_communication,
                AVG(problem_solving) as avg_problem_solving,
                AVG(cultural_fit) as avg_cultural_fit
            FROM manager_feedback
        """)
        avg_ratings = cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'total_feedback': total_feedback,
                'decision_stats': decision_stats,
                'average_ratings': {
                    'overall': round(avg_ratings['avg_overall'] or 0, 2),
                    'technical_skills': round(avg_ratings['avg_technical'] or 0, 2),
                    'communication_skills': round(avg_ratings['avg_communication'] or 0, 2),
                    'problem_solving': round(avg_ratings['avg_problem_solving'] or 0, 2),
                    'cultural_fit': round(avg_ratings['avg_cultural_fit'] or 0, 2)
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting feedback stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
