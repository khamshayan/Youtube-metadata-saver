"""
Platform utilities for the YouTube Metadata Saving Platform.

Single place where OS-specific behaviour lives so the rest of the codebase can
stay platform-agnostic. Nothing outside this module should branch on
sys.platform.
"""

import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

IS_WINDOWS = sys.platform.startswith("win")
IS_MAC = sys.platform == "darwin"
IS_LINUX = not IS_WINDOWS and not IS_MAC

APP_NAME = "Youtube metadata saver"


# ── Application data directory ─────────────────────────────────────────────

def _default_app_data_dir():
    """Return the per-OS directory where settings/history/drafts belong."""
    if IS_WINDOWS:
        base = os.environ.get("APPDATA")
        base = Path(base) if base else Path.home() / "AppData" / "Roaming"
    elif IS_MAC:
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME") or (Path.home() / ".config"))
    return base / APP_NAME


_APP_DATA_DIR = None


def app_data_dir():
    """
    Return the application data directory as a Path, creating it if needed.

    On first run on macOS/Linux this also migrates data from the old
    Windows-shaped fallback location (~/Youtube metadata saver) that earlier
    versions used when %APPDATA% was undefined.
    """
    global _APP_DATA_DIR
    if _APP_DATA_DIR is not None:
        return _APP_DATA_DIR

    target = _default_app_data_dir()
    target.mkdir(parents=True, exist_ok=True)

    if not IS_WINDOWS:
        legacy = Path.home() / APP_NAME
        if legacy.is_dir() and legacy != target:
            for name in ("settings.json", "history.json", "draft.json"):
                src, dst = legacy / name, target / name
                if src.is_file() and not dst.exists():
                    try:
                        dst.write_bytes(src.read_bytes())
                    except OSError as e:
                        print(f"Could not migrate {name}: {e}")

    _APP_DATA_DIR = target
    return _APP_DATA_DIR


def app_data_file(filename):
    """Return the full Path to a file inside the application data directory."""
    return app_data_dir() / filename


# ── Keyboard modifiers ─────────────────────────────────────────────────────

MODIFIER_LABEL = "Cmd" if IS_MAC else "Ctrl"


def paste_key_sequences():
    """
    Tk bind sequences for 'paste' on this platform.

    macOS uses Command; everything else uses Control. Both cases are bound so a
    Caps-Lock/Shift variant still registers.
    """
    if IS_MAC:
        return ("<Command-v>", "<Command-V>")
    return ("<Control-v>", "<Control-V>")


# ── Fonts ──────────────────────────────────────────────────────────────────

_FONT_CANDIDATES = {
    "win": ("Segoe UI", "Tahoma", "Arial"),
    "mac": ("SF Pro Text", "Helvetica Neue", "Lucida Grande", "Arial"),
    "other": ("DejaVu Sans", "Liberation Sans", "Ubuntu", "Arial"),
}

_UI_FONT_FAMILY = None


def ui_font_family():
    """
    Pick the best available UI font family for this platform.

    The installed-family list is probed once a Tk root exists; if probing is not
    possible yet we fall back to the platform's preferred name, and Tk itself
    substitutes a default for any family it does not have.
    """
    global _UI_FONT_FAMILY
    if _UI_FONT_FAMILY is not None:
        return _UI_FONT_FAMILY

    key = "win" if IS_WINDOWS else "mac" if IS_MAC else "other"
    candidates = _FONT_CANDIDATES[key]

    try:
        import tkinter.font as tkfont

        available = {name.lower() for name in tkfont.families()}
        for name in candidates:
            if name.lower() in available:
                _UI_FONT_FAMILY = name
                return _UI_FONT_FAMILY
    except Exception:
        # No root window yet, or a headless display — fall through.
        pass

    return candidates[0]


def ui_font(size, weight=None):
    """Return a Tk font tuple using the platform's UI font family."""
    family = ui_font_family()
    return (family, size, weight) if weight else (family, size)


# ── Opening folders in the OS file manager ─────────────────────────────────

def open_in_file_manager(path):
    """
    Reveal a folder in the platform's file manager.

    Returns True on success, False if the platform call failed.
    """
    path = str(path)
    try:
        if IS_WINDOWS:
            os.startfile(path)  # noqa: F821 - Windows-only, guarded above
        elif IS_MAC:
            subprocess.run(["open", path], check=True)
        else:
            subprocess.run(["xdg-open", path], check=True)
        return True
    except Exception as e:
        print(f"Error opening folder: {e}")
        return False


