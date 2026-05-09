from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Label, Button, Input
from textual.containers import Vertical, Horizontal

class ConfirmationScreen(ModalScreen[bool]):
    def __init__(self, action: str, resource_id: str, confirm_keyword: str):
        super().__init__()
        self.action = action
        self.resource_id = resource_id
        self.confirm_keyword = confirm_keyword

    def compose(self) -> ComposeResult:
        with Vertical(id="confirmation-dialog"):
            yield Label("⚠️ DANGER ACTION REQUIRED", id="confirmation-title")
            yield Label(f"Action: {self.action}")
            yield Label(f"Resource Target: {self.resource_id}")
            yield Label(f"To confirm, type: '{self.confirm_keyword}'")
            yield Input(placeholder=f"Type {self.confirm_keyword} here...", id="confirmation-input")
            with Horizontal():
                yield Button("Cancel", variant="default", id="cancel")
                yield Button("CONFIRM", variant="error", id="confirm")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            confirm_input = self.query_one("#confirmation-input", Input).value.strip().upper()
            if confirm_input == self.confirm_keyword.upper():
                self.dismiss(True)
            else:
                self.notify(f"Invalid confirmation! Please type '{self.confirm_keyword}'", severity="error")
        else:
            self.dismiss(False)
