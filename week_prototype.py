from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, cast

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.css.query import DOMQuery
from textual.reactive import reactive
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Button, Header, Footer, Label, Markdown
from textual.containers import HorizontalGroup, VerticalScroll, Vertical

import ical_helpers as ih

from datetime import datetime, timedelta

if TYPE_CHECKING:
    from typing_extensions import Final


class EventCell(Button):
    """A calendar event"""

    def __init__(self, ical_event) -> None:
        """Initialize the event

        Args: TODO

        TODO: get the dates and times from calDav later
        """
        super().__init__(ical_event["summary"], id="id"+ical_event["uid"])
        self.ical_event = ical_event

class WeekGrid(Widget):
    """The main Grid of events of a week
    
    Returns:
        ComposeResult: The result of adding all events into a week grid view
    """

    WEEK_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    DUMMY_EVENTS = [["0900", "1100"], ["1200", "1500"], ["2000", "2100"]]


    def compose(self) -> ComposeResult:
        """Compose the week grid.
        
        Returns:
            ComposeResult: the result of composing the events into the week grid.
        """
        prototypeCount = 0

        #-----------------------
        # generating week-array
        #-----------------------
        #TODO: make this into passable parameters
        ics_path = Path("./ETH_timetable.ics")
        current_week_monday = datetime(2024, 9, 16, 00, 00, 00)

        try:
            events_this_week = ih.get_week_events(current_week_monday, ics_path)
        except FileNotFoundError:
            print(f"ICS file not found at {ics_path}")
        except Exception as e:
            print(f"Error reading calendar: {e}")
        
        #-----------------------
        # generate the buttons
        #-----------------------

        # create a row column of times
        # timesList = Vertical(*[Label(str(i)+":00\n\n", classes="timesLabel") for i in range(24)], classes="timesContainer")
        #TODO: make it so the top bar is not part of the weekgrid, that way the days stay on top
        
        # generate leftmost columnn of hours
        timesList = [Label("time", classes="weekdayLabel")]
        timesList+=[Label(str(i)+":00", classes="timesLabel") for i in range(24)]

        timesListVertical = Vertical(*timesList, classes="timesContainer")

        # create the actual entries
        weekList = [timesListVertical]
        #weekList = []
        for day, dayIndex in zip(self.WEEK_DAYS, [i for i in range(7)]):
            dayList = [Label(day, classes="weekdayLabel")]
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
        ("q", "quit", "Quit App")
    ]

    def compose(self) -> ComposeResult:
        yield WeekGrid()
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        self.theme = "nord"

if __name__ == "__main__":
    Week().run()
