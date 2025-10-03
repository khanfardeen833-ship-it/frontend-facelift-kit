#!/usr/bin/env python3
"""
Check MySQL database for Shubham's interview data
"""

import mysql.connector
from mysql.connector import Error

def check_mysql_interviews():
    """Check MySQL database for interview data"""
    
    # MySQL configuration (same as in server.py)
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
        print("🔍 Connecting to MySQL database...")
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor(dictionary=True)
        
        # Check what interview-related tables exist
        print("\n📊 Checking interview-related tables...")
        cursor.execute("SHOW TABLES LIKE '%interview%'")
        tables = cursor.fetchall()
        table_names = []
        for table in tables:
            for key, value in table.items():
                table_names.append(value)
        print("Interview tables found:", table_names)
        
        # Check interview_schedules table
        print("\n📅 Checking interview_schedules table...")
        cursor.execute("SELECT COUNT(*) as count FROM interview_schedules")
        count = cursor.fetchone()
        print(f"Total interview schedules: {count['count']}")
        
        if count['count'] > 0:
            cursor.execute("SELECT * FROM interview_schedules LIMIT 5")
            schedules = cursor.fetchall()
            print("Sample interview schedules:")
            for schedule in schedules:
                print(f"  - ID: {schedule['id']}, Candidate: {schedule.get('candidate_id')}, Date: {schedule.get('scheduled_date')}")
        
        # Check for Shubham specifically
        print("\n🔍 Looking for Shubham's data...")
        
        # Check resume_applications table for Shubham
        cursor.execute("""
            SELECT * FROM resume_applications 
            WHERE applicant_name LIKE '%shubham%' OR applicant_name LIKE '%Shubham%'
        """)
        shubham_applications = cursor.fetchall()
        print(f"Found {len(shubham_applications)} applications for Shubham")
        
        for app in shubham_applications:
            print(f"  - Name: {app['applicant_name']}, Email: {app['applicant_email']}, Ticket: {app['ticket_id']}")
            
            # Check if this candidate has interview schedules
            cursor.execute("""
                SELECT * FROM interview_schedules 
                WHERE candidate_id = %s AND ticket_id = %s
            """, (app['id'], app['ticket_id']))
            interviews = cursor.fetchall()
            print(f"    Found {len(interviews)} interviews for this application")
            
            for interview in interviews:
                print(f"      - Interview ID: {interview['id']}, Date: {interview.get('scheduled_date')}, Status: {interview.get('status')}")
        
        # Check interview_rounds table
        print("\n📋 Checking interview_rounds table...")
        cursor.execute("SELECT COUNT(*) as count FROM interview_rounds")
        rounds_count = cursor.fetchone()
        print(f"Total interview rounds: {rounds_count['count']}")
        
        if rounds_count['count'] > 0:
            cursor.execute("SELECT * FROM interview_rounds LIMIT 5")
            rounds = cursor.fetchall()
            print("Sample interview rounds:")
            for round in rounds:
                print(f"  - ID: {round['id']}, Name: {round['round_name']}, Ticket: {round['ticket_id']}")
        
        # Check candidate_interview_status table
        print("\n📊 Checking candidate_interview_status table...")
        cursor.execute("SELECT COUNT(*) as count FROM candidate_interview_status")
        status_count = cursor.fetchone()
        print(f"Total candidate statuses: {status_count['count']}")
        
        if status_count['count'] > 0:
            cursor.execute("SELECT * FROM candidate_interview_status WHERE candidate_name LIKE '%shubham%' OR candidate_name LIKE '%Shubham%'")
            shubham_status = cursor.fetchall()
            print(f"Found {len(shubham_status)} status records for Shubham")
            
            for status in shubham_status:
                print(f"  - Name: {status['candidate_name']}, Status: {status.get('overall_status')}, Rounds: {status.get('rounds_completed')}/{status.get('total_rounds')}")
        
        connection.close()
        print("\n✅ Database check completed")
        
    except Error as e:
        print(f"❌ MySQL Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_mysql_interviews()
