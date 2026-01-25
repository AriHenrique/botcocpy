"""
Bot Settings - Configuracoes centralizadas.
"""

import sys
from pathlib import Path


class Settings:
    """Configuracoes do bot."""

    # Detecta se esta rodando como .exe
    _is_frozen = getattr(sys, "frozen", False)
    if _is_frozen:
        if hasattr(sys, "_MEIPASS"):
            PROJECT_ROOT = Path(sys._MEIPASS)
        else:
            PROJECT_ROOT = Path(sys.executable).parent
    else:
        PROJECT_ROOT = Path(__file__).parent.parent

    # BlueStacks
    BLUESTACK_HOST = "127.0.0.1"
    BLUESTACK_PORT = 5556
    BLUESTACKS_CONF = r"C:\ProgramData\BlueStacks_nxt\bluestacks.conf"
    BLUESTACKS_EXE = r"C:\Program Files\BlueStacks_nxt\HD-Player.exe"

    # Resolucao alvo
    TARGET_WIDTH = "860"
    TARGET_HEIGHT = "732"
    TARGET_DPI = "160"

    # Jogo
    GAME_PACKAGE = "com.supercell.clashofclans"

    # Arquivos
    SCREENSHOT_FILE = "screen.png"
    TEMPLATE_DIR = "templates"
    CONFIG_DIR = "config"
    LOCALES_DIR = "locales"

    # ADB
    _adb_path = None

    @classmethod
    def get_adb_path(cls) -> Path:
        """Retorna caminho do ADB."""
        if cls._adb_path and cls._adb_path.exists():
            return cls._adb_path

        # Tenta encontrar ADB
        paths = [
            cls.PROJECT_ROOT / "resources" / "adb" / "adb.exe",
            Path(r"C:\android\platform-tools\adb.exe"),
            Path(r"C:\Program Files\Android\android-sdk\platform-tools\adb.exe"),
        ]

        for path in paths:
            if path.exists():
                cls._adb_path = path
                return path

        # Tenta no PATH
        import shutil

        adb = shutil.which("adb")
        if adb:
            cls._adb_path = Path(adb)
            return cls._adb_path

        # Fallback
        cls._adb_path = Path(r"C:\android\platform-tools\adb.exe")
        return cls._adb_path

    @classmethod
    def get_template_path(cls, template: str) -> Path:
        """Retorna caminho completo do template."""
        return cls.PROJECT_ROOT / cls.TEMPLATE_DIR / template

    @classmethod
    def get_config_path(cls, filename: str) -> Path:
        """Retorna caminho completo do config."""
        return cls.PROJECT_ROOT / cls.CONFIG_DIR / filename

    @classmethod
    def get_minitouch_path(cls) -> Path:
        """Retorna caminho do minitouch."""
        return cls.PROJECT_ROOT / "resources" / "adb_scripts" / "minitouch"
