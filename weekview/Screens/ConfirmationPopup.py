from textual.screen import ModalScreen
from textual.widgets import Button, Label
from textual.containers import HorizontalGroup, Vertical
from textual.app import ComposeResult
from typing import Callable, Optional

from weekview.Screens.ErrorPopup import ErrorPopup

from icalendar import Event, Calendar

from pathlib import Path

class ConfirmationPopup(ModalScreen):
    """A modal popup screen for confirmations (e.g., delete)."""

    def __init__(self, on_confirm: Optional[Callable[[], None]] = None, on_cancel: Optional[Callable[[], None]] = None, message: str = "") -> None:
        super().__init__()
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.message = message

    def compose(self) -> ComposeResult:
        with Vertical(id="confirmationPopup"):
            yield Label(self.message, id="confirmationMessage")
            with HorizontalGroup():
                yield Button("Cancel", id="cancelButton", variant="primary")
                yield Button("Delete", id="deleteButton", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancelButton":
            self.app.pop_screen()
            if self.on_cancel:
                self.on_cancel()
        elif event.button.id == "deleteButton":
            # Close modal first, then invoke confirm callback
            self.app.pop_screen()
            if self.on_confirm:
                self.on_confirm()

    def key_escape(self, event) -> None:
        """Handle Escape key press."""
        self.app.pop_screen()
        event.prevent_default()
        event.stop()

    def key_q(self, event) -> None:
        """Handle Q key press."""
        self.app.pop_screen()
        event.prevent_default()
        event.stop()