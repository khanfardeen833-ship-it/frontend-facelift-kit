#!/usr/bin/env python3
"""
Verify that Deep candidate has been completely deleted
"""

import requests
import json

# Configuration
API_BASE_URL = "http://localhost:5000"
API_KEY = "sk-hiring-bot-2024-secret-key-xyz789"

def verify_deep_deleted():
    """Verify that Deep candidate has been completely deleted"""
    
    headers = {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json'
    }
    
    print("🔍 Verifying Deep candidate deletion...")
    print("=" * 50)
    
    try:
        # Check candidates list
        response = requests.get(f"{API_BASE_URL}/api/candidates/filter-by-round", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            candidates = data.get('data', {}).get('candidates', [])
            
            deep_candidates = [c for c in candidates if 'deep' in c.get('applicant_name', '').lower() or 'deep' in c.get('applicant_email', '').lower()]
            
            print(f"📊 Total candidates found: {len(candidates)}")
            print(f"📊 Deep candidates found: {len(deep_candidates)}")
            
            if len(deep_candidates) == 0:
                print("✅ SUCCESS: Deep candidate has been completely removed!")
                print("   Deep no longer appears in the candidate list.")
            else:
                print("❌ ISSUE: Deep candidate still found:")
                for candidate in deep_candidates:
                    print(f"   - Name: {candidate.get('applicant_name')}")
                    print(f"   - Email: {candidate.get('applicant_email')}")
                    print(f"   - Job: {candidate.get('job_title')}")
        
        # Check specific job candidates
        print("\n🔍 Checking AI engineer job specifically...")
        ai_engineer_response = requests.get(f"{API_BASE_URL}/api/candidates/filter-by-round?ticket_id=fa4bfd680b", headers=headers)
        
        if ai_engineer_response.status_code == 200:
            ai_data = ai_engineer_response.json()
            ai_candidates = ai_data.get('data', {}).get('candidates', [])
            
            deep_in_ai = [c for c in ai_candidates if 'deep' in c.get('applicant_name', '').lower() or 'deep' in c.get('applicant_email', '').lower()]
            
            print(f"📊 AI engineer candidates: {len(ai_candidates)}")
            print(f"📊 Deep in AI engineer job: {len(deep_in_ai)}")
            
            if len(deep_in_ai) == 0:
                print("✅ SUCCESS: Deep is no longer in the AI engineer job!")
            else:
                print("❌ ISSUE: Deep still found in AI engineer job")
        
        print("\n🎉 Verification completed!")
        
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to API. Is the backend server running?")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    verify_deep_deleted()
