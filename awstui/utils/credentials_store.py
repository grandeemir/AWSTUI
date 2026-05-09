import json
import os
from typing import Dict, Any

# Use a centralized home directory for settings
CONFIG_DIR = os.path.expanduser("~/.awstui")
CREDENTIALS_FILE = os.path.join(CONFIG_DIR, "credentials.json")
LAST_USED_FILE = os.path.join(CONFIG_DIR, "last_used.json")

# Ensure config directory exists
os.makedirs(CONFIG_DIR, exist_ok=True)

def load_stored_credentials() -> Dict[str, Any]:
    if os.path.exists(CREDENTIALS_FILE):
        try:
            with open(CREDENTIALS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_credentials(name: str, access_key: str, secret_key: str):
    creds = load_stored_credentials()
    creds[name] = {
        "access_key": access_key,
        "secret_key": secret_key
    }
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(creds, f, indent=2)

def delete_credentials(name: str):
    creds = load_stored_credentials()
    if name in creds:
        del creds[name]
        with open(CREDENTIALS_FILE, "w") as f:
            json.dump(creds, f, indent=2)

def set_last_used_credential(name: str):
    data = {"last_used": name}
    with open(LAST_USED_FILE, "w") as f:
        json.dump(data, f)

def get_last_used_credential() -> str:
    if os.path.exists(LAST_USED_FILE):
        try:
            with open(LAST_USED_FILE, "r") as f:
                return json.load(f).get("last_used")
        except Exception:
            return None
    return None
