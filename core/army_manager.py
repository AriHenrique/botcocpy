"""
Army Manager - Handles army creation, deletion, and management.
"""
import time
from typing import List, Dict, Optional
from pathlib import Path

from config.config_manager import ConfigManager
from config.settings import Settings
from core.device_manager import DeviceManager
from utils.logger import get_army_logger


class ArmyManager:
    """
    Manages army operations: creation, deletion, training.
    """
    
    def __init__(self, device: DeviceManager, config_manager: ConfigManager = None):
        """
        Initialize army manager.
        
        Args:
            device: DeviceManager instance
            config_manager: ConfigManager instance (creates new if not provided)
        """
        self.device = device
        self.config_manager = config_manager or ConfigManager()
        self.logger = get_army_logger(__name__)
        self._army_config = None
    
    def load_config(self) -> Dict:
        """Load army configuration from file."""
        self._army_config = self.config_manager.load_config(
            "army.json",
            default={"troops": [], "spells": [], "notes": ""}
        )
        return self._army_config
    
    def save_config(self, config: Dict = None) -> bool:
        """
        Save army configuration to file.
        
        Args:
            config: Configuration dict (uses current if not provided)
        """
        config = config or self._army_config
        if not config:
            self.logger.warning("No configuration to save")
            return False
        
        return self.config_manager.save_config("army.json", config)
    
    def list_available_troops(self) -> List[str]:
        """List all available troop templates."""
        troops_dir = Settings.PROJECT_ROOT / Settings.TEMPLATE_DIR / "troops"
        troops = []
        
        if troops_dir.exists():
            for f in troops_dir.glob("*.png"):
                troops.append(f.stem)
        
        return sorted(troops)
    
    def create_army(self, open_menu: bool = True) -> bool:
        """
        Create army based on configuration.
        
        Args:
            open_menu: Whether to open army menu first
            
        Returns:
            True if successful, False otherwise
        """
        if not self._army_config:
            self.load_config()
        
        troops = self._army_config.get("troops", [])
        
        if not troops:
            self.logger.warning("No troops configured in army.json")
            return False
        
        self.logger.info(f"Creating army with {len(troops)} troop types...")
        
        if open_menu:
            # Open army menu
            self.device.tap_image("menu/bt_army.png", threshold=0.8)
            time.sleep(1)
            self.device.tap_image("menu/open_troops_create.png", threshold=0.8)
            time.sleep(1)
        
        scroll_pos = (750, 617)  # Position for scrolling
        
        for troop in troops:
            name = troop.get("name")
            quantity = troop.get("quantity", 1)
            
            if not name:
                continue
            
            template = f"troops/{name}.png"
            self.logger.info(f"Adding {quantity}x {name}")
            
            for i in range(quantity):
                found = self.device.find_and_tap_with_scroll(
                    template=template,
                    scroll_pixels=150,
                    scroll_pos=scroll_pos,
                    max_scrolls=5,
                    threshold=0.75
                )
                
                if not found:
                    self.logger.warning(f"Could not find {name}, skipping...")
                    break
                
                time.sleep(0.1)
        
        self.logger.info("Army creation complete")
        return True
    
    def delete_army(self, delete_castle: bool = True) -> bool:
        """
        Delete current army.
        
        Args:
            delete_castle: Whether to delete castle troops
            
        Returns:
            True if successful, False otherwise
        """
        self.logger.info("Deleting army...")
        
        # Open army menu
        self.device.tap_image("menu/bt_army.png", threshold=0.85)
        time.sleep(0.5)
        
        if delete_castle:
            self.device.tap_image("delete_army/delete_castle.png", threshold=0.85)
            self.device.tap_image("menu/bt_ok.png", threshold=0.85)
            time.sleep(0.3)
        
        self.device.tap_image("delete_army/delete_machines.png", threshold=0.85)
        self.device.tap_image("menu/bt_ok.png", threshold=0.85)
        time.sleep(0.3)
        
        self.device.tap_image("delete_army/delete_spells.png", threshold=0.85)
        self.device.tap_image("menu/bt_ok.png", threshold=0.85)
        time.sleep(0.3)
        
        self.device.tap_image("delete_army/delete_trops.png", threshold=0.85)
        self.device.tap_image("menu/bt_ok.png", threshold=0.85)
        time.sleep(0.3)
        
        self.logger.info("Army deleted")
        return True
    
    def train_army(self) -> bool:
        """
        Train new army: delete current and create new.
        
        Returns:
            True if successful, False otherwise
        """
        self.logger.info("Training new army...")
        
        # Delete current army
        self.delete_army(delete_castle=False)
        time.sleep(0.5)
        
        # Create new army
        self.create_army(open_menu=False)
        
        # Close menu
        self.device.tap_image("menu/bt_close.png", threshold=0.8)
        
        self.logger.info("Training complete")
        return True
