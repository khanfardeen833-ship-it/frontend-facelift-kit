#!/usr/bin/env python3
"""
Test the calendar API endpoint
"""

import requests
import json

def test_calendar_api():
    """Test the calendar API endpoint"""
    try:
        url = "http://localhost:5000/api/interviews/calendar"
        headers = {
            'X-API-Key': 'sk-hiring-bot-2024-secret-key-xyz789',
            'Content-Type': 'application/json'
        }
        
        print(f"Testing API: {url}")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Response successful")
            print(f"Total events: {data.get('total', 0)}")
            
            events = data.get('events', [])
            for i, event in enumerate(events[:3]):  # Show first 3 events
                print(f"\nEvent {i+1}:")
                print(f"  ID: {event.get('id')}")
                print(f"  Candidate: {event.get('candidate_name')}")
                print(f"  Round: {event.get('round_name')}")
                print(f"  Interviewer names: {event.get('interviewer_names')}")
                print(f"  Created by: {event.get('created_by', 'N/A')}")
                print(f"  Job title: {event.get('job_title')}")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_calendar_api()
