"""
Compatibility alias for i18n module.
This file maintains backward compatibility for legacy code.
"""
from utils.i18n import (
    I18n,
    t,
    set_language,
    get_language,
    get_available_languages
)

__all__ = [
    'I18n',
    't',
    'set_language',
    'get_language',
    'get_available_languages'
]
