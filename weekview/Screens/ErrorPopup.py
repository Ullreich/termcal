from textual.screen import ModalScreen
from textual.widgets import Button, Label
from textual.containers import HorizontalGroup, Vertical
from textual.app import ComposeResult

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

    def key_enter(self, event) -> None:
        """Handle Enter key press (same as OK button)."""
        self.app.pop_screen()
        event.prevent_default()
        event.stop()