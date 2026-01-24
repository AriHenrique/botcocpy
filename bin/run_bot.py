"""
Entry point para executar o bot.
Este arquivo facilita a execução: python run_bot.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.bot_controller import BotController
from utils.logger import get_bot_logger

logger = get_bot_logger(__name__)


def main():
    """Main bot execution."""
    try:
        # Initialize bot controller
        bot = BotController()
        
        # Setup BlueStacks (optional - uncomment if needed)
        # bot.setup_bluestacks()
        
        # Initialize game
        bot.initialize_game(move_right=100, move_down=-50)
        
        # Example: Train army
        # bot.train_army()
        
        # Example: Donate to castle
        # bot.donate_to_castle()
        
        # Example: Request from castle
        # bot.request_from_castle()
        
        logger.info("Bot execution completed successfully")
        
    except Exception as e:
        logger.error(f"Bot execution failed: {e}", exc_info=True)


if __name__ == "__main__":
    main()
