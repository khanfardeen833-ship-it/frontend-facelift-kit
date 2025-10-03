#!/usr/bin/env python3
"""
Script to clean up orphaned candidate records
"""

import requests
import json

# Configuration
API_BASE_URL = "http://localhost:5000"
API_KEY = "sk-hiring-bot-2024-secret-key-xyz789"

def cleanup_orphaned_candidates():
    """Clean up orphaned candidate records"""
    
    headers = {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    print("🧹 Cleaning up orphaned candidate records...")
    print("=" * 50)
    
    try:
        response = requests.post(f"{API_BASE_URL}/api/candidates/cleanup-orphaned", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                cleanup_data = data.get('data', {})
                print("✅ Cleanup completed successfully!")
                print(f"   📊 Orphaned status records deleted: {cleanup_data.get('orphaned_status_deleted', 0)}")
                print(f"   📊 Orphaned schedules deleted: {cleanup_data.get('orphaned_schedules_deleted', 0)}")
                print(f"   📊 Orphaned feedback deleted: {cleanup_data.get('orphaned_feedback_deleted', 0)}")
            else:
                print(f"   ❌ Cleanup failed: {data.get('error')}")
        else:
            print(f"   ❌ Request failed: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to API. Is the backend server running?")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    cleanup_orphaned_candidates()
