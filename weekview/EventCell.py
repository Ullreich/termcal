from textual.widgets import Button
from helpers import general_helpers as gh

class EventCell(Button):
    """A calendar event"""

    def __init__(self, ical_event) -> None:
        """Initialize the event

        Args: TODO

        TODO: get the dates and times from calDav later
        """
        super().__init__(ical_event["summary"], id="id"+ical_event["uid"])
        self.ical_event = ical_event
        self.styles.background = gh.convert_summary_to_color(self.ical_event["summary"])