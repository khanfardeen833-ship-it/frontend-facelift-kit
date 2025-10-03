#!/usr/bin/env python3
"""
Test the current running API to see what database it's connecting to
"""

import requests
import json

def test_current_api():
    """Test the current running API"""
    
    try:
        print("🧪 Testing current running API...")
        
        response = requests.get("http://localhost:5000/api/interviews/calendar", headers={
            'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
            'Content-Type': 'application/json'
        })
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                events = data.get('events', [])
                print(f"\n📅 API returned {len(events)} events")
                print(f"Total reported: {data.get('total', 'N/A')}")
                
                # Check if any events have Shubham
                shubham_events = [e for e in events if 'shubham' in e.get('candidate_name', '').lower()]
                
                if shubham_events:
                    print(f"\n🎯 Found {len(shubham_events)} Shubham events in API response!")
                    for event in shubham_events:
                        print(f"  - {event['candidate_name']} - {event['round_name']} ({event['start']})")
                else:
                    print("\n❌ No Shubham events found in API response")
                
                # Show all events
                print(f"\n📋 All {len(events)} events:")
                for i, event in enumerate(events):
                    print(f"  {i+1}. {event.get('candidate_name', 'Unknown')} - {event.get('round_name', 'Unknown')} ({event.get('start', 'No date')})")
                
                # Check if these look like SQLite data (sample data) or MySQL data (real data)
                if any('Fardeen Khan' in event.get('candidate_name', '') for event in events):
                    print("\n🔍 These look like sample/test data (SQLite)")
                else:
                    print("\n🔍 These look like real interview data (MySQL)")
                    
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
    test_current_api()
