from textual.widgets import Button
from helpers import general_helpers as gh

from icalendar import Event

class EventCell(Button):
    """A calendar event"""

    def __init__(self, ical_event: Event) -> None:
        """Initialize the event

        Args: TODO

        TODO: get the dates and times from calDav later
        """
        super().__init__(ical_event.get("SUMMARY"), id="id"+ical_event.get("UID"))
        self.ical_event = ical_event
        self.styles.background = gh.convert_summary_to_color(self.ical_event.get("SUMMARY"))