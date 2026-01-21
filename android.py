import subprocess
import xml.etree.ElementTree as ET
import time
import re
import os
import json
from config import ADB_PATH, BLUESTACK_HOST, BLUESTACK_PORT, SCREENSHOT_FILE, TEMPLATE_DIR
from vision import find_template


class AndroidDevice:
    def __init__(self, host=BLUESTACK_HOST, port=BLUESTACK_PORT):
        self.serial = f"{host}:{port}"
        self._connect()
        self._setup_minitouch()

    # ================= CORE =================
    def _run(self, cmd):
        full = [ADB_PATH, "-s", self.serial] + cmd
        return subprocess.run(full, capture_output=True, text=True)

    def _connect(self):
        print(f"[ADB] Connecting to {self.serial}")
        subprocess.run([ADB_PATH, "connect", self.serial])

    # ================= APP =================
    def open_app(self, package):
        print(f"[ADB] Opening app: {package}")
        self._run([
            "shell", "monkey",
            "-p", package,
            "-c", "android.intent.category.LAUNCHER", "1"
        ])

    # ================= INPUT =================
    def tap(self, x, y):
        print(f"[ADB] Tap at {x},{y}")
        self._run(["shell", "input", "tap", str(x), str(y)])

    def swipe(self, x1, y1, x2, y2, duration=300):
        print(f"[ADB] Swipe {x1},{y1} -> {x2},{y2}")
        self._run([
            "shell", "input", "swipe",
            str(x1), str(y1), str(x2), str(y2), str(duration)
        ])

    def _minitouch_swipe(self, x1, y1, x2, y2, hold_ms=1):
        """
        Swipe direto usando minitouch: pressiona, arrasta, solta.
        Movimento instantâneo e exato.
        """
        screen_w, screen_h = self._get_screen_size()
        max_x, max_y = self._get_touch_info()

        def to_touch(sx, sy):
            tx = int((sx / screen_w) * max_x)
            ty = int((sy / screen_h) * max_y)
            return tx, ty

        commands = ["r"]

        # Touch down na posição inicial
        tx1, ty1 = to_touch(x1, y1)
        commands.append(f"d 0 {tx1} {ty1} 50")
        commands.append("c")
        commands.append(f"w {hold_ms}")

        # Move direto para posição final
        tx2, ty2 = to_touch(x2, y2)
        commands.append(f"m 0 {tx2} {ty2} 50")
        commands.append("c")
        commands.append(f"w {hold_ms}")

        # Touch up
        commands.append("u 0")
        commands.append("c")

        script = "\n".join(commands)
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "swipe_script.txt")
        with open(script_path, "w") as f:
            f.write(script)

        env = os.environ.copy()
        env["MSYS_NO_PATHCONV"] = "1"
        subprocess.run(
            [ADB_PATH, "-s", self.serial, "push", script_path, "/data/local/tmp/swipe.script"],
            env=env, capture_output=True
        )
        subprocess.run(
            [ADB_PATH, "-s", self.serial, "shell", "/data/local/tmp/minitouch", "-f", "/data/local/tmp/swipe.script"],
            env=env, capture_output=True
        )

    def center_view(self, move_right=200, move_down=0, hold_ms=200):
        """
        Centraliza a câmera do jogo com movimento fixo e exato.

        1. Move toda a câmera para o canto esquerdo (arrasta para direita)
        2. Move toda a câmera para cima (arrasta para baixo)
        3. Move valor fixo para a direita
        4. Move valor fixo para baixo (opcional)

        Args:
            move_right: pixels para mover a câmera para a direita
            move_down: pixels para mover a câmera para baixo
            hold_ms: tempo de hold do swipe de ajuste
        """
        screen_w, screen_h = self._get_screen_size()
        center_x = screen_w // 2
        center_y = screen_h // 2

        print("[ADB] Centering view...")

        # Move tudo para o canto esquerdo (arrasta para direita)
        self._minitouch_swipe(100, center_y, screen_w - 100, center_y, hold_ms=200)
        time.sleep(0.2)

        # Move tudo para cima (arrasta para baixo)
        self._minitouch_swipe(center_x, 100, center_x, screen_h - 100, hold_ms=200)
        time.sleep(0.2)

        # Move valor fixo para a direita (arrasta para esquerda)
        if move_right > 0:
            self._minitouch_swipe(
                center_x, center_y,
                center_x - move_right, center_y,
                hold_ms=hold_ms
            )
            time.sleep(0.1)

        # Move valor fixo para baixo (arrasta para cima)
        if move_down > 0:
            self._minitouch_swipe(
                center_x, center_y,
                center_x, center_y - move_down,
                hold_ms=hold_ms
            )

        print(f"[ADB] View centered (moved {move_right}px right, {move_down}px down)")

    def scroll_horizontal(self, scroll_pixels, start_pos=None, hold_ms=50):
        """
        Arrasta horizontalmente a partir de uma posição na tela.

        Args:
            scroll_pixels: pixels para arrastar (positivo = direita para esquerda)
            start_pos: tupla (x, y) da posição inicial. Se None, usa centro da tela.
            hold_ms: tempo de hold do swipe (maior = mais lento, evita ser interpretado como clique)
        """
        screen_w, screen_h = self._get_screen_size()

        if start_pos:
            x, y = start_pos
        else:
            x = screen_w // 2
            y = screen_h // 2

        self._minitouch_swipe(x, y, x - scroll_pixels, y, hold_ms=hold_ms)
        print(f"[ADB] Scrolled {scroll_pixels}px left from ({x}, {y})")

    def find_and_tap_with_scroll(self, template, scroll_pixels=150, scroll_pos=None,
                                  max_scrolls=5, threshold=0.75, scroll_hold_ms=50):
        """
        Procura uma imagem na tela, se não encontrar faz scroll horizontal e tenta novamente.

        Args:
            template: imagem para encontrar e clicar
            scroll_pixels: pixels para arrastar a cada tentativa
            scroll_pos: tupla (x, y) da posição para fazer scroll. Se None, usa centro da tela.
            max_scrolls: número máximo de scrolls antes de desistir
            threshold: limiar de detecção
            scroll_hold_ms: tempo de hold do scroll

        Returns:
            True se encontrou e clicou, False caso contrário
        """
        template_path = os.path.join(TEMPLATE_DIR, template)

        for attempt in range(max_scrolls + 1):
            self.screenshot()
            pos = find_template(SCREENSHOT_FILE, template_path, threshold)

            if pos:
                self.tap(pos[0], pos[1])
                return True

            if attempt < max_scrolls:
                print(f"[ADB] {template} not found, scrolling... ({attempt + 1}/{max_scrolls})")
                self.scroll_horizontal(scroll_pixels, scroll_pos, hold_ms=scroll_hold_ms)
                time.sleep(5)

        print(f"[ADB] {template} not found after {max_scrolls} scrolls")
        return False

    def type(self, text):
        safe = text.replace(" ", "%s")
        print(f"[ADB] Type: {text}")
        self._run(["shell", "input", "text", safe])

    # ================= SCREEN =================
    def screenshot(self, local=SCREENSHOT_FILE):
        self._run(["shell", "screencap", "-p", "/sdcard/screen.png"])
        self._run(["pull", "/sdcard/screen.png", local])
        return local

    # ================= UI XML =================
    def dump_ui(self):
        self._run(["shell", "uiautomator", "dump", "/sdcard/ui.xml"])
        self._run(["pull", "/sdcard/ui.xml", "ui.xml"])
        return ET.parse("ui.xml")

    def _find_node(self, attr, value):
        tree = self.dump_ui()
        for node in tree.iter("node"):
            if node.attrib.get(attr) == value:
                return node
        return None

    def _bounds_center(self, bounds):
        nums = list(map(int, re.findall(r"\d+", bounds)))
        x = (nums[0] + nums[2]) // 2
        y = (nums[1] + nums[3]) // 2
        return x, y

    def tap_text(self, text):
        node = self._find_node("text", text)
        if not node:
            raise Exception(f"Text not found: {text}")
        x, y = self._bounds_center(node.attrib["bounds"])
        self.tap(x, y)

    # ================= VISION =================
    def tap_image(self, template, threshold=0.8, retries=5, delay=1):
        regions = self._load_regions()
        region = None

        meta = regions.get(template)
        if meta and meta.get("use_region"):
            region = meta.get("region")

        template_path = os.path.join(TEMPLATE_DIR, template)
        print(f"[VISION] Looking for {template_path} (region={region})")

        for i in range(retries):
            screen = self.screenshot()
            pos = find_template(screen, template_path, threshold, region=region)
            if pos:
                self.tap(pos[0], pos[1])
                return True
            print(f"[VISION] Retry {i+1}/{retries}")
            time.sleep(delay)

        raise Exception(f"Image not found: {template}")

    def wait_image(self, template, timeout=30, threshold=0.8):
        template_path = os.path.join(TEMPLATE_DIR, template)
        print(f"[VISION] Waiting for {template_path}")
        start = time.time()
        while time.time() - start < timeout:
            screen = self.screenshot()
            pos = find_template(screen, template_path, threshold)
            if pos:
                print(f"[VISION] Found {template_path}")
                return True
            time.sleep(1)

        raise TimeoutError(f"Timeout waiting for {template_path}")

    def _load_regions(self):
        path = os.path.join(TEMPLATE_DIR, "templates.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def zoom_out_hold_fake(self, seconds=3, interval=0.05):
        """
        Simula segurar DPAD_DOWN enviando keyevents rápidos
        """
        import time

        print("[ADB] Fake holding DPAD_DOWN")

        self._run(["shell", "input", "keyevent", "KEYCODE_D"])
        time.sleep(0.2)

        end = time.time() + seconds
        while time.time() < end:
            self._run(["shell", "input", "keyevent", "KEYCODE_DPAD_DOWN"])
            time.sleep(interval)

    # ================= MINITOUCH ZOOM =================
    def _setup_minitouch(self):
        """Instala o minitouch no dispositivo automaticamente"""
        # Verifica se já está instalado e funcionando
        check = self._run(["shell", "test -x /data/local/tmp/minitouch && echo OK"])
        if "OK" in check.stdout:
            print("[MINITOUCH] Already installed")
            return

        print("[MINITOUCH] Installing...")

        # Encontra o binário local
        script_dir = os.path.dirname(os.path.abspath(__file__))
        minitouch_path = os.path.join(script_dir, "adb.scripts", "minitouch")

        if not os.path.exists(minitouch_path):
            raise FileNotFoundError(f"Minitouch binary not found: {minitouch_path}")

        # Push para o dispositivo
        env = os.environ.copy()
        env["MSYS_NO_PATHCONV"] = "1"

        result = subprocess.run(
            [ADB_PATH, "-s", self.serial, "push", minitouch_path, "/data/local/tmp/minitouch"],
            env=env, capture_output=True, text=True
        )

        if result.returncode != 0:
            raise RuntimeError(f"Failed to push minitouch: {result.stderr}")

        # Dá permissão de execução
        self._run(["shell", "chmod", "755", "/data/local/tmp/minitouch"])

        # Verifica se funciona
        test = self._run(["shell", "/data/local/tmp/minitouch", "-h"])
        if "Usage:" in test.stdout:
            print("[MINITOUCH] Installed successfully")
        else:
            raise RuntimeError("Minitouch installation failed - binary may be incompatible")

    def _get_touch_info(self):
        """Obtém informações do touch device (max_x, max_y)"""
        env = os.environ.copy()
        env["MSYS_NO_PATHCONV"] = "1"
        result = subprocess.run(
            [ADB_PATH, "-s", self.serial, "shell",
             "echo '' | /data/local/tmp/minitouch -i"],
            capture_output=True, text=True, env=env, timeout=5
        )
        # Parse: ^ 2 32767 32767 0
        for line in result.stdout.split('\n'):
            if line.startswith('^'):
                parts = line.split()
                return int(parts[2]), int(parts[3])  # max_x, max_y
        return 32767, 32767  # fallback

    def _get_screen_size(self):
        """Obtém tamanho da tela"""
        result = self._run(["shell", "wm", "size"])
        match = re.search(r"(\d+)x(\d+)", result.stdout)
        if match:
            return int(match.group(1)), int(match.group(2))
        return 860, 732  # fallback

    def zoom_out(self, steps=10, duration_ms=300):
        """
        Faz zoom out (pinch in) usando minitouch.
        Os dedos começam nas bordas e vão para o centro.
        """
        screen_w, screen_h = self._get_screen_size()
        max_x, max_y = self._get_touch_info()

        # Centro da tela
        center_x = screen_w // 2
        center_y = screen_h // 2

        # Pontos iniciais (dedos afastados horizontalmente)
        start_offset = min(screen_w, screen_h) // 3
        left_x = center_x - start_offset
        right_x = center_x + start_offset

        # Converter para coordenadas do touch
        def to_touch(sx, sy):
            tx = int((sx / screen_w) * max_x)
            ty = int((sy / screen_h) * max_y)
            return tx, ty

        # Gerar script de pinch
        wait_per_step = duration_ms // steps
        commands = ["r"]  # reset

        # Touch down nos dois pontos
        lx, ly = to_touch(left_x, center_y)
        rx, ry = to_touch(right_x, center_y)
        commands.append(f"d 0 {lx} {ly} 50")
        commands.append(f"d 1 {rx} {ry} 50")
        commands.append("c")
        commands.append(f"w {wait_per_step}")

        # Mover dedos em direção ao centro
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

        # Touch up
        commands.append("u 0")
        commands.append("u 1")
        commands.append("c")

        script = "\n".join(commands)

        # Salvar e executar script
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "zoom_script.txt")
        with open(script_path, "w") as f:
            f.write(script)

        env = os.environ.copy()
        env["MSYS_NO_PATHCONV"] = "1"
        subprocess.run(
            [ADB_PATH, "-s", self.serial, "push", script_path, "/data/local/tmp/zoom.script"],
            env=env
        )
        subprocess.run(
            [ADB_PATH, "-s", self.serial, "shell", "/data/local/tmp/minitouch", "-f", "/data/local/tmp/zoom.script"],
            env=env
        )
        print(f"[MINITOUCH] Zoom out executed")

    def zoom_in(self, steps=10, duration_ms=300):
        """
        Faz zoom in (pinch out) usando minitouch.
        Os dedos começam no centro e vão para as bordas.
        """
        screen_w, screen_h = self._get_screen_size()
        max_x, max_y = self._get_touch_info()

        center_x = screen_w // 2
        center_y = screen_h // 2

        end_offset = min(screen_w, screen_h) // 3

        def to_touch(sx, sy):
            tx = int((sx / screen_w) * max_x)
            ty = int((sy / screen_h) * max_y)
            return tx, ty

        wait_per_step = duration_ms // steps
        commands = ["r"]

        # Começar no centro (ou próximo)
        lx, ly = to_touch(center_x - 10, center_y)
        rx, ry = to_touch(center_x + 10, center_y)
        commands.append(f"d 0 {lx} {ly} 50")
        commands.append(f"d 1 {rx} {ry} 50")
        commands.append("c")
        commands.append(f"w {wait_per_step}")

        # Mover dedos para fora
        for i in range(1, steps + 1):
            progress = i / steps
            curr_left_x = center_x - int(end_offset * progress)
            curr_right_x = center_x + int(end_offset * progress)

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

        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "zoom_script.txt")
        with open(script_path, "w") as f:
            f.write(script)

        env = os.environ.copy()
        env["MSYS_NO_PATHCONV"] = "1"
        subprocess.run(
            [ADB_PATH, "-s", self.serial, "push", script_path, "/data/local/tmp/zoom.script"],
            env=env
        )
        subprocess.run(
            [ADB_PATH, "-s", self.serial, "shell", "/data/local/tmp/minitouch", "-f", "/data/local/tmp/zoom.script"],
            env=env
        )
        print(f"[MINITOUCH] Zoom in executed")

