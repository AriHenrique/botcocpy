"""
Compatibility alias for logger module.
This file maintains backward compatibility for legacy code.
"""
from utils.logger import (
    BotLogger,
    get_bot_logger,
    get_adb_logger,
    get_bs_logger,
    get_vision_logger,
    get_device_logger,
    get_army_logger,
    get_game_logger,
    get_donate_logger
)

__all__ = [
    'BotLogger',
    'get_bot_logger',
    'get_adb_logger',
    'get_bs_logger',
    'get_vision_logger',
    'get_device_logger',
    'get_army_logger',
    'get_game_logger',
    'get_donate_logger'
]
