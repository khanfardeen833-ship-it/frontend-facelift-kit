#!/usr/bin/env python3
"""
Initialize SQLite database for Interview Management System
Creates and populates interview_system.db with required tables
"""

import sqlite3
import json
from datetime import datetime, timedelta
import os

def create_database():
    """Create SQLite database with all required tables"""
    
    # Remove old empty database if exists
    if os.path.exists('interview_system.db') and os.path.getsize('interview_system.db') == 0:
        os.remove('interview_system.db')
        print("Removed empty database file")
    
    conn = sqlite3.connect('interview_system.db')
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Create tables
    tables = [
        # Interview rounds table
        """
        CREATE TABLE IF NOT EXISTS interview_rounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT NOT NULL,
            round_name TEXT NOT NULL,
            round_order INTEGER NOT NULL,
            interview_type TEXT NOT NULL,
            duration_minutes INTEGER DEFAULT 60,
            description TEXT,
            requirements TEXT,
            is_required INTEGER DEFAULT 1,
            can_skip INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """,
        
        # Interview schedules table  
        """
        CREATE TABLE IF NOT EXISTS interview_schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT NOT NULL,
            round_id INTEGER,
            candidate_id TEXT NOT NULL,
            candidate_name TEXT NOT NULL,
            candidate_email TEXT NOT NULL,
            scheduled_date DATE NOT NULL,
            scheduled_time TIME NOT NULL,
            duration_minutes INTEGER DEFAULT 60,
            interview_type TEXT DEFAULT 'video_call',
            meeting_link TEXT,
            location TEXT,
            status TEXT DEFAULT 'scheduled',
            notes TEXT,
            interviewer_names TEXT,
            created_by TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (round_id) REFERENCES interview_rounds(id)
        )
        """,
        
        # Interview feedback table
        """
        CREATE TABLE IF NOT EXISTS interview_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interview_id INTEGER NOT NULL,
            candidate_id TEXT NOT NULL,
            round_id INTEGER,
            overall_rating REAL,
            decision TEXT,
            notes TEXT,
            strengths TEXT,
            areas_of_improvement TEXT,
            submitted_by TEXT,
            submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (interview_id) REFERENCES interview_schedules(id),
            FOREIGN KEY (round_id) REFERENCES interview_rounds(id)
        )
        """,
        
        # Candidate interview status table
        """
        CREATE TABLE IF NOT EXISTS candidate_interview_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT NOT NULL,
            candidate_id TEXT NOT NULL,
            candidate_name TEXT NOT NULL,
            candidate_email TEXT NOT NULL,
            job_title TEXT,
            current_round_id INTEGER,
            interview_status TEXT DEFAULT 'not_started',
            rounds_completed INTEGER DEFAULT 0,
            total_rounds INTEGER DEFAULT 0,
            final_decision TEXT,
            decision_notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(ticket_id, candidate_id)
        )
        """
    ]
    
    # Create all tables
    for table_sql in tables:
        cursor.execute(table_sql)
    
    conn.commit()
    print("✅ Database tables created successfully")
    
    return conn

