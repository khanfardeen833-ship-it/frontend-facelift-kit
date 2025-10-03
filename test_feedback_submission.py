#!/usr/bin/env python3
"""
Test script to verify manager feedback API endpoint
"""

import requests
import json

def test_manager_feedback_api():
    """Test the manager feedback API endpoint"""
    
    # Test data
    test_data = {
        "interview_id": "test-123",
        "candidate_id": "50",
        "candidate_name": "Fardeen Khan",
        "candidate_email": "khanfardeen833@gmail.com",
        "job_title": "gcp engineer",
        "round_name": "HR Final Round",
        "overall_rating": 4,
        "decision": "hire",
        "technical_skills": 4,
        "communication_skills": 4,
        "problem_solving": 4,
        "cultural_fit": 4,
        "strengths": "Good technical skills and communication",
        "areas_for_improvement": "Could improve in some areas",
        "detailed_feedback": "Overall good candidate",
        "recommendation": "Recommend for hire",
        "submitted_by": "Test Manager"
    }
    
    # Test the endpoint
    url = "http://localhost:5000/api/manager-feedback"
    headers = {
        'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
        'Content-Type': 'application/json'
    }
    
    try:
        print("Testing manager feedback API endpoint...")
        print(f"URL: {url}")
        print(f"Data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(url, json=test_data, headers=headers)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"Response Data: {json.dumps(response_data, indent=2)}")
        except:
            print(f"Response Text: {response.text}")
            
        if response.status_code == 200:
            print("✅ API endpoint is working correctly!")
        else:
            print("❌ API endpoint returned an error")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure the backend server is running on port 5000")
    except Exception as e:
        print(f"❌ Error testing API: {e}")

if __name__ == "__main__":
    test_manager_feedback_api()
