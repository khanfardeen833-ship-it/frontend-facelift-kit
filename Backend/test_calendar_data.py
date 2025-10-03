#!/usr/bin/env python3
"""
Test script to check calendar API data and interview participants
"""

import mysql.connector
import json
import os

def test_calendar_data():
    """Test the calendar API data and check interview participants"""
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
        
        # Test 1: Check interview_schedules table
        print("\n=== INTERVIEW SCHEDULES ===")
        cursor.execute("SELECT * FROM interview_schedules LIMIT 5")
        schedules = cursor.fetchall()
        print(f"Found {len(schedules)} interview schedules")
        for schedule in schedules:
            print(f"ID: {schedule['id']}, Candidate: {schedule.get('candidate_id')}, Created by: {schedule.get('created_by')}")
        
        # Test 2: Check interview_participants table
        print("\n=== INTERVIEW PARTICIPANTS ===")
        cursor.execute("SELECT * FROM interview_participants LIMIT 10")
        participants = cursor.fetchall()
        print(f"Found {len(participants)} interview participants")
        for participant in participants:
            print(f"Interview ID: {participant['interview_id']}, Interviewer ID: {participant.get('interviewer_id')}, Interviewer Name: {participant.get('interviewer_name')}")
        
        # Test 3: Check the calendar API query
        print("\n=== CALENDAR API QUERY TEST ===")
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
            LIMIT 5
        """)
        
        calendar_data = cursor.fetchall()
        print(f"Found {len(calendar_data)} calendar events")
        for event in calendar_data:
            print(f"ID: {event['id']}, Candidate: {event['candidate_name']}, Round: {event['round_name']}")
            print(f"  Created by: {event['created_by']}")
            print(f"  Interviewer names: {event['interviewer_names']}")
            print(f"  Job title: {event['job_title']}")
            print()
        
        # Test 4: Check if there are any participants for specific interviews
        print("\n=== PARTICIPANTS FOR SPECIFIC INTERVIEWS ===")
        if calendar_data:
            for event in calendar_data[:3]:  # Check first 3 events
                interview_id = event['id']
                cursor.execute("""
                    SELECT * FROM interview_participants 
                    WHERE interview_id = %s
                """, (interview_id,))
                event_participants = cursor.fetchall()
                print(f"Interview {interview_id} has {len(event_participants)} participants:")
                for p in event_participants:
                    print(f"  - Interviewer ID: {p.get('interviewer_id')}, Name: {p.get('interviewer_name')}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_calendar_data()
