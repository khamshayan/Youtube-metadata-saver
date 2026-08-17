"""
File manager for handling folder creation and file operations.
Manages metadata saving and file copying.
"""

import shutil
from pathlib import Path

from platform_utils import sanitize_filename, unique_path, write_text_file


def create_folder(base_path, folder_name, suffix):
    """
    Create a folder with the specified name and suffix.

    Args:
        base_path (str): Base directory path
        folder_name (str): Name of the folder
        suffix (str): Suffix to append (e.g., "MAIN", "EDITOR")

    Returns:
        str: Full path of created folder or None if failed
    """
    if not base_path or not Path(base_path).exists():
        print(f"Base path does not exist: {base_path}")
        return None

    full_folder_name = f"{folder_name} - {suffix}"
    folder_path = Path(base_path) / full_folder_name

    if folder_path.exists():
        print(f"Folder already exists: {folder_path}")
        return str(folder_path)

    try:
        folder_path.mkdir(parents=True, exist_ok=True)
        print(f"Created folder: {folder_path}")
        return str(folder_path)
    except Exception as e:
        print(f"Error creating folder: {e}")
        return None


def save_metadata(folder_path, title, description):
    """
    Save metadata to Metadata.txt in the specified folder.
    Format: Title, 2 blank lines, Description.

    Args:
        folder_path (str): Path to the folder
        title (str): Video title
        description (str): Video description

    Returns:
        bool: True if successful, False otherwise
    """
    if not folder_path or not Path(folder_path).exists():
        print(f"Folder does not exist: {folder_path}")
        return False

    metadata_file = Path(folder_path) / "Metadata.txt"

    if write_text_file(metadata_file, f"{title}\n\n\n{description}"):
        print(f"Saved metadata: {metadata_file}")
        return True
    return False


def save_transcript(folder_path, transcript_text):
    """
    Save transcript to Transcript.txt in the specified folder.

    Args:
        folder_path (str): Path to the folder
        transcript_text (str): Transcript content

    Returns:
        bool: True if successful, False otherwise
    """
    if not folder_path or not Path(folder_path).exists():
        print(f"Folder does not exist: {folder_path}")
        return False

    transcript_file = Path(folder_path) / "Transcript.txt"

    if write_text_file(transcript_file, transcript_text):
        print(f"Saved transcript: {transcript_file}")
        return True
    return False


def copy_file(source_path, destination_folder, new_filename=None):
    """
    Copy a file to the destination folder.

    Args:
        source_path (str): Path to the source file
        destination_folder (str): Destination folder path
        new_filename (str, optional): New filename for the copied file

    Returns:
        bool: True if successful, False otherwise
    """
    source = Path(source_path) if source_path else None
    if not source or not source.exists():
        print(f"Source file does not exist: {source_path}")
        return False

    destination_folder = Path(destination_folder)
    if not destination_folder.exists():
        print(f"Destination folder does not exist: {destination_folder}")
        return False

    try:
        filename = new_filename if new_filename else source.name
        destination_path = destination_folder / filename

        shutil.copy2(source, destination_path)
        print(f"Copied file: {source} -> {destination_path}")
        return True
    except Exception as e:
        print(f"Error copying file: {e}")
        return False


def save_thumbnail_text(folder_path, title="", transcript=""):
    """
    Save the thumbnail template text file to the THUMB folder.
    Format: title=<value>, three blank lines, script=<value>

    Args:
        folder_path (str): Path to the THUMB folder
        title (str): Video title to populate the title= field
        transcript (str): Transcript to populate the script= field

    Returns:
        bool: True if successful, False otherwise
    """
    if not folder_path or not Path(folder_path).exists():
        print(f"Folder does not exist: {folder_path}")
        return False

    text_file = Path(folder_path) / "Thumbnail.txt"

    if write_text_file(text_file, f"title={title}\n\n\n\nscript={transcript}"):
        print(f"Saved thumbnail text: {text_file}")
        return True
    return False


