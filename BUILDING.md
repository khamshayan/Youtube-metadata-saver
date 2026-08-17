# Building the installers

One codebase, one PyInstaller spec (`main.spec`), one build script (`build.py`).

> **PyInstaller cannot cross-compile.** The Windows installer must be built on
> Windows and the macOS `.dmg` on macOS. There is no way to produce a Windows
> `.exe` from a Mac.

Both builds are driven by the same command:

```bash
python build.py
```

Artifacts land in `installer_output/` (git-ignored, along with `build/` and `dist/`).

---

## macOS

### Prerequisites

The system Python ships Tcl/Tk **8.5**, which CustomTkinter renders poorly on.
Use a Python with Tk **8.6**:

```bash
brew install python@3.11 python-tk@3.11
```

### Build

```bash
/opt/homebrew/bin/python3.11 -m venv venv
./venv/bin/pip install -r requirements.txt pyinstaller
./venv/bin/python build.py
```

### Output

```
dist/Youtube metadata saver.app
installer_output/Youtube metadata saver 1.0.0 (Apple Silicon).dmg
```

The `.dmg` opens to a drag-to-`Applications` window.

### Architecture

The build targets the **host** architecture only — building on Apple Silicon
produces an arm64 app that will **not** run on Intel Macs. For a universal
binary you need a universal2 Python and `target_arch='universal2'` in
`main.spec`; every dependency must also ship universal2 wheels.

### Signing and Gatekeeper

The bundle is **ad-hoc signed, not notarised**. On any Mac other than the build
machine, the first launch is blocked by Gatekeeper. Users can right-click →
**Open**, or:

```bash
xattr -dr com.apple.quarantine "/Applications/Youtube metadata saver.app"
```

To distribute properly you need a paid Apple Developer account, then sign and
notarise:

```bash
codesign --deep --force --options runtime \
  --sign "Developer ID Application: YOUR NAME (TEAMID)" \
  "dist/Youtube metadata saver.app"

xcrun notarytool submit "installer_output/…​.dmg" \
  --apple-id you@example.com --team-id TEAMID --wait

xcrun stapler staple "installer_output/…​.dmg"
```

---

## Windows

### Prerequisites

- Python 3.11 from [python.org](https://www.python.org/downloads/windows/)
  (bundles Tk 8.6 — do not use the Microsoft Store build)
- [Inno Setup 6](https://jrsoftware.org/isdl.php)

### Build

```bat
py -3.11 -m venv venv
venv\Scripts\pip install -r requirements.txt pyinstaller
venv\Scripts\python build.py
```

`build.py` finds `ISCC.exe` on `PATH` or in the default Inno Setup location. If
it is missing, the app folder is still built and you can compile manually:

```bat
ISCC installer.iss
```

### Output

```
dist\Youtube metadata saver\
installer_output\Youtube metadata saver 1.0.0 Setup.exe
```

### Signing

The installer is unsigned, so SmartScreen will warn on first run. Signing needs
a code-signing certificate and `signtool`.

---

## Application icon

There is currently **no icon** — both platforms use the default. To add one,
place `icon.ico` (Windows) and `icon.icns` (macOS) in the repo root, then set
`icon=` in `main.spec` and `SetupIconFile=` in `installer.iss`.

## Version numbers

The version appears in three places; keep them in sync:

- `main.spec` — `APP_VERSION`
- `build.py` — `APP_VERSION`
- `installer.iss` — `AppVersion` and `OutputBaseFilename`
