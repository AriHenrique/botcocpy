"""
Main entry point for Bot COC.
Always starts the GUI interface.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ui.gui import main

if __name__ == "__main__":
    main()
