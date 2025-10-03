#!/usr/bin/env python3
"""
Test the exact SQL query used in the calendar API
"""

import mysql.connector
import json
import os

def test_sql_query():
    """Test the exact SQL query from the calendar API"""
    try:
        # Database configuration
        db_config = {
            'host': os.getenv("MYSQL_HOST", "localhost"),
            'user': os.getenv("MYSQL_USER", "root"),
            'password': os.getenv("MYSQL_PASSWORD", "root"),
            'database': os.getenv("MYSQL_DATABASE", "hiring_bot")
        }
        
        print(f"Connecting to database: {db_config['host']}/{db_config['database']}")
        
        # Connect to database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # Test the exact query from the calendar API
        print("\n=== TESTING CALENDAR API QUERY ===")
        query = """
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
            LIMIT 3
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        print(f"Query returned {len(results)} results:")
        for i, row in enumerate(results):
            print(f"\nResult {i+1}:")
            print(f"  ID: {row['id']}")
            print(f"  Candidate: {row['candidate_name']}")
            print(f"  Round: {row['round_name']}")
            print(f"  Created by: {row['created_by']}")
            print(f"  Interviewer names (raw): '{row['interviewer_names']}'")
            print(f"  Interviewer names (type): {type(row['interviewer_names'])}")
            print(f"  Job title: {row['job_title']}")
            
            # Test the fallback logic
            interviewer_names = row.get('interviewer_names') or row.get('created_by', 'Not assigned')
            print(f"  Final interviewer_names: '{interviewer_names}'")
        
        # Test without GROUP BY to see raw data
        print("\n=== TESTING WITHOUT GROUP BY ===")
        simple_query = """
            SELECT 
                s.id,
                s.created_by,
                p.interviewer_name,
                ra.applicant_name as candidate_name
            FROM interview_schedules s
            LEFT JOIN resume_applications ra ON s.candidate_id = ra.id AND s.ticket_id = ra.ticket_id
            LEFT JOIN interview_participants p ON s.id = p.interview_id
            WHERE s.status IN ('scheduled', 'in_progress', 'completed')
            AND s.scheduled_date IS NOT NULL 
            AND s.scheduled_time IS NOT NULL
            ORDER BY s.id
            LIMIT 5
        """
        
        cursor.execute(simple_query)
        simple_results = cursor.fetchall()
        
        print(f"Simple query returned {len(simple_results)} results:")
        for row in simple_results:
            print(f"  ID: {row['id']}, Candidate: {row['candidate_name']}, Created by: {row['created_by']}, Interviewer: {row['interviewer_name']}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sql_query()
