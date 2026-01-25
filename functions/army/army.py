"""
Funcoes de gerenciamento do exercito.
"""

import json
import time
from typing import Dict, List

from bot.device import Device
from bot.settings import Settings
from functions.config import go_home


def load_army_config() -> Dict:
    """Carrega configuracao do exercito."""
    config_path = Settings.get_config_path("army.json")
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"troops": [], "spells": []}


def save_army_config(config: Dict) -> bool:
    """Salva configuracao do exercito."""
    config_path = Settings.get_config_path("army.json")
    config_path.parent.mkdir(exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    return True


def list_available_troops() -> List[str]:
    """Lista tropas disponiveis na pasta templates/troops."""
    troops_dir = Settings.get_template_path("troops")
    troops = []
    if troops_dir.exists():
        for f in troops_dir.glob("*.png"):
            troops.append(f.stem)
    return sorted(troops)


def open_army_menu(device: Device):
    """Abre menu do exercito."""
    if not device.image_exists("menu/army_open_true.png", threshold=0.85):
        go_home(device)
        device.tap_image("menu/bt_army.png", threshold=0.85)
    time.sleep(0.5)


def delete_army(device, delete_castle: bool = True):
    """
    Deleta exercito atual.

    Args:
        device: Instancia de Device
        delete_castle: Se True, deleta tropas do castelo tambem
    """
    open_army_menu(device)
    time.sleep(0.5)

    if delete_castle:
        if device.tap_image("delete_army/delete_castle.png", retries=1):
            time.sleep(0.3)
            device.tap_image("menu/bt_ok.png", retries=1)

    if device.tap_image("delete_army/delete_machine.png", retries=1):
        time.sleep(0.3)
        device.tap_image("menu/bt_ok.png", retries=1)

    if device.tap_image("delete_army/delete_spell.png", retries=1):
        time.sleep(0.3)
        device.tap_image("menu/bt_ok.png", retries=1)

    if device.tap_image("delete_army/delete_troop.png", retries=1):
        time.sleep(0.3)
        device.tap_image("menu/bt_ok.png", retries=1)


def create_army(device):
    """
    Cria exercito baseado na configuracao.

    Args:
        device: Instancia de Device
        open_menu: Se True, abre menu do exercito primeiro
    """
    config = load_army_config()
    troops = config.get("troops", [])

    if not troops:
        return False

    open_army_menu(device)

    device.tap_image("menu/open_troops_create.png", threshold=0.8)
    time.sleep(1)

    scroll_pos = (750, 617)

    for troop in troops:
        name = troop.get("name")
        quantity = troop.get("quantity", 1)

        if not name:
            continue

        template = f"troops/{name}.png"

        for _ in range(quantity):
            found = device.find_and_tap_with_scroll(
                template=template,
                scroll_pixels=150,
                scroll_pos=scroll_pos,
                max_scrolls=5,
                threshold=0.75,
                sleep=2
            )
            if not found:
                break
            time.sleep(0.1)

    return True


def train_army(device):
    """Treina exercito: deleta atual e cria novo."""
    delete_army(device, delete_castle=False)
    time.sleep(1)
    create_army(device)
    device.tap_image("menu/bt_close.png", threshold=0.8)


