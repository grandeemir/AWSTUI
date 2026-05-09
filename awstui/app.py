import json
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Static, ListItem, ListView, Label, DataTable, Input
from textual.reactive import reactive
from textual import work

from .aws.client import AWSClientManager
from .aws.ec2 import EC2Adapter
from .aws.s3 import S3Adapter
from .aws.iam import IAMAdapter
from .aws.lambda_svc import LambdaAdapter
from .aws.cloudwatch import CloudWatchAdapter
from .aws.ecs import ECSAdapter
from .ui.screens.confirmation import ConfirmationScreen
from .ui.screens.settings import SettingsScreen

class NavigationPanel(Static):
    def compose(self) -> ComposeResult:
        yield ListView(
            ListItem(Label("Dashboard"), id="nav-dashboard"),
            ListItem(Label("EC2"), id="nav-ec2"),
            ListItem(Label("S3"), id="nav-s3"),
            ListItem(Label("IAM"), id="nav-iam"),
            ListItem(Label("Lambda"), id="nav-lambda"),
            ListItem(Label("CloudWatch"), id="nav-cloudwatch"),
            ListItem(Label("ECS"), id="nav-ecs"),
            id="nav-list"
        )

class ResourceList(Static):
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search resources...", id="search-input")
        yield DataTable(id="resource-table")

class ResourceDetails(Static):
    def compose(self) -> ComposeResult:
        yield Label("Resource Details", classes="details-header")
        yield Static("Select a resource to see details", id="details-content")

