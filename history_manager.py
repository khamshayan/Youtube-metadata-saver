"""
History manager for the YouTube Metadata Saving Platform.
Handles reading and writing save history to history.json.
"""

import json
from datetime import datetime
from pathlib import Path

from platform_utils import app_data_file

HISTORY_FILE = app_data_file("history.json")


def _basename(value):
    """Return just the filename portion of a path, or '' when unset."""
    return Path(value).name if value else ""


def load_history():
    """
    Load save history from history.json.
    Returns a list of entry dicts, newest first.
    """
    if HISTORY_FILE.exists():
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

    skip_ref_title = inputs.get("skip_reference_title", False)
    skip_ref_transcript = inputs.get("skip_reference_transcript", False)

    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "folder_name": inputs.get("folder_name", "").strip(),
        "video_title": inputs.get("video_title", ""),
        "description": inputs.get("description", ""),
        "transcript": inputs.get("transcript", ""),
        "thumbnail": _basename(inputs.get("thumbnail", "")),
        "voiceover": _basename(inputs.get("voiceover", "")),
        "main_folder_path": inputs.get("main_folder_path", ""),
        "editor_folder_path": inputs.get("editor_folder_path", ""),
        "short_form_enabled": inputs.get("short_form_enabled", False),
        "short_title": inputs.get("short_title", ""),
        "short_description": inputs.get("short_description", ""),
        "short_transcript": inputs.get("short_transcript", ""),
        "short_audio": _basename(inputs.get("short_audio", "")),
        # ── Reference material ──────────────────────────────────────────
        "reference_title": "" if skip_ref_title else inputs.get("reference_title", ""),
        "reference_transcript": "" if skip_ref_transcript else inputs.get("reference_transcript", ""),
        "skip_reference_title": skip_ref_title,
        "skip_reference_transcript": skip_ref_transcript,
        "reference_thumbnail": _basename(inputs.get("reference_thumbnail", "")),
        "reference_thumbnail_attached": bool(inputs.get("reference_thumbnail")),
        "reference_included": not (skip_ref_title and skip_ref_transcript),
        "reference_notes_created": inputs.get("reference_notes_created", False),
        "reference_folder_path": inputs.get("reference_folder_path", ""),
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
