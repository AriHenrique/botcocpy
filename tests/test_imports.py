"""Testes basicos de import."""


def test_import_settings():
    from bot.settings import Settings

    assert Settings.GAME_PACKAGE == "com.supercell.clashofclans"


def test_import_actions():
    from bot.actions import BotActions

    assert BotActions is not None


def test_import_bluestacks():
    from bot.bluestacks import BlueStacks

    assert BlueStacks is not None


def test_import_i18n():
    from bot.i18n import t

    assert callable(t)
