"""
BlueStacks Manager - Handles BlueStacks emulator control.
"""
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

from config.settings import Settings
from utils.logger import get_bs_logger, get_adb_logger

# Helper to hide CMD windows on Windows
if sys.platform == 'win32':
    _subprocess_flags = {'creationflags': subprocess.CREATE_NO_WINDOW}
else:
    _subprocess_flags = {}


class BlueStacksManager:
    """
    Manages BlueStacks emulator: configuration, startup, shutdown.
    """
    
    def __init__(self):
        """Initialize BlueStacks manager."""
        self.logger = get_bs_logger(__name__)
        self.adb_logger = get_adb_logger(__name__)
    
    def kill(self):
        """Kill all BlueStacks processes."""
        self.logger.info("Killing BlueStacks...")
        for proc in ["HD-Player.exe", "HD-Service.exe", "HD-Frontend.exe"]:
            subprocess.run(
                ["taskkill", "/F", "/IM", proc],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                **_subprocess_flags
            )
    
    def configure(self):
        """Configure BlueStacks with target resolution."""
        if not os.path.exists(Settings.BLUESTACKS_CONF):
            raise RuntimeError("bluestacks.conf not found")
        
        self.logger.info("Reading config...")
        with open(Settings.BLUESTACKS_CONF, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        
        text = "".join(lines)
        instance = self._detect_instance(text)
        
        if not instance:
            self.logger.error("Could not detect BlueStacks instance")
            raise RuntimeError("Could not detect BlueStacks instance")
        
        self.logger.info(f"Detected instance: {instance}")
        
        settings = {
            "fb_width": Settings.TARGET_WIDTH,
            "fb_height": Settings.TARGET_HEIGHT,
            "dpi": Settings.TARGET_DPI,
            "gl_win_height": Settings.TARGET_GL_HEIGHT,
            "show_sidebar": Settings.SHOW_SIDEBAR,
            "display_name": f"BlueStacks5-{instance}",
        }
        
        for key, value in settings.items():
            lines = self._set_key(lines, instance, key, value)
        
        self.logger.info("Writing config...")
        with open(Settings.BLUESTACKS_CONF, "w", encoding="utf-8") as f:
            f.writelines(lines)
        
        self.logger.info("Config applied successfully")
    
    def start(self):
        """Start BlueStacks."""
        self.logger.info("Starting BlueStacks...")
        subprocess.Popen([Settings.BLUESTACKS_EXE])
        time.sleep(15)
        self.logger.info("BlueStacks started")
    
    def validate_adb(self):
        """Validate ADB connection."""
        self.adb_logger.info("Connecting...")
        adb_path = Settings.get_adb_path()
        subprocess.run(
            [str(adb_path), "connect", f"{Settings.BLUESTACK_HOST}:{Settings.BLUESTACK_PORT}"],
            capture_output=True, **_subprocess_flags
        )
        
        size = subprocess.run(
            [str(adb_path), "-s", f"{Settings.BLUESTACK_HOST}:{Settings.BLUESTACK_PORT}", 
             "shell", "wm", "size"],
            capture_output=True, text=True, **_subprocess_flags
        )
        
        dpi = subprocess.run(
            [str(adb_path), "-s", f"{Settings.BLUESTACK_HOST}:{Settings.BLUESTACK_PORT}",
             "shell", "wm", "density"],
            capture_output=True, text=True, **_subprocess_flags
        )
        
        self.adb_logger.info(f"Screen: {size.stdout.strip()}")
        self.adb_logger.info(f"Density: {dpi.stdout.strip()}")
    
    def _detect_instance(self, conf_text: str) -> Optional[str]:
        """Detect BlueStacks instance name from config."""
        match = re.search(r'bst\.instance\.([^.]+)\.adb_port', conf_text)
        return match.group(1) if match else None
    
    def _set_key(self, lines: list, instance: str, key: str, value: str) -> list:
        """Set a configuration key."""
        pattern = re.compile(
            rf'(bst\.instance\.{re.escape(instance)}\.{re.escape(key)}=)"[^"]*"'
        )
        
        replaced = False
        new_lines = []
        for line in lines:
            if pattern.search(line):
                new_lines.append(f'bst.instance.{instance}.{key}="{value}"\n')
                replaced = True
            else:
                new_lines.append(line)
        
        if not replaced:
            new_lines.append(f'bst.instance.{instance}.{key}="{value}"\n')
        
        return new_lines
