import time

from compat.android import AndroidDevice
from functions.base import open_chat, close_chat, open_army
from compat.logger import get_donate_logger

logger = get_donate_logger(__name__)


def donate_castle(game_device: AndroidDevice):
    logger.info("Starting castle donation...")
    open_chat(game_device)
    game_device.tap_image("donate/donate_castle.png", threshold=0.85)

    def donate_loop():
        time.sleep(2)
        if game_device.tap_image("donate/select_super_troop_donate.png", threshold=0.85):
            logger.debug("Donated super troop")
            return True
        if game_device.tap_image("donate/select_spell_donate.png", threshold=0.85):
            logger.debug("Donated spell")
            return True
        if game_device.tap_image("donate/select_troop_donate.png", threshold=0.85):
            logger.debug("Donated troop")
            return True
        return False

    donation_count = 0
    while donate_loop():
        donation_count += 1
        time.sleep(0.5)
    
    logger.info(f"Donation complete. Total donations: {donation_count}")


    # game_device.tap_image("menu/bt_ok.png", threshold=0.85)
    # game_device.tap_image("delete_army/delete_spells.png", threshold=0.85)
    # game_device.tap_image("menu/bt_ok.png", threshold=0.85)
    # game_device.tap_image("delete_army/delete_trops.png", threshold=0.85)
    # game_device.tap_image("menu/bt_ok.png", threshold=0.85)


def request_castle(game_device: AndroidDevice):
    logger.info("Requesting from castle...")
    open_army(game_device)
    game_device.tap_image("donate/request_castle.png", threshold=0.85)
    time.sleep(2)
    game_device.tap_image("donate/send_troops.png", threshold=0.85)
    time.sleep(1)
    logger.info("Request sent successfully")