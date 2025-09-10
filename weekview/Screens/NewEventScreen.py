from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Footer, Label, Rule, Input
from textual.containers import HorizontalGroup, VerticalScroll, Grid
from textual.validation import Length, ValidationResult, Validator

from helpers import general_helpers as gh

from datetime import datetime

from icalendar import Calendar, Event

from pathlib import Path

from uuid import uuid4

from weekview.Screens.ErrorPopup import ErrorPopup

class NewEventScreen(Screen):
    """A screen that allows you to add a new event."""

    BINDINGS = [
        ("q,escape", "app.pop_screen", "Close"),
        ("ctrl+s", "save_event", "Save Event"),
    ]

    def __init__(self, calendar: Calendar, ical_path: Path) -> None:
        """Initialize the screen with Input widgets to add a new event.
        
        Args:
            calendar: The iCalendar object to add the event to
            calendar_path: Optional path to save the calendar file
        """
        super().__init__()
        self.event_data = {}
        self.calendar = calendar
        self.ical_path = ical_path

    def compose(self) -> ComposeResult:
        """Compose the event screen.

        Returns:
            ComposeResult: The result of composing the event screen.
        """
        with VerticalScroll():
            yield Label("Create New Event", id="newEventTitle")
            yield Rule(line_style="ascii")
            
            # Title
            with Grid():
                # Label
                yield Label("Event Title:")
                yield Input(placeholder="Enter event title",
                            id="eventTitleInput",
                            validators=[Length(1, 500)],
                            compact=True)

                # Start
                yield Label("Start Time:")
                yield Input(placeholder=f"8:00 {datetime.today().strftime('%d.%m.%Y')}",
                            id="eventStartInput",
                            validators=[isValidDate()],
                            compact=True)

                # End
                yield Label("End Time:")
                yield Input(placeholder=f"9:00 {datetime.today().strftime('%d.%m.%Y')}",
                            id="eventEndInput",
                            validators=[isValidDate()],
                            compact=True)

                # Location
                yield Label("Location (optional):")
                yield Input(placeholder="Enter location",
                            id="eventLocation",
                            compact=True)

                # Description
                yield Label("Description (optional):")
                yield Input(placeholder="Enter description",
                            id="eventDescription",
                            compact=True)

            with HorizontalGroup():
                yield Button("Save Event", id="saveButton", variant="success")
                yield Button("Cancel", id="cancelButton", variant="error")
        yield Footer()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission (Enter key).
        
        Args:
            event: The input submission event.
        """
        # If user presses Enter in any input field, it switches to the next input field
        self.focus_next()

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
        #TODO: this should be more compact with less code repetition
        """Collect input values and save the event."""
        # get the data from the input fields
        title_input = self.query_one("#eventTitleInput", Input)
        start_input = self.query_one("#eventStartInput", Input)
        end_input = self.query_one("#eventEndInput", Input)
        location_input = self.query_one("#eventLocation", Input)
        description_input = self.query_one("#eventDescription", Input)
        
        # Parse and validate the input data
        parsed_input_data = {
            #metadata
            "uid": str(uuid4()),
            "dtstamp": datetime.now(),
            #input_data
            "summary": title_input.value.strip(),
            "dtstart": gh.validate_date_format(start_input.value.strip(), include_time=True),
            "dtend": gh.validate_date_format(end_input.value.strip(), include_time=True),
            "location": location_input.value.strip(),
            "description": description_input.value.strip(),
        }

        # Handling input errors
        error_msg = None
        error_field = None
        # Validate that we have the non-optional values
        if not title_input.value.strip():
            error_msg = "Error: Event title is required"
            error_field = title_input;
        elif not gh.validate_date_format(start_input.value.strip(), include_time=True):
            error_msg = "Error: Invalid start date/time format"
            error_field = start_input
        elif not gh.validate_date_format(end_input.value.strip(), include_time=True):
            error_msg = "Error: Invalid end date/time format"
            error_field = end_input
        # Assert that start < end
        elif parsed_input_data["dtstart"] >= parsed_input_data["dtend"]:
            error_msg = "Error: start date/time must be before end date/time"
            error_field = start_input
        
        # If one of the errors occurred, raise it
        if error_msg:
            # Show error popup
            error_popup = ErrorPopup(error_msg)
            self.app.push_screen(error_popup)
            error_field.focus()
            return

        # Create the new event with proper iCalendar propertiess
        new_event = Event()
        for key, value in zip(parsed_input_data.keys(), parsed_input_data.values()):
            new_event.add(key, value)
        
        # Add the event to the calendar
        self.calendar.add_component(new_event)
        
        # Save the calendar back to the file
        try:
            with open(self.ical_path, 'wb') as f:
                f.write(self.calendar.to_ical())
        except Exception as e:
            # Show error if saving fails
            error_popup = ErrorPopup(f"Error saving calendar: {str(e)}")
            self.app.push_screen(error_popup)
            return

        # Close screen & refresh week
        self.app.pop_screen()
        self.app.refresh(recompose=True)

# validator classes
class isValidDate(Validator):
    def validate(self, value: str) -> ValidationResult:
        """Check that the input is a valid date"""
        if self.validate_date_format(value):
            return self.success()
        else:
            return self.failure("Not a valid date")

    @staticmethod
    def validate_date_format(value: str) -> bool:
        return True if gh.validate_date_format(value, include_time=True) else False