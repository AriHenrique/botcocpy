"""
Compatibility layer for old imports.
This allows existing code to continue working while migrating to new structure.
"""
# Re-export for backward compatibility
from core.device_manager import DeviceManager as AndroidDevice
from core.vision_engine import VisionEngine
from utils.logger import BotLogger, get_bot_logger, get_adb_logger, get_bs_logger, get_vision_logger, get_device_logger, get_army_logger, get_game_logger, get_donate_logger
from utils.i18n import I18n, t, set_language, get_language, get_available_languages
from config.settings import Settings

# Make find_template function available (for vision.py compatibility)
_vision_engine = VisionEngine()
find_template = _vision_engine.find_template

__all__ = [
    'AndroidDevice',
    'VisionEngine',
    'BotLogger',
    'get_bot_logger',
    'get_adb_logger',
    'get_bs_logger',
    'get_vision_logger',
    'get_device_logger',
    'get_army_logger',
    'get_game_logger',
    'get_donate_logger',
    'I18n',
    't',
    'set_language',
    'get_language',
    'get_available_languages',
    'Settings',
    'find_template'
]
