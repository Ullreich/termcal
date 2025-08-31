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
from textual.widgets import Button, Header, Footer, Label, Rule, Markdown
from textual.containers import HorizontalGroup, VerticalScroll, Vertical, Center, Middle

import ical_helpers as ih
import general_helpers as gh
import argparsing as ap

from datetime import datetime, timedelta

if TYPE_CHECKING:
    from typing_extensions import Final

WEEK_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

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



class WeekGrid(Widget):
    """The main Grid of events of a week
    
    Returns:
        ComposeResult: The result of adding all events into a week grid view
    """
    DUMMY_EVENTS = [["0900", "1100"], ["1200", "1500"], ["2000", "2100"]]

    def __init__(self, ics_path: Path, week_start: datetime) -> None:
        """Initialize the WeekGrid with calendar path and week start date.
        
        Args:
            ics_path: Path to the ICS calendar file
            week_start: Start date of the week (Monday)
        """
        super().__init__()
        self.ics_path = ics_path
        self.week_start = week_start


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

        # create a row column of times
        # timesList = Vertical(*[Label(str(i)+":00\n\n", classes="timesLabel") for i in range(24)], classes="timesContainer")
        #TODO: make it so the top bar is not part of the weekgrid, that way the days stay on top
        
        # generate leftmost columnn of hours
        timesList = [Label("time\n", classes="weekdayLabel")]
        timesList+=[Label(str(i)+":00", classes="timesLabel") for i in range(24)]

        timesListVertical = Vertical(*timesList, classes="timesContainer")

        # create the actual entries
        weekList = [timesListVertical]
        #weekList = []
        for day, dayIndex in zip(WEEK_DAYS, [i for i in range(7)]):
            shifted_day = self.week_start + timedelta(days=dayIndex)
            formatted_date_str = day + "\n" + str(shifted_day.day) + "." + str(shifted_day.month) + "." + str(shifted_day.year)
            dayList = [Label(formatted_date_str, classes="weekdayLabel")]
            for event in (x for x in events_this_week if x["weekday"]==dayIndex):
            #for event in events_this_week:
                dayList.append(EventCell(event))
            
            # Create a Vertical container for each day
            dayContainer = Vertical(*dayList, classes="dayContainer")
            weekList.append(dayContainer)
        
        # Wrap the entire HorizontalGroup in a single VerticalScroll
        weekGroup = HorizontalGroup(*weekList)
        weekGroup.styles.height = "auto"
        
        yield VerticalScroll(weekGroup)

class Week(App):
    """Main week view class."""

    CSS_PATH = "week_prototype.tcss"

    BINDINGS = [
        ("q", "quit", "Quit App"),
        ("n", "next_week", "Next Week"),
        ("p", "previous_week", "Previous Week")
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

    def check_action(self, action: str, parameters) -> bool:
        """Disable certain actions when EventScreen is active.
        
        Args:
            action: The action name to check
            parameters: Action parameters
            
        Returns:
            bool: False if the action should be disabled, True otherwise
        """
        # Disable week navigation when EventScreen is active
        if action in ("next_week", "previous_week"):
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
