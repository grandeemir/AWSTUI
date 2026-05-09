import json
import os
from typing import Dict, Any

CREDENTIALS_FILE = ".awstui_credentials.json"

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
