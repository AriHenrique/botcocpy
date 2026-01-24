"""
Game Actions - Handles in-game actions like donations, requests, etc.
"""
import time
from typing import Optional

from core.device_manager import DeviceManager
from utils.logger import get_donate_logger, get_game_logger


class GameActions:
    """
    Handles various in-game actions.
    """
    
    def __init__(self, device: DeviceManager):
        """
        Initialize game actions.
        
        Args:
            device: DeviceManager instance
        """
        self.device = device
        self.donate_logger = get_donate_logger(__name__)
        self.game_logger = get_game_logger(__name__)
    
    def donate_castle(self) -> bool:
        """
        Donate troops to clan castle.
        
        Returns:
            True if successful, False otherwise
        """
        self.donate_logger.info("Starting castle donation...")
        
        # Open chat
        self._open_chat()
        
        # Tap donate button
        self.device.tap_image("donate/donate_castle.png", threshold=0.85)
        time.sleep(2)
        
        donation_count = 0
        while True:
            if self.device.tap_image("donate/select_super_troop_donate.png", threshold=0.85):
                self.donate_logger.debug("Donated super troop")
                donation_count += 1
            elif self.device.tap_image("donate/select_spell_donate.png", threshold=0.85):
                self.donate_logger.debug("Donated spell")
                donation_count += 1
            elif self.device.tap_image("donate/select_troop_donate.png", threshold=0.85):
                self.donate_logger.debug("Donated troop")
                donation_count += 1
            else:
                break
            
            time.sleep(0.5)
        
        self.donate_logger.info(f"Donation complete. Total donations: {donation_count}")
        return True
    
    def request_castle(self) -> bool:
        """
        Request troops from clan castle.
        
        Returns:
            True if successful, False otherwise
        """
        self.donate_logger.info("Requesting from castle...")
        
        # Open army menu
        self._open_army()
        
        # Tap request button
        self.device.tap_image("donate/request_castle.png", threshold=0.85)
        time.sleep(2)
        
        # Send request
        self.device.tap_image("donate/send_troops.png", threshold=0.85)
        time.sleep(1)
        
        self.donate_logger.info("Request sent successfully")
        return True
    
    def init_game(self, move_right: int = 100, move_down: int = -50) -> bool:
        """
        Initialize game: open app, zoom out, center view.
        
        Args:
            move_right: Pixels to move right for centering
            move_down: Pixels to move down for centering
            
        Returns:
            True if successful, False otherwise
        """
        from config.settings import Settings
        
        self.game_logger.info("Initializing game...")
        
        # Open game
        self.device.open_app(Settings.GAME_PACKAGE)
        
        self.game_logger.info("Waiting for game to load...")
        time.sleep(15)
        
        # Zoom out
        self.game_logger.info("Zooming out...")
        self.device.zoom_out(steps=15, duration_ms=500)
        time.sleep(0.5)
        self.device.zoom_out(steps=15, duration_ms=500)
        time.sleep(0.3)
        
        # Center view
        self.device.center_view(move_right=move_right, move_down=move_down)
        
        self.game_logger.info("Game initialized")
        return True
    
    def _open_chat(self):
        """Open chat menu."""
        try:
            self.device.tap_image("menu/bt_chat.png", threshold=0.85)
        except Exception:
            # Try closing and reopening
            try:
                self.device.tap_image("menu/bt_close_chat.png", threshold=0.85)
            except:
                pass
            self.device.tap_image("menu/bt_chat.png", threshold=0.85)
    
    def _open_army(self):
        """Open army menu."""
        self.device.tap_image("menu/bt_army.png", threshold=0.85)
        time.sleep(0.5)
