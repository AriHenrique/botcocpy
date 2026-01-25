"""
Funcoes relacionadas a vila.
"""

import time


def check_village_loaded(device, retries: int = 5) -> bool:
    """
    Verifica se a vila carregou procurando elementos do menu.

    Args:
        device: Instancia de Device
        retries: Numero de tentativas

    Returns:
        True se vila carregou, False caso contrario
    """
    # Tenta encontrar o botao do exercito (indica que vila carregou)
    for _ in range(retries):
        pos = device.find_template("menu/bt_army.png", threshold=0.7)
        if pos:
            return True
        time.sleep(2)

    # Tenta encontrar botao de ataque como alternativa
    pos = device.find_template("menu/bt_atk.png", threshold=0.7)
    return pos is not None
