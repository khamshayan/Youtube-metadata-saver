"""
GUI module for the YouTube Metadata Saving Platform.
Provides CustomTkinter UI components and layout with drag-and-drop support.
"""

import json
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from pathlib import Path
import os
import subprocess
from history_manager import load_history, update_history_entry

try:
    from tkinterdnd2 import DND_FILES, DND_TEXT
    HAS_DND = True
except (ImportError, Exception):
    HAS_DND = False

_APP_DATA_DIR = os.path.join(
    os.environ.get("APPDATA", os.path.expanduser("~")),
    "Youtube metadata saver"
)
os.makedirs(_APP_DATA_DIR, exist_ok=True)
_DRAFT_FILE = os.path.join(_APP_DATA_DIR, "draft.json")


class SetupDialog:
    """Dialog window for initial setup of Personal, Editor, and Thumbnail paths."""

    def __init__(self, root):
        self.root = root
        self.personal_path = None
        self.editor_path = None
        self.thumbnail_base_path = None
        self.completed = False

        self.dialog = ctk.CTkToplevel(root)
        self.dialog.title("Initial Setup")
        self.dialog.geometry("500x420")
        self.dialog.resizable(False, False)

        self.dialog.transient(root)
        self.dialog.grab_set()

        self.setup_ui()

    def setup_ui(self):
        """Setup the UI components for the dialog."""
        ctk.CTkLabel(
            self.dialog,
            text="YouTube Metadata Platform - Initial Setup",
            font=("Arial", 16, "bold"),
            text_color="#00BFFF"
        ).pack(pady=20)

        # Personal Path
        personal_frame = ctk.CTkFrame(self.dialog)
        personal_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(
            personal_frame,
            text="Personal Path (for MAIN folders):",
            font=("Arial", 11)
        ).pack(anchor="w")

        self.personal_path_var = ctk.StringVar()
        ctk.CTkEntry(
            personal_frame,
            textvariable=self.personal_path_var,
            placeholder_text="Select or paste path"
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(
            personal_frame,
            text="Browse",
            width=100,
            command=self.browse_personal_path
        ).pack(side="left")

        # Editor Path
        editor_frame = ctk.CTkFrame(self.dialog)
        editor_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(
            editor_frame,
            text="Editor Path (for EDITOR folders):",
            font=("Arial", 11)
        ).pack(anchor="w")

        self.editor_path_var = ctk.StringVar()
        ctk.CTkEntry(
            editor_frame,
            textvariable=self.editor_path_var,
            placeholder_text="Select or paste path"
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(
            editor_frame,
            text="Browse",
            width=100,
            command=self.browse_editor_path
        ).pack(side="left")

        # Thumbnail Base Path
        thumb_frame = ctk.CTkFrame(self.dialog)
        thumb_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(
            thumb_frame,
            text="Thumbnail Path (YT Thumbnails folder will be created here):",
            font=("Arial", 11)
        ).pack(anchor="w")

        self.thumbnail_base_path_var = ctk.StringVar()
        ctk.CTkEntry(
            thumb_frame,
            textvariable=self.thumbnail_base_path_var,
            placeholder_text="Select or paste path"
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(
            thumb_frame,
            text="Browse",
            width=100,
            command=self.browse_thumbnail_base_path
        ).pack(side="left")

        # Buttons
        button_frame = ctk.CTkFrame(self.dialog)
        button_frame.pack(pady=20)

        ctk.CTkButton(
            button_frame,
            text="Save & Continue",
            command=self.save_paths,
            font=("Arial", 12),
            width=150
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            button_frame,
            text="Exit",
            command=self.root.quit,
            font=("Arial", 12),
            width=150
        ).pack(side="left", padx=10)

    def browse_personal_path(self):
        """Browse for personal path."""
        path = filedialog.askdirectory(title="Select Personal Path")
        if path:
            self.personal_path_var.set(path)

    def browse_editor_path(self):
        """Browse for editor path."""
        path = filedialog.askdirectory(title="Select Editor Path")
        if path:
            self.editor_path_var.set(path)

    def browse_thumbnail_base_path(self):
        """Browse for thumbnail base path."""
        path = filedialog.askdirectory(title="Select Thumbnail Base Path")
        if path:
            self.thumbnail_base_path_var.set(path)

    def save_paths(self):
        """Validate and save paths."""
        personal = self.personal_path_var.get().strip()
        editor = self.editor_path_var.get().strip()
        thumbnail_base = self.thumbnail_base_path_var.get().strip()

        if not personal or not editor or not thumbnail_base:
            messagebox.showerror("Error", "Please specify all three paths")
            return

        if not Path(personal).exists() or not Path(editor).exists() or not Path(thumbnail_base).exists():
            messagebox.showerror("Error", "One or more paths do not exist")
            return

        self.personal_path = personal
        self.editor_path = editor
        self.thumbnail_base_path = thumbnail_base
        self.completed = True
        self.dialog.destroy()


class ThumbnailPathDialog:
    """Dialog shown to existing users who need to set the thumbnail base path."""

    def __init__(self, root):
        self.root = root
        self.thumbnail_base_path = None
        self.completed = False

        self.dialog = ctk.CTkToplevel(root)
        self.dialog.title("Thumbnail Path Setup")
        self.dialog.geometry("500x220")
        self.dialog.resizable(False, False)

        self.dialog.transient(root)
        self.dialog.grab_set()

        self._setup_ui()

    def _setup_ui(self):
        ctk.CTkLabel(
            self.dialog,
            text="New: Separate Thumbnail Storage",
            font=("Arial", 15, "bold"),
            text_color="#00BFFF"
        ).pack(pady=(20, 4))

        ctk.CTkLabel(
            self.dialog,
            text="Choose a base directory. A 'YT Thumbnails' folder will be created there.",
            font=("Arial", 11),
            text_color="#AAAAAA"
        ).pack(pady=(0, 14))

        path_frame = ctk.CTkFrame(self.dialog)
        path_frame.pack(pady=4, padx=20, fill="x")

        self.path_var = ctk.StringVar()
        ctk.CTkEntry(
            path_frame,
            textvariable=self.path_var,
            placeholder_text="Select or paste path"
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(
            path_frame,
            text="Browse",
            width=100,
            command=self._browse
        ).pack(side="left")

        ctk.CTkButton(
            self.dialog,
            text="Save & Continue",
            command=self._save,
            font=("Arial", 12),
            width=150
        ).pack(pady=20)

    def _browse(self):
        path = filedialog.askdirectory(title="Select Thumbnail Base Path")
        if path:
            self.path_var.set(path)

    def _save(self):
        path = self.path_var.get().strip()
        if not path:
            messagebox.showerror("Error", "Please specify a path", parent=self.dialog)
            return
        if not Path(path).exists():
            messagebox.showerror("Error", "Path does not exist", parent=self.dialog)
            return
        self.thumbnail_base_path = path
        self.completed = True
        self.dialog.destroy()


class MainWindow:
    """Main application window."""

    def __init__(self, root, on_process_callback):
        self.root = root
        self.on_process_callback = on_process_callback
        self._draft_after_id = None
        self._loading_draft = False

        self.root.title("YouTube Metadata Saving Platform")
        self.root.geometry("700x900")

        # Configure color scheme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.setup_ui()

    def setup_ui(self):
        """Setup the main UI components."""
        # Header
        header = ctk.CTkLabel(
            self.root,
            text="YouTube Metadata Saving Platform",
            font=("Arial", 20, "bold"),
            text_color="#00BFFF"
        )
        header.pack(pady=20)

        # Draft indicator label
        self.draft_label = ctk.CTkLabel(
            self.root,
            text="",
            font=("Arial", 10),
            text_color="#FFA500"
        )
        self.draft_label.pack(pady=(0, 5))

        # Main frame with scrolling
        main_frame = ctk.CTkScrollableFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Folder Name
        self.add_input_field(main_frame, "Folder Name", "folder_name", "e.g., Video_001")

        # Video Title
        self.add_input_field(main_frame, "Video Title", "video_title", "e.g., My Awesome Video")

        # Video Description
        self.add_text_area(main_frame, "Video Description", "description")

        # Transcript
        self.add_text_area(main_frame, "Transcript", "transcript")

        # Thumbnail
        self.add_file_selector(
            main_frame, "Thumbnail (Image)", "thumbnail",
            allowed_extensions={".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"},
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.webp *.tiff")]
        )

        # Skip Thumbnail toggle
        skip_frame = ctk.CTkFrame(main_frame)
        skip_frame.pack(pady=(0, 5), fill="x")
        self.skip_thumbnail_var = tk.BooleanVar(value=False)
        self.skip_thumbnail_var.trace_add("write", lambda *args: self._schedule_draft_save())
        ctk.CTkCheckBox(
            skip_frame,
            text="Skip Thumbnail  —  no thumbnail available yet (emergency fallback)",
            variable=self.skip_thumbnail_var,
            onvalue=True,
            offvalue=False,
            font=("Arial", 11),
            text_color="#FFA500"
        ).pack(anchor="w", padx=10, pady=8)

        # Voice Over
        self.add_file_selector(
            main_frame, "Voice Over (Audio)", "voiceover",
            allowed_extensions={".mp3", ".wav", ".aac", ".ogg", ".flac", ".m4a", ".wma", ".opus"},
            filetypes=[("Audio files", "*.mp3 *.wav *.aac *.ogg *.flac *.m4a *.wma *.opus")]
        )

        # ── Short Form Content section ──────────────────────────────────────
        ctk.CTkFrame(main_frame, height=2, fg_color="#333333").pack(fill="x", pady=(15, 5))

        short_toggle_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        short_toggle_frame.pack(pady=5, fill="x")

        ctk.CTkLabel(
            short_toggle_frame,
            text="Short Form Content (YouTube Shorts)",
            font=("Arial", 12, "bold"),
            text_color="#FFFFFF"
        ).pack(side="left", padx=10)

        self.short_form_var = tk.BooleanVar(value=False)
        ctk.CTkSwitch(
            short_toggle_frame,
            text="Enable",
            variable=self.short_form_var,
            command=self._toggle_short_form,
            font=("Arial", 11),
            progress_color="#FFA500"
        ).pack(side="left", padx=10)

        # Short form container — hidden by default, parented to main_frame
        self.short_form_frame = ctk.CTkFrame(main_frame, fg_color="#1e1e1e", border_width=1, border_color="#FFA500")
        self._build_short_form_fields()

        # Load draft after all widgets exist
        self._load_draft()

        # Buttons Frame
        button_frame = ctk.CTkFrame(self.root)
        button_frame.pack(pady=20)

        ctk.CTkButton(
            button_frame,
            text="Process",
            command=self.on_process,
            font=("Arial", 14, "bold"),
            width=150,
            height=50
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            button_frame,
            text="Clear",
            command=self.clear_all,
            font=("Arial", 14, "bold"),
            width=150,
            height=50
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            button_frame,
            text="History",
            command=self.open_history,
            font=("Arial", 14, "bold"),
            width=150,
            height=50,
            fg_color="#2a5a8a",
            hover_color="#1a4a7a"
        ).pack(side="left", padx=10)

    def _build_short_form_fields(self):
        """Build the short form content fields inside short_form_frame."""
        ctk.CTkLabel(
            self.short_form_frame,
            text="  Short Form Content",
            font=("Arial", 13, "bold"),
            text_color="#FFA500"
        ).pack(anchor="w", padx=10, pady=(10, 2))

        ctk.CTkLabel(
            self.short_form_frame,
            text="  No thumbnail needed for Shorts.",
            font=("Arial", 10),
            text_color="#888888"
        ).pack(anchor="w", padx=10, pady=(0, 8))

        self.add_input_field(self.short_form_frame, "Short Title", "short_title", "e.g., My Short Video")
        self.add_text_area(self.short_form_frame, "Short Description", "short_description")
        self.add_text_area(self.short_form_frame, "Short Transcript", "short_transcript")
        self.add_file_selector(
            self.short_form_frame, "Short Audio", "short_audio",
            allowed_extensions={".mp3", ".wav", ".aac", ".ogg", ".flac", ".m4a", ".wma", ".opus"},
            filetypes=[("Audio files", "*.mp3 *.wav *.aac *.ogg *.flac *.m4a *.wma *.opus")]
        )

    def _toggle_short_form(self):
        """Show or hide the short form fields based on the toggle state."""
        if self.short_form_var.get():
            self.short_form_frame.pack(pady=10, padx=5, fill="x")
        else:
            self.short_form_frame.pack_forget()
        self._schedule_draft_save()

    # ── Draft auto-save ────────────────────────────────────────────────────

    def _schedule_draft_save(self, event=None):
        """Debounce draft saves — fire 800 ms after the last change."""
        if self._loading_draft:
            return
        if self._draft_after_id:
            self.root.after_cancel(self._draft_after_id)
        self._draft_after_id = self.root.after(800, self._save_draft)

    def _save_draft(self):
        """Write current field values to draft.json."""
        self._draft_after_id = None
        try:
            draft = {
                "folder_name": self.folder_name_entry.get(),
                "video_title": self.video_title_entry.get(),
                "description": self.description_text.get("1.0", "end-1c"),
                "transcript": self.transcript_text.get("1.0", "end-1c"),
                "thumbnail": self.thumbnail_entry.get(),
                "voiceover": self.voiceover_entry.get(),
                "skip_thumbnail": self.skip_thumbnail_var.get(),
                "short_form_enabled": self.short_form_var.get(),
            }
            if self.short_form_var.get():
                draft.update({
                    "short_title": self.short_title_entry.get(),
                    "short_description": self.short_description_text.get("1.0", "end-1c"),
                    "short_transcript": self.short_transcript_text.get("1.0", "end-1c"),
                    "short_audio": self.short_audio_entry.get(),
                })
            with open(_DRAFT_FILE, 'w', encoding='utf-8') as f:
                json.dump(draft, f, indent=2, ensure_ascii=False)
            self.draft_label.configure(text="Draft auto-saved")
        except Exception as e:
            print(f"Error saving draft: {e}")

    def _load_draft(self):
        """Populate fields from draft.json if it exists."""
        if not os.path.exists(_DRAFT_FILE):
            return
        try:
            with open(_DRAFT_FILE, 'r', encoding='utf-8') as f:
                draft = json.load(f)
        except Exception:
            return

        if not draft:
            return

        self._loading_draft = True
        try:
            if draft.get("folder_name"):
                self.folder_name_entry.insert(0, draft["folder_name"])
            if draft.get("video_title"):
                self.video_title_entry.insert(0, draft["video_title"])
            if draft.get("description"):
                self.description_text.insert("1.0", draft["description"])
            if draft.get("transcript"):
                self.transcript_text.insert("1.0", draft["transcript"])

            thumb = draft.get("thumbnail", "")
            if thumb and os.path.exists(thumb):
                self.update_thumbnail(thumb)

            vo = draft.get("voiceover", "")
            if vo and os.path.exists(vo):
                self.update_voiceover(vo)

            self.skip_thumbnail_var.set(draft.get("skip_thumbnail", False))

            if draft.get("short_form_enabled"):
                self.short_form_var.set(True)
                self._toggle_short_form()

                if draft.get("short_title"):
                    self.short_title_entry.insert(0, draft["short_title"])
                if draft.get("short_description"):
                    self.short_description_text.insert("1.0", draft["short_description"])
                if draft.get("short_transcript"):
                    self.short_transcript_text.insert("1.0", draft["short_transcript"])

                sa = draft.get("short_audio", "")
                if sa and os.path.exists(sa):
                    self.update_short_audio(sa)

            if any(draft.get(k) for k in ("folder_name", "video_title", "description", "transcript")):
                self.draft_label.configure(text="Draft restored — continue where you left off")
        finally:
            self._loading_draft = False

    def clear_draft(self):
        """Cancel any pending draft save and delete the draft file."""
        if self._draft_after_id:
            self.root.after_cancel(self._draft_after_id)
            self._draft_after_id = None
        try:
            if os.path.exists(_DRAFT_FILE):
                os.remove(_DRAFT_FILE)
        except Exception as e:
            print(f"Error clearing draft: {e}")
        self.draft_label.configure(text="")

    # ── Field builders ─────────────────────────────────────────────────────

    def add_input_field(self, parent, label_text, key, placeholder=""):
        """Add a single-line input field."""
        frame = ctk.CTkFrame(parent)
        frame.pack(pady=10, fill="x")

        ctk.CTkLabel(
            frame,
            text=label_text,
            font=("Arial", 11, "bold")
        ).pack(anchor="w")

        entry = ctk.CTkEntry(
            frame,
            placeholder_text=placeholder,
            height=35
        )
        entry.pack(fill="x", pady=(5, 0))
        entry.bind("<KeyRelease>", self._schedule_draft_save)

        setattr(self, f"{key}_entry", entry)

    def add_text_area(self, parent, label_text, key):
        """Add a multi-line text area."""
        frame = ctk.CTkFrame(parent)
        frame.pack(pady=10, fill="x")

        ctk.CTkLabel(
            frame,
            text=label_text,
            font=("Arial", 11, "bold")
        ).pack(anchor="w")

        text_area = ctk.CTkTextbox(
            frame,
            height=100
        )
        text_area.pack(fill="x", pady=(5, 0))

        word_count_label = ctk.CTkLabel(
            frame,
            text="0 words",
            font=("Arial", 15, "bold"),
            text_color="#AAAAAA",
            anchor="e"
        )
        word_count_label.pack(anchor="e", pady=(4, 0))

        def update_word_count(event=None):
            text = text_area.get("1.0", "end-1c")
            count = len(text.split()) if text.strip() else 0
            word_count_label.configure(text=f"{count} word{'s' if count != 1 else ''}")

        text_area.bind("<KeyRelease>", update_word_count)
        text_area.bind("<<Paste>>", lambda e: text_area.after(10, update_word_count))
        text_area.bind("<KeyRelease>", self._schedule_draft_save, add="+")
        text_area.bind("<<Paste>>", lambda e: text_area.after(20, self._schedule_draft_save), add="+")

        setattr(self, f"{key}_text", text_area)

    def add_file_selector(self, parent, label_text, key, allowed_extensions=None, filetypes=None):
        """Add a file selector with browse button and drag-drop zone."""
        frame = ctk.CTkFrame(parent)
        frame.pack(pady=10, fill="x")

        ctk.CTkLabel(
            frame,
            text=label_text,
            font=("Arial", 11, "bold")
        ).pack(anchor="w")

        file_frame = ctk.CTkFrame(frame)
        file_frame.pack(fill="x", pady=(5, 0))

        drop_zone = ctk.CTkFrame(
            file_frame,
            fg_color="#2a2a2a",
            border_width=2,
            border_color="#555555"
        )
        drop_zone.pack(side="left", fill="both", expand=True, padx=(0, 10), ipady=15)

        file_label = ctk.CTkLabel(
            drop_zone,
            text="🎯 Drag file here or use Browse",
            font=("Arial", 10),
            text_color="#888888"
        )
        file_label.pack(pady=15, padx=15, fill="both", expand=True)

        file_path_var = tk.StringVar(value="")

        def update_display(file_path):
            if file_path:
                filename = os.path.basename(file_path)
                file_label.configure(text=f"✓ {filename}", text_color="#00FF00")
                drop_zone.configure(border_color="#00AA00", fg_color="#1a3a1a")
                file_path_var.set(file_path)
            else:
                file_label.configure(text="🎯 Drag file here or use Browse", text_color="#888888")
                drop_zone.configure(border_color="#555555", fg_color="#2a2a2a")
                file_path_var.set("")
            self._schedule_draft_save()

        def browse_file():
            dialog_filetypes = (filetypes or []) + [("All files", "*.*")]
            file_path = filedialog.askopenfilename(
                title=f"Select {label_text}",
                filetypes=dialog_filetypes
            )
            if file_path:
                update_display(file_path)

        def on_drop(event):
            try:
                files = self.root.tk.splitlist(event.data)
                if files:
                    file_path = files[0].strip('{}')
                    if not os.path.exists(file_path):
                        messagebox.showerror("Error", f"File not found: {file_path}")
                        return
                    if allowed_extensions:
                        ext = os.path.splitext(file_path)[1].lower()
                        if ext not in allowed_extensions:
                            allowed_str = ", ".join(sorted(allowed_extensions))
                            messagebox.showerror(
                                "Wrong File Type",
                                f"'{os.path.basename(file_path)}' is not allowed here.\n\n"
                                f"Accepted types: {allowed_str}"
                            )
                            return
                    update_display(file_path)
            except Exception as e:
                print(f"Drop error: {e}")

        def on_enter(e):
            if not file_path_var.get():
                drop_zone.configure(border_color="#00BFFF")
                file_label.configure(text_color="#00BFFF")

        def on_leave(e):
            if not file_path_var.get():
                drop_zone.configure(border_color="#555555")
                file_label.configure(text_color="#888888")

        drop_zone.bind("<Enter>", on_enter)
        drop_zone.bind("<Leave>", on_leave)
        file_label.bind("<Enter>", on_enter)
        file_label.bind("<Leave>", on_leave)

        if HAS_DND:
            try:
                drop_zone.drop_target_register(DND_FILES)
                drop_zone.dnd_bind('<<Drop>>', on_drop)
                file_label.drop_target_register(DND_FILES)
                file_label.dnd_bind('<<Drop>>', on_drop)
            except Exception as e:
                print(f"Note: Native drag-drop not available on this system. Use Browse button instead.")

        ctk.CTkButton(
            file_frame,
            text="Browse",
            command=browse_file,
            width=100,
            height=45
        ).pack(side="left")

        setattr(self, f"{key}_entry", file_path_var)
        setattr(self, f"get_{key}", lambda: file_path_var.get())
        setattr(self, f"update_{key}", update_display)

    # ── Data helpers ───────────────────────────────────────────────────────

    def get_all_inputs(self):
        """Collect all input values."""
        short_enabled = self.short_form_var.get()
        inputs = {
            "folder_name": self.folder_name_entry.get(),
            "video_title": self.video_title_entry.get(),
            "description": self.description_text.get("1.0", "end-1c"),
            "transcript": self.transcript_text.get("1.0", "end-1c"),
            "thumbnail": self.get_thumbnail(),
            "voiceover": self.get_voiceover(),
            "skip_thumbnail": self.skip_thumbnail_var.get(),
            "short_form_enabled": short_enabled,
        }
        if short_enabled:
            inputs.update({
                "short_title": self.short_title_entry.get(),
                "short_description": self.short_description_text.get("1.0", "end-1c"),
                "short_transcript": self.short_transcript_text.get("1.0", "end-1c"),
                "short_audio": self.get_short_audio(),
            })
        return inputs

    def clear_all(self):
        """Clear all input fields and delete the saved draft."""
        self.folder_name_entry.delete(0, "end")
        self.video_title_entry.delete(0, "end")
        self.description_text.delete("1.0", "end")
        self.transcript_text.delete("1.0", "end")
        self.update_thumbnail("")
        self.update_voiceover("")
        self.skip_thumbnail_var.set(False)

        # Clear short form fields
        self.short_title_entry.delete(0, "end")
        self.short_description_text.delete("1.0", "end")
        self.short_transcript_text.delete("1.0", "end")
        self.update_short_audio("")
        self.short_form_var.set(False)
        self.short_form_frame.pack_forget()

        self.clear_draft()

    def on_process(self):
        """Handle process button click."""
        inputs = self.get_all_inputs()

        if not inputs["folder_name"].strip():
            messagebox.showerror("Validation Error", "Folder Name is required")
            return

        if not inputs["video_title"].strip():
            messagebox.showerror("Validation Error", "Video Title is required")
            return

        if not inputs["description"].strip():
            messagebox.showerror("Validation Error", "Video Description is required")
            return

        if not inputs["skip_thumbnail"] and not inputs["thumbnail"]:
            messagebox.showerror("Validation Error", "Thumbnail file is required")
            return

        if not inputs["voiceover"]:
            messagebox.showerror("Validation Error", "Voice Over file is required")
            return

        if not inputs["transcript"].strip():
            messagebox.showerror("Validation Error", "Transcript is required")
            return

        transcript_word_count = len(inputs["transcript"].split())
        if transcript_word_count < 2000:
            proceed = messagebox.askokcancel(
                "Warning: Short Transcript",
                f"Your transcript is only {transcript_word_count} word{'s' if transcript_word_count != 1 else ''}, "
                f"which seems too short.\n\n"
                f"You may have accidentally entered the description instead of the transcript.\n\n"
                f"Click OK to proceed anyway, or Cancel to go back and check."
            )
            if not proceed:
                return

        # Short form validation
        if inputs.get("short_form_enabled"):
            if not inputs.get("short_title", "").strip():
                messagebox.showerror("Validation Error", "Short Title is required when Short Form Content is enabled")
                return
            if not inputs.get("short_description", "").strip():
                messagebox.showerror("Validation Error", "Short Description is required when Short Form Content is enabled")
                return
            if not inputs.get("short_transcript", "").strip():
                messagebox.showerror("Validation Error", "Short Transcript is required when Short Form Content is enabled")
                return
            if not inputs.get("short_audio"):
                messagebox.showerror("Validation Error", "Short Audio file is required when Short Form Content is enabled")
                return

        self.on_process_callback(inputs)

    def open_history(self):
        """Open the history window."""
        HistoryWindow(self.root)

    def show_success(self, message):
        """Show success message."""
        messagebox.showinfo("Success", message)

    def show_error(self, message):
        """Show error message."""
        messagebox.showerror("Error", message)


class HistoryWindow:
    """Window that displays the full save history with editing and folder access."""

    def __init__(self, root):
        self.root = root
        self.history = load_history()
        self._current_index = None
        self._list_frames = []
        self._list_labels = []
        self._edit_fields = {}

        self.window = ctk.CTkToplevel(root)
        self.window.title("Save History")
        self.window.geometry("950x650")
        self.window.transient(root)

        self.setup_ui()

    def setup_ui(self):
        """Build the history window layout."""
        ctk.CTkLabel(
            self.window,
            text="Save History",
            font=("Arial", 18, "bold"),
            text_color="#00BFFF"
        ).pack(pady=15)

        if not self.history:
            ctk.CTkLabel(
                self.window,
                text="No saves yet. Process some metadata to see history here.",
                font=("Arial", 12),
                text_color="#888888"
            ).pack(expand=True)
            return

        content = ctk.CTkFrame(self.window)
        content.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=2)
        content.rowconfigure(0, weight=1)

        left_panel = ctk.CTkScrollableFrame(
            content,
            label_text=f"All Saves ({len(self.history)})",
            label_font=("Arial", 11, "bold"),
            width=270
        )
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        self.detail_panel = ctk.CTkScrollableFrame(
            content,
            label_text="Details",
            label_font=("Arial", 11, "bold")
        )
        self.detail_panel.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        ctk.CTkLabel(
            self.detail_panel,
            text="Select an entry on the left to view and edit its details.",
            font=("Arial", 11),
            text_color="#888888"
        ).pack(pady=30)

        for i, entry in enumerate(self.history):
            self._add_list_item(left_panel, entry, i)

    def _add_list_item(self, parent, entry, index):
        """Add one clickable row to the list panel."""
        frame = ctk.CTkFrame(parent, fg_color="#252525", corner_radius=6)
        frame.pack(fill="x", pady=3, padx=4)
        self._list_frames.append(frame)

        ts_label = ctk.CTkLabel(
            frame,
            text=entry.get("timestamp", ""),
            font=("Arial", 9),
            text_color="#777777"
        )
        ts_label.pack(anchor="w", padx=10, pady=(7, 0))

        folder_label = ctk.CTkLabel(
            frame,
            text=entry.get("folder_name", "(no folder)"),
            font=("Arial", 11, "bold"),
            text_color="#FFFFFF"
        )
        folder_label.pack(anchor="w", padx=10)

        title_label = ctk.CTkLabel(
            frame,
            text=entry.get("video_title", ""),
            font=("Arial", 10),
            text_color="#AAAAAA"
        )
        title_label.pack(anchor="w", padx=10, pady=(0, 7))

        self._list_labels.append((folder_label, title_label))

        def on_click(e, idx=index, f=frame):
            self._highlight(f)
            self._show_detail(idx)

        def on_enter(e, f=frame):
            if f.cget("fg_color") != "#1a4a7a":
                f.configure(fg_color="#303030")

        def on_leave(e, f=frame):
            if f.cget("fg_color") != "#1a4a7a":
                f.configure(fg_color="#252525")

        for widget in (frame, ts_label, folder_label, title_label):
            widget.bind("<Button-1>", on_click)
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

    def _highlight(self, selected_frame):
        for f in self._list_frames:
            f.configure(fg_color="#1a4a7a" if f is selected_frame else "#252525")

    def _show_detail(self, index):
        """Populate the detail panel with editable fields for the selected entry."""
        self._current_index = index
        self._edit_fields = {}
        entry = self.history[index]

        for widget in self.detail_panel.winfo_children():
            widget.destroy()

        btn_frame = ctk.CTkFrame(self.detail_panel, fg_color="transparent")
        btn_frame.pack(fill="x", padx=12, pady=(12, 4))

        main_path = entry.get("main_folder_path", "")
        editor_path = entry.get("editor_folder_path", "")

        ctk.CTkButton(
            btn_frame,
            text="Open MAIN Folder",
            command=lambda p=main_path: self._open_folder(p),
            width=160,
            height=36,
            fg_color="#1a5a2a",
            hover_color="#0f4a1a"
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_frame,
            text="Open EDITOR Folder",
            command=lambda p=editor_path: self._open_folder(p),
            width=160,
            height=36,
            fg_color="#1a3a5a",
            hover_color="#0f2a4a"
        ).pack(side="left")

        ctk.CTkFrame(self.detail_panel, height=1, fg_color="#333333").pack(
            fill="x", padx=12, pady=(10, 0)
        )

        self._add_readonly(
            "Saved On", entry.get("timestamp", ""),
            "Thumbnail File", entry.get("thumbnail", ""),
            "Voice Over File", entry.get("voiceover", "")
        )

        self._add_entry_field("Folder Name", "folder_name", entry.get("folder_name", ""))
        self._add_entry_field("Video Title", "video_title", entry.get("video_title", ""))
        self._add_text_field("Description", "description", entry.get("description", ""))
        self._add_text_field("Transcript", "transcript", entry.get("transcript", ""))

        # Show short form data if present
        if entry.get("short_form_enabled"):
            ctk.CTkFrame(self.detail_panel, height=1, fg_color="#FFA500").pack(
                fill="x", padx=12, pady=(12, 0)
            )
            ctk.CTkLabel(
                self.detail_panel,
                text="Short Form Content",
                font=("Arial", 11, "bold"),
                text_color="#FFA500"
            ).pack(anchor="w", padx=12, pady=(8, 2))
            self._add_readonly(
                "Short Audio", entry.get("short_audio", "")
            )
            self._add_entry_field("Short Title", "short_title", entry.get("short_title", ""))
            self._add_text_field("Short Description", "short_description", entry.get("short_description", ""))
            self._add_text_field("Short Transcript", "short_transcript", entry.get("short_transcript", ""))

        ctk.CTkButton(
            self.detail_panel,
            text="Save Changes",
            command=self._save_changes,
            font=("Arial", 12, "bold"),
            width=160,
            height=38,
            fg_color="#2a5a8a",
            hover_color="#1a4a7a"
        ).pack(pady=14)

    def _add_readonly(self, *pairs):
        for i in range(0, len(pairs), 2):
            label, value = pairs[i], pairs[i + 1]
            row = ctk.CTkFrame(self.detail_panel, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=(8, 0))
            ctk.CTkLabel(
                row, text=f"{label}:", font=("Arial", 10, "bold"),
                text_color="#777777", width=110, anchor="w"
            ).pack(side="left")
            ctk.CTkLabel(
                row, text=value or "(none)", font=("Arial", 10),
                text_color="#AAAAAA", anchor="w"
            ).pack(side="left", fill="x", expand=True)

    def _add_entry_field(self, label, key, value):
        ctk.CTkLabel(
            self.detail_panel, text=label,
            font=("Arial", 10, "bold"), text_color="#00BFFF", anchor="w"
        ).pack(anchor="w", padx=12, pady=(12, 2))

        entry_widget = ctk.CTkEntry(self.detail_panel, height=34)
        entry_widget.pack(fill="x", padx=12)
        entry_widget.insert(0, value)
        self._edit_fields[key] = ("entry", entry_widget)

    def _add_text_field(self, label, key, value):
        ctk.CTkLabel(
            self.detail_panel, text=label,
            font=("Arial", 10, "bold"), text_color="#00BFFF", anchor="w"
        ).pack(anchor="w", padx=12, pady=(12, 2))

        tb = ctk.CTkTextbox(self.detail_panel, height=100)
        tb.pack(fill="x", padx=12, pady=(0, 2))
        tb.insert("1.0", value)
        self._edit_fields[key] = ("text", tb)

    def _save_changes(self):
        if self._current_index is None:
            return

        updated = dict(self.history[self._current_index])

        for key, (kind, widget) in self._edit_fields.items():
            updated[key] = widget.get() if kind == "entry" else widget.get("1.0", "end-1c")

        if update_history_entry(self._current_index, updated):
            self.history[self._current_index] = updated
            folder_lbl, title_lbl = self._list_labels[self._current_index]
            folder_lbl.configure(text=updated.get("folder_name", ""))
            title_lbl.configure(text=updated.get("video_title", ""))
            messagebox.showinfo("Saved", "Changes saved to history.", parent=self.window)
        else:
            messagebox.showerror("Error", "Failed to save changes.", parent=self.window)

    def _open_folder(self, path):
        if not path:
            messagebox.showerror(
                "Not Available",
                "Folder path was not stored for this entry.\n"
                "Re-process the video to get folder links.",
                parent=self.window
            )
            return
        if not os.path.exists(path):
            messagebox.showerror(
                "Folder Not Found",
                f"The folder no longer exists at:\n{path}",
                parent=self.window
            )
            return
        os.startfile(path)
