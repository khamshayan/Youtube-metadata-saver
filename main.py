"""
Main entry point for the YouTube Metadata Saving Platform.
Initializes the application and coordinates between modules.
"""

from datetime import datetime
from pathlib import Path

import customtkinter as ctk
from gui import SetupDialog, MainWindow, ThumbnailPathDialog
from config_handler import load_config, save_config, config_exists
from file_manager import (
    create_folder, save_metadata, save_transcript, copy_file,
    save_thumbnail_text, folder_exists, save_short_metadata,
    create_reference_folder, save_reference_notes, save_reference_thumbnail
)
from history_manager import save_history_entry
from platform_utils import write_text_file


class YouTubeMetadataApp:
    """Main application class."""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.personal_path = None
        self.editor_path = None
        self.thumbnail_base_path = None

        # Check configuration
        self.check_initial_setup()
    
    def check_initial_setup(self):
        """Check if this is the first launch and prompt for setup."""
        if not config_exists():
            # First launch - show setup dialog
            setup_dialog = SetupDialog(self.root)
            self.root.wait_window(setup_dialog.dialog)

            if setup_dialog.completed:
                self.personal_path = setup_dialog.personal_path
                self.editor_path = setup_dialog.editor_path
                self.thumbnail_base_path = setup_dialog.thumbnail_base_path
                save_config(self.personal_path, self.editor_path, self.thumbnail_base_path)
                self.show_main_window()
            else:
                self.root.destroy()
        else:
            # Load existing configuration
            config = load_config()
            if config:
                self.personal_path = config.get("personal_path")
                self.editor_path = config.get("editor_path")
                self.thumbnail_base_path = config.get("thumbnail_base_path")

                # Existing users who don't yet have a thumbnail path configured
                if not self.thumbnail_base_path:
                    thumb_dialog = ThumbnailPathDialog(self.root)
                    self.root.wait_window(thumb_dialog.dialog)
                    if thumb_dialog.completed:
                        self.thumbnail_base_path = thumb_dialog.thumbnail_base_path
                        save_config(self.personal_path, self.editor_path, self.thumbnail_base_path)
                    else:
                        self.root.destroy()
                        return

                self.show_main_window()
            else:
                self.root.destroy()
    
    def show_main_window(self):
        """Display the main application window."""
        self.main_window = MainWindow(self.root, self.process_metadata)
    
    def process_metadata(self, inputs):
        """
        Process the metadata and create folders/files.

        Args:
            inputs (dict): Dictionary containing all user inputs
        """
        try:
            folder_name = inputs["folder_name"].strip()
            skip_thumbnail = inputs.get("skip_thumbnail", False)

            # Generate a single timestamp for this processing session so all
            # folders share the same suffix and sort together chronologically.
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            timestamped_name = f"{folder_name} - {timestamp}"

            # Check if folders already exist
            if folder_exists(self.personal_path, timestamped_name, "MAIN"):
                self.main_window.show_error(
                    f"Folder '{timestamped_name} - MAIN' already exists in Personal Path"
                )
                return

            if folder_exists(self.editor_path, timestamped_name, "EDITOR"):
                self.main_window.show_error(
                    f"Folder '{timestamped_name} - EDITOR' already exists in Editor Path"
                )
                return

            # Create MAIN folder
            main_folder = create_folder(self.personal_path, timestamped_name, "MAIN")
            if not main_folder:
                self.main_window.show_error("Failed to create MAIN folder")
                return

            # Save metadata in MAIN folder
            if not save_metadata(
                main_folder,
                inputs["video_title"],
                inputs["description"]
            ):
                self.main_window.show_error("Failed to save metadata")
                return

            # Copy thumbnail to MAIN folder (skipped when no thumbnail is available)
            if not skip_thumbnail:
                if not copy_file(inputs["thumbnail"], main_folder):
                    self.main_window.show_error("Failed to copy thumbnail")
                    return

            # Create EDITOR folder
            editor_folder = create_folder(self.editor_path, timestamped_name, "EDITOR")
            if not editor_folder:
                self.main_window.show_error("Failed to create EDITOR folder")
                return

            # Save transcript in EDITOR folder
            if not save_transcript(editor_folder, inputs["transcript"]):
                self.main_window.show_error("Failed to save transcript")
                return

            # Copy voice over to EDITOR folder
            if not copy_file(inputs["voiceover"], editor_folder):
                self.main_window.show_error("Failed to copy voice over")
                return

            # Create THUMB folder inside YT Thumbnails parent — always created
            yt_thumbnails_dir = Path(self.thumbnail_base_path) / "YT Thumbnails"
            yt_thumbnails_dir.mkdir(parents=True, exist_ok=True)

            thumb_folder = create_folder(yt_thumbnails_dir, timestamped_name, "THUMB")
            if not thumb_folder:
                self.main_window.show_error("Failed to create THUMB folder")
                return

            # Image is only copied when a thumbnail file is available
            if not skip_thumbnail:
                if not copy_file(inputs["thumbnail"], thumb_folder):
                    self.main_window.show_error("Failed to copy thumbnail to THUMB folder")
                    return

            if not save_thumbnail_text(thumb_folder, inputs["video_title"], inputs["transcript"]):
                self.main_window.show_error("Failed to create thumbnail text file")
                return

            # ── Reference material ─────────────────────────────────────────
            # Lives in a 'Reference' subfolder of THUMB. MAIN and EDITOR are
            # untouched by this feature.
            reference_note = self.process_reference_material(thumb_folder, inputs)
            if reference_note is None:
                return  # error already surfaced

            # ── Short form content ─────────────────────────────────────────
            short_note = ""
            if inputs.get("short_form_enabled"):
                date_str = datetime.now().strftime("%Y-%m-%d")
                short_folder = Path(editor_folder) / "Short"
                short_folder.mkdir(parents=True, exist_ok=True)

                # Short transcript in Short subfolder
                short_transcript_name = f"{folder_name}_SHORT_{date_str}_Transcript.txt"
                short_transcript_path = short_folder / short_transcript_name
                if not write_text_file(short_transcript_path, inputs["short_transcript"]):
                    self.main_window.show_error("Failed to save short transcript")
                    return

                # Short audio in Short subfolder with naming convention
                short_audio = inputs.get("short_audio", "")
                if short_audio:
                    audio_ext = Path(short_audio).suffix
                    short_audio_name = f"{folder_name}_SHORT_{date_str}{audio_ext}"
                    if not copy_file(short_audio, short_folder, short_audio_name):
                        self.main_window.show_error("Failed to copy short audio")
                        return

                # Short metadata (title + description + transcript) in MAIN folder
                if not save_short_metadata(
                    main_folder,
                    inputs["short_title"],
                    inputs["short_description"],
                    inputs["short_transcript"]
                ):
                    self.main_window.show_error("Failed to save short form metadata")
                    return

                short_note = f"✓ Short form saved in EDITOR/Short subfolder\n"

            # Attach folder paths so history can open them later
            inputs["main_folder_path"] = str(main_folder)
            inputs["editor_folder_path"] = str(editor_folder)

            # Save to history
            save_history_entry(inputs)

            # Build success message
            thumb_note = "" if not skip_thumbnail else " (image not included)"
            thumb_line = f"✓ {timestamped_name} - THUMB (inside YT Thumbnails){thumb_note}\n"
            self.main_window.show_success(
                f"Successfully created:\n\n"
                f"✓ {timestamped_name} - MAIN (at Personal Path)\n"
                f"✓ {timestamped_name} - EDITOR (at Editor Path)\n"
                f"{thumb_line}"
                f"{reference_note}"
                f"{short_note}\n"
                f"All files have been saved and copied."
            )

            # Clear inputs
            self.main_window.clear_all()

        except Exception as e:
            self.main_window.show_error(f"An unexpected error occurred: {str(e)}")
            print(f"Error: {e}")
    
    def process_reference_material(self, thumb_folder, inputs):
        """
        Create the 'Reference' subfolder inside the THUMB folder and populate it.

        Granular behaviour:
          * only one field skipped  -> notes file holds just the other one
          * both skipped            -> no notes file is written at all
          * neither skipped         -> both are included
        The reference thumbnail is copied in when one was attached, and its
        absence never blocks folder creation.

        Args:
            thumb_folder (str): Path to the already-created THUMB folder
            inputs (dict): User inputs; mutated with the results for history

        Returns:
            str: A summary line for the success dialog, or None if creation
                 failed (in which case the error has already been shown).
        """
        skip_title = inputs.get("skip_reference_title", False)
        skip_transcript = inputs.get("skip_reference_transcript", False)
        reference_image = inputs.get("reference_thumbnail", "")

        inputs["reference_notes_created"] = False
        inputs["reference_folder_path"] = ""

        reference_folder = create_reference_folder(thumb_folder)
        if not reference_folder:
            self.main_window.show_error("Failed to create Reference folder inside THUMB")
            return None

        inputs["reference_folder_path"] = str(reference_folder)

        notes_created = save_reference_notes(
            reference_folder,
            inputs.get("reference_title", ""),
            inputs.get("reference_transcript", ""),
            skip_title=skip_title,
            skip_transcript=skip_transcript
        )

        # A False return when both fields were skipped is the expected path,
        # not a failure — only treat it as an error if something was meant
        # to be written.
        if not notes_created and not (skip_title and skip_transcript):
            self.main_window.show_error("Failed to save Reference Notes file")
            return None

        inputs["reference_notes_created"] = notes_created

        image_saved = False
        if reference_image:
            image_saved = save_reference_thumbnail(reference_folder, reference_image)
            if not image_saved:
                self.main_window.show_error("Failed to copy the Reference Thumbnail")
                return None

        if notes_created and image_saved:
            detail = "notes + image"
        elif notes_created:
            detail = "notes only"
        elif image_saved:
            detail = "image only"
        else:
            detail = "empty — both fields skipped, no image"

        return f"✓ Reference subfolder inside THUMB ({detail})\n"

    def run(self):
        """Start the application."""
        self.root.mainloop()


if __name__ == "__main__":
    app = YouTubeMetadataApp()
    app.run()
