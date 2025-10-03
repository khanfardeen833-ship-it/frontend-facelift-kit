#!/usr/bin/env python3
"""
Test the metadata file filtering logic
"""
import glob
import os

def test_filtering():
    print("🧪 Testing metadata file filtering logic...")
    
    # Simulate the filtering logic from the backend
    ticket_id = "c8c0c0d23e"
    
    # Get all metadata files
    metadata_files = glob.glob("Backend/approved_tickets/*/metadata.json")
    print(f"All metadata files: {metadata_files}")
    
    # Filter by ticket_id
    metadata_files_to_search = [path for path in metadata_files if ticket_id in path]
    print(f"Filtered files for ticket {ticket_id}: {metadata_files_to_search}")
    
    # Check each file
    for metadata_path in metadata_files_to_search:
        print(f"\n📄 Checking: {metadata_path}")
        if ticket_id in metadata_path:
            print(f"   ✅ Contains ticket_id {ticket_id}")
        else:
            print(f"   ❌ Does not contain ticket_id {ticket_id}")
    
    # Check if the filtering is working correctly
    expected_file = f"Backend/approved_tickets/c8c0c0d23e_AI-engineer/metadata.json"
    if expected_file in metadata_files_to_search:
        print(f"\n✅ Correct file found: {expected_file}")
    else:
        print(f"\n❌ Correct file not found: {expected_file}")
        print(f"   Available files: {metadata_files_to_search}")

if __name__ == "__main__":
    test_filtering()
