#!/usr/bin/env python3
"""
Test script to debug candidate status update issue
"""
import requests
import json

# Test the candidate status update API
def test_candidate_update():
    url = "http://localhost:5000/api/candidates/status"
    headers = {
        'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
        'Content-Type': 'application/json'
    }
    
    # Test data matching the frontend request
    data = {
        "candidate_id": 2,
        "ticket_id": "c8c0c0d23e",
        "overall_status": "hired",
        "final_decision": "hire"
    }
    
    print("🔄 Testing candidate status update...")
    print(f"Request URL: {url}")
    print(f"Request data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.put(url, headers=headers, json=data)
        print(f"Response status: {response.status_code}")
        print(f"Response data: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("\n✅ Update successful! Now testing fetch...")
            test_candidate_fetch()
        else:
            print(f"\n❌ Update failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_candidate_fetch():
    url = "http://localhost:5000/api/interviews/candidate/2?ticket_id=c8c0c0d23e"
    headers = {
        'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
        'Content-Type': 'application/json'
    }
    
    print(f"\n🔄 Testing candidate fetch...")
    print(f"Request URL: {url}")
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response data: {json.dumps(data, indent=2)}")
            
            if data.get('success') and data.get('data', {}).get('candidate'):
                candidate = data['data']['candidate']
                print(f"\n📊 Candidate final_decision: {candidate.get('final_decision')}")
                print(f"📊 Candidate interview_status: {candidate.get('interview_status')}")
            else:
                print("❌ No candidate data in response")
        else:
            print(f"❌ Fetch failed with status {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_candidate_update()
