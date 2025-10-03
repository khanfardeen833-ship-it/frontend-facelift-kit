#!/usr/bin/env python3
"""
Test the updated calendar API that connects to MySQL
"""

import requests
import json

def test_mysql_calendar_api():
    """Test the updated calendar API"""
    
    try:
        print("🧪 Testing Updated Calendar API (MySQL)...")
        
        response = requests.get("http://localhost:5000/api/interviews/calendar", headers={
            'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
            'Content-Type': 'application/json'
        })
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Response:")
            print(json.dumps(data, indent=2))
            
            if data.get('success'):
                events = data.get('events', [])
                print(f"\n📅 Found {len(events)} interview events from MySQL")
                
                # Look for Shubham's interviews
                shubham_interviews = [event for event in events if 'shubham' in event.get('candidate_name', '').lower()]
                
                if shubham_interviews:
                    print(f"\n🎯 Found {len(shubham_interviews)} interviews for Shubham:")
                    for interview in shubham_interviews:
                        print(f"  - {interview.get('candidate_name')} - {interview.get('round_name')}")
                        print(f"    Date: {interview.get('start')}")
                        print(f"    Duration: {interview.get('duration')} minutes")
                        print(f"    Status: {interview.get('status')}")
                        print(f"    Job: {interview.get('job_title')}")
                        print()
                else:
                    print("\n❌ No interviews found for Shubham")
                
                # Show all interviews
                for i, event in enumerate(events[:5]):  # Show first 5 events
                    print(f"\nEvent {i+1}:")
                    print(f"  - Candidate: {event.get('candidate_name')}")
                    print(f"  - Round: {event.get('round_name')}")
                    print(f"  - Date: {event.get('start')}")
                    print(f"  - Duration: {event.get('duration')} minutes")
                    print(f"  - Type: {event.get('interview_type')}")
                    print(f"  - Job: {event.get('job_title')}")
            else:
                print("❌ API returned success=False")
                print(f"Error: {data.get('error')}")
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API server")
        print("Make sure the backend server is running on localhost:5000")
    except Exception as e:
        print(f"❌ Error testing API: {e}")

if __name__ == "__main__":
    test_mysql_calendar_api()
