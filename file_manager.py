"""
File manager for handling folder creation and file operations.
Manages metadata saving and file copying.
"""

import os
import shutil
from pathlib import Path


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
    if not base_path or not os.path.exists(base_path):
        print(f"Base path does not exist: {base_path}")
        return None
    
    full_folder_name = f"{folder_name} - {suffix}"
    folder_path = os.path.join(base_path, full_folder_name)
    
    if os.path.exists(folder_path):
        print(f"Folder already exists: {folder_path}")
        return folder_path
    
    try:
        os.makedirs(folder_path, exist_ok=True)
        print(f"Created folder: {folder_path}")
        return folder_path
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
    if not folder_path or not os.path.exists(folder_path):
        print(f"Folder does not exist: {folder_path}")
        return False
    
    metadata_file = os.path.join(folder_path, "Metadata.txt")
    
    try:
        with open(metadata_file, 'w', encoding='utf-8') as f:
            f.write(title)
            f.write("\n\n\n")
            f.write(description)
        print(f"Saved metadata: {metadata_file}")
        return True
    except Exception as e:
        print(f"Error saving metadata: {e}")
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
    if not folder_path or not os.path.exists(folder_path):
        print(f"Folder does not exist: {folder_path}")
        return False
    
    transcript_file = os.path.join(folder_path, "Transcript.txt")
    
    try:
        with open(transcript_file, 'w', encoding='utf-8') as f:
            f.write(transcript_text)
        print(f"Saved transcript: {transcript_file}")
        return True
    except Exception as e:
        print(f"Error saving transcript: {e}")
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
    if not os.path.exists(source_path):
        print(f"Source file does not exist: {source_path}")
        return False
    
    if not os.path.exists(destination_folder):
        print(f"Destination folder does not exist: {destination_folder}")
        return False
    
    try:
        if new_filename:
            destination_path = os.path.join(destination_folder, new_filename)
        else:
            filename = os.path.basename(source_path)
            destination_path = os.path.join(destination_folder, filename)
        
        shutil.copy2(source_path, destination_path)
        print(f"Copied file: {source_path} -> {destination_path}")
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
    if not folder_path or not os.path.exists(folder_path):
        print(f"Folder does not exist: {folder_path}")
        return False

    text_file = os.path.join(folder_path, "Thumbnail.txt")

    try:
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(f"title={title}\n\n\n\nscript={transcript}")
        print(f"Saved thumbnail text: {text_file}")
        return True
    except Exception as e:
        print(f"Error saving thumbnail text: {e}")
        return False


def save_short_metadata(folder_path, short_title, short_description, short_transcript):
    """
    Save short form metadata to Short_Metadata.txt in the specified folder.
    Format: SHORT FORM TITLE, SHORT FORM DESCRIPTION, SHORT FORM TRANSCRIPT.

    Returns:
        bool: True if successful, False otherwise
    """
    if not folder_path or not os.path.exists(folder_path):
        print(f"Folder does not exist: {folder_path}")
        return False

    metadata_file = os.path.join(folder_path, "Short_Metadata.txt")

    try:
        with open(metadata_file, 'w', encoding='utf-8') as f:
            f.write(f"SHORT FORM TITLE:\n{short_title}\n\n\n")
            f.write(f"SHORT FORM DESCRIPTION:\n{short_description}\n\n\n")
            f.write(f"SHORT FORM TRANSCRIPT:\n{short_transcript}")
        print(f"Saved short metadata: {metadata_file}")
        return True
    except Exception as e:
        print(f"Error saving short metadata: {e}")
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
    folder_path = os.path.join(base_path, full_folder_name)
    return os.path.exists(folder_path)
