# -*- mode: python ; coding: utf-8 -*-
"""
Cross-platform PyInstaller spec.

One spec drives both targets:
  * Windows -> dist/Youtube metadata saver/  (exe + _internal, consumed by installer.iss)
  * macOS   -> dist/Youtube metadata saver.app  (bundle, packaged into a .dmg)

PyInstaller cannot cross-compile: run it on Windows for the Windows build and
on macOS for the macOS build.
"""
import sys

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

IS_MAC = sys.platform == 'darwin'

APP_NAME = 'Youtube metadata saver'
APP_VERSION = '1.0.0'
BUNDLE_ID = 'com.khamshayan.youtubemetadatasaver'

# Collect all data files for customtkinter (themes, images, etc.)
customtkinter_datas = collect_data_files('customtkinter', includes=['**/*'])

# Collect tkinterdnd2 data files (Tcl scripts and the per-platform native lib).
# The package ships linux64/osx64/win64 folders; collecting everything keeps a
# single spec valid on every platform.
tkinterdnd2_datas = collect_data_files('tkinterdnd2', includes=['**/*'])
tkinterdnd2_bins = collect_dynamic_libs('tkinterdnd2')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=tkinterdnd2_bins,
    datas=customtkinter_datas + tkinterdnd2_datas,
    hiddenimports=[
        'customtkinter',
        'PIL',
        'PIL._imagingtk',
        'PIL.Image',
        'PIL.ImageGrab',   # clipboard screenshot paste
        'PIL.ImageTk',
        'tkinterdnd2',
        'platform_utils',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,       # no black console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,    # host architecture; see BUILDING.md for universal2
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=APP_NAME,
)

if IS_MAC:
    app = BUNDLE(
        coll,
        name=f'{APP_NAME}.app',
        icon=None,
        bundle_identifier=BUNDLE_ID,
        version=APP_VERSION,
        info_plist={
            'CFBundleName': APP_NAME,
            'CFBundleDisplayName': APP_NAME,
            'CFBundleShortVersionString': APP_VERSION,
            'CFBundleVersion': APP_VERSION,
            # Without this the whole UI renders blurry on Retina displays.
            'NSHighResolutionCapable': True,
            'LSMinimumSystemVersion': '10.13.0',
            'LSApplicationCategoryType': 'public.app-category.productivity',
            # Pillow reads clipboard images by shelling out to osascript.
            'NSAppleEventsUsageDescription':
                'Used to read screenshots from the clipboard when you paste a thumbnail.',
        },
    )
