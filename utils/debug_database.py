#!/usr/bin/env python3
"""
Debug script to check database candidate ID mapping
"""
import sqlite3
import json
import os
import glob

def check_database():
    print("🔍 Checking database for candidate ID mapping issue...")
    
    # Check metadata files
    print("\n📁 Checking metadata files...")
    metadata_files = glob.glob("Backend/approved_tickets/*/metadata.json")
    print(f"Found {len(metadata_files)} metadata files")
    
    for metadata_path in metadata_files:
        print(f"\n📄 Checking: {metadata_path}")
        try:
            with open(metadata_path, 'r', encoding='utf-8', errors='ignore') as f:
                metadata = json.load(f)
            
            ticket_id = metadata.get('ticket_id')
            print(f"  Ticket ID: {ticket_id}")
            
            if 'resumes' in metadata:
                print(f"  Resumes count: {len(metadata['resumes'])}")
                for i, resume in enumerate(metadata['resumes']):
                    if i < 3:  # Show first 3 candidates
                        print(f"    [{i+1}] {resume.get('applicant_name')} - {resume.get('applicant_email')}")
                        
                        # Check if this is RAJESH KUMAR SHARMA
                        if resume.get('applicant_name') == 'RAJESH KUMAR SHARMA':
                            print(f"    🎯 FOUND RAJESH at index {i+1} in ticket {ticket_id}")
                            
        except Exception as e:
            print(f"  ❌ Error reading {metadata_path}: {e}")

def check_mysql_database():
    print("\n🗄️ Checking MySQL database...")
    
    try:
        # Try to connect to MySQL (you might need to adjust connection details)
        import mysql.connector
        
        # This is a placeholder - you'll need to adjust the connection details
        print("  ⚠️ MySQL connection details needed - please check your database config")
        
    except ImportError:
        print("  ⚠️ mysql-connector-python not installed")
    except Exception as e:
        print(f"  ❌ MySQL connection error: {e}")

def check_sqlite_database():
    print("\n🗄️ Checking SQLite database...")
    
    sqlite_path = "Backend/interview_system.db"
    if os.path.exists(sqlite_path):
        try:
            conn = sqlite3.connect(sqlite_path)
            cursor = conn.cursor()
            
            # Check candidate_interview_status table
            cursor.execute("SELECT * FROM candidate_interview_status LIMIT 5")
            rows = cursor.fetchall()
            
            print(f"  candidate_interview_status table has {len(rows)} records (showing first 5):")
            for row in rows:
                print(f"    {row}")
                
            conn.close()
            
        except Exception as e:
            print(f"  ❌ SQLite error: {e}")
    else:
        print(f"  ⚠️ SQLite database not found at {sqlite_path}")

if __name__ == "__main__":
    check_database()
    check_sqlite_database()
    check_mysql_database()
