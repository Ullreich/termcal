from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Button, Header, Footer

from datetime import datetime, timedelta

# Import week view components
from weekview.WeekGrid import WeekGrid
from weekview.EventCell import EventCell
from weekview.Screens.EventScreen import EventScreen
from weekview.Screens.NewEventScreen import NewEventScreen

class Week(App):
    """Main week view class."""

    CSS_PATH = "../css/week.tcss"

    BINDINGS = [
        ("q", "quit", "Quit App"),
        ("p", "previous_week", "Previous Week"),
        ("n", "next_week", "Next Week"),
        ("a", "new_event_screen", "New Event")
    ]
    
    def __init__(self, ics_path: Path, week_start: datetime) -> None:
        """Initialize the Week app with calendar path and week start date.
        
        Args:
            ics_path: Path to the ICS calendar file
            week_start: Start date of the week (Monday)
        """
        super().__init__()
        self.ics_path = ics_path
        self.week_start = week_start

    def compose(self) -> ComposeResult:
        yield WeekGrid(self.ics_path, self.week_start)
        yield Header()
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events.

        Args:
            event: The button press event.
        """
        if isinstance(event.button, EventCell):
            # Create a new EventScreen instance with the event data
            event_screen = EventScreen(event.button.ical_event)
            self.push_screen(event_screen)

    def on_mount(self) -> None:
        self.theme = "nord"
        # self.title = self.week_start

    def action_next_week(self) -> None:
        """Navigate to the next week."""
        self.week_start += timedelta(days=7)
        self.refresh(recompose=True)

    def action_previous_week(self) -> None:
        """Navigate to the previous week."""
        self.week_start -= timedelta(days=7)
        self.refresh(recompose=True)

    def action_new_event_screen(self):
        """Open the new event screen and handle the returned data."""
        new_event_screen = NewEventScreen()
        self.push_screen(new_event_screen, callback=self._handle_new_event)

    def _handle_new_event(self, event_data: dict | None) -> None:
        """Handle the data returned from the NewEventScreen.
        
        Args:
            event_data: The event data returned from the screen, or None if cancelled
        """
        if event_data:
            # TODO: Integrate with actual calendar system
            # For now, just show that we received the data
            self.notify(f"New event created: {event_data['title']}")
        else:
            # User cancelled
            self.notify("Event creation cancelled")


    def check_action(self, action: str, parameters) -> bool:
        """Disable certain actions when EventScreen or NewEventScreen is active.
        
        Args:
            action: The action name to check
            parameters: Action parameters
            
        Returns:
            bool: False if the action should be disabled, True otherwise
        """
        # Disable week navigation when EventScreen or NewEventScreen is active
        if action in ("next_week", "previous_week", "new_event_screen", "quit"):
            # Check if there are any EventScreen or NewEventScreen instances in the screen stack
            for screen in self.screen_stack:
                if isinstance(screen, (EventScreen, NewEventScreen)):
                    return False
        return super().check_action(action, parameters)