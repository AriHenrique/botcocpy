from android import AndroidDevice
from functions.base import open_army


def delete_army(game_device: AndroidDevice, castel_delete: bool = True):
    open_army(game_device)
    print("Delete Army function is not implemented yet.")
    if castel_delete:
        game_device.tap_image("delete_army/delete_castle.png", threshold=0.85)
        game_device.tap_image("menu/bt_ok.png", threshold=0.85)
    game_device.tap_image("delete_army/delete_machines.png", threshold=0.85)
    game_device.tap_image("menu/bt_ok.png", threshold=0.85)
    game_device.tap_image("delete_army/delete_spells.png", threshold=0.85)
    game_device.tap_image("menu/bt_ok.png", threshold=0.85)
    game_device.tap_image("delete_army/delete_trops.png", threshold=0.85)
    game_device.tap_image("menu/bt_ok.png", threshold=0.85)

