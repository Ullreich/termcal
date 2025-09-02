from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING, cast

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.css.query import DOMQuery
from textual.reactive import reactive
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Button, Header, Footer, Label, Rule, Input
from textual.containers import HorizontalGroup, VerticalScroll, Vertical, Center

import ical_helpers as ih
import general_helpers as gh
import layout_helpers as lh
import argparsing as ap

from datetime import datetime, timedelta

if TYPE_CHECKING:
    from typing_extensions import Final

WEEK_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
HOUR_HEIGHT = 4


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
            yield Label(f"Start: {WEEK_DAYS[self.ical_event['weekday']]}, the {self.ical_event['start']}", id="eventStart")
            yield Label(f"End: {WEEK_DAYS[self.ical_event['weekday']]}, the {self.ical_event['end']}", id="eventEnd")
            if self.ical_event.get('location'):
                yield Label(f"Location: {self.ical_event['location']}", id="eventLocation")
            if self.ical_event.get('description'):
                yield Label(f"Description: {self.ical_event['description']}", id="eventDescription")
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

class EventEditScreen(Screen):
    pass

class NewEventScreen(Screen):
    """A screen that allows you to add a new event."""

    BINDINGS = [
        ("escape,space,q", "app.pop_screen", "Close"),
        ("ctrl+s", "save_event", "Save Event"),
    ]
    """Bindings for the event screen."""

    def __init__(self) -> None:
        """Initialize the screen with Input widgets to add a new event.
        """
        super().__init__()
        self.event_data = {}

    def compose(self) -> ComposeResult:
        """Compose the event screen.

        Returns:
            ComposeResult: The result of composing the event screen.
        """
        with VerticalScroll():
            yield Label("Create New Event", id="newEventTitle")
            yield Rule(line_style="ascii")
            yield Label("Event Title:")
            yield Input(placeholder="Enter event title", id="eventTitleInput")
            yield Label("Location (optional):")
            yield Input(placeholder="Enter location", id="eventLocation")
            yield Label("Description (optional):")
            yield Input(placeholder="Enter description", id="eventDescription")
            yield Rule(line_style="ascii")
            yield Label("", id="errorMessage")  # For showing validation errors
        with Center():
            yield Button("Save Event", id="saveButton", variant="success")
            yield Button("Cancel", id="cancelButton", variant="error")
        yield Footer()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission (Enter key).
        
        Args:
            event: The input submission event.
        """
        # If user presses Enter in any input field, try to save
        self._save_event()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events.

        Args:
            event: The button press event.
        """
        if event.button.id == "saveButton":
            self._save_event()
        elif event.button.id == "cancelButton":
            self.app.pop_screen()

    def action_save_event(self) -> None:
        """Action to save the event (triggered by Ctrl+S)."""
        self._save_event()

    def _save_event(self) -> None:
        """Collect input values and save the event."""
        # Get input values
        title_input = self.query_one("#eventTitleInput", Input)
        location_input = self.query_one("#eventLocation", Input)
        description_input = self.query_one("#eventDescription", Input)
        error_label = self.query_one("#errorMessage", Label)
        
        # Collect the data
        self.event_data = {
            "title": title_input.value.strip(),
            "location": location_input.value.strip(),
            "description": description_input.value.strip()
        }
        
        # Validate that we have at least a title
        if not self.event_data["title"]:
            error_label.update("Error: Event title is required!")
            error_label.styles.color = "red"
            title_input.focus()
            return
        
        # Clear any previous error messages
        error_label.update("")
        
        # For now, just write to file for testing (TODO: integrate with calendar)
        with open("new_events.txt", "a") as f:
            f.write(f"Title: {self.event_data['title']}\n")
            f.write(f"Location: {self.event_data['location']}\n")
            f.write(f"Description: {self.event_data['description']}\n")
            f.write("---\n")
        
        # Return the data and close screen
        self.app.pop_screen()


