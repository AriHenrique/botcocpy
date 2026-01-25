"""
Funcoes de doacao e solicitacao de tropas.
"""

import time

from functions.army import open_army_menu
from functions.config import go_home


def open_chat(device):
    """Abre chat."""
    if device.image_exists("menu/bt_chat.png", threshold=0.85):
        device.tap_image("menu/bt_chat.png", threshold=0.85)
        return True
    if device.image_exists("menu/bt_close_chat.png", threshold=0.85):
        return True

    if go_home(device):
        if device.image_exists("menu/bt_chat.png", threshold=0.85):
            device.tap_image("menu/bt_chat.png", threshold=0.85)
            return True

    return False


def close_chat(device):
    """Fecha chat."""
    device.tap_image("menu/bt_close_chat.png", threshold=0.85)


def donate_castle(device) -> int:
    """
    Doa tropas para o castelo do cla.

    Returns:
        Quantidade de doacoes realizadas
    """
    open_chat(device)
    device.tap_image("donate/donate_castle.png", threshold=0.85)
    time.sleep(2)

    donation_count = 0
    while True:
        if device.tap_image("donate/select_super_troop_donate.png", threshold=0.85, retries=1):
            donation_count += 1
        elif device.tap_image("donate/select_spell_donate.png", threshold=0.85, retries=1):
            donation_count += 1
        elif device.tap_image("donate/select_troop_donate.png", threshold=0.85, retries=1):
            donation_count += 1
        else:
            break
        time.sleep(0.5)

    return donation_count


def request_castle(device):
    """Solicita tropas do castelo."""
    open_army_menu(device)
    device.tap_image("donate/request_castle.png", threshold=0.85)
    time.sleep(2)
    device.tap_image("donate/send_troops.png", threshold=0.85)
    time.sleep(1)
