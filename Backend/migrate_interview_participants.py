#!/usr/bin/env python3
"""
Migration script to add interviewer_name column to interview_participants table
"""

import mysql.connector
import os
from pathlib import Path

def migrate_interview_participants():
    """Add interviewer_name column to interview_participants table if it doesn't exist"""
    try:
        # Database configuration - you can modify these values as needed
        db_config = {
            'host': os.getenv("MYSQL_HOST", "localhost"),
            'user': os.getenv("MYSQL_USER", "root"),
            'password': os.getenv("MYSQL_PASSWORD", "root"),
            'database': os.getenv("MYSQL_DATABASE", "hiring_bot")
        }
        
        print(f"Connecting to database: {db_config['host']}/{db_config['database']}")
        
        # Connect to database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Check if interviewer_name column exists
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'interview_participants' 
            AND COLUMN_NAME = 'interviewer_name'
        """, (db_config['database'],))
        
        column_exists = cursor.fetchone()
        
        if not column_exists:
            print("Adding interviewer_name column to interview_participants table...")
            
            # Add the column
            cursor.execute("""
                ALTER TABLE interview_participants 
                ADD COLUMN interviewer_name VARCHAR(255) AFTER interviewer_id
            """)
            
            # Add index for the new column
            cursor.execute("""
                ALTER TABLE interview_participants 
                ADD INDEX idx_interviewer_name (interviewer_name)
            """)
            
            conn.commit()
            print("✅ Successfully added interviewer_name column and index")
        else:
            print("✅ interviewer_name column already exists")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        print("Please check your database connection settings and ensure the database is running.")
        print("You can set environment variables: MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Starting migration for interview_participants table...")
    success = migrate_interview_participants()
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed!")
        exit(1)
