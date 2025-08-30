from datetime import datetime, timedelta
import re
from typing import Optional


def get_week_start_from_date(date_input: str) -> datetime:
    """
    Generate the first day (Monday) of the week given a date string.
    
    Args:
        date_input: Date string in various formats (YYYY-MM-DD, DD.MM.YYYY, DD/MM/YYYY, etc.)
    
    Returns:
        datetime: The Monday of the week containing the given date
        
    Raises:
        ValueError: If the date format is invalid or the date is invalid
    """
    # Common date formats to try
    date_formats = [
        '%Y-%m-%d',      # 2024-09-16
        '%d.%m.%Y',      # 16.09.2024
        '%d/%m/%Y',      # 16/09/2024
        '%m/%d/%Y',      # 09/16/2024
        '%Y/%m/%d',      # 2024/09/16
        '%d-%m-%Y',      # 16-09-2024
        '%m-%d-%Y',      # 09-16-2024
    ]
    
    # Clean the input string
    date_input = date_input.strip()
    
    # Try to parse the date with different formats
    parsed_date = None
    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(date_input, fmt)
            break
        except ValueError:
            continue
    
    if parsed_date is None:
        raise ValueError(f"Invalid date format: '{date_input}'. "
                        f"Supported formats include: YYYY-MM-DD, DD.MM.YYYY, DD/MM/YYYY, MM/DD/YYYY")
    
    # Validate the date is reasonable (not too far in past/future)
    current_year = datetime.now().year
    if parsed_date.year < 1900 or parsed_date.year > current_year + 10:
        raise ValueError(f"Date year {parsed_date.year} seems unreasonable. Please check your date.")
    
    # Calculate the Monday of the week containing this date
    # Monday is weekday 0, Sunday is weekday 6
    days_since_monday = parsed_date.weekday()
    week_start = parsed_date - timedelta(days=days_since_monday)
    
    # Set time to beginning of day
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    return week_start


def validate_date_format(date_string: str) -> bool:
    """
    Validate if a date string has a supported format.
    
    Args:
        date_string: The date string to validate
        
    Returns:
        bool: True if the format is valid, False otherwise
    """
    try:
        get_week_start_from_date(date_string)
        return True
    except ValueError:
        return False