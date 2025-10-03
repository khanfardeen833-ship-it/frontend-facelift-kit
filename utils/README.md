# Utils Folder

This folder contains utility scripts, test files, and debugging tools for the HRMS Candidate Portal project.

## Scripts Overview

### API Testing Scripts
- **`test_stop_start_feature.py`** - Tests the stop/start job visibility feature API endpoints
- **`cleanup_orphaned_candidates.py`** - Cleans up orphaned candidate records in the database

### Candidate Management Scripts
- **`force_delete_deep.py`** - Force deletes a specific candidate (Deep) from all database tables
- **`verify_deep_deleted.py`** - Verifies that a candidate has been completely removed from the system

### Database Debugging Scripts
- **`check_database_directly.py`** - Direct database connection and query testing
- **`check_duplicates.py`** - Checks for duplicate records in the database
- **`check_mysql_records.py`** - Verifies MySQL database records and connections

### Testing Scripts
- **`test_backend_logs.py`** - Tests backend logging functionality
- **`test_backend_logs_simple.py`** - Simplified backend logging tests
- **`test_candidate_update.py`** - Tests candidate data update functionality
- **`test_complete_update.py`** - Tests complete candidate profile updates
- **`test_deletion_and_duplicates.py`** - Tests candidate deletion and duplicate handling
- **`test_exact_issue.py`** - Tests specific issues and edge cases
- **`test_filtering.py`** - Tests AI resume filtering functionality
- **`test_help_fix.py`** - Helper script for fixing various issues
- **`test_new_logic.py`** - Tests new business logic implementations

### Debugging Scripts
- **`debug_candidate_mapping.py`** - Debugs candidate data mapping issues
- **`debug_database.py`** - General database debugging utilities

## Usage

Most scripts can be run directly with Python:

```bash
python script_name.py
```

Some scripts require the backend server to be running, while others can work independently.

## Requirements

- Python 3.x
- MySQL database connection (for database scripts)
- Backend server running (for API testing scripts)
- Required Python packages: `requests`, `mysql-connector-python`

## Notes

- These scripts are for development, testing, and maintenance purposes
- Always backup your database before running deletion or cleanup scripts
- Some scripts may modify database data - use with caution
- Check script comments for specific usage instructions
