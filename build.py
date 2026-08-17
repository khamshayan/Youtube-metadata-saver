#!/usr/bin/env python3
"""
Build the distributable for whichever platform you run this on.

    python build.py

  macOS   -> dist/Youtube metadata saver.app
             installer_output/Youtube metadata saver <version> (<arch>).dmg
  Windows -> dist/Youtube metadata saver/
             installer_output/Youtube metadata saver <version> Setup.exe
             (the .exe step needs Inno Setup installed; the app folder is
              built either way)

PyInstaller cannot cross-compile — run this on each target OS.
"""

import platform
import shutil
import subprocess
import sys
from pathlib import Path

APP_NAME = "Youtube metadata saver"
APP_VERSION = "1.0.0"

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
BUILD = ROOT / "build"
OUTPUT = ROOT / "installer_output"

IS_MAC = sys.platform == "darwin"
IS_WINDOWS = sys.platform.startswith("win")


def run(cmd, **kwargs):
    """Run a command, echoing it first, and abort the build if it fails."""
    print(f"\n$ {' '.join(str(c) for c in cmd)}\n", flush=True)
    result = subprocess.run(cmd, **kwargs)
    if result.returncode != 0:
        sys.exit(f"\nBuild step failed: {cmd[0]}")
    return result


def clean():
    for path in (BUILD, DIST):
        if path.exists():
            shutil.rmtree(path)
    OUTPUT.mkdir(exist_ok=True)


def build_app():
    """Freeze the app with PyInstaller using the shared spec."""
    run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "main.spec"], cwd=ROOT)


def package_macos():
    """Wrap the .app in a drag-to-Applications .dmg."""
    app = DIST / f"{APP_NAME}.app"
    if not app.is_dir():
        sys.exit(f"Expected bundle not found: {app}")

    arch = "Apple Silicon" if platform.machine() == "arm64" else "Intel"
    dmg = OUTPUT / f"{APP_NAME} {APP_VERSION} ({arch}).dmg"

    staging = BUILD / "dmg"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)

    run(["cp", "-R", str(app), str(staging)])
    # The Applications symlink is what makes the drag-to-install window work.
    run(["ln", "-s", "/Applications", str(staging / "Applications")])
    run([
        "hdiutil", "create",
        "-volname", APP_NAME,
        "-srcfolder", str(staging),
        "-ov", "-format", "UDZO",
        str(dmg),
    ])
    print(f"\nBuilt: {dmg}")
    print(
        "\nNote: the bundle is ad-hoc signed, not notarised. On another Mac the "
        "first launch needs right-click > Open, or:\n"
        f'  xattr -dr com.apple.quarantine "/Applications/{APP_NAME}.app"'
    )


def package_windows():
    """Compile the Inno Setup installer, if the compiler is available."""
    app_dir = DIST / APP_NAME
    if not app_dir.is_dir():
        sys.exit(f"Expected build folder not found: {app_dir}")

    iscc = shutil.which("ISCC") or shutil.which("iscc")
    if not iscc:
        for candidate in (
            r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
            r"C:\Program Files\Inno Setup 6\ISCC.exe",
        ):
            if Path(candidate).is_file():
                iscc = candidate
                break

    if not iscc:
        print(
            "\nInno Setup (ISCC.exe) not found — the app folder was built but the "
            "installer was not.\nInstall from https://jrsoftware.org/isdl.php, then "
            "re-run, or compile manually:\n    ISCC installer.iss"
        )
        return

    run([iscc, "installer.iss"], cwd=ROOT)
    print(f"\nBuilt: {OUTPUT / (APP_NAME + ' ' + APP_VERSION + ' Setup.exe')}")


def main():
    if not (IS_MAC or IS_WINDOWS):
        sys.exit("This build script supports macOS and Windows only.")

    print(f"Building {APP_NAME} {APP_VERSION} for {platform.system()} "
          f"({platform.machine()})")

    clean()
    build_app()

    if IS_MAC:
        package_macos()
    else:
        package_windows()


if __name__ == "__main__":
    main()
