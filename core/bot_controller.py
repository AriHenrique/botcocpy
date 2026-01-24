"""
Bot Controller - Main orchestrator for bot operations.
"""
from typing import Optional

from core.device_manager import DeviceManager
from core.army_manager import ArmyManager
from core.game_actions import GameActions
from config.config_manager import ConfigManager
from config.settings import Settings
from utils.logger import get_bot_logger


class BotController:
    """
    Main bot controller that orchestrates all bot operations.
    """
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[str] = None,
        config_manager: Optional[ConfigManager] = None
    ):
        """
        Initialize bot controller.
        
        Args:
            host: ADB host (defaults to Settings)
            port: ADB port (defaults to Settings)
            config_manager: ConfigManager instance (creates new if not provided)
        """
        self.logger = get_bot_logger(__name__)
        self.config_manager = config_manager or ConfigManager()
        
        # Initialize components
        self.device = DeviceManager(host=host, port=port)
        self.army_manager = ArmyManager(self.device, self.config_manager)
        self.game_actions = GameActions(self.device)
        
        self.logger.info("Bot controller initialized")
    
    def setup_bluestacks(self):
        """Setup and configure BlueStacks."""
        from core.bluestacks_manager import BlueStacksManager
        
        bs_manager = BlueStacksManager()
        bs_manager.kill()
        bs_manager.configure()
        bs_manager.start()
        bs_manager.validate_adb()
    
    def initialize_game(self, move_right: int = 100, move_down: int = -50) -> bool:
        """
        Initialize game session.
        
        Args:
            move_right: Pixels to move right for centering
            move_down: Pixels to move down for centering
            
        Returns:
            True if successful
        """
        return self.game_actions.init_game(move_right=move_right, move_down=move_down)
    
    def train_army(self) -> bool:
        """
        Train new army.
        
        Returns:
            True if successful
        """
        return self.army_manager.train_army()
    
    def donate_to_castle(self) -> bool:
        """
        Donate troops to clan castle.
        
        Returns:
            True if successful
        """
        return self.game_actions.donate_castle()
    
    def request_from_castle(self) -> bool:
        """
        Request troops from clan castle.
        
        Returns:
            True if successful
        """
        return self.game_actions.request_castle()
    
    def delete_army(self, delete_castle: bool = True) -> bool:
        """
        Delete current army.
        
        Args:
            delete_castle: Whether to delete castle troops
            
        Returns:
            True if successful
        """
        return self.army_manager.delete_army(delete_castle=delete_castle)
    
    def create_army(self, open_menu: bool = True) -> bool:
        """
        Create army from configuration.
        
        Args:
            open_menu: Whether to open army menu first
            
        Returns:
            True if successful
        """
        return self.army_manager.create_army(open_menu=open_menu)
