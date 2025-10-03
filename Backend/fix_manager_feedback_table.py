#!/usr/bin/env python3
"""
Fix Manager Feedback Table
Drops and recreates the manager_feedback table with correct schema
"""

import sqlite3
import os

def fix_manager_feedback_table():
    """Fix the manager_feedback table schema"""
    
    db_path = os.path.join(os.path.dirname(__file__), 'interview_system.db')
    print(f"Database path: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Drop the existing table if it exists
        print("Dropping existing manager_feedback table...")
        cursor.execute("DROP TABLE IF EXISTS manager_feedback")
        
        # Create the new table with correct schema
        print("Creating new manager_feedback table...")
        cursor.execute("""
            CREATE TABLE manager_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interview_id INTEGER,
                candidate_id TEXT,
                candidate_name TEXT,
                candidate_email TEXT,
                job_title TEXT,
                round_name TEXT,
                
                -- Overall Assessment
                overall_rating INTEGER,
                decision TEXT,
                
                -- Detailed Ratings
                technical_skills INTEGER,
                communication_skills INTEGER,
                problem_solving INTEGER,
                cultural_fit INTEGER,
                leadership_potential INTEGER,
                
                -- Feedback Text
                strengths TEXT,
                areas_for_improvement TEXT,
                detailed_feedback TEXT,
                recommendation TEXT,
                
                -- Additional Info
                would_hire_again BOOLEAN,
                team_fit TEXT,
                salary_expectation TEXT,
                start_date TEXT,
                
                -- Metadata
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                submitted_by TEXT,
                feedback_token TEXT UNIQUE
            )
        """)
        
        conn.commit()
        print("✅ Manager feedback table created successfully!")
        
        # Verify the table structure
        cursor.execute("PRAGMA table_info(manager_feedback)")
        columns = cursor.fetchall()
        print("\n📋 Table structure:")
        for column in columns:
            print(f"  - {column[1]} ({column[2]})")
        
        conn.close()
        print("\n🎉 Database fix completed successfully!")
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")

if __name__ == "__main__":
    fix_manager_feedback_table()
