#!/usr/bin/env python3
"""
Test the exact calendar API query
"""

import mysql.connector
from mysql.connector import Error

def test_calendar_query():
    """Test the exact calendar API query"""
    
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
        print("🧪 Testing exact calendar API query...")
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)
        
        # Execute the exact query from the calendar API
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
            ORDER BY s.scheduled_date, s.scheduled_time
        """)
        
        results = cursor.fetchall()
        print(f"📅 Calendar API query returned {len(results)} total results")
        
        # Look for Shubham in the results
        shubham_found = []
        for i, result in enumerate(results):
            if result['candidate_name'] and 'shubham' in result['candidate_name'].lower():
                shubham_found.append(result)
                print(f"\n🎯 Found Shubham at position {i+1}:")
                print(f"  - ID: {result['id']}")
                print(f"  - Name: {result['candidate_name']}")
                print(f"  - Round: {result['round_name']}")
                print(f"  - Date: {result['scheduled_date']} {result['scheduled_time']}")
                print(f"  - Status: {result['status']}")
                print(f"  - Job: {result['job_title']}")
        
        print(f"\n📊 Summary: Found {len(shubham_found)} Shubham interviews out of {len(results)} total interviews")
        
        # Show first 10 results to see what we're getting
        print(f"\n📋 First 10 results:")
        for i, result in enumerate(results[:10]):
            print(f"  {i+1}. {result['candidate_name']} - {result['round_name']} ({result['scheduled_date']})")
        
        connection.close()
        
    except Error as e:
        print(f"❌ MySQL Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_calendar_query()
