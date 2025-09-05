from datetime import datetime, timedelta
from textual.color import Color


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
    parsed_date = validate_date_format(date_input)
    
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

# TODO: is this a good function? is it even ever used? 
def validate_date_format(date_input: str, include_time = False) -> datetime:
    """
    Validate if a date string has a supported format.
    
    Args:
        date_string: The date string to validate
        
    Returns:
        datetime if is a date, otherwise raises exception
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
    
    time_formats = [
        '%H:%M',         # 08:25
    ]

    time_separators = [
        ':',
        ' ',
        '/',
    ]

    # Clean the input string
    date_input = date_input.strip()
    
    # Try to parse the date with different formats
    if include_time:
        iteration_formats = []

        for time in time_formats:
            for separators in time_separators:
                for date in date_formats:
                    iteration_formats.append(time+separators+date)
                    iteration_formats.append(date+separators+time)
        # TODO: implement better, just for testing atm
        # if __name__ == "__main__":
        #     for i in iteration_formats:
        #         print(i)

    else:
        iteration_formats = date_formats

    parsed_date = None
    for fmt in iteration_formats:
        try:
            parsed_date = datetime.strptime(date_input, fmt)
            break
        except ValueError:
            continue
    
    # if parsed_date is None:
    #     raise ValueError(f"Invalid date format: '{date_input}'. "
    #                    f"Supported formats include: YYYY-MM-DD, DD.MM.YYYY, DD/MM/YYYY, MM/DD/YYYY")
    
    return parsed_date
    
def convert_summary_to_color(summary: str) -> Color:
    """
    Convert a string to a textual Color in r,g,b

    Args:
        summary: the summary of a eventCell
    
    Returns:
        Color: a textual Color

    This fomula was kinda just invented with the following reasoning:
    dividing the string into 3 equal length parts, converting to bistring
    so that we can do math on it and always get same color for same summary.
    The * 57 should not be too expensive, computationally and randomize the colors
    of very similar names through a little 
    """
    bitstring = summary.encode("utf-8")

    r = (57 * (sum(bitstring[:int(len(bitstring)/3)]) % 255)) % 192
    g = (57 * (sum(bitstring[int(len(bitstring)/3):int(2*len(bitstring)/3)])) % 255) % 192
    b = (57 * (sum(bitstring[int(2*len(bitstring)/3):]) % 255)) % 192

    return Color(r,g,b)

# TODO: move to actual testing files
if __name__ == "__main__":
    val = validate_date_format("14:25 2024-12-4", True)
    if val:
        print(val)

    val = validate_date_format("14 25 2024-12-4", True)
    if val:
        print(val)