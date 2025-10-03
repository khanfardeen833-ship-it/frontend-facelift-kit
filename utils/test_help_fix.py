#!/usr/bin/env python3
"""
Test script to verify that the help functionality works correctly
when a user is in the middle of a job posting conversation.
"""

import requests
import json
import time

# Test configuration
BASE_URL = "http://localhost:5000"
API_KEY = "sk-hiring-bot-2024-secret-key-xyz789"

def test_help_during_job_posting():
    """Test that help requests properly interrupt job posting flow"""
    
    print("🧪 Testing Help Functionality During Job Posting...")
    print("=" * 60)
    
    # Step 1: Start a chat session
    print("1. Starting chat session...")
    start_response = requests.post(
        f"{BASE_URL}/api/chat/start",
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
        json={"user_id": "test_user_123"}
    )
    
    if start_response.status_code != 200:
        print(f"❌ Failed to start chat: {start_response.text}")
        return False
    
    session_data = start_response.json()
    session_id = session_data["session_id"]
    user_id = session_data["user_id"]
    
    print(f"✅ Chat started - Session ID: {session_id}")
    
    # Step 2: Start a job posting conversation
    print("\n2. Starting job posting conversation...")
    job_response = requests.post(
        f"{BASE_URL}/api/chat/message",
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
        json={
            "session_id": session_id,
            "user_id": user_id,
            "message": "I want to post a job"
        }
    )
    
    if job_response.status_code != 200:
        print(f"❌ Failed to start job posting: {job_response.text}")
        return False
    
    job_data = job_response.json()
    print(f"✅ Job posting started - Response: {job_data['response'][:100]}...")
    
    # Step 3: Provide some job details to establish context
    print("\n3. Providing job details to establish hiring context...")
    details_response = requests.post(
        f"{BASE_URL}/api/chat/message",
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
        json={
            "session_id": session_id,
            "user_id": user_id,
            "message": "Software Engineer position"
        }
    )
    
    if details_response.status_code != 200:
        print(f"❌ Failed to provide job details: {details_response.text}")
        return False
    
    details_data = details_response.json()
    print(f"✅ Job details provided - Response: {details_data['response'][:100]}...")
    
    # Step 4: Request help (this should interrupt the job posting flow)
    print("\n4. Requesting help (should interrupt job posting flow)...")
    help_response = requests.post(
        f"{BASE_URL}/api/chat/message",
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
        json={
            "session_id": session_id,
            "user_id": user_id,
            "message": "I need help"
        }
    )
    
    if help_response.status_code != 200:
        print(f"❌ Failed to request help: {help_response.text}")
        return False
    
    help_data = help_response.json()
    help_message = help_data['response']
    
    # Check if the response is a help response (not a job posting question)
    is_help_response = any(keyword in help_message.lower() for keyword in [
        'welcome to your premium ai hiring assistant',
        'what i can do',
        'job management',
        'strategic hiring support'
    ])
    
    if is_help_response:
        print("✅ Help request properly handled!")
        print(f"   Response contains help content: {help_message[:100]}...")
    else:
        print("❌ Help request not properly handled!")
        print(f"   Response: {help_message}")
        return False
    
    # Step 5: Verify that the next message is not treated as job posting
    print("\n5. Testing that next message is not treated as job posting...")
    test_response = requests.post(
        f"{BASE_URL}/api/chat/message",
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
        json={
            "session_id": session_id,
            "user_id": user_id,
            "message": "What can you do?"
        }
    )
    
    if test_response.status_code != 200:
        print(f"❌ Failed to send test message: {test_response.text}")
        return False
    
    test_data = test_response.json()
    test_message = test_data['response']
    
    # Check if this is still being treated as a job posting question
    is_job_posting_question = any(keyword in test_message.lower() for keyword in [
        'what position',
        'where will this position',
        'how many years of experience',
        'what is the salary',
        'what skills are required'
    ])
    
    if is_job_posting_question:
        print("❌ Context not properly cleared - still asking job posting questions!")
        print(f"   Response: {test_message}")
        return False
    else:
        print("✅ Context properly cleared - no longer in job posting mode!")
        print(f"   Response: {test_message[:100]}...")
    
    print("\n" + "=" * 60)
    print("🎉 All tests passed! Help functionality is working correctly.")
    return True

if __name__ == "__main__":
    try:
        success = test_help_during_job_posting()
        if success:
            print("\n✅ Test completed successfully!")
        else:
            print("\n❌ Test failed!")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