FILE_MANAGER_NAME = "File Explorer" if IS_WINDOWS else "Finder" if IS_MAC else "file manager"


# ── Filename sanitisation and collision handling ───────────────────────────

# Union of characters that are illegal on Windows and macOS. ':' and '/' are the
# macOS-invalid ones; the rest come from Windows.
_ILLEGAL_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')

_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    *{f"COM{i}" for i in range(1, 10)},
    *{f"LPT{i}" for i in range(1, 10)},
}


def sanitize_filename(name, fallback="Untitled"):
    """
    Strip characters that are illegal in a file or folder name on Windows,
    macOS, or Linux.

    Also collapses whitespace, trims trailing dots/spaces (invalid on Windows),
    dodges Windows reserved device names, and caps length so the result stays
    within filesystem limits.
    """
    cleaned = _ILLEGAL_CHARS.sub("_", str(name))
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = cleaned.rstrip(". ")

    # A name made up entirely of replaced characters carries no meaning.
    if not cleaned or not cleaned.strip("_. "):
        return fallback

    stem = cleaned.split(".")[0].upper()
    if stem in _RESERVED_NAMES:
        cleaned = f"_{cleaned}"

    if len(cleaned) > 150:
        cleaned = cleaned[:150].rstrip(". ")

    return cleaned or fallback


def unique_path(parent, name):
    """
    Return a Path inside `parent` for `name` that does not yet exist,
    auto-numbering on collision: "Reference", "Reference (2)", "Reference (3)".

    Works for both files and folders — the suffix is preserved for files.
    """
    parent = Path(parent)
    candidate = parent / name
    if not candidate.exists():
        return candidate

    stem = candidate.stem
    suffix = candidate.suffix
    counter = 2
    while True:
        candidate = parent / f"{stem} ({counter}){suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def write_text_file(path, content):
    """
    Write text with explicit UTF-8 encoding and LF line endings so files are
    byte-identical whichever platform produced them.

    newline="\n" disables the platform translation that would otherwise turn
    every "\n" into "\r\n" on Windows.

    Returns True on success, False on failure.
    """
    try:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing text file {path}: {e}")
        return False


# ── Clipboard images ───────────────────────────────────────────────────────

_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"}


def clipboard_image_to_file(target_dir=None, prefix="Pasted"):
    """
    Grab an image from the system clipboard and return the path to it.

    Handles both clipboard payload shapes that PIL returns:
      * a raw bitmap (a real screenshot / copied image) — written to a new PNG
      * a list of file paths (files copied in Explorer/Finder) — the first
        image among them is returned as-is

    Works on Windows and macOS with Pillow's ImageGrab; on Linux it needs
    xclip/wl-paste to be installed.

    Returns:
        str: path to an image file, or None if the clipboard holds no image.
    """
    try:
        from PIL import ImageGrab
    except ImportError:
        print("Pillow is not installed — clipboard paste unavailable.")
        return None

    try:
        grabbed = ImageGrab.grabclipboard()
    except Exception as e:
        print(f"Clipboard read failed: {e}")
        return None

    if grabbed is None:
        return None

    # Files copied in the OS file manager come back as a list of paths.
    if isinstance(grabbed, list):
        for item in grabbed:
            candidate = Path(str(item))
            if candidate.is_file() and candidate.suffix.lower() in _IMAGE_EXTENSIONS:
                return str(candidate)
        return None

    target_dir = Path(target_dir) if target_dir else app_data_dir() / "clipboard"
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        _prune_old_files(target_dir, max_age_days=7)

        stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        out_path = unique_path(target_dir, f"{prefix}_{stamp}.png")

        image = grabbed
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGBA")
        image.save(out_path, "PNG")
        return str(out_path)
    except Exception as e:
        print(f"Error saving clipboard image: {e}")
        return None


def _prune_old_files(directory, max_age_days=7):
    """Delete cached clipboard images older than max_age_days."""
    cutoff = time.time() - (max_age_days * 86400)
    try:
        for item in Path(directory).iterdir():
            if item.is_file() and item.stat().st_mtime < cutoff:
                item.unlink(missing_ok=True)
    except OSError:
        pass
