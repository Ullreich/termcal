from textual.app import ComposeResult, App
from textual.screen import Screen
from textual.widgets import Button, Footer, Label, Rule, Input
from textual.containers import HorizontalGroup, VerticalScroll, Grid
from textual.validation import Length, ValidationResult, Validator

from helpers import general_helpers as gh
from helpers import layout_helpers as lh

from datetime import datetime, timezone

from icalendar import Calendar, Event, vDatetime

from pathlib import Path

from weekview.Screens.ErrorPopup import ErrorPopup
from weekview.Screens.ConfirmationPopup import ConfirmationPopup

from icalendar import Event

from typing import Optional

from uuid import uuid4

class BaseEditEventScreen(Screen):
    """A screen that allows you to edit an event."""

    BINDINGS = [
        ("q,escape", "app.pop_screen", "Close"),
        ("ctrl+s", "save_event", "Save Event"),
        # TODO: add for edit of  event
        ("d", "delete_event", "Delete Event"),
    ]

    def __init__(self, calendar: Calendar, ical_path: Path, ical_event: Optional[Event] = None) -> None:
        """Initialize the screen with Input widgets to add or edit an event.
        
        Args:
            calendar: The iCalendar object to add the event to
            calendar_path: Optional path to save the calendar file
            ical_event: an Event object to edit. Optional.
        """
        super().__init__()
        self.calendar = calendar
        self.ical_path = ical_path
        self.ical_event = ical_event

    def compose(self) -> ComposeResult:
        """Compose the event screen.

        Returns:
            ComposeResult: The result of composing the event screen.
        """
        with VerticalScroll():
            yield Label("Edit Event", id="baseEditEventTitle")
            yield Rule(line_style="ascii")
            
            # Title
            with Grid():
                # Label
                yield Label("Event Title:")
                ip = Input( placeholder="Enter event title",
                            id="eventTitleInput",
                            validators=[Length(1, 500)],
                            compact=True)
                if self.ical_event:
                    ip.value=self.ical_event.get("SUMMARY")
                yield ip

                # Start
                yield Label("Start Time:")
                ip = Input( placeholder=f"8:00 {datetime.today().strftime('%d.%m.%Y')}",
                            id="eventStartInput",
                            validators=[isValidDate()],
                            compact=True)
                if self.ical_event:
                    ip.value = self.ical_event.get("DTSTART").dt.strftime("%H:%M %d.%m.%Y")
                else:
                    ip.value = f"8:00 {datetime.today().strftime('%d.%m.%Y')}"
                yield ip

                # End
                yield Label("End Time:")
                ip = Input( placeholder=f"9:00 {datetime.today().strftime('%d.%m.%Y')}",
                            id="eventEndInput",
                            validators=[isValidDate()],
                            compact=True)
                if self.ical_event:
                    ip.value=self.ical_event.get("DTEND").dt.strftime("%H:%M %d.%m.%Y")
                else:
                    ip.value = f"9:00 {datetime.today().strftime('%d.%m.%Y')}"
                yield ip

                # Location
                yield Label("Location (optional):")
                ip = Input( placeholder="Enter location",
                            id="eventLocation",
                            compact=True)
                if self.ical_event:
                    ip.value = self.ical_event.get("LOCATION")
                yield ip

                # Description
                yield Label("Description (optional):")
                ip = Input( placeholder="Enter description",
                            id="eventDescription",
                            compact=True)
                if self.ical_event:
                    ip.value = self.ical_event.get("DESCRIPTION")
                yield ip

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
        # get the data from the input fields
        title_input = self.query_one("#eventTitleInput", Input)
        start_input = self.query_one("#eventStartInput", Input)
        end_input = self.query_one("#eventEndInput", Input)
        location_input = self.query_one("#eventLocation", Input)
        description_input = self.query_one("#eventDescription", Input)
        
        # Parse and validate the input data
        parsed_input_data = {
            #metadata
            "UID": str(uuid4()),
            "DTSTAMP": vDatetime(datetime.now(timezone.utc)),
            #input_data
            "SUMMARY": title_input.value.strip(),
            "DTSTART": vDatetime(gh.validate_date_format(start_input.value.strip(), include_time=True)),
            "DTEND": vDatetime(gh.validate_date_format(end_input.value.strip(), include_time=True)),
            "LOCATION": location_input.value.strip(),
            "DESCRIPTION": description_input.value.strip(),
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
        elif parsed_input_data["DTSTART"].dt >= parsed_input_data["DTEND"].dt:
            error_msg = "Error: start date/time must be before end date/time"
            error_field = start_input
        
        # If one of the errors occurred, raise it
        if error_msg:
            # Show error popup
            error_popup = ErrorPopup(error_msg)
            self.app.push_screen(error_popup)
            error_field.focus()
            return
        
        # if self.ical_event we are editing and only want to pop the edit screen
        if not self.ical_event:
            self.ical_event = Event()
            self.calendar.add_component(self.ical_event)
        # overwrite new input
        for key, value in zip(parsed_input_data.keys(), parsed_input_data.values()):
            if key == "UID" and self.ical_event.get("UID"):
                pass
            else:
                self.ical_event[key] = value

        self.save_to_disk()

        lh.pop_all_screens(self.app)
        lh.refresh_and_restore_scroll(self.app)
    
    def save_to_disk(self) -> None:
        try:
            with open(self.ical_path, 'wb') as f:
                f.write(self.calendar.to_ical())
                # self.app.push_screen(ErrorPopup("got here"))
        except Exception as e:
            # Show error if saving fails
            error_popup = ErrorPopup(f"Error saving calendar: {str(e)}")
            self.app.push_screen(error_popup)
            return

    
    def action_delete_event(self) -> None:
        # make sure we actually have an event to delete
        if not self.ical_event:
            return
        # deletion action
        def confirm_delete() -> None:
            vevent = self.ical_event
            removed = False
            # Try by identity
            try:
                self.calendar.subcomponents.remove(vevent)
                removed = True
            except ValueError:
                # Fallback by UID
                uid = str(vevent.get('UID'))
                for comp in list(self.calendar.walk('VEVENT')):
                    if str(comp.get('UID')) == uid:
                        self.calendar.subcomponents.remove(comp)
                        removed = True
                        break
            if not removed:
                self.app.push_screen(ErrorPopup("Event not found in calendar"))
                return
            self.save_to_disk()
            
            lh.pop_all_screens(main_app=self.app)
            lh.refresh_and_restore_scroll(self.app)

        #cancel action
        def cancel_delete() -> None:
            # No-op; modal already closed
            pass

        popup = ConfirmationPopup(on_confirm=confirm_delete, on_cancel=cancel_delete, message="Do you really want to delete this event?")
        self.app.push_screen(popup)

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