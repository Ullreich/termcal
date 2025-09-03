import argparse
import sys
from pathlib import Path
from datetime import datetime
from helpers import general_helpers as gh

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Terminal Calendar - View weekly calendar events from an iCal file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Date format examples:
    2024-09-16    (YYYY-MM-DD)
    16.09.2024    (DD.MM.YYYY)
    16/09/2024    (DD/MM/YYYY)
    09/16/2024    (MM/DD/YYYY)
    2024/09/16    (YYYY/MM/DD)
    16-09-2024    (DD-MM-YYYY)
    09-16-2024    (MM-DD-YYYY)
        """
    )
    
    parser.add_argument(
        'ical_path',
        type=str,
        help='Path to the .ical/.ics calendar file'
    )
    
    parser.add_argument(
        'date',
        type=str,
        nargs='?',
        default=datetime.now().strftime('%Y-%m-%d'),
        help='Date to display the week for (various formats supported). Defaults to today.'
    )
    
    return parser.parse_args()


def validate_arguments(args):
    """Validate the parsed arguments."""
    # Validate iCal file path
    ics_path = Path(args.ical_path)
    if not ics_path.exists():
        print(f"Error: iCal file '{ics_path}' does not exist.", file=sys.stderr)
        sys.exit(1)
    
    if not ics_path.is_file():
        print(f"Error: '{ics_path}' is not a file.", file=sys.stderr)
        sys.exit(1)
    
    if not ics_path.suffix.lower() in ['.ics', '.ical']:
        print(f"Warning: '{ics_path}' does not have a typical iCal extension (.ics or .ical)")
    
    # Validate date format
    try:
        week_start = gh.get_week_start_from_date(args.date)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    return ics_path, week_start