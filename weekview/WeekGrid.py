from __future__ import annotations

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label
from textual.containers import HorizontalGroup, VerticalScroll, Vertical

from datetime import datetime, timedelta

from icalendar import Calendar

# Import helper modules
from helpers import ical_helpers as ih
from helpers import layout_helpers as lh

# Import week view components
from weekview.EventCell import EventCell

# Import constants
import GLOBALS

class WeekGrid(Widget):
    """The main Grid of events of a week
    
    Returns:
        ComposeResult: The result of adding all events into a week grid view
    """
    def __init__(self, calendar: Calendar, week_start: datetime) -> None:
        """Initialize the WeekGrid with calendar path and week start date.
        
        Args:
            ics_path: Path to the ICS calendar file
            week_start: Start date of the week (Monday)
        """
        super().__init__()
        self.calendar = calendar
        self.week_start = week_start

    def on_mount(self) -> None:
        """Called when the WeekGrid is mounted. Set initial scroll position."""
        # Set initial scroll position to around 8 AM (adjust as needed)
        scroll_widget = self.query_one("#week-scroll", VerticalScroll)
        initial_scroll_y = 8 * GLOBALS.HOUR_HEIGHT
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
            events_this_week = ih.get_week_events(self.week_start, self.calendar)
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
        for day, dayIndex in zip(GLOBALS.WEEK_DAYS, [i for i in range(7)]):
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
        for day, dayIndex in zip(GLOBALS.WEEK_DAYS, [i for i in range(7)]):
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
