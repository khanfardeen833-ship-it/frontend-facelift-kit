#!/usr/bin/env python3
"""
Check MySQL database for duplicate candidate records
"""
import requests
import json

def check_candidate_records():
    print("🔍 Checking for duplicate candidate records in database...")
    
    # Test the candidate fetch with different approaches
    headers = {
        'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
        'Content-Type': 'application/json'
    }
    
    # Test 1: Fetch by candidate ID 2
    print("\n📊 Test 1: Fetching candidate ID 2")
    try:
        response = requests.get(
            "http://localhost:5000/api/interviews/candidate/2?ticket_id=c8c0c0d23e",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            candidate = data.get('data', {}).get('candidate', {})
            print(f"  Database ID: {candidate.get('id')}")
            print(f"  Name: {candidate.get('applicant_name')}")
            print(f"  Email: {candidate.get('applicant_email')}")
            print(f"  Final Decision: {candidate.get('final_decision')}")
            print(f"  Interview Status: {candidate.get('interview_status')}")
        else:
            print(f"  ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test 2: Check if there are multiple records for the same email
    print("\n📊 Test 2: Checking for multiple records...")
    
    # Let's also test the update again to see the actual candidate ID being updated
    print("\n📊 Test 3: Testing update again...")
    update_data = {
        "candidate_id": 2,
        "ticket_id": "c8c0c0d23e",
        "overall_status": "hired",
        "final_decision": "hire"
    }
    
    try:
        response = requests.put(
            "http://localhost:5000/api/candidates/status",
            headers=headers,
            json=update_data
        )
        if response.status_code == 200:
            data = response.json()
            details = data.get('details', {})
            print(f"  Updated candidate ID: {details.get('actual_candidate_id')}")
            print(f"  Rows affected: {details.get('rows_affected')}")
        else:
            print(f"  ❌ Update failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    check_candidate_records()
