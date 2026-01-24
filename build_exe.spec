# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Bot COC.
Run: pyinstaller build_exe.spec
"""

import os
from pathlib import Path

block_cipher = None

# Project paths
# Get project root from current working directory (when PyInstaller runs, it's in the project root)
# Or use the spec file location if __file__ is available
try:
    # Try to use __file__ if available
    spec_dir = Path(__file__).parent if '__file__' in globals() else Path.cwd()
    project_root = spec_dir if spec_dir.name != 'build' else spec_dir.parent
except:
    # Fallback to current working directory
    project_root = Path.cwd()

resources_dir = project_root / "resources"
adb_dir = resources_dir / "adb"
adb_scripts_dir = project_root / "adb.scripts"

# Build binaries list (ADB executables and DLLs - these are compiled into the .exe)
binaries_list = []
if adb_dir.exists():
    # Include ADB executable
    adb_exe = adb_dir / "adb.exe"
    if adb_exe.exists():
        binaries_list.append((str(adb_exe), "resources/adb"))
        print(f"[BUILD] Including ADB executable: {adb_exe}")
    else:
        print(f"[BUILD] WARNING: ADB executable not found at {adb_exe}")
        print(f"[BUILD] Run 'make setup' or 'python scripts/setup_resources.py' to copy ADB")
    
    # Include ADB DLLs (required dependencies for ADB to work)
    for dll_name in ["AdbWinApi.dll", "AdbWinUsbApi.dll"]:
        dll_path = adb_dir / dll_name
        if dll_path.exists():
            binaries_list.append((str(dll_path), "resources/adb"))
            print(f"[BUILD] Including ADB DLL: {dll_name}")
        else:
            print(f"[BUILD] WARNING: ADB DLL not found: {dll_name}")
else:
    print(f"[BUILD] WARNING: ADB directory not found: {adb_dir}")
    print(f"[BUILD] Run 'make setup' or 'python scripts/setup_resources.py' to prepare ADB")

# Build datas list (non-executable resources)
datas_list = []
# Include resources directory (excluding adb subdirectory which is in binaries)
# This ensures other resources are included while ADB is handled separately
if resources_dir.exists():
    # Include resources directory structure
    # ADB files will be in binaries, but directory structure is preserved
    datas_list.append((str(resources_dir), "resources"))
# Include templates
if (project_root / "templates").exists():
    datas_list.append((str(project_root / "templates"), "templates"))
# Include config
if (project_root / "config").exists():
    datas_list.append((str(project_root / "config"), "config"))
# Include locales
if (project_root / "locales").exists():
    datas_list.append((str(project_root / "locales"), "locales"))
# Include ADB scripts (minitouch binaries and scripts)
if adb_scripts_dir.exists():
    datas_list.append((str(adb_scripts_dir), "adb_scripts"))
    print(f"[BUILD] Including ADB scripts from: {adb_scripts_dir}")
else:
    print(f"[BUILD] WARNING: ADB scripts directory not found: {adb_scripts_dir}")

print(f"[BUILD] Total binaries to include: {len(binaries_list)}")
print(f"[BUILD] Total data files to include: {len(datas_list)}")

a = Analysis(
    [str(project_root / 'bin' / 'main.py')],
    pathex=[str(project_root)],
    binaries=binaries_list,
    datas=datas_list,
    hiddenimports=[
        'core',
        'core.bot_controller',
        'core.device_manager',
        'core.army_manager',
        'core.game_actions',
        'core.vision_engine',
        'core.bluestacks_manager',
        'utils',
        'utils.logger',
        'utils.i18n',
        'utils.resource_manager',
        'utils.compat',
        'compat',
        'compat.android',
        'compat.config',
        'compat.logger',
        'compat.i18n',
        'compat.vision',
        'config',
        'config.settings',
        'config.config_manager',
        'ui',
        'ui.gui',
        'functions',
        'functions.base',
        'functions.bluestacks_control',
        'functions.create_army',
        'functions.delete_army',
        'functions.donate',
        'cv2',
        'numpy',
        'PIL',
        'pytesseract',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BotCOC',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging (shows console window)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one
)
