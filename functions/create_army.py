import json
import os
import time
from compat.logger import get_army_logger

ARMY_CONFIG = os.path.join(os.path.dirname(__file__), "..", "config", "army.json")
logger = get_army_logger(__name__)


def load_army_config():
    """Carrega configuração do exército do arquivo JSON"""
    with open(ARMY_CONFIG, "r", encoding="utf-8") as f:
        return json.load(f)


def list_available_troops():
    """Lista todas as tropas disponíveis na pasta templates/troops"""
    troops_dir = os.path.join(os.path.dirname(__file__), "..", "templates", "troops")
    troops = []
    for f in os.listdir(troops_dir):
        if f.endswith(".png"):
            troops.append(f.replace(".png", ""))
    return sorted(troops)


def create_army(device, open_menu=True):
    """
    Cria o exército baseado na configuração do army.json

    Args:
        device: AndroidDevice instance
        open_menu: Se True, abre o menu do exército antes de criar
    """
    config = load_army_config()
    troops = config.get("troops", [])

    if not troops:
        logger.warning("No troops configured in army.json")
        return

    logger.info(f"Creating army with {len(troops)} troop types...")

    if open_menu:
        # Abre menu do exército
        device.tap_image("menu/bt_army.png", threshold=0.8)
        time.sleep(1)
    device.tap_image("menu/open_troops_create.png", threshold=0.8)
    time.sleep(1)
    # Posição para fazer scroll (baseado nas regiões do templates.json)
    # Área das tropas: Y entre 544-690, centro em ~617
    scroll_pos = (750, 617)  # Lado direito da área das tropas

    for troop in troops:
        name = troop.get("name")
        quantity = troop.get("quantity", 1)

        if not name:
            continue

        template = f"troops/{name}.png"

        logger.info(f"Adding {quantity}x {name}")

        for i in range(quantity):
            # Tenta encontrar e clicar, com scroll se necessário
            found = device.find_and_tap_with_scroll(
                template=template,
                scroll_pixels=150,
                scroll_pos=scroll_pos,
                max_scrolls=5,
                threshold=0.75
            )

            if not found:
                logger.warning(f"Could not find {name}, skipping...")
                break

            time.sleep(0.1)

    logger.info("Army creation complete")


def train_army(device):
    """
    Treina o exército: abre menu, deleta tropas existentes e cria novo exército
    """
    from functions.delete_army import delete_army

    logger.info("Training new army...")

    # Deleta exército atual
    delete_army(device, castel_delete=False, open_menu=False)
    time.sleep(1)

    # Cria novo exército
    create_army(device, open_menu=False)

    # Fecha menu
    device.tap_image("menu/bt_close.png", threshold=0.8)

    logger.info("Training complete")
