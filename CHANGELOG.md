# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-06-23

First complete release. The application handles the full workflow end to end and
ships as a standalone Windows installer.

### Added

**Core workflow**
- Single-form submission that creates `MAIN`, `EDITOR`, and `THUMB` folders across three
  configured locations in one action.
- Shared timestamp suffix (`YYYY-MM-DD_HH-MM-SS`) applied to all folders from one submission,
  so related folders sort together chronologically.
- `Metadata.txt` (title + description), `Transcript.txt`, and a `Thumbnail.txt` template
  written automatically; thumbnail and voice over files copied to their destinations.
- Collision detection that aborts before writing if a target folder already exists.

**Setup and configuration**
- First-launch setup wizard for the personal, editor, and thumbnail directories.
- Configuration persisted to `%APPDATA%\Youtube metadata saver\settings.json`.
- Follow-up dialog that prompts existing users for the thumbnail path when it is missing,
  so upgrades do not require a reconfiguration from scratch.

**Interface**
- Dark-themed CustomTkinter interface with a scrollable form layout.
- Drag-and-drop file fields with extension validation and clear rejection messages,
  falling back to Browse buttons when `tkinterdnd2` is unavailable.
- Debounced auto-saving drafts (800 ms) restored on the next launch and cleared on submit.
- Input validation for all required fields, plus a confirmation prompt when the transcript
  is under 2,000 words — the usual sign that a description was pasted into the wrong field.
- "Skip Thumbnail" fallback that creates the full folder set without an image when the
  thumbnail is not ready yet.

**Short form content**
- Optional YouTube Shorts section with its own title, description, transcript, and audio.
- Short assets filed into an `EDITOR/Short/` subfolder using a
  `<name>_SHORT_<date>` naming convention.
- `Short_Metadata.txt` written alongside the main metadata.

**History**
- Every submission recorded to `history.json`, newest first.
- History window for browsing past saves, editing stored fields in place, and opening the
  resulting folders directly in the file explorer.

**Distribution**
- PyInstaller spec that bundles CustomTkinter themes and the `tkinterdnd2` Tcl scripts and
  native library into a windowed, console-free executable.
- Inno Setup script producing a per-user installer with Start Menu entries and an optional
  desktop shortcut.

[1.0.0]: https://github.com/khamshayan/Youtube-metadata-saver/releases/tag/v1.0.0
