from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Footer, Label, Rule, Input
from textual.containers import HorizontalGroup, VerticalScroll

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
        with HorizontalGroup():
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
