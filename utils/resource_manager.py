"""
Resource Manager - Handles embedded resources for standalone .exe execution.
Extracts ADB and other binaries when running as compiled executable.
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional
import tempfile

from config.settings import Settings
from utils.logger import get_bot_logger

# Helper to hide CMD windows on Windows
if sys.platform == 'win32':
    _subprocess_flags = {'creationflags': subprocess.CREATE_NO_WINDOW}
else:
    _subprocess_flags = {}


class ResourceManager:
    """
    Manages embedded resources for standalone execution.
    Handles extraction of ADB binaries and scripts.
    """
    
    def __init__(self):
        """Initialize resource manager."""
        self.logger = get_bot_logger(__name__)
        self._is_frozen = getattr(sys, 'frozen', False)
        self._base_path = Path(sys.executable).parent if self._is_frozen else Settings.PROJECT_ROOT
        
        # Resources directory (where binaries will be extracted)
        self.resources_dir = self._base_path / "resources"
        self.adb_dir = self.resources_dir / "adb"
        self.adb_scripts_dir = self.resources_dir / "adb_scripts"
        
        # Ensure directories exist
        self.resources_dir.mkdir(exist_ok=True)
        self.adb_dir.mkdir(exist_ok=True)
        self.adb_scripts_dir.mkdir(exist_ok=True)
    
    def is_frozen(self) -> bool:
        """Check if running as compiled executable."""
        return self._is_frozen
    
    def get_resource_path(self, *parts: str) -> Path:
        """
        Get path to a resource file.
        
        Args:
            *parts: Path parts relative to resources directory
            
        Returns:
            Full path to resource
        """
        return self.resources_dir.joinpath(*parts)
    
    def find_adb(self) -> Optional[Path]:
        """
        Find ADB executable.
        Priority:
        1. Embedded ADB in resources/adb/
        2. System ADB (if available)
        3. None if not found
        
        Returns:
            Path to ADB executable or None
        """
        # Try embedded ADB first
        embedded_adb = self.adb_dir / "adb.exe"
        if embedded_adb.exists():
            self.logger.debug(f"Using embedded ADB: {embedded_adb}")
            return embedded_adb
        
        # Try system ADB
        system_paths = [
            r"C:\android\platform-tools\adb.exe",
            r"C:\Program Files\Android\android-sdk\platform-tools\adb.exe",
            r"C:\Users\{}\AppData\Local\Android\Sdk\platform-tools\adb.exe".format(os.getenv('USERNAME', '')),
        ]
        
        for path in system_paths:
            if os.path.exists(path):
                self.logger.debug(f"Using system ADB: {path}")
                return Path(path)
        
        # Try ADB in PATH
        try:
            result = subprocess.run(
                ["adb", "version"],
                capture_output=True,
                text=True,
                timeout=2,
                **_subprocess_flags
            )
            if result.returncode == 0:
                # Find adb.exe in PATH
                import shutil
                adb_path = shutil.which("adb")
                if adb_path:
                    self.logger.debug(f"Using ADB from PATH: {adb_path}")
                    return Path(adb_path)
        except Exception:
            pass
        
        self.logger.warning("ADB not found. Please install ADB or include it in resources/adb/")
        return None
    
    def get_minitouch_path(self, device_type: str = "Normal1") -> Optional[Path]:
        """
        Get path to minitouch binary for device.
        
        Args:
            device_type: Device type (e.g., "Normal1", "Normal1.BlueStacks5")
            
        Returns:
            Path to minitouch binary or None
        """
        # Try embedded scripts first
        embedded_minitouch = self.adb_scripts_dir / f"{device_type}.minitouch"
        if embedded_minitouch.exists():
            return embedded_minitouch
        
        # Try project adb.scripts directory
        project_minitouch = Settings.PROJECT_ROOT / "adb.scripts" / f"{device_type}.minitouch"
        if project_minitouch.exists():
            return project_minitouch
        
        # Try generic minitouch
        generic_minitouch = self.adb_scripts_dir / "minitouch"
        if generic_minitouch.exists():
            return generic_minitouch
        
        project_generic = Settings.PROJECT_ROOT / "adb.scripts" / "minitouch"
        if project_generic.exists():
            return project_generic
        
        self.logger.warning(f"Minitouch binary not found for {device_type}")
        return None
    
    def extract_resource(self, resource_name: str, target_path: Path) -> bool:
        """
        Extract embedded resource to target path.
        Used when running as compiled .exe.
        
        Args:
            resource_name: Name of resource in package
            target_path: Where to extract the resource
            
        Returns:
            True if successful, False otherwise
        """
        if not self._is_frozen:
            # Not running as .exe, resources should be in project directory
            return False
        
        try:
            # In frozen mode, resources might be in _MEIPASS or similar
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller
                source = Path(sys._MEIPASS) / "resources" / resource_name
            elif hasattr(sys, '_MEIPASS2'):
                # cx_Freeze
                source = Path(sys._MEIPASS2) / "resources" / resource_name
            else:
                # Try relative to executable
                source = self._base_path / "resources" / resource_name
            
            if source.exists():
                shutil.copy2(source, target_path)
                self.logger.debug(f"Extracted {resource_name} to {target_path}")
                return True
        except Exception as e:
            self.logger.error(f"Error extracting resource {resource_name}: {e}")
        
        return False
    
    def ensure_adb_available(self) -> Optional[Path]:
        """
        Ensure ADB is available, extracting if necessary.
        
        Returns:
            Path to ADB executable or None
        """
        adb_path = self.find_adb()
        
        if not adb_path and self._is_frozen:
            # Try to extract embedded ADB
            target_adb = self.adb_dir / "adb.exe"
            if self.extract_resource("adb/adb.exe", target_adb):
                adb_path = target_adb
        
        return adb_path
    
    def get_adb_scripts_path(self) -> Path:
        """Get path to ADB scripts directory."""
        # Prefer embedded scripts
        if self.adb_scripts_dir.exists() and any(self.adb_scripts_dir.iterdir()):
            return self.adb_scripts_dir
        
        # Fallback to project directory
        project_scripts = Settings.PROJECT_ROOT / "adb.scripts"
        if project_scripts.exists():
            return project_scripts
        
        return self.adb_scripts_dir