def save_short_metadata(folder_path, short_title, short_description, short_transcript):
    """
    Save short form metadata to Short_Metadata.txt in the specified folder.
    Format: SHORT FORM TITLE, SHORT FORM DESCRIPTION, SHORT FORM TRANSCRIPT.

    Returns:
        bool: True if successful, False otherwise
    """
    if not folder_path or not Path(folder_path).exists():
        print(f"Folder does not exist: {folder_path}")
        return False

    metadata_file = Path(folder_path) / "Short_Metadata.txt"

    content = (
        f"SHORT FORM TITLE:\n{short_title}\n\n\n"
        f"SHORT FORM DESCRIPTION:\n{short_description}\n\n\n"
        f"SHORT FORM TRANSCRIPT:\n{short_transcript}"
    )

    if write_text_file(metadata_file, content):
        print(f"Saved short metadata: {metadata_file}")
        return True
    return False


def folder_exists(base_path, folder_name, suffix):
    """
    Check if a folder already exists.

    Args:
        base_path (str): Base directory path
        folder_name (str): Name of the folder
        suffix (str): Suffix to check (e.g., "MAIN", "EDITOR")

    Returns:
        bool: True if folder exists, False otherwise
    """
    if not base_path:
        return False

    full_folder_name = f"{folder_name} - {suffix}"
    return (Path(base_path) / full_folder_name).exists()


# ── Reference material ─────────────────────────────────────────────────────

def create_reference_folder(thumb_folder):
    """
    Create the 'Reference' subfolder inside an existing THUMB folder.

    The folder name is sanitised and auto-numbered on collision so behaviour
    matches the rest of the app's file naming.

    Args:
        thumb_folder (str): Path to the THUMB folder

    Returns:
        str: Full path of the created folder, or None if it failed
    """
    if not thumb_folder or not Path(thumb_folder).exists():
        print(f"THUMB folder does not exist: {thumb_folder}")
        return None

    folder_path = unique_path(thumb_folder, sanitize_filename("Reference"))

    try:
        folder_path.mkdir(parents=True, exist_ok=False)
        print(f"Created reference folder: {folder_path}")
        return str(folder_path)
    except Exception as e:
        print(f"Error creating reference folder: {e}")
        return None


def save_reference_notes(folder_path, reference_title="", reference_transcript="",
                         skip_title=False, skip_transcript=False):
    """
    Write 'Reference Notes.txt' into the Reference folder.

    Only the sections that were not skipped are included — a skipped field
    leaves no blank heading or placeholder behind. When both are skipped no
    file is written at all.

    Returns:
        bool: True if the file was written, False if nothing was written
              (either both fields were skipped, or the write failed).
    """
    if skip_title and skip_transcript:
        print("Both reference fields skipped — no notes file created.")
        return False

    if not folder_path or not Path(folder_path).exists():
        print(f"Reference folder does not exist: {folder_path}")
        return False

    sections = []
    if not skip_title:
        sections.append(f"REFERENCE TITLE:\n{reference_title}")
    if not skip_transcript:
        sections.append(f"REFERENCE TRANSCRIPT:\n{reference_transcript}")

    notes_file = unique_path(folder_path, sanitize_filename("Reference Notes.txt"))

    if write_text_file(notes_file, "\n\n\n".join(sections)):
        print(f"Saved reference notes: {notes_file}")
        return True
    return False


def save_reference_thumbnail(folder_path, image_path):
    """
    Copy the reference thumbnail image into the Reference folder, sanitising
    the filename and auto-numbering on collision.

    Returns:
        bool: True if the image was copied, False otherwise.
    """
    source = Path(image_path) if image_path else None
    if not source or not source.exists():
        print(f"Reference thumbnail does not exist: {image_path}")
        return False

    if not folder_path or not Path(folder_path).exists():
        print(f"Reference folder does not exist: {folder_path}")
        return False

    safe_name = sanitize_filename(source.stem, fallback="Reference Thumbnail") + source.suffix
    destination = unique_path(folder_path, safe_name)

    try:
        shutil.copy2(source, destination)
        print(f"Copied reference thumbnail: {source} -> {destination}")
        return True
    except Exception as e:
        print(f"Error copying reference thumbnail: {e}")
        return False
