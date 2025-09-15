from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Footer, Label, Rule
from textual.containers import VerticalScroll, Center, Grid

from icalendar import Event, Calendar

from pathlib import Path

import GLOBALS

class EventScreen(Screen):
    """A screen that displays details for a specific calendar event."""

    BINDINGS = [
        ("q,escape", "event_pop_screen", "Close"),
        ("e", "edit_event", "Edit Event"),
    ]

    def __init__(self, ical_event: Event, calendar: Calendar, ical_path: Path) -> None:
        """Initialize the event screen with event data.
        
        Args:
            ical_event: The calendar event data to display
        """
        super().__init__()
        self.ical_event = ical_event
        self.calendar = calendar
        self.ical_path = ical_path
        self.called_edit = False

    def compose(self) -> ComposeResult:
        """Compose the event screen.

        Returns:
            ComposeResult: The result of composing the event screen.
        """
        with VerticalScroll():
            yield Label(f"{self.ical_event.get("SUMMARY")}", id="eventTitle")
            yield Rule(line_style="ascii")
            with Grid():
                # Start
                yield Label("Start:", classes="type")
                yield Label(f"{GLOBALS.WEEK_DAYS[self.ical_event.get("DTSTART").dt.weekday()]}, the {self.ical_event.get("DTSTART").dt}",
                            id="eventStart",
                            classes="data")

                # End
                yield Label("End:", classes="type")
                yield Label(f"{GLOBALS.WEEK_DAYS[self.ical_event.get("DTSTART").dt.weekday()]}, the {self.ical_event.get("DTEND").dt}",
                            id="eventEnd",
                            classes="data")
                
                # Location
                if self.ical_event.get('location'):
                    yield Label("Location:", classes="type") 
                    yield Label(f"{self.ical_event.get("LOCATION")}",
                                id="eventLocation",
                                classes="data")
                
                # Description
                if self.ical_event.get('description'):
                    yield Label("Description:", classes="type") 
                    yield Label(f"{self.ical_event.get("DESCRIPTION")}",
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
            # Close this screen first to reveal WeekGrid
            self.app.pop_screen()
            if self.called_edit:
                self.refresh_and_restore_scroll()

    def action_event_pop_screen(self) -> None:
        # Close this screen first to reveal WeekGrid
        self.app.pop_screen()
        if self.called_edit:
            self.refresh_and_restore_scroll()

    #TODO: make this a helper function?
    def refresh_and_restore_scroll(self) -> None: 
        # Capture current scroll position
        y_scroll = 0
        scroll_widget = self.app.query_one("#week-scroll", VerticalScroll)
        y_scroll = scroll_widget.scroll_y

        # Refresh and restore
        self.app.refresh(recompose=True)

        def restore_scroll() -> None:
            new_scroll = self.app.query_one("#week-scroll", VerticalScroll)
            new_scroll.scroll_to(y=y_scroll, animate=False)
        
        self.app.call_after_refresh(restore_scroll)

    def action_edit_event(self):
        """Open the new event screen and handle the returned data."""
        from weekview.Screens.BaseEditEventScreen import BaseEditEventScreen
        self.called_edit = True
        edit_event_screen = BaseEditEventScreen(self.calendar, self.ical_path, self.ical_event, )
        self.app.push_screen(edit_event_screen)
