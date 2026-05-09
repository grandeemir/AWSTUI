from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Label, Button, Input, Select, TabbedContent, TabPane
from textual.containers import Vertical, Horizontal
import boto3
from awstui.utils.credentials_store import load_stored_credentials, save_credentials

class SettingsScreen(ModalScreen[dict]):
    def __init__(self, current_profile: str, current_region: str):
        super().__init__()
        self.current_profile = current_profile
        self.current_region = current_region
        
        try:
            self.profiles = boto3.Session().available_profiles
        except Exception:
            self.profiles = []
        
        self.stored_users = load_stored_credentials()
        
        self.regions = [
            "us-east-1", "us-east-2", "us-west-1", "us-west-2",
            "eu-central-1", "eu-west-1", "eu-west-2", "eu-west-3",
            "ap-southeast-1", "ap-southeast-2", "ap-northeast-1",
            "sa-east-1", "me-south-1"
        ]

    def compose(self) -> ComposeResult:
        with Vertical(id="settings-dialog"):
            yield Label("AWS CONFIGURATION", id="settings-title")
            
            with TabbedContent():
                with TabPane("Existing Profiles"):
                    yield Label("Select Profile:")
                    profile_options = [(p, p) for p in self.profiles]
                    for name in self.stored_users.keys():
                        profile_options.append((f"Stored: {name}", f"STORED:{name}"))
                    
                    yield Select(
                        profile_options,
                        value=self.current_profile or "default",
                        id="profile-select"
                    )
                
                with TabPane("Add New Keys"):
                    yield Label("Friendly Name:")
                    yield Input(placeholder="e.g. MyProductionUser", id="new-name")
                    yield Label("Access Key ID:")
                    yield Input(placeholder="AKIA...", id="new-access-key")
                    yield Label("Secret Access Key:")
                    yield Input(placeholder="Secret...", id="new-secret-key", password=True)
                    yield Button("Save & Use These Keys", variant="success", id="save-keys")

            yield Label("Select Region:")
            yield Select(
                [(r, r) for r in self.regions],
                value=self.current_region or "us-east-1",
                id="region-select"
            )
            
            with Horizontal(id="settings-buttons"):
                yield Button("Cancel", variant="default", id="cancel")
                yield Button("Apply Changes", variant="primary", id="apply")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "apply":
            profile_val = self.query_one("#profile-select", Select).value
            region = self.query_one("#region-select", Select).value
            
            if profile_val and profile_val.startswith("STORED:"):
                user_name = profile_val.replace("STORED:", "")
                creds = self.stored_users[user_name]
                self.dismiss({
                    "profile": None, 
                    "region": region,
                    "access_key": creds["access_key"],
                    "secret_key": creds["secret_key"]
                })
            else:
                self.dismiss({
                    "profile": profile_val, 
                    "region": region,
                    "access_key": None,
                    "secret_key": None
                })
        
        elif event.button.id == "save-keys":
            name = self.query_one("#new-name", Input).value
            access = self.query_one("#new-access-key", Input).value
            secret = self.query_one("#new-secret-key", Input).value
            region = self.query_one("#region-select", Select).value
            
            if name and access and secret:
                save_credentials(name, access, secret)
                self.notify(f"Credentials for '{name}' saved locally.")
                self.dismiss({
                    "profile": None,
                    "region": region,
                    "access_key": access,
                    "secret_key": secret
                })
            else:
                self.notify("All fields (Name, Access Key, Secret) are required!", severity="error")
        
        else:
            self.dismiss(None)
