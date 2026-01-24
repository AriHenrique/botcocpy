"""
Device Manager - Handles Android device communication via ADB.
Complete implementation with all methods from android.py
"""
import subprocess
import sys
import xml.etree.ElementTree as ET
import time
import re
import os
import json
from pathlib import Path
from typing import Optional, Tuple

from config.settings import Settings
from core.vision_engine import VisionEngine
from utils.logger import get_adb_logger, get_vision_logger, get_device_logger

# Helper to hide CMD windows on Windows
if sys.platform == 'win32':
    _subprocess_flags = {'creationflags': subprocess.CREATE_NO_WINDOW}
else:
    _subprocess_flags = {}


class DeviceManager:
    """
    Manages Android device communication and operations.
    Handles ADB commands, touch input, screenshots, and UI interactions.
    Complete replacement for AndroidDevice class.
    """
    
    def __init__(self, host: str = None, port: str = None):
        """
        Initialize device manager.
        
        Args:
            host: ADB host (defaults to Settings.BLUESTACK_HOST)
            port: ADB port (defaults to Settings.BLUESTACK_PORT)
        """
        self.host = host or Settings.BLUESTACK_HOST
        self.port = port or Settings.BLUESTACK_PORT
        self.serial = f"{self.host}:{self.port}"
        
        self.logger = get_adb_logger(__name__)
        self.vision_logger = get_vision_logger(__name__)
        self.device_logger = get_device_logger(__name__)
        
        # Initialize vision engine
        self.vision = VisionEngine()
        
        self._connect()
        self._setup_minitouch()
    
    # ================= CORE =================
    def _run(self, cmd: list) -> subprocess.CompletedProcess:
        """Execute ADB command."""
        adb_path = Settings.get_adb_path()
        full_cmd = [str(adb_path), "-s", self.serial] + cmd
        return subprocess.run(full_cmd, capture_output=True, text=True, **_subprocess_flags)
    
    def _connect(self):
        """Connect to device via ADB."""
        self.logger.info(f"Connecting to {self.serial}")
        adb_path = Settings.get_adb_path()
        subprocess.run([str(adb_path), "connect", self.serial], **_subprocess_flags)
    
    # ================= APP =================
    def open_app(self, package: str):
        """Open an application by package name."""
        self.logger.info(f"Opening app: {package}")
        self._run([
            "shell", "monkey",
            "-p", package,
            "-c", "android.intent.category.LAUNCHER", "1"
        ])
    
    # ================= INPUT =================
    def tap(self, x: int, y: int):
        """Tap at coordinates."""
        self.logger.debug(f"Tap at {x},{y}")
        self._run(["shell", "input", "tap", str(x), str(y)])
    
    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300):
        """Perform swipe gesture."""
        self.logger.debug(f"Swipe {x1},{y1} -> {x2},{y2} (duration={duration}ms)")
        self._run([
            "shell", "input", "swipe",
            str(x1), str(y1), str(x2), str(y2), str(duration)
        ])
    
    def type(self, text: str):
        """Type text on device."""
        safe = text.replace(" ", "%s")
        self.logger.debug(f"Type: {text}")
        self._run(["shell", "input", "text", safe])
    
    def _minitouch_swipe(self, x1: int, y1: int, x2: int, y2: int, hold_ms: int = 1):
        """
        Swipe using minitouch: press, drag, release.
        Instant and precise movement.
        """
        screen_w, screen_h = self._get_screen_size()
        max_x, max_y = self._get_touch_info()
        
        def to_touch(sx, sy):
            tx = int((sx / screen_w) * max_x)
            ty = int((sy / screen_h) * max_y)
            return tx, ty
        
        commands = ["r"]
        
        # Touch down at initial position
        tx1, ty1 = to_touch(x1, y1)
        commands.append(f"d 0 {tx1} {ty1} 50")
        commands.append("c")
        commands.append(f"w {hold_ms}")
        
        # Move to final position
        tx2, ty2 = to_touch(x2, y2)
        commands.append(f"m 0 {tx2} {ty2} 50")
        commands.append("c")
        commands.append(f"w {hold_ms}")
        
        # Touch up
        commands.append("u 0")
        commands.append("c")
        
        script = "\n".join(commands)
        script_path = Settings.PROJECT_ROOT / "swipe_script.txt"
        with open(script_path, "w") as f:
            f.write(script)
        
        env = os.environ.copy()
        env["MSYS_NO_PATHCONV"] = "1"
        adb_path = Settings.get_adb_path()
        subprocess.run(
            [str(adb_path), "-s", self.serial, "push", str(script_path), "/data/local/tmp/swipe.script"],
            env=env, capture_output=True, **_subprocess_flags
        )
        subprocess.run(
            [str(adb_path), "-s", self.serial, "shell", "/data/local/tmp/minitouch", "-f", "/data/local/tmp/swipe.script"],
            env=env, capture_output=True, **_subprocess_flags
        )
    
    def center_view(self, move_right: int = 200, move_down: int = 0, hold_ms: int = 200):
        """
        Center game camera with fixed and exact movement.
        
        Args:
            move_right: pixels to move camera right
            move_down: pixels to move camera down
            hold_ms: swipe hold time
        """
        screen_w, screen_h = self._get_screen_size()
        center_x = screen_w // 2
        center_y = screen_h // 2
        
        self.logger.info("Centering view...")
        
        # Move everything to left corner (drag right)
        self._minitouch_swipe(100, center_y, screen_w - 100, center_y, hold_ms=200)
        time.sleep(0.2)
        
        # Move everything up (drag down)
        self._minitouch_swipe(center_x, 100, center_x, screen_h - 100, hold_ms=200)
        time.sleep(0.2)
        
        # Move fixed value right (drag left)
        if move_right > 0:
            self._minitouch_swipe(
                center_x, center_y,
                center_x - move_right, center_y,
                hold_ms=hold_ms
            )
            time.sleep(0.1)
        
        # Move fixed value down (drag up)
        if move_down > 0:
            self._minitouch_swipe(
                center_x, center_y,
                center_x, center_y - move_down,
                hold_ms=hold_ms
            )
        
        self.logger.info(f"View centered (moved {move_right}px right, {move_down}px down)")
    
    def scroll_horizontal(self, scroll_pixels: int, start_pos: Optional[Tuple[int, int]] = None, hold_ms: int = 50):
        """
        Drag horizontally from a screen position.
        
        Args:
            scroll_pixels: pixels to drag (positive = right to left)
            start_pos: tuple (x, y) of initial position. If None, uses screen center.
            hold_ms: swipe hold time
        """
        screen_w, screen_h = self._get_screen_size()
        
        if start_pos:
            x, y = start_pos
        else:
            x = screen_w // 2
            y = screen_h // 2
        
        self._minitouch_swipe(x, y, x - scroll_pixels, y, hold_ms=hold_ms)
        self.logger.debug(f"Scrolled {scroll_pixels}px left from ({x}, {y})")
    
    def find_and_tap_with_scroll(
        self,
        template: str,
        scroll_pixels: int = 150,
        scroll_pos: Optional[Tuple[int, int]] = None,
        max_scrolls: int = 5,
        threshold: float = 0.75,
        scroll_hold_ms: int = 50
    ) -> bool:
        """
        Find image on screen, if not found scroll horizontally and try again.
        
        Args:
            template: image to find and click
            scroll_pixels: pixels to drag each attempt
            scroll_pos: tuple (x, y) for scroll position. If None, uses screen center.
            max_scrolls: maximum scrolls before giving up
            threshold: detection threshold
            scroll_hold_ms: scroll hold time
            
        Returns:
            True if found and clicked, False otherwise
        """
        template_path = Settings.get_template_path(template)
        
        for attempt in range(max_scrolls + 1):
            self.screenshot()
            pos = self.vision.find_template(
                Settings.SCREENSHOT_FILE,
                str(template_path),
                threshold
            )
            
            if pos:
                self.tap(pos[0], pos[1])
                return True
            
            if attempt < max_scrolls:
                self.logger.warning(f"{template} not found, scrolling... ({attempt + 1}/{max_scrolls})")
                self.scroll_horizontal(scroll_pixels, scroll_pos, hold_ms=scroll_hold_ms)
                time.sleep(5)
        
        self.logger.error(f"{template} not found after {max_scrolls} scrolls")
        return False
    
    # ================= SCREEN =================
    def screenshot(self, local: str = None) -> str:
        """
        Take a screenshot.
        
        Args:
            local: Local filename (defaults to Settings.SCREENSHOT_FILE)
            
        Returns:
            Path to screenshot file
        """
        local = local or Settings.SCREENSHOT_FILE
        self._run(["shell", "screencap", "-p", "/sdcard/screen.png"])
        self._run(["pull", "/sdcard/screen.png", local])
        return local
    
    # ================= UI XML =================
    def dump_ui(self) -> ET.ElementTree:
        """Dump UI hierarchy to XML."""
        self._run(["shell", "uiautomator", "dump", "/sdcard/ui.xml"])
        self._run(["pull", "/sdcard/ui.xml", "ui.xml"])
        return ET.parse("ui.xml")
    
    def _find_node(self, attr: str, value: str) -> Optional[ET.Element]:
        """Find UI node by attribute."""
        tree = self.dump_ui()
        for node in tree.iter("node"):
            if node.attrib.get(attr) == value:
                return node
        return None
    
    def _bounds_center(self, bounds: str) -> Tuple[int, int]:
        """Get center of bounds string."""
        nums = list(map(int, re.findall(r"\d+", bounds)))
        x = (nums[0] + nums[2]) // 2
        y = (nums[1] + nums[3]) // 2
        return x, y
    
    def tap_text(self, text: str):
        """Tap on UI element by text."""
        node = self._find_node("text", text)
        if not node:
            raise Exception(f"Text not found: {text}")
        x, y = self._bounds_center(node.attrib["bounds"])
        self.tap(x, y)
    
    # ================= VISION =================
    def tap_image(self, template: str, threshold: float = 0.8, retries: int = 5, delay: float = 1) -> bool:
        """
        Find and tap image on screen.
        
        Args:
            template: Template path (e.g., "menu/bt_army.png")
            threshold: Matching threshold
            retries: Number of retries
            delay: Delay between retries
            
        Returns:
            True if found and tapped, raises Exception if not found
        """
        regions = self._load_regions()
        region = None
        
        meta = regions.get(template)
        if meta and meta.get("use_region"):
            region = meta.get("region")
        
        template_path = Settings.get_template_path(template)
        self.vision_logger.info(f"Looking for {template_path} (region={region}, threshold={threshold})")
        
        for i in range(retries):
            screen = self.screenshot()
            pos = self.vision.find_template(
                screen,
                str(template_path),
                threshold,
                region=region
            )
            if pos:
                self.vision_logger.debug(f"Found {template} at {pos}")
                self.tap(pos[0], pos[1])
                return True
            self.vision_logger.warning(f"Retry {i+1}/{retries} - {template} not found")
            time.sleep(delay)
        
        self.vision_logger.error(f"Image not found after {retries} retries: {template}")
        return False
    
    def wait_image(self, template: str, timeout: float = 30, threshold: float = 0.8) -> bool:
        """
        Wait for image to appear on screen.
        
        Args:
            template: Template path
            timeout: Maximum time to wait (seconds)
            threshold: Matching threshold
            
        Returns:
            True if found, raises TimeoutError if not found
        """
        template_path = Settings.get_template_path(template)
        self.vision_logger.info(f"Waiting for {template_path} (timeout={timeout}s)")
        start = time.time()
        
        while time.time() - start < timeout:
            screen = self.screenshot()
            pos = self.vision.find_template(
                screen,
                str(template_path),
                threshold
            )
            if pos:
                self.vision_logger.info(f"Found {template_path} at {pos}")
                return True
            time.sleep(1)
        
        self.vision_logger.error(f"Timeout waiting for {template_path}")
        raise TimeoutError(f"Timeout waiting for {template_path}")
    
    def _load_regions(self) -> dict:
        """Load template regions from JSON."""
        path = Settings.get_template_path("templates.json")
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Error loading regions: {e}")
        return {}
    
    def zoom_out_hold_fake(self, seconds: float = 3, interval: float = 0.05):
        """
        Simulate holding DPAD_DOWN by sending rapid keyevents.
        """
        self.logger.debug("Fake holding DPAD_DOWN")
        
        self._run(["shell", "input", "keyevent", "KEYCODE_D"])
        time.sleep(0.2)
        
        end = time.time() + seconds
        while time.time() < end:
            self._run(["shell", "input", "keyevent", "KEYCODE_DPAD_DOWN"])
            time.sleep(interval)
    
    # ================= MINITOUCH ZOOM =================
    def _setup_minitouch(self):
        """Install minitouch on device automatically."""
        check = self._run(["shell", "test -x /data/local/tmp/minitouch && echo OK"])
        if "OK" in check.stdout:
            self.logger.info("Minitouch already installed")
            return
        
        self.logger.info("Installing minitouch...")
        
        # Try to find minitouch using ResourceManager
        from utils.resource_manager import ResourceManager
        resource_manager = ResourceManager()
        
        # Try different device types
        minitouch_path = None
        for device_type in ["Normal1.BlueStacks5", "Normal1", "minitouch"]:
            path = resource_manager.get_minitouch_path(device_type)
            if path and path.exists():
                minitouch_path = path
                break
        
        if not minitouch_path or not minitouch_path.exists():
            # Fallback to project directory
            minitouch_path = Settings.PROJECT_ROOT / "adb.scripts" / "minitouch"
            if not minitouch_path.exists():
                raise FileNotFoundError(
                    f"Minitouch binary not found. "
                    f"Please ensure minitouch is in resources/adb_scripts/ or adb.scripts/"
                )
        
        env = os.environ.copy()
        env["MSYS_NO_PATHCONV"] = "1"
        adb_path = Settings.get_adb_path()
        
        result = subprocess.run(
            [str(adb_path), "-s", self.serial, "push", str(minitouch_path), "/data/local/tmp/minitouch"],
            env=env, capture_output=True, text=True, **_subprocess_flags
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Failed to push minitouch: {result.stderr}")
        
        self._run(["shell", "chmod", "755", "/data/local/tmp/minitouch"])
        
        test = self._run(["shell", "/data/local/tmp/minitouch", "-h"])
        if "Usage:" not in test.stdout:
            self.logger.error("Minitouch installation failed - binary may be incompatible")
            raise RuntimeError("Minitouch installation failed - binary may be incompatible")
        
        self.logger.info("Minitouch installed successfully")
    
    def _get_touch_info(self) -> Tuple[int, int]:
        """Get touch device info (max_x, max_y)."""
        env = os.environ.copy()
        env["MSYS_NO_PATHCONV"] = "1"
        adb_path = Settings.get_adb_path()
        result = subprocess.run(
            [str(adb_path), "-s", self.serial, "shell",
             "echo '' | /data/local/tmp/minitouch -i"],
            capture_output=True, text=True, env=env, timeout=5, **_subprocess_flags
        )
        # Parse: ^ 2 32767 32767 0
        for line in result.stdout.split('\n'):
            if line.startswith('^'):
                parts = line.split()
                return int(parts[2]), int(parts[3])  # max_x, max_y
        return 32767, 32767  # fallback
    
    def _get_screen_size(self) -> Tuple[int, int]:
        """Get device screen size."""
        result = self._run(["shell", "wm", "size"])
        match = re.search(r"(\d+)x(\d+)", result.stdout)
        if match:
            return int(match.group(1)), int(match.group(2))
        return 860, 732  # fallback
    
    def zoom_out(self, steps: int = 10, duration_ms: int = 300):
        """
        Perform zoom out (pinch in) using minitouch.
        Fingers start at edges and move to center.
        """
        screen_w, screen_h = self._get_screen_size()
        max_x, max_y = self._get_touch_info()
        
        center_x = screen_w // 2
        center_y = screen_h // 2
        
        start_offset = min(screen_w, screen_h) // 3
        left_x = center_x - start_offset
        right_x = center_x + start_offset
        
        def to_touch(sx, sy):
            tx = int((sx / screen_w) * max_x)
            ty = int((sy / screen_h) * max_y)
            return tx, ty
        
        wait_per_step = duration_ms // steps
        commands = ["r"]
        
        lx, ly = to_touch(left_x, center_y)
        rx, ry = to_touch(right_x, center_y)
        commands.append(f"d 0 {lx} {ly} 50")
        commands.append(f"d 1 {rx} {ry} 50")
        commands.append("c")
        commands.append(f"w {wait_per_step}")
        
        for i in range(1, steps + 1):
            progress = i / steps
            curr_left_x = left_x + int((center_x - left_x) * progress)
            curr_right_x = right_x - int((right_x - center_x) * progress)
            
            lx, ly = to_touch(curr_left_x, center_y)
            rx, ry = to_touch(curr_right_x, center_y)
            commands.append(f"m 0 {lx} {ly} 50")
            commands.append(f"m 1 {rx} {ry} 50")
            commands.append("c")
            commands.append(f"w {wait_per_step}")
        
        commands.append("u 0")
        commands.append("u 1")
        commands.append("c")
        
        script = "\n".join(commands)
        script_path = Settings.PROJECT_ROOT / "zoom_script.txt"
        with open(script_path, "w") as f:
            f.write(script)
        
        env = os.environ.copy()
        env["MSYS_NO_PATHCONV"] = "1"
        adb_path = Settings.get_adb_path()
        subprocess.run(
            [str(adb_path), "-s", self.serial, "push", str(script_path), "/data/local/tmp/zoom.script"],
            env=env, **_subprocess_flags
        )
        subprocess.run(
            [str(adb_path), "-s", self.serial, "shell", "/data/local/tmp/minitouch", "-f", "/data/local/tmp/zoom.script"],
            env=env, **_subprocess_flags
        )
        self.logger.debug("Zoom out executed")
    
    def zoom_in(self, steps: int = 10, duration_ms: int = 300):
        """
        Perform zoom in (pinch out) using minitouch.
        Fingers start at center and move to edges.
        """
        screen_w, screen_h = self._get_screen_size()
        max_x, max_y = self._get_touch_info()
        
        center_x = screen_w // 2
        center_y = screen_h // 2
        
        end_offset = min(screen_w, screen_h) // 3
        
        def to_touch(sx, sy):
            tx = int((sx / screen_w) * max_x)
            ty = int((sy / screen_h) * max_y)
            return tx, ty
        
        wait_per_step = duration_ms // steps
        commands = ["r"]
        
        lx, ly = to_touch(center_x - 10, center_y)
        rx, ry = to_touch(center_x + 10, center_y)
        commands.append(f"d 0 {lx} {ly} 50")
        commands.append(f"d 1 {rx} {ry} 50")
        commands.append("c")
        commands.append(f"w {wait_per_step}")
        
        for i in range(1, steps + 1):
            progress = i / steps
            curr_left_x = center_x - int(end_offset * progress)
            curr_right_x = center_x + int(end_offset * progress)
            
            lx, ly = to_touch(curr_left_x, center_y)
            rx, ry = to_touch(curr_right_x, center_y)
            commands.append(f"m 0 {lx} {ly} 50")
            commands.append(f"m 1 {rx} {ry} 50")
            commands.append("c")
            commands.append(f"w {wait_per_step}")
        
        commands.append("u 0")
        commands.append("u 1")
        commands.append("c")
        
        script = "\n".join(commands)
        script_path = Settings.PROJECT_ROOT / "zoom_script.txt"
        with open(script_path, "w") as f:
            f.write(script)
        
        env = os.environ.copy()
        env["MSYS_NO_PATHCONV"] = "1"
        adb_path = Settings.get_adb_path()
        subprocess.run(
            [str(adb_path), "-s", self.serial, "push", str(script_path), "/data/local/tmp/zoom.script"],
            env=env, **_subprocess_flags
        )
        subprocess.run(
            [str(adb_path), "-s", self.serial, "shell", "/data/local/tmp/minitouch", "-f", "/data/local/tmp/zoom.script"],
            env=env, **_subprocess_flags
        )
        self.logger.debug("Zoom in executed")
