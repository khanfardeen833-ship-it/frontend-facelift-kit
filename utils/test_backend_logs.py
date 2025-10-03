#!/usr/bin/env python3
"""
Simple test to trigger backend debugging logs
"""
import requests
import json

def test_backend_logs():
    print("🔍 Testing backend to see debugging logs...")
    
    headers = {
        'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
        'Content-Type': 'application/json'
    }
    
    # Test 1: Update operation
    print("\n1️⃣ Testing UPDATE operation...")
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
        print(f"   Update response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Updated candidate ID: {data.get('details', {}).get('actual_candidate_id')}")
    except Exception as e:
        print(f"   ❌ Update error: {e}")
    
    # Test 2: Fetch operation
    print("\n2️⃣ Testing FETCH operation...")
    try:
        response = requests.get(
            "http://localhost:5000/api/interviews/candidate/2?ticket_id=c8c0c0d23e",
            headers=headers
        )
        print(f"   Fetch response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            candidate = data.get('data', {}).get('candidate', {})
            print(f"   Fetched candidate ID: {candidate.get('id')}")
            print(f"   Final decision: {candidate.get('final_decision')}")
    except Exception as e:
        print(f"   ❌ Fetch error: {e}")

if __name__ == "__main__":
    test_backend_logs()
