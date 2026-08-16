<div align="center">

# YouTube Metadata Saver

**A desktop app that turns one form submission into a complete, correctly-named YouTube production folder set.**

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-1f6aa5)](https://github.com/TomSchimansky/CustomTkinter)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)](#installation)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-orange.svg)](CHANGELOG.md)

</div>

---

## Overview

Publishing a YouTube video means shuffling the same assets into the same folders every single time — the title and description somewhere you can find them, the transcript and voice over where your editor can reach them, the thumbnail where your designer works. Doing it by hand is repetitive, and one inconsistent folder name is enough to lose an asset.

YouTube Metadata Saver collapses that routine into a single form. You fill in the metadata, drop in the thumbnail and voice over, and press **Process**. The app creates three timestamped folders in the three locations you configured once, writes the text files, copies the media, and records the whole thing in a searchable history.

It was built for a real two-person workflow — a creator and an editor working out of separate synced folders — and the folder conventions reflect that.

## Features

- **One-time setup wizard** — point the app at your personal, editor, and thumbnail directories on first launch; the configuration persists in `%APPDATA%` and never has to be entered again.
- **Three-way folder routing** — every submission produces a `MAIN`, an `EDITOR`, and a `THUMB` folder, each in its own location, each carrying the same timestamp so they sort together chronologically.
- **Drag and drop with type checking** — drop a thumbnail or an audio file straight onto the field. Files with the wrong extension are rejected with an explanation instead of being silently accepted.
- **Automatic draft saving** — every keystroke is debounced and written to disk. Close the app mid-form, reopen it, and your work is exactly where you left it.
- **YouTube Shorts support** — an optional section captures a separate short title, description, transcript, and audio, filed into a `Short/` subfolder with its own naming convention.
- **Input validation with a transcript sanity check** — required fields are enforced, and a transcript under 2,000 words triggers a confirmation prompt, because that usually means the description was pasted into the wrong box.
- **Skip Thumbnail fallback** — for the case where the video is ready but the thumbnail isn't. Folders are still created; only the image copy is skipped.
- **Editable save history** — browse every past submission, correct a typo in a saved title, and open the resulting folders in Explorer without leaving the app.
- **Ships as a real Windows app** — a PyInstaller spec and an Inno Setup script build a standalone `.exe` and an installer, so the end user never sees Python.

## Output Structure

Submitting the folder name `Video_001` produces the following, where `<timestamp>` is the moment you pressed Process (`2026-08-16_14-30-00`):

```
<Personal Path>/
└── Video_001 - <timestamp> - MAIN/
    ├── Metadata.txt              # title, blank lines, description
    ├── thumbnail.jpg             # copied as-is
    └── Short_Metadata.txt        # only when Short Form is enabled

<Editor Path>/
└── Video_001 - <timestamp> - EDITOR/
    ├── Transcript.txt
    ├── voiceover.mp3             # copied as-is
    └── Short/                    # only when Short Form is enabled
        ├── Video_001_SHORT_<date>_Transcript.txt
        └── Video_001_SHORT_<date>.mp3

<Thumbnail Path>/YT Thumbnails/
└── Video_001 - <timestamp> - THUMB/
    ├── thumbnail.jpg             # skipped when "Skip Thumbnail" is checked
    └── Thumbnail.txt             # title= / script= template for the designer
```

The shared timestamp is the point: the three folders belong to one video and stay adjacent to each other no matter how many videos come later.

## Installation

### Option 1 — Installer (end users)

Download the latest `Youtube metadata saver Setup.exe` from the [Releases](../../releases) page and run it. No Python required. The installer requests no admin rights and offers an optional desktop shortcut.

### Option 2 — From source (developers)

```bash
git clone https://github.com/khamshayan/Youtube-metadata-saver.git
cd Youtube-metadata-saver

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
python main.py
```

**Requirements:** Python 3.9 or newer.

| Package | Purpose |
| --- | --- |
| `customtkinter` | Modern dark-themed widget set |
| `pillow` | Image handling for CustomTkinter |
| `tkinterdnd2` | Native drag-and-drop targets |

Drag and drop is the only optional piece — if `tkinterdnd2` fails to load, the app falls back to Browse buttons rather than crashing.

## Usage

1. **First launch** — the setup wizard asks for three directories:
   - **Personal Path** — where `MAIN` folders (metadata + thumbnail) are created
   - **Editor Path** — where `EDITOR` folders (transcript + voice over) are created, typically a shared or synced drive
   - **Thumbnail Path** — the parent under which a `YT Thumbnails` folder holds all `THUMB` folders
2. **Fill the form** — folder name, video title, description, transcript, thumbnail, voice over.
3. *(Optional)* **Enable Short Form Content** and fill in the Shorts fields.
4. **Press Process** — folders are created, files written and copied, and a summary confirms exactly what was made.
5. **Press History** at any time to review, edit, or open past saves.

## Configuration

The app stores its state outside the repository, in `%APPDATA%\Youtube metadata saver\`:

| File | Contents |
| --- | --- |
| `settings.json` | The three configured directory paths |
| `history.json` | Every processed submission, newest first |
| `draft.json` | The in-progress form, auto-saved and cleared on submit |

Deleting `settings.json` re-triggers the setup wizard on the next launch.

## Building from Source

Building the distributable is a two-stage process on Windows.

**1. Build the executable** with [PyInstaller](https://pyinstaller.org/):

```bash
pip install pyinstaller
pyinstaller main.spec
```

The spec file collects the CustomTkinter themes and the `tkinterdnd2` Tcl scripts and native library, which the default PyInstaller analysis misses. Output lands in `dist/Youtube metadata saver/`.

**2. Build the installer** with [Inno Setup](https://jrsoftware.org/isinfo.php) — open `installer.iss` in the Inno Setup Compiler and build, or:

```bash
iscc installer.iss
```

The signed-off installer appears in `installer_output/`.

## Project Structure

```
Youtube-metadata-saver/
├── main.py               # Entry point; orchestrates setup, GUI, and processing
├── gui.py                # All CustomTkinter windows, dialogs, and widgets
├── file_manager.py       # Folder creation, file writing, and copying
├── config_handler.py     # Reads and writes the persisted path configuration
├── history_manager.py    # Save-history persistence and editing
├── requirements.txt      # Runtime dependencies
├── main.spec             # PyInstaller build definition
└── installer.iss         # Inno Setup installer definition
```

The layout is deliberately flat and single-purpose: `main.py` holds the workflow, and each module owns exactly one concern. The GUI never touches the filesystem directly, and the file layer knows nothing about widgets.

## Roadmap

- [ ] Cross-platform configuration paths (macOS and Linux support)
- [ ] Configurable folder-naming templates
- [ ] Search and filter in the history window
- [ ] Bulk export of history to CSV
- [ ] Optional YouTube API integration for direct uploads

## Contributing

Contributions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) for the workflow and code conventions.

## License

Released under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">

Built by [Khamshayan](https://github.com/khamshayan)

</div>
