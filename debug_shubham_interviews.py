#!/usr/bin/env python3
"""
Debug Shubham's interview data specifically
"""

import mysql.connector
from mysql.connector import Error

def debug_shubham_interviews():
    """Debug Shubham's interview data"""
    
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'root',
        'database': 'hiring_bot',
        'charset': 'utf8mb4',
        'autocommit': True,
        'connection_timeout': 10,
        'connect_timeout': 10
    }
    
    try:
        print("🔍 Debugging Shubham's interview data...")
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)
        
        # First, let's see all interview schedules for Shubham's candidate IDs
        print("\n📅 All interview schedules for Shubham's applications:")
        cursor.execute("""
            SELECT s.*, ra.applicant_name, ra.applicant_email, ra.ticket_id as app_ticket_id
            FROM interview_schedules s
            LEFT JOIN resume_applications ra ON s.candidate_id = ra.id AND s.ticket_id = ra.ticket_id
            WHERE ra.applicant_name LIKE '%shubham%' OR ra.applicant_name LIKE '%Shubham%'
            ORDER BY s.scheduled_date, s.scheduled_time
        """)
        shubham_schedules = cursor.fetchall()
        
        for schedule in shubham_schedules:
            print(f"\nInterview ID: {schedule['id']}")
            print(f"  - Candidate ID: {schedule['candidate_id']}")
            print(f"  - Applicant Name: {schedule['applicant_name']}")
            print(f"  - Applicant Email: {schedule['applicant_email']}")
            print(f"  - Ticket ID: {schedule['ticket_id']}")
            print(f"  - App Ticket ID: {schedule['app_ticket_id']}")
            print(f"  - Date: {schedule['scheduled_date']}")
            print(f"  - Time: {schedule['scheduled_time']}")
            print(f"  - Status: {schedule['status']}")
            print(f"  - Round ID: {schedule['round_id']}")
        
        # Now let's test the exact query used in the calendar API
        print("\n🧪 Testing calendar API query:")
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
                t.subject as job_title
            FROM interview_schedules s
            LEFT JOIN interview_rounds r ON s.round_id = r.id
            LEFT JOIN resume_applications ra ON s.candidate_id = ra.id AND s.ticket_id = ra.ticket_id
            LEFT JOIN tickets t ON s.ticket_id = t.ticket_id
            WHERE s.status IN ('scheduled', 'in_progress', 'completed')
            AND s.scheduled_date IS NOT NULL 
            AND s.scheduled_time IS NOT NULL
            AND (ra.applicant_name LIKE '%shubham%' OR ra.applicant_name LIKE '%Shubham%')
            ORDER BY s.scheduled_date, s.scheduled_time
        """)
        
        api_results = cursor.fetchall()
        print(f"Calendar API query found {len(api_results)} results for Shubham")
        
        for result in api_results:
            print(f"\nAPI Result:")
            print(f"  - ID: {result['id']}")
            print(f"  - Candidate Name: {result['candidate_name']}")
            print(f"  - Round Name: {result['round_name']}")
            print(f"  - Date: {result['scheduled_date']}")
            print(f"  - Time: {result['scheduled_time']}")
            print(f"  - Status: {result['status']}")
            print(f"  - Job Title: {result['job_title']}")
        
        # Check if there are any round names for these interviews
        print("\n📋 Checking round names for Shubham's interviews:")
        for schedule in shubham_schedules:
            if schedule['round_id']:
                cursor.execute("SELECT * FROM interview_rounds WHERE id = %s", (schedule['round_id'],))
                round_info = cursor.fetchone()
                if round_info:
                    print(f"  - Interview {schedule['id']}: Round '{round_info['round_name']}'")
                else:
                    print(f"  - Interview {schedule['id']}: No round found for ID {schedule['round_id']}")
            else:
                print(f"  - Interview {schedule['id']}: No round_id")
        
        connection.close()
        print("\n✅ Debug completed")
        
    except Error as e:
        print(f"❌ MySQL Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_shubham_interviews()
