"""
Compatibility alias for android module.
This file maintains backward compatibility for legacy code.
"""
from core.device_manager import DeviceManager

# Alias for backward compatibility
AndroidDevice = DeviceManager

__all__ = ['AndroidDevice']
