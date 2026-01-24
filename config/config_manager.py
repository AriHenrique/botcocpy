"""
Configuration manager for loading and saving configuration files.
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
from config.settings import Settings
from utils.logger import get_bot_logger


class ConfigManager:
    """Manages application configuration files."""
    
    def __init__(self):
        self.logger = get_bot_logger(__name__)
        self._cache: Dict[str, Any] = {}
    
    def load_config(self, filename: str, default: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Load a configuration file.
        
        Args:
            filename: Name of the config file
            default: Default values if file doesn't exist
            
        Returns:
            Configuration dictionary
        """
        config_path = Settings.get_config_path(filename)
        
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self._cache[filename] = config
                    self.logger.debug(f"Loaded config: {filename}")
                    return config
            except Exception as e:
                self.logger.error(f"Error loading config {filename}: {e}")
                if default:
                    return default
                return {}
        else:
            if default:
                self.save_config(filename, default)
                return default
            return {}
    
    def save_config(self, filename: str, config: Dict[str, Any]) -> bool:
        """
        Save a configuration file.
        
        Args:
            filename: Name of the config file
            config: Configuration dictionary to save
            
        Returns:
            True if successful, False otherwise
        """
        config_path = Settings.get_config_path(filename)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self._cache[filename] = config
            self.logger.debug(f"Saved config: {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving config {filename}: {e}")
            return False
    
    def get_cached(self, filename: str) -> Optional[Dict[str, Any]]:
        """Get cached configuration."""
        return self._cache.get(filename)
    
    def clear_cache(self):
        """Clear configuration cache."""
        self._cache.clear()
