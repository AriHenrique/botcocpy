"""
Setup script to prepare resources for .exe compilation.
Copies ADB binaries and scripts to resources directory.
"""
import shutil
import os
from pathlib import Path


def setup_resources():
    """Setup resources directory with ADB and scripts."""
    project_root = Path(__file__).parent.parent
    # Resources directory in project root (not in bot_coc/)
    resources_dir = project_root / "resources"
    adb_dir = resources_dir / "adb"
    adb_scripts_dir = resources_dir / "adb_scripts"
    
    # Create directories
    adb_dir.mkdir(parents=True, exist_ok=True)
    adb_scripts_dir.mkdir(parents=True, exist_ok=True)
    
    print("=== Setting up resources for .exe compilation ===\n")
    
    # Copy ADB if available
    adb_sources = [
        r"C:\android\platform-tools\adb.exe",
        r"C:\Program Files\Android\android-sdk\platform-tools\adb.exe",
    ]
    
    adb_copied = False
    for source in adb_sources:
        if os.path.exists(source):
            target = adb_dir / "adb.exe"
            print(f"Copying ADB from {source}...")
            shutil.copy2(source, target)
            print(f"✓ ADB copied to {target}")
            adb_copied = True
            break
    
    if not adb_copied:
        print("⚠ ADB not found in common locations.")
        print(f"  Please copy adb.exe manually to: {adb_dir}/adb.exe")
    
    # Copy ADB scripts
    source_scripts = project_root / "adb.scripts"
    if source_scripts.exists():
        print(f"\nCopying ADB scripts from {source_scripts}...")
        for item in source_scripts.iterdir():
            if item.is_file() and (item.suffix == "" or item.name.endswith(".minitouch")):
                target = adb_scripts_dir / item.name
                shutil.copy2(item, target)
                print(f"  ✓ {item.name}")
        print(f"✓ ADB scripts copied to {adb_scripts_dir}")
    else:
        print(f"⚠ ADB scripts directory not found: {source_scripts}")
    
    # Copy other ADB tools if available
    adb_tools = ["AdbWinApi.dll", "AdbWinUsbApi.dll"]
    for tool in adb_tools:
        for source_path in adb_sources:
            source_file = Path(source_path).parent / tool
            if source_file.exists():
                target = adb_dir / tool
                shutil.copy2(source_file, target)
                print(f"✓ {tool} copied")
                break
    
    print("\n=== Setup complete ===")
    print(f"\nResources directory: {resources_dir}")
    print("\nNext steps:")
    print("1. Ensure all required files are in resources/")
    print("2. Use PyInstaller or similar to compile to .exe")
    print("3. Include resources/ in your build configuration")


if __name__ == "__main__":
    setup_resources()