class AWSTUIApp(App):
    CSS_PATH = "ui/styles/app.tcss"
    TITLE = "AWS TUI Manager"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "toggle_danger_mode", "Toggle Danger Mode"),
        ("r", "refresh_resources", "Refresh"),
        ("s", "stop_resource", "Stop Resource"),
        ("t", "start_resource", "Start Resource"),
        ("x", "terminate_resource", "Terminate Resource"),
        ("p", "open_settings", "Settings (Profile/Region)"),
    ]

    danger_mode = reactive(False)
    current_service = reactive("nav-dashboard")
    resources = reactive([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client_manager = AWSClientManager()
        self.adapters = {
            "nav-ec2": EC2Adapter(self.client_manager),
            "nav-s3": S3Adapter(self.client_manager),
            "nav-iam": IAMAdapter(self.client_manager),
            "nav-lambda": LambdaAdapter(self.client_manager),
            "nav-cloudwatch": CloudWatchAdapter(self.client_manager),
            "nav-ecs": ECSAdapter(self.client_manager),
        }

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield NavigationPanel(id="navigation")
            with Vertical(id="main-content"):
                yield ResourceList(id="list-pane")
            yield ResourceDetails(id="details-pane")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#resource-table", DataTable)
        table.cursor_type = "row"
        self.update_subtitle()

    def action_toggle_danger_mode(self) -> None:
        self.danger_mode = not self.danger_mode
        mode_str = "[DANGER]" if self.danger_mode else "[READ-ONLY]"
        self.notify(f"UI Mode changed to {mode_str}")
        self.update_subtitle()

    def update_subtitle(self) -> None:
        mode_str = "[DANGER]" if self.danger_mode else "[READ-ONLY]"
        if self.client_manager.access_key:
            profile = "Manual Keys"
        else:
            profile = self.client_manager.profile_name or "default"
        region = self.client_manager.region_name or "default"
        self.sub_title = f"{mode_str} | Auth: {profile} | Region: {region}"

    @work
    async def action_open_settings(self) -> None:
        result = await self.push_screen_wait(
            SettingsScreen(
                current_profile=self.client_manager.profile_name,
                current_region=self.client_manager.region_name
            )
        )
        if result:
            self.client_manager.update_config(
                profile_name=result.get("profile"),
                region_name=result.get("region"),
                access_key=result.get("access_key"),
                secret_key=result.get("secret_key")
            )
            self.update_subtitle()
            self.notify(f"Config updated: {result.get('profile') or 'Manual Keys'} @ {result.get('region')}")
            self.refresh_resources()

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.item and event.item.id:
            self.current_service = event.item.id
            self.refresh_resources()

    @work(exclusive=True)
    async def refresh_resources(self) -> None:
        table = self.query_one("#resource-table", DataTable)
        table.clear(columns=True)
        
        if self.current_service == "nav-dashboard":
            table.add_column("Welcome")
            table.add_row(["Select a service from the left to begin management."])
            table.add_row(["Press 'd' to toggle Danger Mode for write actions."])
            table.add_row(["Press 'r' to refresh the current list."])
            return

        adapter = self.adapters.get(self.current_service)
        if not adapter:
            table.add_column("Message")
            table.add_row(["Select a supported service or Dashboard (Coming Soon)"])
            return

        self.notify(f"Fetching {self.current_service.split('-')[1].upper()} resources...")
        try:
            resources = await adapter.list_resources()
            self.resources = resources
            if resources:
                cols = list(resources[0].keys())
                table.add_columns(*[c.capitalize() for c in cols])
                for res in resources:
                    table.add_row(*[str(res.get(c, "")) for c in cols])
            else:
                table.add_column("Status")
                table.add_row(["No resources found"])
        except Exception as e:
            self.notify(f"Error: {str(e)}", severity="error")

    async def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        # Get the first cell (usually ID or Name)
        resource_id = event.data_table.get_row_at(event.cursor_row)[0]
        adapter = self.adapters.get(self.current_service)
        if adapter:
            self.show_details(resource_id, adapter)

    @work(exclusive=True)
    async def show_details(self, resource_id: str, adapter) -> None:
        content = self.query_one("#details-content", Static)
        content.update("Loading details...")
        try:
            details = await adapter.get_details(resource_id)
            content.update(json.dumps(details, indent=2, default=str))
        except Exception as e:
            content.update(f"Error loading details: {str(e)}")

    def action_refresh_resources(self) -> None:
        self.refresh_resources()

    @work
    async def action_stop_resource(self) -> None:
        if not self.danger_mode:
            self.notify("Danger Mode must be ENABLED for this action", severity="warning")
            return
        
        table = self.query_one("#resource-table", DataTable)
        if table.cursor_row < 0:
            return
            
        try:
            resource_id = table.get_row_at(table.cursor_row)[0]
        except Exception:
            return
        
        if self.current_service == "nav-ec2":
            confirmed = await self.push_screen_wait(ConfirmationScreen("STOP EC2 Instance", resource_id, "STOP EC2"))
            if confirmed:
                await self.execute_action(self.adapters["nav-ec2"].stop_instance, resource_id)

    @work
    async def action_start_resource(self) -> None:
        if not self.danger_mode:
            self.notify("Danger Mode must be ENABLED for this action", severity="warning")
            return
            
        table = self.query_one("#resource-table", DataTable)
        if table.cursor_row < 0:
            return
            
        try:
            resource_id = table.get_row_at(table.cursor_row)[0]
        except Exception:
            return
        
        if self.current_service == "nav-ec2":
            confirmed = await self.push_screen_wait(ConfirmationScreen("START EC2 Instance", resource_id, "START EC2"))
            if confirmed:
                await self.execute_action(self.adapters["nav-ec2"].start_instance, resource_id)

    @work
    async def action_terminate_resource(self) -> None:
        if not self.danger_mode:
            self.notify("Danger Mode must be ENABLED for this action", severity="warning")
            return
            
        table = self.query_one("#resource-table", DataTable)
        if table.cursor_row < 0:
            return
            
        try:
            resource_id = table.get_row_at(table.cursor_row)[0]
        except Exception:
            return
        
        if self.current_service == "nav-ec2":
            confirmed = await self.push_screen_wait(ConfirmationScreen("TERMINATE EC2 Instance", resource_id, "TERMINATE EC2"))
            if confirmed:
                await self.execute_action(self.adapters["nav-ec2"].terminate_instance, resource_id)

    async def execute_action(self, action_func, resource_id: str) -> None:
        self.notify(f"Executing action on {resource_id}...")
        try:
            await action_func(resource_id)
            self.notify("Action completed successfully", severity="information")
            self.refresh_resources()
        except Exception as e:
            self.notify(f"Action failed: {str(e)}", severity="error")

if __name__ == "__main__":
    app = AWSTUIApp()
    app.run()
