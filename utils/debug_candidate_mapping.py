#!/usr/bin/env python3
"""
Debug script to understand candidate ID mapping issue
"""
import requests
import json

def debug_candidate_mapping():
    print("🔍 Debugging Candidate ID Mapping Issue...")
    
    headers = {
        'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
        'Content-Type': 'application/json'
    }
    
    # Test with candidate ID 3 and ticket c8c0c0d23e
    candidate_id = 3
    ticket_id = "c8c0c0d23e"
    
    print(f"\n📊 Testing candidate ID {candidate_id} in ticket {ticket_id}")
    
    # 1. Check what the fetch operation returns
    print("\n1️⃣ FETCH operation:")
    try:
        response = requests.get(
            f"http://localhost:5000/api/interviews/candidate/{candidate_id}?ticket_id={ticket_id}",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            candidate = data.get('data', {}).get('candidate', {})
            print(f"   Database ID: {candidate.get('id')}")
            print(f"   Name: {candidate.get('applicant_name')}")
            print(f"   Email: {candidate.get('applicant_email')}")
            print(f"   Final Decision: {candidate.get('final_decision')}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. Check what the update operation would find
    print("\n2️⃣ UPDATE operation simulation:")
    try:
        response = requests.put(
            "http://localhost:5000/api/candidates/status",
            headers=headers,
            json={
                "candidate_id": candidate_id,
                "ticket_id": ticket_id,
                "overall_status": "hired",
                "final_decision": "hire"
            }
        )
        if response.status_code == 200:
            data = response.json()
            details = data.get('details', {})
            print(f"   Updated candidate ID: {details.get('actual_candidate_id')}")
            print(f"   Rows affected: {details.get('rows_affected')}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Check all candidates for this ticket
    print("\n3️⃣ All candidates for this ticket:")
    try:
        response = requests.get(
            f"http://localhost:5000/api/interviews/candidates/{ticket_id}",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            candidates = data.get('data', {}).get('candidates', [])
            print(f"   Found {len(candidates)} candidates:")
            for i, candidate in enumerate(candidates):
                print(f"     [{i+1}] ID: {candidate.get('id')}, Name: {candidate.get('applicant_name')}, Email: {candidate.get('applicant_email')}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 4. Check if there are multiple records for the same email
    print("\n4️⃣ Checking for duplicate email records:")
    try:
        # Get the email from the fetch operation
        response = requests.get(
            f"http://localhost:5000/api/interviews/candidate/{candidate_id}?ticket_id={ticket_id}",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            candidate = data.get('data', {}).get('candidate', {})
            email = candidate.get('applicant_email')
            
            if email:
                print(f"   Checking for duplicates of email: {email}")
                # This would require a direct database query, but we can check by looking at all tickets
                print("   (Would need direct database access to check for cross-ticket duplicates)")
        else:
            print(f"   ❌ Failed to get candidate email: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    debug_candidate_mapping()
