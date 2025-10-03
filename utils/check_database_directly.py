#!/usr/bin/env python3
"""
Check database directly to understand the candidate mapping issue
"""
import mysql.connector
import json
import os

def check_database():
    print("🔍 Checking database directly...")
    
    try:
        # Try to connect to MySQL database
        # You may need to adjust these connection parameters
        conn = mysql.connector.connect(
            host='localhost',
            user='root',  # Adjust as needed
            password='',  # Adjust as needed
            database='hrms_database'  # Adjust as needed
        )
        
        cursor = conn.cursor(dictionary=True)
        
        # Check all candidates with the email aman1212345@gmail.com
        print("\n1️⃣ Checking for candidates with email 'aman1212345@gmail.com':")
        cursor.execute("""
            SELECT id, ticket_id, applicant_name, applicant_email, status 
            FROM resume_applications 
            WHERE applicant_email = 'aman1212345@gmail.com'
            ORDER BY id
        """)
        
        candidates = cursor.fetchall()
        print(f"   Found {len(candidates)} candidates with this email:")
        for candidate in candidates:
            print(f"     ID: {candidate['id']}, Ticket: {candidate['ticket_id']}, Name: {candidate['applicant_name']}, Status: {candidate['status']}")
        
        # Check all candidates in ticket c8c0c0d23e
        print("\n2️⃣ Checking all candidates in ticket 'c8c0c0d23e':")
        cursor.execute("""
            SELECT id, ticket_id, applicant_name, applicant_email, status 
            FROM resume_applications 
            WHERE ticket_id = 'c8c0c0d23e'
            ORDER BY id
        """)
        
        candidates = cursor.fetchall()
        print(f"   Found {len(candidates)} candidates in this ticket:")
        for candidate in candidates:
            print(f"     ID: {candidate['id']}, Name: {candidate['applicant_name']}, Email: {candidate['applicant_email']}, Status: {candidate['status']}")
        
        # Check candidate_interview_status table
        print("\n3️⃣ Checking candidate_interview_status table:")
        cursor.execute("""
            SELECT candidate_id, ticket_id, overall_status, final_decision 
            FROM candidate_interview_status 
            WHERE ticket_id = 'c8c0c0d23e'
            ORDER BY candidate_id
        """)
        
        statuses = cursor.fetchall()
        print(f"   Found {len(statuses)} status records:")
        for status in statuses:
            print(f"     Candidate ID: {status['candidate_id']}, Status: {status['overall_status']}, Decision: {status['final_decision']}")
        
        cursor.close()
        conn.close()
        
    except mysql.connector.Error as e:
        print(f"❌ MySQL connection error: {e}")
        print("   Please check your database connection parameters")
    except Exception as e:
        print(f"❌ Error: {e}")

def check_metadata_files():
    print("\n🔍 Checking metadata files...")
    
    import glob
    
    # Check metadata files
    metadata_files = glob.glob("Backend/approved_tickets/*/metadata.json")
    print(f"Found {len(metadata_files)} metadata files")
    
    for metadata_path in metadata_files:
        print(f"\n📄 {metadata_path}:")
        try:
            with open(metadata_path, 'r', encoding='utf-8', errors='ignore') as f:
                metadata = json.load(f)
            
            ticket_id = metadata.get('ticket_id')
            resumes = metadata.get('resumes', [])
            
            print(f"   Ticket ID: {ticket_id}")
            print(f"   Resumes count: {len(resumes)}")
            
            for i, resume in enumerate(resumes):
                if i < 5:  # Show first 5
                    print(f"     [{i+1}] {resume.get('applicant_name')} - {resume.get('applicant_email')}")
                    
        except Exception as e:
            print(f"   ❌ Error reading {metadata_path}: {e}")

if __name__ == "__main__":
    check_database()
    check_metadata_files()
