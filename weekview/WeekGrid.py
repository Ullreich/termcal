from __future__ import annotations

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label, Button
from textual.containers import HorizontalGroup, Grid, VerticalScroll, Vertical

from datetime import datetime, timedelta

from icalendar import Calendar

# Import helper modules
from helpers import ical_helpers as ih
from helpers import layout_helpers as lh

# Import week view components
from weekview.EventCell import EventCell

# Import constants
import GLOBALS

class NextButton(Button):
    """button to increment the overlap event"""
    def __init__(self, weekday: str, nr_overlaps: int, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.weekday = weekday
        self.nr_overlaps = nr_overlaps

class PrevButton(Button):
    """button to decrement the overlap event"""
    def __init__(self, weekday: str, nr_overlaps: int, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.weekday = weekday
        self.nr_overlaps = nr_overlaps

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
        self.overlap_index = {day: 0 for day in GLOBALS.WEEK_DAYS}
        self.vscroll = None

    def on_mount(self) -> None:
        """Called when the WeekGrid is mounted. Set initial scroll position."""
        # Set initial scroll position to around 8 AM (adjust as needed)
        # scroll_widget = self.query_one("#week-scroll", VerticalScroll)
        initial_scroll_y = 8 * GLOBALS.HOUR_HEIGHT
        self.call_after_refresh(lambda: self.vscroll.scroll_to(y=initial_scroll_y, animate=False))


    def compose(self) -> ComposeResult:
        """Compose the week grid.
        
        Returns:
            ComposeResult: the result of composing the events into the week grid.
        """
        #-----------------------
        # generating week-array
        #-----------------------
        # TODO: this should be in the week.py
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
            # TODO: move this to daylist init
            Label("time\n", classes="timesTopBar"),
            *dayList,
            classes="topBar"
        )

        # generate overlap bar
        #TODO: should be a grid later (?), for now proof of concept
        overlap_bar = [Label("overlap", classes="overlapIndicatorLabel")]

        # create a column of times
        timesList = [Label(str(i)+":00", classes="timesLabel") for i in range(24)]
        timesListVertical = Vertical(*timesList, classes="timesContainer")

        # create the actual entries
        weekList = [timesListVertical]
        for day, dayIndex in zip(GLOBALS.WEEK_DAYS, [i for i in range(7)]):
            dayList = []

            overlap_list = lh.overlap_list([x for x in events_this_week if x.get("DTSTART").dt.weekday()==dayIndex])

            if len(overlap_list) != 0:
                height, padding = lh.calc_padding_and_height(overlap_list[0])

            # make the next/prev button and label
            if len(overlap_list) > 1:
                g = Grid(
                    PrevButton(weekday=day, nr_overlaps=len(overlap_list), label="<", classes="nextPrevButton", compact=True),
                    Label(f"{self.overlap_index[day]+1}/{len(overlap_list)}", classes="innerText"),
                    NextButton(weekday=day, nr_overlaps=len(overlap_list), label=">", classes="nextPrevButton", compact=True),
                    classes="overlapGrid"
                )

                overlap_bar.append(g)
            else:
                overlap_bar.append(Label(classes="overlapGridBar"))

            #TODO: remove eventually
            # lh.write_overlap_list(overlap_list)

            # for event in (x for x in events_this_week if x["weekday"]==dayIndex):
            # for event in events_this_week:
            oi = self.overlap_index[day]

            # TODO: fix
            if len(overlap_list) != 0:
            # if len(overlap_list) == 0:
                for event, i in zip(overlap_list[oi], range(len(overlap_list[oi]))):
                    event_in_cell = EventCell(event)
                    # event_in_cell = Label("event")
                    event_in_cell.styles.height = height[i]
                    event_in_cell.styles.margin = (padding[i], 0, 0, 0)  # (top, right, bottom, left) - vertical spacing

                    dayList.append(event_in_cell)

            # Create a Vertical container for each day
            dayContainer = Vertical(*dayList, classes="dayContainer")
            weekList.append(dayContainer)

        #TODO: clean up
        yield HorizontalGroup(
            *overlap_bar,
            classes="overlapBar"
        )
        
        # Wrap the entire HorizontalGroup in a single VerticalScroll
        weekGroup = HorizontalGroup(*weekList)
        weekGroup.styles.height = "auto"
        
        # Create VerticalScroll with an ID so we can access it later
        self.vscroll = VerticalScroll(weekGroup, id="week-scroll")
        yield self.vscroll
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events.

        Args:
            event: The button press event.
        """
        # Capture current scroll position before making changes
        # TODO: ugly code lol
        if isinstance(event.button, NextButton) or isinstance(event.button, PrevButton):
            y_scroll = self.vscroll.scroll_y
            
            curr_index = self.overlap_index[event.button.weekday]
                
            if isinstance(event.button, NextButton):
                # Increment and wrap around
                curr_index = (curr_index + 1) % event.button.nr_overlaps
            else:
                curr_index = (curr_index - 1) % event.button.nr_overlaps

            self.overlap_index[event.button.weekday] = curr_index

            # Refresh this widget specifically
            self.refresh(recompose=True)
            
            # Restore scroll position after refresh - get fresh reference to scroll widget
            self.call_after_refresh(lambda: self.vscroll.scroll_to(y=y_scroll, animate=False))