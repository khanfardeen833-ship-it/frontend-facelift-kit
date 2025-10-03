"""
Date utility functions for consistent DD/MM/YYYY format throughout the backend
"""

from datetime import datetime, date
import re
import logging

logger = logging.getLogger(__name__)

def parse_ddmmyyyy_to_date(ddmmyyyy_string):
    """
    Parse DD/MM/YYYY format string to Python date object
    
    Args:
        ddmmyyyy_string (str): Date string in DD/MM/YYYY format
        
    Returns:
        date: Python date object or None if invalid
    """
    if not ddmmyyyy_string or not isinstance(ddmmyyyy_string, str):
        return None
    
    try:
        # Handle DD/MM/YYYY format
        if re.match(r'^\d{2}/\d{2}/\d{4}$', ddmmyyyy_string):
            day, month, year = ddmmyyyy_string.split('/')
            return date(int(year), int(month), int(day))
        
        # Handle other formats as fallback
        # Try to parse as ISO format (YYYY-MM-DD)
        if re.match(r'^\d{4}-\d{2}-\d{2}$', ddmmyyyy_string):
            return datetime.strptime(ddmmyyyy_string, '%Y-%m-%d').date()
        
        # Try to parse as datetime and extract date
        parsed_date = datetime.fromisoformat(ddmmyyyy_string.replace('Z', '+00:00'))
        return parsed_date.date()
        
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to parse date '{ddmmyyyy_string}': {e}")
        return None

def format_date_to_ddmmyyyy(date_obj):
    """
    Format Python date/datetime object to DD/MM/YYYY string
    
    Args:
        date_obj: Python date or datetime object
        
    Returns:
        str: Date string in DD/MM/YYYY format
    """
    if not date_obj:
        return ''
    
    try:
        if isinstance(date_obj, datetime):
            date_obj = date_obj.date()
        
        if isinstance(date_obj, date):
            return date_obj.strftime('%d/%m/%Y')
        
        return str(date_obj)
        
    except (AttributeError, TypeError) as e:
        logger.warning(f"Failed to format date '{date_obj}': {e}")
        return str(date_obj)

def parse_ddmmyyyy_to_datetime(ddmmyyyy_string, time_string='00:00'):
    """
    Parse DD/MM/YYYY format string with time to Python datetime object
    
    Args:
        ddmmyyyy_string (str): Date string in DD/MM/YYYY format
        time_string (str): Time string in HH:MM format
        
    Returns:
        datetime: Python datetime object or None if invalid
    """
    date_part = parse_ddmmyyyy_to_date(ddmmyyyy_string)
    if not date_part:
        return None
    
    try:
        # Parse time if provided
        if time_string and isinstance(time_string, str):
            # Handle HH:MM:SS format
            if ':' in time_string:
                time_parts = time_string.split(':')
                hour = int(time_parts[0])
                minute = int(time_parts[1])
                second = int(time_parts[2]) if len(time_parts) > 2 else 0
            else:
                hour = minute = second = 0
        else:
            hour = minute = second = 0
        
        return datetime.combine(date_part, datetime.min.time().replace(
            hour=hour, minute=minute, second=second
        ))
        
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to parse datetime '{ddmmyyyy_string} {time_string}': {e}")
        return None

def convert_html_date_to_ddmmyyyy(html_date_string):
    """
    Convert YYYY-MM-DD format (from HTML date input) to DD/MM/YYYY
    
    Args:
        html_date_string (str): Date string in YYYY-MM-DD format
        
    Returns:
        str: Date string in DD/MM/YYYY format
    """
    if not html_date_string or not isinstance(html_date_string, str):
        return ''
    
    try:
        if re.match(r'^\d{4}-\d{2}-\d{2}$', html_date_string):
            date_obj = datetime.strptime(html_date_string, '%Y-%m-%d').date()
            return date_obj.strftime('%d/%m/%Y')
        
        return html_date_string
        
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to convert HTML date '{html_date_string}': {e}")
        return html_date_string

def convert_ddmmyyyy_to_html_date(ddmmyyyy_string):
    """
    Convert DD/MM/YYYY format to YYYY-MM-DD format (for HTML date input)
    
    Args:
        ddmmyyyy_string (str): Date string in DD/MM/YYYY format
        
    Returns:
        str: Date string in YYYY-MM-DD format
    """
    if not ddmmyyyy_string or not isinstance(ddmmyyyy_string, str):
        return ''
    
    try:
        if re.match(r'^\d{2}/\d{2}/\d{4}$', ddmmyyyy_string):
            day, month, year = ddmmyyyy_string.split('/')
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        return ddmmyyyy_string
        
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to convert DD/MM/YYYY date '{ddmmyyyy_string}': {e}")
        return ddmmyyyy_string

def is_valid_ddmmyyyy(date_string):
    """
    Validate if a string is a valid DD/MM/YYYY date
    
    Args:
        date_string (str): Date string to validate
        
    Returns:
        bool: True if valid DD/MM/YYYY format
    """
    if not date_string or not isinstance(date_string, str):
        return False
    
    try:
        if not re.match(r'^\d{2}/\d{2}/\d{4}$', date_string):
            return False
        
        day, month, year = date_string.split('/')
        day, month, year = int(day), int(month), int(year)
        
        # Check if it's a valid date
        test_date = date(year, month, day)
        return test_date.day == day and test_date.month == month and test_date.year == year
        
    except (ValueError, TypeError):
        return False

def get_current_date_ddmmyyyy():
    """
    Get current date in DD/MM/YYYY format
    
    Returns:
        str: Current date in DD/MM/YYYY format
    """
    return datetime.now().strftime('%d/%m/%Y')

def get_current_datetime_ddmmyyyy():
    """
    Get current datetime in DD/MM/YYYY HH:MM format
    
    Returns:
        str: Current datetime in DD/MM/YYYY HH:MM format
    """
    return datetime.now().strftime('%d/%m/%Y %H:%M')

def format_datetime_for_display(datetime_obj):
    """
    Format datetime object for display in DD/MM/YYYY HH:MM format
    
    Args:
        datetime_obj: Python datetime object
        
    Returns:
        str: Formatted datetime string
    """
    if not datetime_obj:
        return ''
    
    try:
        if isinstance(datetime_obj, str):
            # Try to parse the string first
            datetime_obj = datetime.fromisoformat(datetime_obj.replace('Z', '+00:00'))
        
        if isinstance(datetime_obj, datetime):
            return datetime_obj.strftime('%d/%m/%Y %H:%M')
        elif isinstance(datetime_obj, date):
            return datetime_obj.strftime('%d/%m/%Y')
        
        return str(datetime_obj)
        
    except (ValueError, TypeError, AttributeError) as e:
        logger.warning(f"Failed to format datetime '{datetime_obj}': {e}")
        return str(datetime_obj)
