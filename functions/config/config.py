"""
Funcoes de configuracao do emulador e jogo.
"""

import time

from bot.settings import Settings
from functions.vila import check_village_loaded


def init_game(device, move_right: int = 100, move_down: int = 50):
    """
    Inicializa o jogo: abre app, zoom out, centraliza.

    Args:
        device: Instancia de Device
        move_right: Pixels para mover para direita
        move_down: Pixels para mover para baixo
    """
    device.open_app(Settings.GAME_PACKAGE)
    for _attempt in range(10):
        if device.image_exists("menu/bt_army.png", threshold=0.85):
            break
        time.sleep(5)

    # Zoom out
    device.zoom_out(steps=15, duration_ms=500)
    time.sleep(0.5)
    device.zoom_out(steps=15, duration_ms=500)
    time.sleep(0.3)

    # Centraliza (so move para direita)
    device.center_view(move_right=move_right, move_down=move_down)

    return True


def setup_emulator(callback=None):
    """
    Configura emulador completo:
    1. Mata BlueStacks
    2. Configura resolucao
    3. Inicia BlueStacks
    4. Conecta ADB
    5. Define resolucao via ADB
    6. Abre jogo
    7. Verifica se vila carregou

    Args:
        callback: Funcao para reportar progresso (opcional)

    Returns:
        (success, device): Tupla com resultado e instancia do Device
    """
    from bot.bluestacks import BlueStacks
    from bot.device import Device

    device = None

    def log(msg):
        if callback:
            callback(msg)

    try:
        # 1. Mata BlueStacks
        log("[SETUP] Encerrando BlueStacks...")
        BlueStacks.kill()
        time.sleep(2)

        # 2. Configura resolucao
        log("[SETUP] Configurando resolucao 860x732...")
        BlueStacks.configure()

        # 3. Inicia BlueStacks
        log("[SETUP] Iniciando BlueStacks (aguarde ~15s)...")
        BlueStacks.start()

        # 4. Valida e conecta ADB
        log("[SETUP] Conectando ADB...")
        BlueStacks.validate_adb()
        time.sleep(2)

        # 5. Reconecta device
        log("[SETUP] Reconectando dispositivo...")
        device = Device()

        # 6. Define resolucao via ADB
        log("[SETUP] Aplicando resolucao 860x732 via ADB...")
        device.set_screen_size(860, 732)
        device.set_density(160)
        time.sleep(1)

        # 7. Abre o jogo

        log("[SETUP] Abrindo Clash of Clans...")
        init_game(device)

        # 9. Verifica se vila carregou
        log("[SETUP] Verificando se vila carregou...")
        if check_village_loaded(device):
            config_language(device)
            config_atk_layout(device)
            log("[SETUP] Vila detectada! Configuracao concluida com sucesso.")
            return (True, device)
        else:
            log("[SETUP] AVISO: Vila nao detectada. Verifique manualmente.")
            return (False, device)

    except Exception as e:
        log(f"[SETUP] ERRO: {e}")
        return (False, device)


def go_home(device, max_presses: int = 10, delay: float = 1):
    """
    Retorna para a pagina home do jogo pressionando ESC consecutivamente.
    
    Args:
        device: Instancia de Device
        max_presses: Numero maximo de vezes para pressionar ESC
        delay: Delay entre cada pressionamento (em segundos)
    
    Returns:
        True se executou com sucesso
    """
    # Codigo da tecla BACK/ESC no Android: 4
    KEYCODE_BACK = 4
    if device.image_exists("menu/bt_army.png", threshold=0.85):
        return True
    for i in range(max_presses):
        device.keyevent(KEYCODE_BACK)
        time.sleep(0.5)
        if device.image_exists("menu/bt_army.png", threshold=0.85):
            return True
        if device.image_exists("menu/bt_cancel.png", threshold=0.85):
            device.tap_image("menu/bt_cancel.png", threshold=0.85)
            return True
        time.sleep(delay)
    return False


def config_atk_layout(device):
    """
    Configura layout de ataque para padrao.

    Args:
        device: Instancia de Device
    """
    go_home(device)
    device.tap_image("menu/bt_config.png", threshold=0.85)
    time.sleep(1)
    repet = 3
    device.tap_image("menu/more_settings.png", threshold=0.85)
    for _ in range(repet):
        if device.image_exists("menu/ajust_bar_size.png", threshold=0.85):
            device.tap_image("menu/ajust_bar_size.png", threshold=0.85)
            time.sleep(1)
            device.drag_from_image(
                template="menu/bt_bar_size.png",
                target_x=115,
                target_y=472,
                threshold=0.85,
                hold_ms=300
            )
            time.sleep(1)
            # device.tap_image("menu/bt_bar_size_no_two_rows.png", threshold=0.85)
            time.sleep(1)
            go_home(device)
            return True
        device.scroll_vertical(50)
        time.sleep(1)
    return False


def config_language(device):
    """
    Configura idioma do jogo para Ingles.

    Args:
        device: Instancia de Device
    """

    go_home(device)
    device.tap_image("menu/bt_config.png", threshold=0.85)
    time.sleep(1)
    if device.image_exists("menu/english_ok.png", threshold=0.85):
        go_home(device)
        return True
    device.tap_image("menu/bt_language.png", threshold=0.85)
    time.sleep(1)
    if not device.image_exists("menu/bt_english.png", threshold=0.85):
        repet = 3
        for _ in range(repet):
            device.drag_from_image(
                template="menu/drag_language.png",
                target_x=731,
                target_y=700,
                threshold=0.85,
                hold_ms=300
            )
            time.sleep(0.5)
            if device.image_exists("menu/bt_english.png", threshold=0.85):
                break
    device.tap_image("menu/bt_english.png", threshold=0.85)
    time.sleep(1)
    device.tap_image("menu/bt_ok_all.png", threshold=0.85)
    go_home(device)
    return True