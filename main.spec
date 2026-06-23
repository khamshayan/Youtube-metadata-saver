# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

# Collect all data files for customtkinter (themes, images, etc.)
customtkinter_datas = collect_data_files('customtkinter', includes=['**/*'])

# Collect tkinterdnd2 data files (Tcl scripts and native DLL)
tkinterdnd2_datas = collect_data_files('tkinterdnd2', includes=['**/*'])
tkinterdnd2_bins  = collect_dynamic_libs('tkinterdnd2')

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
        'tkinterdnd2',
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
    name='Youtube metadata saver',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,       # no black console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
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
    name='Youtube metadata saver',
)
