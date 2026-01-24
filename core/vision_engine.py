"""
Vision Engine - Handles template matching and image recognition.
"""
import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Tuple

from config.settings import Settings
from utils.logger import get_vision_logger


class VisionEngine:
    """
    Handles computer vision operations: template matching, image recognition.
    """
    
    def __init__(self):
        """Initialize vision engine."""
        self.logger = get_vision_logger(__name__)
    
    def find_template(
        self,
        screenshot_path: str,
        template_path: str,
        threshold: float = 0.8,
        region: Optional[Tuple[int, int, int, int]] = None
    ) -> Optional[Tuple[int, int]]:
        """
        Find template in screenshot.
        Compatible with old vision.find_template signature.
        
        Args:
            screenshot_path: Path to screenshot image
            template_path: Path to template image (can be relative or absolute)
            threshold: Matching threshold (0.0-1.0)
            region: Optional region (x1, y1, x2, y2) to search in (old format)
                   or (x, y, width, height) if tuple has 4 elements
            
        Returns:
            Tuple (x, y) of center of match, or None if not found
        """
        # Read images in grayscale (compatible with old version)
        img = cv2.imread(screenshot_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            self.logger.error(f"Could not read screenshot: {screenshot_path}")
            return None
        
        # Get full template path if relative
        if not Path(template_path).is_absolute():
            template_path = str(Settings.get_template_path(template_path))
        
        tmp = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if tmp is None:
            self.logger.error(f"Could not read template: {template_path}")
            return None
        
        # Handle region (old format: x1, y1, x2, y2)
        search_img = img
        offset_x = 0
        offset_y = 0
        
        if region:
            if len(region) == 4:
                # Old format: (x1, y1, x2, y2)
                x1, y1, x2, y2 = region
                search_img = img[y1:y2, x1:x2]
                offset_x = x1
                offset_y = y1
        
        # Template matching
        res = cv2.matchTemplate(search_img, tmp, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        
        if max_val < threshold:
            self.logger.debug(
                f"Template not found (confidence: {max_val:.2f}, threshold: {threshold})"
            )
            return None
        
        # Calculate center position
        h, w = tmp.shape
        x = max_loc[0] + w // 2 + offset_x
        y = max_loc[1] + h // 2 + offset_y
        
        self.logger.debug(
            f"Found template at ({x}, {y}) with confidence {max_val:.2f}"
        )
        return (x, y)
    
    def wait_for_template(
        self,
        screenshot_path: str,
        template_path: str,
        timeout: float = 30.0,
        threshold: float = 0.8,
        check_interval: float = 1.0
    ) -> Optional[Tuple[int, int]]:
        """
        Wait for template to appear in screenshot.
        
        Args:
            screenshot_path: Path to screenshot (will be updated)
            template_path: Path to template image
            timeout: Maximum time to wait (seconds)
            threshold: Matching threshold
            check_interval: Time between checks (seconds)
            
        Returns:
            Tuple (x, y) of center of match, or None if timeout
        """
        import time
        
        start_time = time.time()
        self.logger.info(f"Waiting for template: {template_path} (timeout: {timeout}s)")
        
        while time.time() - start_time < timeout:
            result = self.find_template(screenshot_path, template_path, threshold)
            if result:
                return result
            time.sleep(check_interval)
        
        self.logger.warning(f"Timeout waiting for template: {template_path}")
        return None
