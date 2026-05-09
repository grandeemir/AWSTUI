# AWS TUI (AWSTUI)

A professional Terminal User Interface (TUI) for AWS management.

## Features
- **Multi-service Support:** EC2, S3, IAM, Lambda, CloudWatch, ECS.
- **Security First:** Default Read-Only mode. "Danger Mode" required for destructive actions.
- **Async Performance:** Built with Textual and aiobotocore for non-blocking UI.
- **Keyboard Centric:** Navigate, search, and manage resources without leaving the terminal.
- **Multi-pane Layout:** Sidebar navigation, resource list, and deep-dive details.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repo-url>
    cd AWSTUI
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure AWS Credentials:**
    Ensure you have your AWS credentials configured in `~/.aws/credentials` or via environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`).

## Usage

Run the application:
```bash
python main.py
```

### Key Bindings
- `q`: Quit application
- `d`: Toggle Danger Mode (allows write/destructive actions)
- `r`: Refresh current resource list
- `s`: Stop selected resource (EC2 only, Danger Mode required)
- `t`: Start selected resource (EC2 only, Danger Mode required)
- `Enter`: Select resource from table to see details in the right pane
- `Tab`: Cycle focus between navigation, list, and search

## Safety & Security
- Destructive actions require **Danger Mode** to be active.
- Destructive actions trigger a **Modal Confirmation Screen** where you must type the Resource ID to confirm.
- Secrets are never displayed in plain text unless explicitly mapped in the details view (not recommended).

## Architecture
The project follows a modular adapter pattern:
- `awstui/aws/`: Service-specific adapters wrapping `aiobotocore`.
- `awstui/ui/`: Textual screens, widgets, and styles.
- `awstui/app.py`: Main application logic and state.
