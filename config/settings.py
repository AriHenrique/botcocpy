"""
Application settings and constants.
"""
import os
import sys
from pathlib import Path


class Settings:
    """Centralized application settings."""
    
    # Project root directory
    # If running as .exe, use _MEIPASS (where PyInstaller extracts files) or executable directory
    _is_frozen = getattr(sys, 'frozen', False)
    if _is_frozen:
        # PyInstaller creates _MEIPASS temp folder with extracted files
        if hasattr(sys, '_MEIPASS'):
            PROJECT_ROOT = Path(sys._MEIPASS)
        else:
            PROJECT_ROOT = Path(sys.executable).parent
    else:
        # config/settings.py -> config/ -> bot_coc/ (project root)
        PROJECT_ROOT = Path(__file__).parent.parent
    
    # ADB Configuration - Will be resolved dynamically
    _adb_path = None
    BLUESTACK_HOST = "127.0.0.1"
    BLUESTACK_PORT = 5556
    
    @classmethod
    def get_adb_path(cls) -> Path:
        """
        Get ADB path, resolving from resources or system.
        
        Returns:
            Path to ADB executable
        """
        if cls._adb_path and cls._adb_path.exists():
            return cls._adb_path
        
        # Try to resolve ADB
        from utils.resource_manager import ResourceManager
        resource_manager = ResourceManager()
        adb_path = resource_manager.ensure_adb_available()
        
        if adb_path:
            cls._adb_path = adb_path
            return adb_path
        
        # Fallback to default (will show error if not found)
        default_path = Path(r"C:\android\platform-tools\adb.exe")
        cls._adb_path = default_path
        return default_path
    
    @classmethod
    def set_adb_path(cls, path: Path):
        """Set custom ADB path."""
        cls._adb_path = Path(path)
    
    @property
    def ADB_PATH(self) -> str:
        """Get ADB path as string (for backward compatibility)."""
        return str(self.get_adb_path())
    
    # Game Configuration
    GAME_PACKAGE = "com.supercell.clashofclans"
    DEFAULT_TIMEOUT = 30
    
    # File paths
    SCREENSHOT_FILE = "screen.png"
    TEMPLATE_DIR = "templates"
    LOG_DIR = "logs"
    CONFIG_DIR = "config"
    LOCALES_DIR = "locales"
    
    # BlueStacks Configuration
    # These paths are system-specific and cannot be embedded
    BLUESTACKS_CONF = r"C:\ProgramData\BlueStacks_nxt\bluestacks.conf"
    BLUESTACKS_EXE = r"C:\Program Files\BlueStacks_nxt\HD-Player.exe"
    
    # Resources directories (for embedded files)
    RESOURCES_DIR = "resources"
    ADB_DIR = "resources/adb"
    ADB_SCRIPTS_DIR = "resources/adb_scripts"
    
    # Target resolution
    TARGET_WIDTH = "860"
    TARGET_HEIGHT = "732"
    TARGET_DPI = "160"
    TARGET_GL_HEIGHT = "732"
    SHOW_SIDEBAR = "0"
    
    # Default language
    DEFAULT_LANGUAGE = "pt-BR"
    FALLBACK_LANGUAGE = "en-US"
    
    @classmethod
    def get_template_path(cls, template: str) -> Path:
        """Get full path to a template file."""
        return cls.PROJECT_ROOT / cls.TEMPLATE_DIR / template
    
    @classmethod
    def get_config_path(cls, filename: str) -> Path:
        """Get full path to a config file."""
        return cls.PROJECT_ROOT / cls.CONFIG_DIR / filename
    
    @classmethod
    def get_locale_path(cls, filename: str) -> Path:
        """Get full path to a locale file."""
        return cls.PROJECT_ROOT / cls.LOCALES_DIR / filename
    
    @classmethod
    def get_log_path(cls, filename: str) -> Path:
        """Get full path to a log file."""
        log_dir = cls.PROJECT_ROOT / cls.LOG_DIR
        log_dir.mkdir(exist_ok=True)
        return log_dir / filename
    
    @classmethod
    def get_adb_dir(cls) -> Path:
        """Get ADB directory path."""
        return cls.PROJECT_ROOT / cls.ADB_DIR
    
    @classmethod
    def get_adb_scripts_dir(cls) -> Path:
        """Get ADB scripts directory path."""
        return cls.PROJECT_ROOT / cls.ADB_SCRIPTS_DIR
    
    @classmethod
    def get_resources_dir(cls) -> Path:
        """Get resources directory path."""
        return cls.PROJECT_ROOT / cls.RESOURCES_DIR