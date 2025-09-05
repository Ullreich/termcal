from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Footer, Label, Rule
from textual.containers import VerticalScroll, Center, Grid

import GLOBALS

class EventScreen(Screen):
    """A screen that displays details for a specific calendar event."""

    BINDINGS = [("escape,space,q", "app.pop_screen", "Close")]
    """Bindings for the event screen."""

    def __init__(self, ical_event: dict) -> None:
        """Initialize the event screen with event data.
        
        Args:
            ical_event: The calendar event data to display
        """
        super().__init__()
        self.ical_event = ical_event

    def compose(self) -> ComposeResult:
        """Compose the event screen.

        Returns:
            ComposeResult: The result of composing the event screen.
        """
        with VerticalScroll():
            yield Label(f"{self.ical_event['summary']}", id="eventTitle")
            yield Rule(line_style="ascii")
            with Grid():
                # Start
                yield Label("Start:", classes="type")
                yield Label(f"{GLOBALS.WEEK_DAYS[self.ical_event['weekday']]}, the {self.ical_event['start']}",
                            id="eventStart",
                            classes="data")

                # End
                yield Label("End:", classes="type")
                yield Label(f"{GLOBALS.WEEK_DAYS[self.ical_event['weekday']]}, the {self.ical_event['end']}",
                            id="eventEnd",
                            classes="data")
                
                # Location
                if self.ical_event.get('location'):
                    yield Label("Location:", classes="type") 
                    yield Label(f"{self.ical_event['location']}",
                                id="eventLocation",
                                classes="data")
                
                # Description
                if self.ical_event.get('description'):
                    yield Label("Description:", classes="type") 
                    yield Label(f"{self.ical_event['description']}",
                                id="eventDescription",
                                classes="data")
            with Center():
                yield Button("Close", id="closeButton")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events.

        Args:
            event: The button press event.
        """
        if event.button.id == "closeButton":
            self.app.pop_screen()
