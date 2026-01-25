"""
Bot COC - Ponto de entrada principal.
"""

import os
import sys

# Adiciona diretorio raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.gui import main

if __name__ == "__main__":
    main()
