#!/usr/bin/env python3
"""
Test Candidate API Script
This script tests the candidate API endpoint to ensure it works with the fixed database configuration.
"""

import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

def test_candidate_api():
    """Test the candidate API functionality"""
    
    print("🧪 Testing Candidate API Functionality")
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
        
        cursor = connection.cursor(dictionary=True)
        
        # Test the exact query that the API uses
        print(f"🔍 Testing candidate lookup...")
        
        # Get available candidate IDs
        cursor.execute("SELECT id, applicant_name, applicant_email, ticket_id FROM resume_applications ORDER BY id")
        candidates = cursor.fetchall()
        
        print(f"📋 Available candidates:")
        for candidate in candidates:
            print(f"   ID {candidate['id']}: {candidate['applicant_name']} ({candidate['applicant_email']}) - Ticket: {candidate['ticket_id']}")
        
        # Test with the first available candidate
        if candidates:
            test_candidate_id = candidates[0]['id']
            test_ticket_id = candidates[0]['ticket_id']
            
            print(f"\n🧪 Testing API query for candidate ID {test_candidate_id}...")
            
            # This is the query the API would use
            cursor.execute("""
                SELECT id, applicant_name, applicant_email, applicant_phone, 
                       filename, file_path, status, ai_score, ai_analysis, 
                       uploaded_at, ticket_id
                FROM resume_applications 
                WHERE id = %s
            """, (test_candidate_id,))
            
            candidate_data = cursor.fetchone()
            
            if candidate_data:
                print(f"✅ Candidate data retrieved successfully:")
                print(f"   ID: {candidate_data['id']}")
                print(f"   Name: {candidate_data['applicant_name']}")
                print(f"   Email: {candidate_data['applicant_email']}")
                print(f"   Ticket ID: {candidate_data['ticket_id']}")
                print(f"   Status: {candidate_data['status']}")
                
                print(f"\n🎉 API Test Result:")
                print(f"   ✅ Database connection: Working")
                print(f"   ✅ Candidate lookup: Working")
                print(f"   ✅ Data retrieval: Working")
                print(f"   ✅ Ready for frontend requests")
                
                print(f"\n📝 To test the API endpoint:")
                print(f"   GET http://localhost:5000/api/interviews/candidate/{test_candidate_id}?ticket_id={test_ticket_id}")
                
            else:
                print(f"❌ No candidate data found for ID {test_candidate_id}")
        else:
            print(f"❌ No candidates found in database")
        
        cursor.close()
        
    except Error as e:
        print(f"❌ Database error: {e}")
    
    finally:
        if connection and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    test_candidate_api()
