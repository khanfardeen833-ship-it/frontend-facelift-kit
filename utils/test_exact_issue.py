#!/usr/bin/env python3
"""
Test the exact issue with candidate ID mapping
"""
import requests
import json

def test_exact_issue():
    print("🔍 Testing exact candidate ID mapping issue...")
    
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
            
            # Store the correct candidate info
            correct_candidate = {
                'id': candidate.get('id'),
                'name': candidate.get('applicant_name'),
                'email': candidate.get('applicant_email')
            }
        else:
            print(f"   ❌ Failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
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
            updated_id = details.get('actual_candidate_id')
            print(f"   Updated candidate ID: {updated_id}")
            print(f"   Rows affected: {details.get('rows_affected')}")
            
            # Check if the IDs match
            if updated_id == correct_candidate['id']:
                print("   ✅ UPDATE and FETCH are using the same candidate ID!")
            else:
                print(f"   ❌ MISMATCH: UPDATE used ID {updated_id}, but FETCH returned ID {correct_candidate['id']}")
                print(f"   ❌ UPDATE is updating the wrong candidate!")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Check all candidates for this ticket to see the correct mapping
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
                
                # Check if this is the candidate we're looking for
                if candidate.get('id') == correct_candidate['id']:
                    print(f"         ✅ This is the correct candidate for frontend ID {candidate_id}")
                elif i + 1 == candidate_id:
                    print(f"         ❌ This should be the candidate for frontend ID {candidate_id}, but it's wrong!")
        else:
            print(f"   ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_exact_issue()
