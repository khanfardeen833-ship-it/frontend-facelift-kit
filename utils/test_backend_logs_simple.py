#!/usr/bin/env python3
"""
Test backend logs to see what's happening with the UPDATE operation
"""
import requests
import json

def test_backend_logs():
    print("🔍 Testing backend logs for UPDATE operation...")
    
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
        else:
            print(f"❌ UPDATE failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n📋 Check the backend server logs to see what happened!")

if __name__ == "__main__":
    test_backend_logs()
