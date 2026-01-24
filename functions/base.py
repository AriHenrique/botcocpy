from compat.android import AndroidDevice


def open_army(game_device: AndroidDevice):
    game_device.tap_image("menu/bt_army.png", threshold=0.85)


def open_chat(game_device: AndroidDevice):
    try:
        game_device.tap_image("menu/bt_chat.png", threshold=0.85)
    except Exception:
        close_chat(game_device)
        open_chat(game_device)


def close_chat(game_device: AndroidDevice):
    game_device.tap_image("menu/bt_close_chat.png", threshold=0.85)


