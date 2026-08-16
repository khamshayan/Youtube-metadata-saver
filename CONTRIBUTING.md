# Contributing

Thanks for taking an interest in this project. Bug reports, ideas, and pull requests are all welcome.

## Getting Set Up

```bash
git clone https://github.com/khamshayan/Youtube-metadata-saver.git
cd Youtube-metadata-saver

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
python main.py
```

Python 3.9 or newer is required.

## Reporting a Bug

Open an issue and include:

- What you did, what you expected, and what happened instead
- Your OS and Python version (or the installer version, if you are running the packaged app)
- Any console output — running `python main.py` from a terminal surfaces messages the
  packaged executable hides

## Suggesting a Feature

Open an issue describing the workflow problem before the solution. This app exists to remove
repetitive steps from a real publishing routine, so the most useful proposals explain which
manual step is being eliminated.

## Pull Requests

1. Fork the repository and branch from `main`:
   `git checkout -b feature/short-description`
2. Make your change, keeping it focused on a single concern.
3. Run the app and walk through the full workflow — submit a form, check the created folders,
   open the history window.
4. Commit in the imperative mood: `Add CSV export to history window`.
5. Open a pull request explaining what changed and why, with screenshots for UI changes.

## Code Conventions

The codebase follows a few consistent patterns. Matching them keeps diffs readable:

- **Module boundaries.** `gui.py` owns widgets and never touches the filesystem directly.
  `file_manager.py` owns disk operations and knows nothing about widgets. `main.py`
  coordinates between them. Keep that separation intact.
- **Return values over exceptions.** File operations return `True`/`False` (or a path/`None`)
  and print the failure. Callers check the result and surface an error dialog.
- **Docstrings on every function**, in the existing format: a one-line summary, then `Args:`
  and `Returns:` sections where they apply.
- **PEP 8** naming and four-space indentation. Private helpers are prefixed with `_`.
- **Never commit runtime state.** `settings.json`, `history.json`, and `draft.json` are
  generated in `%APPDATA%` at runtime and are gitignored. Do not add real folder paths,
  personal directories, or sample history data to the repository.

## Testing Changes

The project has no automated test suite yet. Before opening a pull request, manually verify:

- A first launch with no configuration shows the setup wizard and saves the paths
- A full submission creates all three folders with the correct names and contents
- The Short Form toggle produces the `Short/` subfolder and `Short_Metadata.txt`
- The "Skip Thumbnail" path creates folders without an image and without errors
- A draft survives closing and reopening the app, and is cleared after a successful submit
- The history window lists the new entry, edits save, and folder links open

Contributions that add automated coverage for any of the above are especially welcome.
