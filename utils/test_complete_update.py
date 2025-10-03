#!/usr/bin/env python3
"""
Comprehensive test for the update functionality
"""

import requests
import json

# Test configuration
BASE_URL = "http://localhost:5000"
API_KEY = "sk-hiring-bot-2024-secret-key-xyz789"

def test_complete_update_flow():
    """Test the complete update flow"""
    
    print("🧪 Testing Complete Update Flow...")
    print("=" * 60)
    
    # Start a chat session
    start_response = requests.post(
        f"{BASE_URL}/api/chat/start",
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
        json={"user_id": "test_update_user_123"}
    )
    
    session_data = start_response.json()
    session_id = session_data["session_id"]
    user_id = session_data["user_id"]
    
    print(f"Session ID: {session_id}")
    
    # Step 1: Start update request
    print("\n1. Starting update request...")
    update_start_response = requests.post(
        f"{BASE_URL}/api/chat/message",
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
        json={
            "session_id": session_id,
            "user_id": user_id,
            "message": "i want to update Ticket: fc74b73c7f"
        }
    )
    
    if update_start_response.status_code != 200:
        print(f"❌ Failed to start update: {update_start_response.text}")
        return False
    
    update_start_data = update_start_response.json()
    print(f"✅ Update started: {update_start_data['response'][:100]}...")
    
    # Step 2: Provide update details
    print("\n2. Providing update details...")
    update_details_response = requests.post(
        f"{BASE_URL}/api/chat/message",
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
        json={
            "session_id": session_id,
            "user_id": user_id,
            "message": "update Salary: 20 to 50 K"
        }
    )
    
    if update_details_response.status_code != 200:
        print(f"❌ Failed to provide update details: {update_details_response.text}")
        return False
    
    update_details_data = update_details_response.json()
    print(f"Update response: {update_details_data['response']}")
    print(f"Update metadata: {update_details_data.get('metadata', {})}")
    
    # Check if the update was successful
    is_success = any(keyword in update_details_data['response'].lower() for keyword in [
        'successfully updated',
        'updated fields',
        'updated ticket'
    ])
    
    if is_success:
        print("✅ Update functionality is working correctly!")
        return True
    else:
        print("❌ Update functionality is not working properly")
        print(f"   Response: {update_details_data['response']}")
        return False

if __name__ == "__main__":
    try:
        success = test_complete_update_flow()
        if success:
            print("\n🎉 All tests passed! Update functionality is working correctly.")
        else:
            print("\n❌ Test failed!")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
