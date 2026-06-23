"""
History manager for the YouTube Metadata Saving Platform.
Handles reading and writing save history to history.json.
"""

import json
import os
from datetime import datetime


_APP_DATA_DIR = os.path.join(
    os.environ.get("APPDATA", os.path.expanduser("~")),
    "Youtube metadata saver"
)
os.makedirs(_APP_DATA_DIR, exist_ok=True)
HISTORY_FILE = os.path.join(_APP_DATA_DIR, "history.json")


def load_history():
    """
    Load save history from history.json.
    Returns a list of entry dicts, newest first.
    """
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")
            return []
    return []


def save_history_entry(inputs):
    """
    Append a new entry to the history file.

    Args:
        inputs (dict): The processed inputs dict from the main window.
    Returns:
        bool: True on success, False on failure.
    """
    history = load_history()
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "folder_name": inputs.get("folder_name", "").strip(),
        "video_title": inputs.get("video_title", ""),
        "description": inputs.get("description", ""),
        "transcript": inputs.get("transcript", ""),
        "thumbnail": os.path.basename(inputs.get("thumbnail", "")),
        "voiceover": os.path.basename(inputs.get("voiceover", "")),
        "main_folder_path": inputs.get("main_folder_path", ""),
        "editor_folder_path": inputs.get("editor_folder_path", ""),
        "short_form_enabled": inputs.get("short_form_enabled", False),
        "short_title": inputs.get("short_title", ""),
        "short_description": inputs.get("short_description", ""),
        "short_transcript": inputs.get("short_transcript", ""),
        "short_audio": os.path.basename(inputs.get("short_audio", "")) if inputs.get("short_audio") else "",
    }
    history.insert(0, entry)  # newest first
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving history: {e}")
        return False


def update_history_entry(index, updated_entry):
    """
    Overwrite a specific history entry by index.

    Args:
        index (int): Position in the history list (0 = newest).
        updated_entry (dict): The updated entry dict.
    Returns:
        bool: True on success, False on failure.
    """
    history = load_history()
    if 0 <= index < len(history):
        history[index] = updated_entry
        try:
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error updating history: {e}")
    return False
