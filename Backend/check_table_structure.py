#!/usr/bin/env python3
"""
Check Table Structure Script
This script checks the actual structure of the resume_applications table.
"""

import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

def check_table_structure():
    """Check the structure of resume_applications table"""
    
    print("🔍 Checking resume_applications Table Structure")
    print("=" * 50)
    
    # Get database configuration
    host = os.getenv('MYSQL_HOST', 'localhost')
    user = os.getenv('MYSQL_USER', 'root')
    password = os.getenv('MYSQL_PASSWORD', '')
    database = os.getenv('MYSQL_DATABASE', 'hiring_bot')
    
    connection = None
    
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        
        cursor = connection.cursor()
        
        # Check table structure
        print(f"📋 Table Structure:")
        cursor.execute("DESCRIBE resume_applications")
        columns = cursor.fetchall()
        
        print(f"   Columns in resume_applications table:")
        for column in columns:
            print(f"   - {column[0]} ({column[1]})")
        
        # Check actual data
        print(f"\n📊 Sample Data:")
        cursor.execute("SELECT * FROM resume_applications LIMIT 3")
        rows = cursor.fetchall()
        
        if rows:
            print(f"   Found {len(rows)} sample records:")
            for i, row in enumerate(rows, 1):
                print(f"   Record {i}: {row}")
        else:
            print(f"   No data found in table")
        
        # Check candidate ID 2 specifically
        print(f"\n👤 Checking Candidate ID 2:")
        cursor.execute("SELECT * FROM resume_applications WHERE id = 2")
        candidate = cursor.fetchone()
        
        if candidate:
            print(f"✅ Candidate ID 2 found:")
            # Get column names
            cursor.execute("SHOW COLUMNS FROM resume_applications")
            column_names = [row[0] for row in cursor.fetchall()]
            
            for i, value in enumerate(candidate):
                if i < len(column_names):
                    print(f"   {column_names[i]}: {value}")
        else:
            print(f"❌ Candidate ID 2 not found")
            
            # Show available IDs
            cursor.execute("SELECT id FROM resume_applications ORDER BY id")
            ids = cursor.fetchall()
            if ids:
                print(f"   Available candidate IDs: {[id[0] for id in ids]}")
        
        cursor.close()
        
    except Error as e:
        print(f"❌ Error: {e}")
    
    finally:
        if connection and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    check_table_structure()
