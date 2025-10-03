#!/usr/bin/env python3
"""
Test script to verify the stop/start feature is working
"""

import requests
import json

# Configuration
API_BASE_URL = "http://localhost:5000"
API_KEY = "sk-hiring-bot-2024-secret-key-xyz789"

def test_api_endpoints():
    """Test the new API endpoints"""
    
    headers = {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    print("🧪 Testing Stop/Start Feature API Endpoints")
    print("=" * 50)
    
    # Test 1: Get dashboard jobs (should show all jobs including hidden)
    print("\n1. Testing GET /api/jobs/dashboard")
    try:
        response = requests.get(f"{API_BASE_URL}/api/jobs/dashboard", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                jobs = data.get('data', {}).get('jobs', [])
                print(f"   ✅ Found {len(jobs)} jobs")
                
                if jobs:
                    # Show first job details
                    first_job = jobs[0]
                    print(f"   📋 First job: {first_job.get('job_title', 'Unknown')}")
                    print(f"   🆔 Job ID: {first_job.get('ticket_id', 'Unknown')}")
                    print(f"   👁️  Visible: {first_job.get('is_visible', 'Not set')}")
                    
                    # Test 2: Toggle visibility
                    job_id = first_job.get('ticket_id')
                    if job_id:
                        print(f"\n2. Testing POST /api/jobs/{job_id}/toggle-visibility")
                        toggle_response = requests.post(
                            f"{API_BASE_URL}/api/jobs/{job_id}/toggle-visibility", 
                            headers=headers
                        )
                        print(f"   Status: {toggle_response.status_code}")
                        
                        if toggle_response.status_code == 200:
                            toggle_data = toggle_response.json()
                            if toggle_data.get('success'):
                                print(f"   ✅ Toggle successful!")
                                print(f"   📊 New visibility: {toggle_data.get('data', {}).get('is_visible')}")
                                print(f"   📝 Message: {toggle_data.get('message')}")
                            else:
                                print(f"   ❌ Toggle failed: {toggle_data.get('error')}")
                        else:
                            print(f"   ❌ Toggle request failed: {toggle_response.text}")
                else:
                    print("   ⚠️  No jobs found to test with")
            else:
                print(f"   ❌ API returned error: {data.get('error')}")
        else:
            print(f"   ❌ Request failed: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to API. Is the backend server running?")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Get approved jobs (should only show visible jobs)
    print(f"\n3. Testing GET /api/jobs/approved")
    try:
        response = requests.get(f"{API_BASE_URL}/api/jobs/approved", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                jobs = data.get('data', {}).get('jobs', [])
                print(f"   ✅ Found {len(jobs)} visible jobs for career portal")
            else:
                print(f"   ❌ API returned error: {data.get('error')}")
        else:
            print(f"   ❌ Request failed: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to API. Is the backend server running?")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_api_endpoints()
