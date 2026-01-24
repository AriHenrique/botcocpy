import time

from compat.android import AndroidDevice
from functions.base import open_army
from compat.logger import get_army_logger

logger = get_army_logger(__name__)


def delete_army(game_device: AndroidDevice, castel_delete: bool = True, open_menu: bool = True):
    logger.info("Deleting army...")
    if open_menu:
        open_army(game_device)
    time.sleep(0.5)  # Wait for menu to open
    
    if castel_delete:
        # game_device.tap_image("delete_army/empty_castle.png")
        # game_device.tap_image("menu/bt_ok.png")
        if game_device.tap_image("delete_army/delete_castle.png", retries=1):
            time.sleep(0.3)
            game_device.tap_image("menu/bt_ok.png", retries=1)
    
    # game_device.tap_image("delete_army/empty_machine.png")
    # game_device.tap_image("menu/bt_ok.png")
    if game_device.tap_image("delete_army/delete_machine.png", retries=1):
        time.sleep(0.3)
        game_device.tap_image("menu/bt_ok.png", retries=1)
    
    # game_device.tap_image("delete_army/empty_spell.png")
    # game_device.tap_image("menu/bt_ok.png")
    if game_device.tap_image("delete_army/delete_spell.png", retries=1):
        time.sleep(0.3)
        game_device.tap_image("menu/bt_ok.png", retries=1)
    
    # game_device.tap_image("delete_army/empty_troop.png")
    # game_device.tap_image("menu/bt_ok.png")
    if game_device.tap_image("delete_army/delete_troop.png", retries=1):
        time.sleep(0.3)
        game_device.tap_image("menu/bt_ok.png", retries=1)