class WeekGrid(Widget):
    """The main Grid of events of a week
    
    Returns:
        ComposeResult: The result of adding all events into a week grid view
    """
    def __init__(self, ics_path: Path, week_start: datetime) -> None:
        """Initialize the WeekGrid with calendar path and week start date.
        
        Args:
            ics_path: Path to the ICS calendar file
            week_start: Start date of the week (Monday)
        """
        super().__init__()
        self.ics_path = ics_path
        self.week_start = week_start

    def on_mount(self) -> None:
        """Called when the WeekGrid is mounted. Set initial scroll position."""
        # Set initial scroll position to around 8 AM (adjust as needed)
        scroll_widget = self.query_one("#week-scroll", VerticalScroll)
        initial_scroll_y = 8 * HOUR_HEIGHT
        self.call_after_refresh(lambda: scroll_widget.scroll_to(y=initial_scroll_y, animate=False))


    def compose(self) -> ComposeResult:
        """Compose the week grid.
        
        Returns:
            ComposeResult: the result of composing the events into the week grid.
        """
        #-----------------------
        # generating week-array
        #-----------------------
        try:
            events_this_week = ih.get_week_events(self.week_start, self.ics_path)
        except FileNotFoundError:
            print(f"ICS file not found at {self.ics_path}")
            events_this_week = []
        except Exception as e:
            print(f"Error reading calendar: {e}")
            events_this_week = []
        
        #-----------------------
        # generate the buttons
        #-----------------------
        
        # generate the top bar
        # TODO: clean up this code, put in function or something since it's copy-pasted from below
        dayList = []
        for day, dayIndex in zip(WEEK_DAYS, [i for i in range(7)]):
            shifted_day = self.week_start + timedelta(days=dayIndex)
            formatted_date_str = day + "\n" + str(shifted_day.day) + "." + str(shifted_day.month) + "." + str(shifted_day.year)
            dayList += [Label(formatted_date_str, classes="weekdayTopBar")]
        
        yield HorizontalGroup(
            Label("time\n", classes="timesTopBar"),
            *dayList,
            classes="topBar"
        )

        # create a column of times
        timesList = [Label(str(i)+":00", classes="timesLabel") for i in range(24)]
        timesListVertical = Vertical(*timesList, classes="timesContainer")

        # create the actual entries
        weekList = [timesListVertical]
        for day, dayIndex in zip(WEEK_DAYS, [i for i in range(7)]):
            dayList = []

            overlap_list = lh.overlap_list([x for x in events_this_week if x["weekday"]==dayIndex])
            if len(overlap_list) != 0:
                height, padding = lh.calc_padding_and_height(overlap_list[0])

            #TODO: remove eventually
            # lh.write_overlap_list(overlap_list)

            # for event in (x for x in events_this_week if x["weekday"]==dayIndex):
            # for event in events_this_week:
            if len(overlap_list) != 0:
                for event, i in zip(overlap_list[0], range(len(overlap_list[0]))):
                    event_in_cell = EventCell(event)
                    event_in_cell.styles.height = height[i]
                    event_in_cell.styles.margin = (padding[i], 0, 0, 0)  # (top, right, bottom, left) - vertical spacing

                    dayList.append(event_in_cell)
            
            # Create a Vertical container for each day
            dayContainer = Vertical(*dayList, classes="dayContainer")
            weekList.append(dayContainer)
        
        # Wrap the entire HorizontalGroup in a single VerticalScroll
        weekGroup = HorizontalGroup(*weekList)
        weekGroup.styles.height = "auto"
        
        # Create VerticalScroll with an ID so we can access it later
        yield VerticalScroll(weekGroup, id="week-scroll")

class Week(App):
    """Main week view class."""

    CSS_PATH = "week_prototype.tcss"

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
        """Disable certain actions when EventScreen is active.
        
        Args:
            action: The action name to check
            parameters: Action parameters
            
        Returns:
            bool: False if the action should be disabled, True otherwise
        """
        # Disable week navigation when EventScreen is active
        if action in ("next_week", "previous_week", "new_event_screen"):
            # Check if there are any EventScreen instances in the screen stack
            for screen in self.screen_stack:
                if isinstance(screen, EventScreen):
                    return False
        return super().check_action(action, parameters)

if __name__ == "__main__":
    try:
        args = ap.parse_arguments()
        ics_path, week_start = ap.validate_arguments(args)
        
        app = Week(ics_path, week_start)
        app.run()
        
    except KeyboardInterrupt:
        print("\nExiting...", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
