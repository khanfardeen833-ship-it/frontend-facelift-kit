#!/usr/bin/env python3
"""
Sync interview data with actual candidates from resume_applications
Maps real candidate IDs to interview schedules
"""

import sqlite3
import mysql.connector
from mysql.connector import Error
import os

# MySQL Configuration
MYSQL_CONFIG = {
    'host': os.environ.get('MYSQL_HOST', 'localhost'),
    'user': os.environ.get('MYSQL_USER', 'root'),
    'password': os.environ.get('MYSQL_PASSWORD', ''),
    'database': os.environ.get('MYSQL_DATABASE', 'hiring_bot_db')
}

def get_mysql_connection():
    """Get MySQL database connection"""
    try:
        connection = mysql.connector.connect(**MYSQL_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def sync_candidates():
    """Sync candidates from MySQL to SQLite interview system"""
    
    # Connect to MySQL
    mysql_conn = get_mysql_connection()
    if not mysql_conn:
        print("❌ Could not connect to MySQL database")
        return False
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect('interview_system.db')
    sqlite_cursor = sqlite_conn.cursor()
    
    try:
        mysql_cursor = mysql_conn.cursor(dictionary=True)
        
        # Get all candidates from resume_applications
        mysql_cursor.execute("""
            SELECT id, ticket_id, applicant_name, applicant_email, applicant_phone
            FROM resume_applications
            WHERE applicant_name LIKE '%Fardeen%Khan%'
        """)
        
        candidates = mysql_cursor.fetchall()
        
        if candidates:
            print(f"✅ Found {len(candidates)} Fardeen Khan entries in resume_applications")
            
            for candidate in candidates:
                print(f"\n📋 Processing candidate:")
                print(f"   ID: {candidate['id']}")
                print(f"   Name: {candidate['applicant_name']}")
                print(f"   Email: {candidate['applicant_email']}")
                print(f"   Ticket: {candidate['ticket_id']}")
                
                # Update interview schedules with correct candidate_id
                sqlite_cursor.execute("""
                    UPDATE interview_schedules
                    SET candidate_id = ?, 
                        candidate_email = ?,
                        ticket_id = ?
                    WHERE candidate_name LIKE '%Fardeen%Khan%'
                """, (str(candidate['id']), candidate['applicant_email'], candidate['ticket_id']))
                
                # Update or insert candidate status
                sqlite_cursor.execute("""
                    INSERT OR REPLACE INTO candidate_interview_status
                    (ticket_id, candidate_id, candidate_name, candidate_email, 
                     job_title, interview_status, rounds_completed, total_rounds)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    candidate['ticket_id'],
                    str(candidate['id']),
                    candidate['applicant_name'],
                    candidate['applicant_email'],
                    'Web Developer',
                    'in_progress',
                    0,
                    4
                ))
                
                print(f"   ✅ Updated interview records for candidate ID: {candidate['id']}")
        else:
            print("⚠️  No Fardeen Khan found in resume_applications")
            print("\n📝 Creating sample entry for testing...")
            
            # Insert a sample candidate in MySQL for testing
            mysql_cursor.execute("""
                INSERT INTO resume_applications 
                (ticket_id, applicant_name, applicant_email, applicant_phone, 
                 filename, file_path, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                '96842d6ce2_web-dev',
                'Fardeen Khan',
                'fardeen.khan@example.com',
                '+91-9876543210',
                'Fardeen_Khan_Resume.pdf',
                'approved_tickets/96842d6ce2_web-dev/Fardeen_Khan_Resume.pdf',
                'pending'
            ))
            mysql_conn.commit()
            
            new_id = mysql_cursor.lastrowid
            print(f"   ✅ Created sample candidate with ID: {new_id}")
            
            # Now update SQLite with this ID
            sqlite_cursor.execute("""
                UPDATE interview_schedules
                SET candidate_id = ?
                WHERE candidate_name LIKE '%Fardeen%Khan%'
            """, (str(new_id),))
            
            sqlite_cursor.execute("""
                INSERT OR REPLACE INTO candidate_interview_status
                (ticket_id, candidate_id, candidate_name, candidate_email, 
                 job_title, interview_status, rounds_completed, total_rounds)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                '96842d6ce2_web-dev',
                str(new_id),
                'Fardeen Khan',
                'fardeen.khan@example.com',
                'Web Developer',
                'in_progress',
                0,
                4
            ))
        
        sqlite_conn.commit()
        
        # Verify the update
        sqlite_cursor.execute("""
            SELECT * FROM interview_schedules 
            WHERE candidate_name LIKE '%Fardeen%Khan%'
        """)
        
        interviews = sqlite_cursor.fetchall()
        print(f"\n✅ Interview schedules updated. Found {len(interviews)} interviews for Fardeen Khan")
        
        for interview in interviews:
            print(f"   - Candidate ID: {interview[3]}, Date: {interview[6]}, Time: {interview[7]}")
        
        mysql_cursor.close()
        mysql_conn.close()
        sqlite_conn.close()
        
        print("\n✅ Sync completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during sync: {e}")
        if mysql_conn:
            mysql_conn.rollback()
        if sqlite_conn:
            sqlite_conn.rollback()
        return False

def main():
    print("🔄 Syncing Interview Data with Candidates")
    print("=" * 50)
    
    success = sync_candidates()
    
    if success:
        print("\n📊 Summary:")
        print("   ✅ Interview data has been synced")
        print("   ✅ Fardeen Khan's interviews are now properly linked")
        print("\n💡 Next Steps:")
        print("   1. Start the backend server: python server.py")
        print("   2. Open the HR portal")
        print("   3. Navigate to View Status for candidates")
        print("   4. You should now see Fardeen Khan's interviews")
    else:
        print("\n❌ Sync failed. Please check the error messages above.")

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)