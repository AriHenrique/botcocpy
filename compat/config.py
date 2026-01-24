"""
Compatibility alias for config module.
This file maintains backward compatibility for legacy code.
"""
from config.settings import Settings

# Export GAME_PACKAGE as a module-level constant for backward compatibility
GAME_PACKAGE = Settings.GAME_PACKAGE

# Export TEMPLATE_DIR and SCREENSHOT_FILE for backward compatibility
# TEMPLATE_DIR should be the full path to templates directory
TEMPLATE_DIR = str(Settings.PROJECT_ROOT / Settings.TEMPLATE_DIR)
SCREENSHOT_FILE = Settings.SCREENSHOT_FILE

__all__ = ['GAME_PACKAGE', 'TEMPLATE_DIR', 'SCREENSHOT_FILE']
