#!/usr/bin/env python3
"""
Force delete Deep candidate using the API
"""

import requests
import json

# Configuration
API_BASE_URL = "http://localhost:5000"
API_KEY = "sk-hiring-bot-2024-secret-key-xyz789"

def force_delete_deep():
    """Force delete Deep candidate using API calls"""
    
    headers = {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    print("🔍 Force deleting Deep candidate...")
    print("=" * 50)
    
    # First, get all candidates to find Deep
    try:
        print("1. Finding Deep's records...")
        response = requests.get(f"{API_BASE_URL}/api/candidates/filter-by-round", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            candidates = data.get('data', {}).get('candidates', [])
            
            deep_candidates = [c for c in candidates if 'deep' in c.get('applicant_name', '').lower() or 'deep' in c.get('applicant_email', '').lower()]
            
            print(f"   Found {len(deep_candidates)} Deep candidates:")
            for candidate in deep_candidates:
                print(f"   - Name: {candidate.get('applicant_name')}")
                print(f"   - Email: {candidate.get('applicant_email')}")
                print(f"   - Job: {candidate.get('job_title')}")
                print(f"   - Ticket ID: {candidate.get('ticket_id')}")
                print(f"   - Candidate ID: {candidate.get('candidate_id')}")
                print()
            
            # Delete each Deep candidate
            for candidate in deep_candidates:
                print(f"2. Deleting {candidate.get('applicant_name')}...")
                
                delete_data = {
                    'candidate_id': candidate.get('candidate_id'),
                    'ticket_id': candidate.get('ticket_id'),
                    'candidate_email': candidate.get('applicant_email'),
                    'candidate_name': candidate.get('applicant_name')
                }
                
                delete_response = requests.post(
                    f"{API_BASE_URL}/api/candidates/delete", 
                    headers=headers,
                    json=delete_data
                )
                
                if delete_response.status_code == 200:
                    result = delete_response.json()
                    if result.get('success'):
                        print(f"   ✅ Successfully deleted {candidate.get('applicant_name')}")
                    else:
                        print(f"   ❌ Failed to delete: {result.get('error')}")
                else:
                    print(f"   ❌ Delete request failed: {delete_response.text}")
        
        # Run cleanup
        print("\n3. Running cleanup...")
        cleanup_response = requests.post(f"{API_BASE_URL}/api/candidates/cleanup-orphaned", headers=headers)
        
        if cleanup_response.status_code == 200:
            cleanup_data = cleanup_response.json()
            if cleanup_data.get('success'):
                cleanup_info = cleanup_data.get('data', {})
                print("   ✅ Cleanup completed!")
                print(f"   📊 Orphaned records cleaned: {cleanup_info.get('orphaned_status_deleted', 0) + cleanup_info.get('orphaned_schedules_deleted', 0) + cleanup_info.get('orphaned_feedback_deleted', 0)}")
            else:
                print(f"   ❌ Cleanup failed: {cleanup_data.get('error')}")
        
        print("\n✅ Force deletion process completed!")
        
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to API. Is the backend server running?")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    force_delete_deep()
