#!/usr/bin/env python3
"""
Check for duplicate candidate records in the database
"""
import requests
import json

def check_duplicate_records():
    print("🔍 Checking for duplicate candidate records...")
    
    headers = {
        'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
        'Content-Type': 'application/json'
    }
    
    # Test multiple approaches to see if we can find the same candidate with different IDs
    print("\n📊 Testing different candidate fetch approaches...")
    
    # Approach 1: Fetch by candidate ID 2 (current approach)
    print("\n1️⃣ Fetching by candidate ID 2:")
    try:
        response = requests.get(
            "http://localhost:5000/api/interviews/candidate/2?ticket_id=c8c0c0d23e",
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
    
    # Approach 2: Try to find all candidates with the same email
    print("\n2️⃣ Checking if there are multiple records for the same email...")
    
    # Let's try to get all candidates for the ticket to see if there are duplicates
    try:
        response = requests.get(
            "http://localhost:5000/api/interviews/candidates/c8c0c0d23e",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            candidates = data.get('data', {}).get('candidates', [])
            print(f"   Found {len(candidates)} candidates for ticket c8c0c0d23e")
            
            # Look for RAJESH KUMAR SHARMA
            rajesh_candidates = [c for c in candidates if c.get('applicant_name') == 'RAJESH KUMAR SHARMA']
            print(f"   Found {len(rajesh_candidates)} records for RAJESH KUMAR SHARMA:")
            for i, candidate in enumerate(rajesh_candidates):
                print(f"     [{i+1}] ID: {candidate.get('id')}, Email: {candidate.get('applicant_email')}, Final Decision: {candidate.get('final_decision')}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Approach 3: Test update and then immediate fetch
    print("\n3️⃣ Testing update then immediate fetch...")
    
    # First, update candidate ID 2
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
            updated_id = details.get('actual_candidate_id')
            print(f"   Updated candidate ID: {updated_id}")
            
            # Now immediately fetch candidate ID 2
            response = requests.get(
                "http://localhost:5000/api/interviews/candidate/2?ticket_id=c8c0c0d23e",
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                candidate = data.get('data', {}).get('candidate', {})
                fetched_id = candidate.get('id')
                print(f"   Fetched candidate ID: {fetched_id}")
                print(f"   Final Decision: {candidate.get('final_decision')}")
                
                if updated_id == fetched_id:
                    print("   ✅ Update and fetch are using the same candidate ID!")
                else:
                    print(f"   ❌ MISMATCH: Update used ID {updated_id}, but fetch returned ID {fetched_id}")
            else:
                print(f"   ❌ Fetch failed: {response.status_code}")
        else:
            print(f"   ❌ Update failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    check_duplicate_records()
