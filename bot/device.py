"""
Device - Comunicacao com dispositivo Android via ADB.
Consolida DeviceManager + VisionEngine.
"""

import json
import os
import re
import subprocess
import sys
import time
from typing import Optional, Tuple

import cv2

from bot.settings import Settings

# Esconde janelas CMD no Windows
if sys.platform == "win32":
    _subprocess_flags = {"creationflags": subprocess.CREATE_NO_WINDOW}
else:
    _subprocess_flags = {}


class Device:
    """
    Gerencia comunicacao com dispositivo Android.
    Combina ADB + reconhecimento de imagem.
    """

    def __init__(self, host: str = None, port: int = None):
        self.host = host or Settings.BLUESTACK_HOST
        self.port = port or Settings.BLUESTACK_PORT
        self.serial = f"{self.host}:{self.port}"
        self._connect()
        self._setup_minitouch()

    # ==================== ADB ====================

    def _run(self, cmd: list) -> subprocess.CompletedProcess:
        """Executa comando ADB."""
        adb = str(Settings.get_adb_path())
        full_cmd = [adb, "-s", self.serial] + cmd
        return subprocess.run(full_cmd, capture_output=True, text=True, **_subprocess_flags)

    def _connect(self):
        """Conecta ao dispositivo."""
        adb = str(Settings.get_adb_path())
        subprocess.run([adb, "connect", self.serial], **_subprocess_flags)

    def open_app(self, package: str):
        """Abre aplicativo pelo package name."""
        self._run(["shell", "monkey", "-p", package, "-c", "android.intent.category.LAUNCHER", "1"])

    def tap(self, x: int, y: int):
        """Toca nas coordenadas."""
        self._run(["shell", "input", "tap", str(x), str(y)])

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300):
        """Faz gesto de swipe."""
        self._run(["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration)])

    def keyevent(self, keycode: int):
        """Envia evento de tecla via ADB.
        
        Args:
            keycode: Codigo da tecla (ex: 4 = BACK/ESC, 3 = HOME)
        """
        self._run(["shell", "input", "keyevent", str(keycode)])

    def screenshot(self, local: str = None) -> str:
        """Captura screenshot."""
        local = local or Settings.SCREENSHOT_FILE
        self._run(["shell", "screencap", "-p", "/sdcard/screen.png"])
        self._run(["pull", "/sdcard/screen.png", local])
        return local

    def _get_screen_size(self) -> Tuple[int, int]:
        """Retorna tamanho da tela."""
        result = self._run(["shell", "wm", "size"])
        match = re.search(r"(\d+)x(\d+)", result.stdout)
        if match:
            return int(match.group(1)), int(match.group(2))
        return 860, 732

    def set_screen_size(self, width: int = 860, height: int = 732):
        """Define tamanho da tela via ADB."""
        self._run(["shell", "wm", "size", f"{width}x{height}"])

    def set_density(self, dpi: int = 160):
        """Define densidade da tela via ADB."""
        self._run(["shell", "wm", "density", str(dpi)])

    def reset_screen(self):
        """Reseta configuracoes de tela para padrao."""
        self._run(["shell", "wm", "size", "reset"])
        self._run(["shell", "wm", "density", "reset"])

    # ==================== VISION ====================

    def find_template(
        self, template: str, threshold: float = 0.8, region: Tuple[int, int, int, int] = None
    ) -> Optional[Tuple[int, int]]:
        """
        Encontra template na tela.

        Args:
            template: Caminho do template (relativo a templates/)
            threshold: Limiar de correspondencia
            region: Regiao para buscar (x1, y1, x2, y2)

        Returns:
            (x, y) do centro ou None
        """
        self.screenshot()

        img = cv2.imread(Settings.SCREENSHOT_FILE, cv2.IMREAD_GRAYSCALE)
        if img is None:
            return None

        template_path = str(Settings.get_template_path(template))
        tmp = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if tmp is None:
            return None

        search_img = img
        offset_x, offset_y = 0, 0

        if region:
            x1, y1, x2, y2 = region
            search_img = img[y1:y2, x1:x2]
            offset_x, offset_y = x1, y1

        res = cv2.matchTemplate(search_img, tmp, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)

        if max_val < threshold:
            return None

        h, w = tmp.shape
        x = max_loc[0] + w // 2 + offset_x
        y = max_loc[1] + h // 2 + offset_y
        return (x, y)

    def image_exists(
        self, template: str, threshold: float = 0.8, region: Tuple[int, int, int, int] = None
    ) -> bool:
        """
        Verifica se uma imagem existe na tela sem clicar.

        Args:
            template: Caminho do template (relativo a templates/)
            threshold: Limiar de correspondencia
            region: Regiao para buscar (x1, y1, x2, y2)

        Returns:
            True se encontrou, False caso contrario
        """
        return self.find_template(template, threshold, region) is not None

    def tap_image(
        self, template: str, threshold: float = 0.8, retries: int = 5, delay: float = 1
    ) -> bool:
        """
        Encontra e clica na imagem.

        Returns:
            True se encontrou e clicou
        """
        regions = self._load_regions()
        region = None

        meta = regions.get(template)
        if meta and meta.get("use_region"):
            region = meta.get("region")

        for _ in range(retries):
            pos = self.find_template(template, threshold, region)
            if pos:
                self.tap(pos[0], pos[1])
                return True
            time.sleep(delay)

        return False

    def find_and_tap_with_scroll(
        self,
        template: str,
        scroll_pixels: int = 150,
        scroll_pos: Tuple[int, int] = None,
        max_scrolls: int = 5,
        threshold: float = 0.75,
        sleep: float = 0.5
    ) -> bool:
        """
        Encontra imagem, se nao achar faz scroll e tenta novamente.
        """
        for attempt in range(max_scrolls + 1):
            pos = self.find_template(template, threshold)
            if pos:
                self.tap(pos[0], pos[1])
                return True

            if attempt < max_scrolls:
                self.scroll_horizontal(scroll_pixels, scroll_pos)
                time.sleep(sleep)

        return False

    def drag_from_image(
        self,
        template: str,
        target_x: int,
        target_y: int,
        threshold: float = 0.8,
        hold_ms: int = 200,
        retries: int = 5,
        delay: float = 1,
        region: Tuple[int, int, int, int] = None
    ) -> bool:
        """
        Encontra uma imagem, segura nela e arrasta para uma posicao de destino.
        
        Args:
            template: Caminho do template (relativo a templates/)
            target_x: Coordenada X de destino
            target_y: Coordenada Y de destino
            threshold: Limiar de correspondencia
            hold_ms: Tempo de segurar antes de mover (em milissegundos)
            retries: Numero de tentativas para encontrar a imagem
            delay: Delay entre tentativas (em segundos)
            region: Regiao para buscar (x1, y1, x2, y2)
        
        Returns:
            True se encontrou a imagem e executou o drag, False caso contrario
        """
        regions = self._load_regions()
        search_region = None

        meta = regions.get(template)
        if meta and meta.get("use_region"):
            search_region = meta.get("region")
        
        if region:
            search_region = region

        for _ in range(retries):
            pos = self.find_template(template, threshold, search_region)
            if pos:
                # Encontrou a imagem, faz o drag usando minitouch
                self._minitouch_swipe(pos[0], pos[1], target_x, target_y, hold_ms=hold_ms)
                return True
            time.sleep(delay)

        return False

    def _load_regions(self) -> dict:
        """Carrega regioes dos templates."""
        path = Settings.get_template_path("templates.json")
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    # ==================== MINITOUCH ====================

    def _setup_minitouch(self):
        """Instala minitouch no dispositivo."""
        check = self._run(["shell", "test -x /data/local/tmp/minitouch && echo OK"])
        if "OK" in check.stdout:
            return

        minitouch_path = Settings.get_minitouch_path()
        if not minitouch_path.exists():
            return

        env = os.environ.copy()
        env["MSYS_NO_PATHCONV"] = "1"
        adb = str(Settings.get_adb_path())

        subprocess.run(
            [adb, "-s", self.serial, "push", str(minitouch_path), "/data/local/tmp/minitouch"],
            env=env,
            capture_output=True,
            **_subprocess_flags,
        )
        self._run(["shell", "chmod", "755", "/data/local/tmp/minitouch"])

    def _get_touch_info(self) -> Tuple[int, int]:
        """Retorna info do touch (max_x, max_y)."""
        env = os.environ.copy()
        env["MSYS_NO_PATHCONV"] = "1"
        adb = str(Settings.get_adb_path())

        result = subprocess.run(
            [adb, "-s", self.serial, "shell", "echo '' | /data/local/tmp/minitouch -i"],
            capture_output=True,
            text=True,
            env=env,
            timeout=5,
            **_subprocess_flags,
        )

        for line in result.stdout.split("\n"):
            if line.startswith("^"):
                parts = line.split()
                return int(parts[2]), int(parts[3])
        return 32767, 32767

    def _minitouch_swipe(self, x1: int, y1: int, x2: int, y2: int, hold_ms: int = 1):
        """Swipe usando minitouch."""
        screen_w, screen_h = self._get_screen_size()
        max_x, max_y = self._get_touch_info()

        def to_touch(sx, sy):
            tx = int((sx / screen_w) * max_x)
            ty = int((sy / screen_h) * max_y)
            return tx, ty

        commands = ["r"]
        tx1, ty1 = to_touch(x1, y1)
        commands.append(f"d 0 {tx1} {ty1} 50")
        commands.append("c")
        commands.append(f"w {hold_ms}")

        tx2, ty2 = to_touch(x2, y2)
        commands.append(f"m 0 {tx2} {ty2} 50")
        commands.append("c")
        commands.append(f"w {hold_ms}")

        commands.append("u 0")
        commands.append("c")

        script = "\n".join(commands)
        script_path = Settings.PROJECT_ROOT / "swipe_script.txt"
        with open(script_path, "w") as f:
            f.write(script)

        env = os.environ.copy()
        env["MSYS_NO_PATHCONV"] = "1"
        adb = str(Settings.get_adb_path())

        subprocess.run(
            [adb, "-s", self.serial, "push", str(script_path), "/data/local/tmp/swipe.script"],
            env=env,
            capture_output=True,
            **_subprocess_flags,
        )
        subprocess.run(
            [
                adb,
                "-s",
                self.serial,
                "shell",
                "/data/local/tmp/minitouch",
                "-f",
                "/data/local/tmp/swipe.script",
            ],
            env=env,
            capture_output=True,
            **_subprocess_flags,
        )

    def scroll_horizontal(self, pixels: int, start_pos: Tuple[int, int] = None):
        """Scroll horizontal."""
        screen_w, screen_h = self._get_screen_size()
        if start_pos:
            x, y = start_pos
        else:
            x, y = screen_w // 2, screen_h // 2

        self._minitouch_swipe(x, y, x - pixels, y, hold_ms=50)

    def scroll_vertical(self, pixels: int, start_pos: Tuple[int, int] = None):
        """Scroll vertical.
        
        Args:
            pixels: Pixels para scroll (positivo = para baixo, negativo = para cima)
            start_pos: Posicao inicial (x, y). Se None, usa o centro da tela.
        """
        screen_w, screen_h = self._get_screen_size()
        if start_pos:
            x, y = start_pos
        else:
            x, y = screen_w // 2, screen_h // 2

        self._minitouch_swipe(x, y, x, y - pixels, hold_ms=50)

    def center_view(self, move_right: int = 200, move_down: int = 0):
        """Centraliza camera do jogo."""
        screen_w, screen_h = self._get_screen_size()
        center_x, center_y = screen_w // 2, screen_h // 2

        # Move tudo para canto esquerdo
        self._minitouch_swipe(100, center_y, screen_w - 100, center_y, hold_ms=200)
        time.sleep(0.2)

        # Move tudo para cima
        self._minitouch_swipe(center_x, 100, center_x, screen_h - 100, hold_ms=200)
        time.sleep(0.2)

        # Ajuste fino
        if move_right > 0:
            self._minitouch_swipe(center_x, center_y, center_x - move_right, center_y, hold_ms=200)
            time.sleep(0.1)

        if move_down > 0:
            self._minitouch_swipe(center_x, center_y, center_x, center_y + move_down, hold_ms=200)

    def zoom_out(self, steps: int = 10, duration_ms: int = 300):
        """Zoom out usando minitouch (pinch in)."""
        screen_w, screen_h = self._get_screen_size()
        max_x, max_y = self._get_touch_info()

        center_x, center_y = screen_w // 2, screen_h // 2
        start_offset = min(screen_w, screen_h) // 3
        left_x = center_x - start_offset
        right_x = center_x + start_offset

        def to_touch(sx, sy):
            return int((sx / screen_w) * max_x), int((sy / screen_h) * max_y)

        wait_per_step = duration_ms // steps
        commands = ["r"]

        lx, ly = to_touch(left_x, center_y)
        rx, ry = to_touch(right_x, center_y)
        commands.append(f"d 0 {lx} {ly} 50")
        commands.append(f"d 1 {rx} {ry} 50")
        commands.append("c")
        commands.append(f"w {wait_per_step}")

        for i in range(1, steps + 1):
            progress = i / steps
            curr_left_x = left_x + int((center_x - left_x) * progress)
            curr_right_x = right_x - int((right_x - center_x) * progress)

            lx, ly = to_touch(curr_left_x, center_y)
            rx, ry = to_touch(curr_right_x, center_y)
            commands.append(f"m 0 {lx} {ly} 50")
            commands.append(f"m 1 {rx} {ry} 50")
            commands.append("c")
            commands.append(f"w {wait_per_step}")

        commands.append("u 0")
        commands.append("u 1")
        commands.append("c")

        script = "\n".join(commands)
        script_path = Settings.PROJECT_ROOT / "zoom_script.txt"
        with open(script_path, "w") as f:
            f.write(script)

        env = os.environ.copy()
        env["MSYS_NO_PATHCONV"] = "1"
        adb = str(Settings.get_adb_path())

        subprocess.run(
            [adb, "-s", self.serial, "push", str(script_path), "/data/local/tmp/zoom.script"],
            env=env,
            **_subprocess_flags,
        )
        subprocess.run(
            [
                adb,
                "-s",
                self.serial,
                "shell",
                "/data/local/tmp/minitouch",
                "-f",
                "/data/local/tmp/zoom.script",
            ],
            env=env,
            **_subprocess_flags,
        )