def insert_sample_data(conn):
    """Insert sample interview data including for Fardeen Khan"""
    cursor = conn.cursor()
    
    # Sample ticket ID
    ticket_id = "96842d6ce2_web-dev"
    
    # Insert interview rounds
    rounds_data = [
        (ticket_id, "HR Screening", 1, "hr_round", 30, "Initial HR screening and cultural fit assessment", None, 1, 0),
        (ticket_id, "Technical Round 1", 2, "technical_round", 60, "Technical skills assessment and coding challenge", "Laptop required", 1, 0),
        (ticket_id, "Technical Round 2", 3, "technical_round", 90, "System design and architecture discussion", None, 1, 0),
        (ticket_id, "HR Final Round", 4, "hr_final_round", 45, "Final HR discussion and offer negotiation", None, 1, 1)
    ]
    
    cursor.executemany("""
        INSERT INTO interview_rounds 
        (ticket_id, round_name, round_order, interview_type, duration_minutes, description, requirements, is_required, can_skip)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rounds_data)
    
    # Get inserted round IDs
    cursor.execute("SELECT id, round_name FROM interview_rounds WHERE ticket_id = ?", (ticket_id,))
    rounds = {row[1]: row[0] for row in cursor.fetchall()}
    
    # Insert Fardeen Khan's interview schedule
    tomorrow = (datetime.now() + timedelta(days=1)).date()
    
    interview_data = [
        (ticket_id, rounds["HR Screening"], "candidate_001", "Fardeen Khan", "fardeen.khan@example.com",
         str(tomorrow), "10:00", 30, "video_call", "https://meet.google.com/abc-defg-hij",
         None, "scheduled", "Please be ready 5 minutes early", "Sarah Johnson", "hr@company.com"),
         
        (ticket_id, rounds["Technical Round 1"], "candidate_001", "Fardeen Khan", "fardeen.khan@example.com",
         str(tomorrow + timedelta(days=2)), "14:00", 60, "video_call", "https://meet.google.com/xyz-uvwx-rst",
         None, "scheduled", "Coding test will be conducted", "John Smith, Mike Wilson", "tech@company.com")
    ]
    
    cursor.executemany("""
        INSERT INTO interview_schedules
        (ticket_id, round_id, candidate_id, candidate_name, candidate_email,
         scheduled_date, scheduled_time, duration_minutes, interview_type, meeting_link,
         location, status, notes, interviewer_names, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, interview_data)
    
    # Insert candidate status for Fardeen Khan
    cursor.execute("""
        INSERT INTO candidate_interview_status
        (ticket_id, candidate_id, candidate_name, candidate_email, job_title,
         current_round_id, interview_status, rounds_completed, total_rounds)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (ticket_id, "candidate_001", "Fardeen Khan", "fardeen.khan@example.com",
          "Web Developer", rounds["HR Screening"], "in_progress", 0, 4))
    
    # Add more sample candidates
    other_candidates = [
        ("candidate_002", "Sarah Williams", "sarah.w@example.com"),
        ("candidate_003", "Michael Chen", "m.chen@example.com")
    ]
    
    for cand_id, name, email in other_candidates:
        cursor.execute("""
            INSERT INTO candidate_interview_status
            (ticket_id, candidate_id, candidate_name, candidate_email, job_title,
             interview_status, rounds_completed, total_rounds)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (ticket_id, cand_id, name, email, "Web Developer", "not_started", 0, 4))
    
    conn.commit()
    print("✅ Sample data inserted successfully")
    print(f"   - Created 4 interview rounds for ticket {ticket_id}")
    print(f"   - Scheduled 2 interviews for Fardeen Khan")
    print(f"   - Added 3 candidates to the system")

def verify_data(conn):
    """Verify the inserted data"""
    cursor = conn.cursor()
    
    print("\n📊 Database Verification:")
    print("=" * 50)
    
    # Check interview rounds
    cursor.execute("SELECT COUNT(*) FROM interview_rounds")
    rounds_count = cursor.fetchone()[0]
    print(f"Interview Rounds: {rounds_count}")
    
    # Check interview schedules
    cursor.execute("SELECT COUNT(*) FROM interview_schedules")
    schedules_count = cursor.fetchone()[0]
    print(f"Interview Schedules: {schedules_count}")
    
    # Check Fardeen Khan's interviews
    cursor.execute("""
        SELECT s.*, r.round_name 
        FROM interview_schedules s
        LEFT JOIN interview_rounds r ON s.round_id = r.id
        WHERE s.candidate_name LIKE '%Fardeen%Khan%'
    """)
    fardeen_interviews = cursor.fetchall()
    
    print(f"\n🎯 Fardeen Khan's Interviews:")
    for interview in fardeen_interviews:
        print(f"   - Round: {interview[-1]}")
        print(f"     Date: {interview[6]} at {interview[7]}")
        print(f"     Status: {interview[11]}")
        print(f"     Meeting Link: {interview[9]}")
    
    # Check candidate status
    cursor.execute("SELECT * FROM candidate_interview_status WHERE candidate_name LIKE '%Fardeen%'")
    status = cursor.fetchone()
    if status:
        print(f"\n📋 Fardeen Khan's Overall Status:")
        print(f"   - Interview Status: {status[7]}")
        print(f"   - Rounds Completed: {status[8]}/{status[9]}")
    
    print("=" * 50)

def main():
    print("🚀 Initializing Interview System Database")
    print("=" * 50)
    
    try:
        # Create database and tables
        conn = create_database()
        
        # Insert sample data
        insert_sample_data(conn)
        
        # Verify data
        verify_data(conn)
        
        conn.close()
        
        print("\n✅ Database initialization complete!")
        print("\n📝 Next Steps:")
        print("1. The interview_system.db file has been created")
        print("2. Fardeen Khan's interviews are now in the database")
        print("3. You should be able to see them in the View Status page")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)