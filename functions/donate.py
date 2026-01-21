import time

from android import AndroidDevice
from functions.base import open_chat, close_chat, open_army


def donate_castle(game_device: AndroidDevice):
    open_chat(game_device)
    game_device.tap_image("donate/donate_castle.png", threshold=0.85)

    def donate_loop():
        time.sleep(2)
        if game_device.tap_image("donate/select_super_troop_donate.png", threshold=0.85):
            return True
        if game_device.tap_image("donate/select_spell_donate.png", threshold=0.85):
            return True
        if game_device.tap_image("donate/select_troop_donate.png", threshold=0.85):
            return True
        return False

    while donate_loop():
        time.sleep(0.5)


    # game_device.tap_image("menu/bt_ok.png", threshold=0.85)
    # game_device.tap_image("delete_army/delete_spells.png", threshold=0.85)
    # game_device.tap_image("menu/bt_ok.png", threshold=0.85)
    # game_device.tap_image("delete_army/delete_trops.png", threshold=0.85)
    # game_device.tap_image("menu/bt_ok.png", threshold=0.85)


def request_castle(game_device: AndroidDevice):
    open_army(game_device)
    game_device.tap_image("donate/request_castle.png", threshold=0.85)
    time.sleep(2)
    game_device.tap_image("donate/send_troops.png", threshold=0.85)
    time.sleep(1)