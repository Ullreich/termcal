from textual.app import ComposeResult
from textual.screen import Screen, ModalScreen
from textual.widgets import Button, Footer, Label, Rule, Input
from textual.containers import HorizontalGroup, VerticalScroll, Vertical
from textual.validation import Length, ValidationResult, Validator

from helpers import general_helpers as gh

from datetime import datetime

class ErrorPopup(ModalScreen):
    """A modal popup screen for displaying error messages."""

    def __init__(self, error_message: str) -> None:

        super().__init__()
        self.error_message = error_message

    def compose(self) -> ComposeResult:
        with Vertical(id="errorPopup"):
            yield Label(self.error_message, id="errorMessage")
            with HorizontalGroup():
                yield Button("OK", id="okButton", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "okButton":
            self.app.pop_screen()

    def key_escape(self) -> None:
        self.app.pop_screen()

    def key_enter(self) -> None:
        self.app.pop_screen()

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

            # Title
            yield Label("Event Title:")
            yield Input(placeholder="Enter event title",
                        id="eventTitleInput",
                        validators=[Length(1, 500)])

            # Start
            yield Label("Start Time:")
            yield Input(placeholder=f"8:00 {datetime.today().strftime('%d.%m.%Y')}",
                        id="eventStartInput",
                        validators=[isValidDate()])

            # End
            yield Label("End Time:")
            yield Input(placeholder=f"9:00 {datetime.today().strftime('%d.%m.%Y')}",
                        id="eventEndInput",
                        validators=[isValidDate()])

            # Location
            yield Label("Location (optional):")
            yield Input(placeholder="Enter location", id="eventLocation")

            # Description
            yield Label("Description (optional):")
            yield Input(placeholder="Enter description", id="eventDescription")

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
        """Collect input values and save the event."""
        # Get input values

        # TODO: make into icalendar Object instead
        title_input = self.query_one("#eventTitleInput", Input)
        start_input = self.query_one("#eventStartInput", Input)
        end_input = self.query_one("#eventEndInput", Input)
        location_input = self.query_one("#eventLocation", Input)
        description_input = self.query_one("#eventDescription", Input)
        
        # Collect the data
        self.event_data = {
            "title": title_input.value.strip(),
            "start": start_input.value.strip(),
            "end": end_input.value.strip(),
            "location": location_input.value.strip(),
            "description": description_input.value.strip()
        }
        
        # Handling input errors
        error_msg = None
        # Validate that we have the non-optional values
        if not (self.event_data["title"] and
                self.event_data["start"] and
                self.event_data["end"]):
            error_msg = "Error: missing required input"
        # Assert that start < end
        elif not (self.event_data["start"] < self.event_data["end"]):
            error_msg = "Error: start date is after end date"
        # if one of the errors occured, rais it
        if error_msg:
            # Show error popup
            error_popup = ErrorPopup(error_msg)
            self.app.push_screen(error_popup)
            title_input.focus()
            return
        
        # For now, just write to file for testing (#TODO: integrate with calendar)
        with open("new_events.txt", "a") as f:
            f.write(f"Title: {self.event_data['title']}\n")
            f.write(f"Start: {self.event_data['start']}\n")
            f.write(f"End: {self.event_data['end']}\n")
            f.write(f"Location: {self.event_data['location']}\n")
            f.write(f"Description: {self.event_data['description']}\n")
            f.write("---\n")
        
        # Return the data and close screen
        self.app.pop_screen()

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