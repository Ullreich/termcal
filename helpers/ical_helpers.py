import icalendar
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

ics_path = Path("./ETH_timetable.ics")

def get_week_events(week_start_utc: datetime, ics_file_path) -> List[Dict[str, Any]]:
    """
    Get all events from the ICS calendar for a given week.
    
    Args:
        week_start_utc (datetime): The start of the week in UTC (should be a Monday)
        ics_file_path (Path): Path to the ICS file (defaults to ETH_timetable.ics)
    
    Returns:
        List[Dict[str, Any]]: List of events with their details
    """
    # Calculate week end (Sunday 23:59:59)
    week_end_utc = week_start_utc + timedelta(days=6, hours=23, minutes=59, seconds=59)
    
    # Load the calendar
    calendar = icalendar.Calendar.from_ical(ics_file_path.read_bytes())
    
    week_events = []
    
    # Iterate through all components in the calendar
    for component in calendar.walk():
        if component.name == "VEVENT":
            event_start = component.get('DTSTART')
            event_end = component.get('DTEND')
            
            if event_start and event_end:
                # Convert to datetime if needed
                start_dt = event_start.dt
                end_dt = event_end.dt
                
                # Handle date vs datetime objects
                if hasattr(start_dt, 'date'):
                    start_date = start_dt.date() if hasattr(start_dt, 'date') else start_dt
                else:
                    start_date = start_dt
                    
                if hasattr(end_dt, 'date'):
                    end_date = end_dt.date() if hasattr(end_dt, 'date') else end_dt
                else:
                    end_date = end_dt
                
                # Check if event falls within the week
                week_start_date = week_start_utc.date()
                week_end_date = week_end_utc.date()
                
                # Event is in the week if it starts before week ends and ends after week starts
                #TODO: handle multiweek events
                if (start_date <= week_end_date and end_date >= week_start_date):
                    event_data = {
                        'summary': str(component.get('SUMMARY', 'No Title')),
                        'description': str(component.get('DESCRIPTION', '')),
                        'location': str(component.get('LOCATION', '')),
                        'start': start_dt,
                        'end': end_dt,
                        'weekday': start_date.weekday(),
                        'uid': str(component.get('UID', '')),
                        'status': str(component.get('STATUS', '')),
                        'organizer': str(component.get('ORGANIZER', ''))
                    }
                    week_events.append(event_data)
    
    # Sort events by start time
    week_events.sort(key=lambda x: x['start'])
    
    return week_events