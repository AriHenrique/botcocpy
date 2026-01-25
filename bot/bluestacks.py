"""
BlueStacks - Controle do emulador.
"""

import os
import re
import subprocess
import sys
import time

from bot.settings import Settings

# Esconde janelas CMD no Windows
if sys.platform == "win32":
    _subprocess_flags = {"creationflags": subprocess.CREATE_NO_WINDOW}
else:
    _subprocess_flags = {}


class BlueStacks:
    """Controle do BlueStacks."""

    @staticmethod
    def kill():
        """Encerra todos os processos do BlueStacks."""
        for proc in ["HD-Player.exe", "HD-Service.exe", "HD-Frontend.exe"]:
            subprocess.run(
                ["taskkill", "/F", "/IM", proc],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                **_subprocess_flags,
            )

    @staticmethod
    def start():
        """Inicia o BlueStacks."""
        if os.path.exists(Settings.BLUESTACKS_EXE):
            subprocess.Popen([Settings.BLUESTACKS_EXE])
            time.sleep(15)

    @staticmethod
    def configure():
        """Configura resolucao do BlueStacks."""
        conf_path = Settings.BLUESTACKS_CONF

        if not os.path.exists(conf_path):
            raise RuntimeError("bluestacks.conf not found")

        with open(conf_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        text = "".join(lines)

        # Detecta instancia
        match = re.search(r"bst\.instance\.([^.]+)\.adb_port", text)
        if not match:
            raise RuntimeError("Could not detect BlueStacks instance")

        instance = match.group(1)

        # Configuracoes
        settings = {
            "fb_width": Settings.TARGET_WIDTH,
            "fb_height": Settings.TARGET_HEIGHT,
            "dpi": Settings.TARGET_DPI,
            "gl_win_height": Settings.TARGET_HEIGHT,
            "show_sidebar": "0",
        }

        # Aplica configuracoes
        for key, value in settings.items():
            pattern = re.compile(
                rf'(bst\.instance\.{re.escape(instance)}\.{re.escape(key)}=)"[^"]*"'
            )

            replaced = False
            new_lines = []
            for line in lines:
                if pattern.search(line):
                    new_lines.append(f'bst.instance.{instance}.{key}="{value}"\n')
                    replaced = True
                else:
                    new_lines.append(line)

            if not replaced:
                new_lines.append(f'bst.instance.{instance}.{key}="{value}"\n')

            lines = new_lines

        with open(conf_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    @staticmethod
    def validate_adb():
        """Valida conexao ADB."""
        adb = str(Settings.get_adb_path())
        device = f"{Settings.BLUESTACK_HOST}:{Settings.BLUESTACK_PORT}"

        subprocess.run([adb, "connect", device], **_subprocess_flags)
        result = subprocess.run(
            [adb, "-s", device, "shell", "wm", "size"],
            capture_output=True,
            text=True,
            **_subprocess_flags,
        )
        return result.stdout.strip()
