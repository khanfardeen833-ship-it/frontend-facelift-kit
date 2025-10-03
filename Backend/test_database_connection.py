#!/usr/bin/env python3
"""
Database Connection Test Script
This script tests the MySQL database connection to help troubleshoot connection issues.
"""

import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

def test_database_connection():
    """Test MySQL database connection"""
    
    print("🔍 Testing MySQL Database Connection")
    print("=" * 50)
    
    # Get database configuration
    host = os.getenv('MYSQL_HOST', 'localhost')
    user = os.getenv('MYSQL_USER', 'root')
    password = os.getenv('MYSQL_PASSWORD', '')
    database = os.getenv('MYSQL_DATABASE', 'hiring_bot')
    
    print(f"📊 Database Configuration:")
    print(f"   Host: {host}")
    print(f"   User: {user}")
    print(f"   Password: {'*' * len(password) if password else '(empty)'}")
    print(f"   Database: {database}")
    
    connection = None
    
    try:
        # Test connection without database first
        print(f"\n🔌 Testing connection to MySQL server...")
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        
        if connection.is_connected():
            print(f"✅ Successfully connected to MySQL server!")
            
            # Get server info
            db_info = connection.get_server_info()
            print(f"   MySQL Server version: {db_info}")
            
            # Test database selection
            print(f"\n📁 Testing database selection...")
            cursor = connection.cursor()
            cursor.execute(f"USE {database}")
            print(f"✅ Successfully selected database: {database}")
            
            # Test table existence
            print(f"\n📋 Testing table existence...")
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            if tables:
                print(f"✅ Found {len(tables)} tables:")
                for table in tables:
                    print(f"   - {table[0]}")
                
                # Test resume_applications table specifically
                if any('resume_applications' in table for table in tables):
                    print(f"\n👤 Testing resume_applications table...")
                    cursor.execute("SELECT COUNT(*) FROM resume_applications")
                    count = cursor.fetchone()[0]
                    print(f"✅ resume_applications table has {count} records")
                    
                    # Test candidate ID 2 specifically
                    cursor.execute("SELECT id, name, email FROM resume_applications WHERE id = 2")
                    candidate = cursor.fetchone()
                    
                    if candidate:
                        print(f"✅ Candidate ID 2 found: {candidate[1]} ({candidate[2]})")
                    else:
                        print(f"❌ Candidate ID 2 not found in database")
                        print(f"   Available candidate IDs:")
                        cursor.execute("SELECT id, name FROM resume_applications LIMIT 5")
                        candidates = cursor.fetchall()
                        for cand in candidates:
                            print(f"   - ID {cand[0]}: {cand[1]}")
                else:
                    print(f"❌ resume_applications table not found")
            else:
                print(f"❌ No tables found in database")
            
            cursor.close()
            
    except Error as e:
        print(f"❌ Database connection error: {e}")
        
        # Provide specific solutions based on error
        if "Access denied" in str(e):
            print(f"\n🔧 Solutions for Access Denied Error:")
            print(f"1. Check MySQL password in config.env")
            print(f"2. Try empty password: MYSQL_PASSWORD=")
            print(f"3. Or set correct password: MYSQL_PASSWORD=your_actual_password")
            print(f"4. Make sure MySQL is running")
            print(f"5. Check if user 'root' exists and has permissions")
        elif "Can't connect" in str(e):
            print(f"\n🔧 Solutions for Connection Error:")
            print(f"1. Make sure MySQL server is running")
            print(f"2. Check if MySQL is installed")
            print(f"3. Try starting MySQL service")
        elif "Unknown database" in str(e):
            print(f"\n🔧 Solutions for Unknown Database:")
            print(f"1. Create the database: CREATE DATABASE {database};")
            print(f"2. Or change database name in config.env")
    
    finally:
        if connection and connection.is_connected():
            connection.close()
            print(f"\n🔒 Database connection closed")

def show_mysql_setup_help():
    """Show MySQL setup help"""
    
    print(f"\n📚 MySQL Setup Help:")
    print(f"=" * 30)
    
    print(f"\n🔧 If MySQL is not installed:")
    print(f"1. Download MySQL from: https://dev.mysql.com/downloads/")
    print(f"2. Install MySQL Server")
    print(f"3. Set root password during installation")
    print(f"4. Update MYSQL_PASSWORD in config.env")
    
    print(f"\n🔧 If MySQL is installed but not running:")
    print(f"1. Start MySQL service:")
    print(f"   - Windows: Services > MySQL > Start")
    print(f"   - Or: net start mysql")
    print(f"2. Or: mysqld --console")
    
    print(f"\n🔧 If you forgot the root password:")
    print(f"1. Stop MySQL service")
    print(f"2. Start MySQL in safe mode: mysqld --skip-grant-tables")
    print(f"3. Connect: mysql -u root")
    print(f"4. Reset password: ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';")
    print(f"5. Restart MySQL normally")
    
    print(f"\n🔧 Quick test without password:")
    print(f"1. Set MYSQL_PASSWORD= in config.env")
    print(f"2. Restart the server")
    print(f"3. This works if MySQL was installed without a password")

if __name__ == "__main__":
    test_database_connection()
    show_mysql_setup_help()
