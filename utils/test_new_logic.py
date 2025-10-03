#!/usr/bin/env python3
"""
Test if the new logic is being executed
"""
import requests
import json

def test_new_logic():
    print("🔍 Testing if the new logic is being executed...")
    
    headers = {
        'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
        'Content-Type': 'application/json'
    }
    
    # Test with candidate ID 3 and ticket c8c0c0d23e
    candidate_id = 3
    ticket_id = "c8c0c0d23e"
    
    print(f"\n📊 Testing candidate ID {candidate_id} in ticket {ticket_id}")
    
    # Make the UPDATE request and check the response
    print("\n🔄 Making UPDATE request...")
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
            print(f"✅ UPDATE successful: {data}")
            
            # Check the details
            details = data.get('details', {})
            print(f"   Updated candidate ID: {details.get('actual_candidate_id')}")
            print(f"   Rows affected: {details.get('rows_affected')}")
            
            # Check if the candidate ID is correct
            if details.get('actual_candidate_id') == 49:
                print("   ✅ SUCCESS: UPDATE is now using the correct candidate ID!")
            else:
                print(f"   ❌ FAILED: UPDATE is still using wrong candidate ID {details.get('actual_candidate_id')} instead of 49")
        else:
            print(f"❌ UPDATE failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n📋 Check the backend server logs to see if the new logic was executed!")

if __name__ == "__main__":
    test_new_logic()
