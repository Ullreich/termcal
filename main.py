"""
Terminal Calendar - Main entry point
"""
import sys
from pathlib import Path

# Add the project root to the path so we can import our modules
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from weekview.week import Week
from helpers import argparsing as ap

def main():
    """Main entry point for the terminal calendar application."""
    try:
        args = ap.parse_arguments()
        ics_path, week_start = ap.validate_arguments(args)
        
        app = Week(ics_path, week_start)
        app.run()

    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
