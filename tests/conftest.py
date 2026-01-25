"""Configuracao do pytest."""

import sys
from pathlib import Path

# Adiciona diretorio raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))
