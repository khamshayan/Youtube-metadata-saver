"""
Configuration handler for managing settings.json
Handles reading and writing persistent folder paths.
"""

import json
import os
from pathlib import Path


_APP_DATA_DIR = os.path.join(
    os.environ.get("APPDATA", os.path.expanduser("~")),
    "Youtube metadata saver"
)
os.makedirs(_APP_DATA_DIR, exist_ok=True)
CONFIG_FILE = os.path.join(_APP_DATA_DIR, "settings.json")


def load_config():
    """
    Load configuration from settings.json.
    Returns a dictionary with personal_path and editor_path.
    """
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config
        except Exception as e:
            print(f"Error loading config: {e}")
            return None
    return None


def save_config(personal_path, editor_path, thumbnail_base_path=None):
    """
    Save configuration to settings.json.

    Args:
        personal_path (str): Path for MAIN folders
        editor_path (str): Path for EDITOR folders
        thumbnail_base_path (str): Base path where yt THUMBNAILS parent folder is created
    """
    config = {
        "personal_path": personal_path,
        "editor_path": editor_path,
        "thumbnail_base_path": thumbnail_base_path
    }
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


def config_exists():
    """Check if settings.json exists."""
    return os.path.exists(CONFIG_FILE)
