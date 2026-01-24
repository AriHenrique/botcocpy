import os
import re
import subprocess
import sys
import time
from compat.logger import get_bs_logger, get_adb_logger

# Helper to hide CMD windows on Windows
if sys.platform == 'win32':
    _subprocess_flags = {'creationflags': subprocess.CREATE_NO_WINDOW}
else:
    _subprocess_flags = {}

# =========================
# CONFIG
# =========================
BLUESTACKS_CONF = r"C:\ProgramData\BlueStacks_nxt\bluestacks.conf"
BLUESTACKS_EXE = r"C:\Program Files\BlueStacks_nxt\HD-Player.exe"

ADB = r"C:\android\platform-tools\adb.exe"
DEVICE = "127.0.0.1:5556"

TARGET_WIDTH = "860"
TARGET_HEIGHT = "732"
TARGET_DPI = "160"
TARGET_GL_HEIGHT = "732"
SHOW_SIDEBAR = "0"

# =========================
# UTILS
# =========================

logger = get_bs_logger(__name__)
adb_logger = get_adb_logger(__name__)

def run(cmd, silent=False):
    if not silent:
        logger.debug(f"Running command: {' '.join(cmd)}")
    return subprocess.run(cmd, capture_output=True, text=True, **_subprocess_flags)


# =========================
# BLUESTACKS CONTROL
# =========================

def kill_bluestacks():
    logger.info("Killing BlueStacks...")
    for proc in ["HD-Player.exe", "HD-Service.exe", "HD-Frontend.exe"]:
        subprocess.run(
            ["taskkill", "/F", "/IM", proc],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            **_subprocess_flags
        )


def detect_instance(conf_text):
    """
    Finds instance name from:
    bst.instance.<INSTANCE>.adb_port="5556"
    """
    match = re.search(r'bst\.instance\.([^.]+)\.adb_port', conf_text)
    if not match:
        return None
    return match.group(1)


def set_key(lines, instance, key, value):
    pattern = re.compile(
        rf'(bst\.instance\.{re.escape(instance)}\.{re.escape(key)}=)"[^"]*"'
    )

    replaced = False
    new_lines = []
    for line in lines:
        if pattern.search(line):
            new_lines.append(
                f'bst.instance.{instance}.{key}="{value}"\n'
            )
            replaced = True
        else:
            new_lines.append(line)

    # Se não existia, adiciona no final
    if not replaced:
        new_lines.append(
            f'bst.instance.{instance}.{key}="{value}"\n'
        )

    return new_lines


def configure_bluestacks():
    if not os.path.exists(BLUESTACKS_CONF):
        raise RuntimeError("bluestacks.conf not found")

    logger.info("Reading config...")
    with open(BLUESTACKS_CONF, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    text = "".join(lines)
    instance = detect_instance(text)

    if not instance:
        logger.error("Could not detect BlueStacks instance")
        raise RuntimeError("Could not detect BlueStacks instance")

    logger.info(f"Detected instance: {instance}")

    settings = {
        "fb_width": TARGET_WIDTH,
        "fb_height": TARGET_HEIGHT,
        "dpi": TARGET_DPI,
        "gl_win_height": TARGET_GL_HEIGHT,
        "show_sidebar": SHOW_SIDEBAR,
        "display_name": f"BlueStacks5-{instance}",
    }

    for key, value in settings.items():
        lines = set_key(lines, instance, key, value)

    logger.info("Writing config...")
    with open(BLUESTACKS_CONF, "w", encoding="utf-8") as f:
        f.writelines(lines)

    logger.info("Config applied successfully")


def start_bluestacks():
    logger.info("Starting BlueStacks...")
    subprocess.Popen([BLUESTACKS_EXE])
    time.sleep(15)
    logger.info("BlueStacks started")


def adb_validate():
    adb_logger.info("Connecting...")
    run([ADB, "connect", DEVICE], silent=True)

    size = run([ADB, "-s", DEVICE, "shell", "wm", "size"], silent=True)
    dpi = run([ADB, "-s", DEVICE, "shell", "wm", "density"], silent=True)

    adb_logger.info(f"Screen: {size.stdout.strip()}")
    adb_logger.info(f"Density: {dpi.stdout.strip()}")


# =========================
# MAIN
# =========================

def main():
    logger.info("=== BLUESTACKS RESOLUTION CONTROLLER ===")

    kill_bluestacks()
    time.sleep(2)

    configure_bluestacks()
    start_bluestacks()
    adb_validate()

    logger.info("=== DONE ===")
