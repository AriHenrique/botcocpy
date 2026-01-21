import time
from android import AndroidDevice
from config import GAME_PACKAGE
from functions.bluestacks_control import configure_bluestacks, start_bluestacks, kill_bluestacks, adb_validate
from functions.donate import donate_castle, request_castle
from functions.delete_army import *
from functions.create_army import create_army


# ================= SETUP =================
def setup_bluestacks():
    """Configura e inicia o BlueStacks com a resolução correta"""
    print("[BOT] Setting up BlueStacks...")
    kill_bluestacks()
    time.sleep(2)
    configure_bluestacks()
    start_bluestacks()
    adb_validate()

def init_game(device):
    """Abre o jogo, faz zoom out máximo e centraliza"""
    device.open_app(GAME_PACKAGE)

    print("[BOT] Waiting for game to load...")
    time.sleep(8)

    print("[BOT] Zooming out...")
    device.zoom_out(steps=15, duration_ms=500)
    time.sleep(0.5)
    device.zoom_out(steps=15, duration_ms=500)
    time.sleep(0.3)

    # Centraliza: move tudo para esquerda, depois move X pixels para direita
    device.center_view(move_right=100, move_down=-50)  # Ajuste este valor para centralizar
    print("[BOT] Ready")

# ================= MAIN =================
if __name__ == "__main__":
    try:
        # Descomentar para reiniciar BlueStacks com config correta:
        # setup_bluestacks()

        d = AndroidDevice()
        # init_game(d)
        # d.center_view(move_right=100, move_down=-50)
        # request_castle(d)
        d.find_and_tap_with_scroll(
            template="troops/corredor.png",
            scroll_pixels=150,
            scroll_pos=(500, 580),  # Posição para arrastar
            max_scrolls=5
        )

        # ================= FLOW =================
        # Adicione seu fluxo aqui
        # delete_army(d, castel_delete=True)
        # d.tap_image("menu/bt_atk.png", threshold=0.85)
        # donate_castle(d)

        print("[BOT] Flow completed successfully")

    except Exception as e:
        print("[BOT] ERROR:", e)