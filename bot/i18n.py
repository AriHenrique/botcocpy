"""
i18n - Sistema de traducao simplificado.
"""

import json

from bot.settings import Settings


class I18n:
    """Gerenciador de traducoes."""

    _translations = {}
    _current_language = "pt-BR"
    _fallback_language = "en-US"

    @classmethod
    def load(cls):
        """Carrega traducoes dos arquivos JSON."""
        locales_dir = Settings.PROJECT_ROOT / Settings.LOCALES_DIR

        if not locales_dir.exists():
            return

        for lang_file in locales_dir.glob("*.json"):
            lang_code = lang_file.stem
            try:
                with open(lang_file, "r", encoding="utf-8") as f:
                    cls._translations[lang_code] = json.load(f)
            except Exception:
                pass

    @classmethod
    def set_language(cls, lang: str):
        """Define idioma atual."""
        if lang in cls._translations:
            cls._current_language = lang
        else:
            cls._current_language = cls._fallback_language

    @classmethod
    def get_language(cls) -> str:
        """Retorna idioma atual."""
        return cls._current_language

    @classmethod
    def get_available_languages(cls) -> list:
        """Retorna idiomas disponiveis."""
        if not cls._translations:
            cls.load()
        return list(cls._translations.keys())

    @classmethod
    def t(cls, key: str, *args, **kwargs) -> str:
        """
        Traduz uma chave.

        Args:
            key: Chave de traducao (ex: 'gui.buttons.create_army')
            *args, **kwargs: Argumentos para formatacao

        Returns:
            String traduzida ou a chave se nao encontrar
        """
        if not cls._translations:
            cls.load()

        # Tenta idioma atual
        translation = cls._get_nested(cls._translations.get(cls._current_language, {}), key)

        # Fallback
        if translation is None:
            translation = cls._get_nested(cls._translations.get(cls._fallback_language, {}), key)

        if translation is None:
            return key

        if args or kwargs:
            try:
                return translation.format(*args, **kwargs)
            except Exception:
                return translation

        return translation

    @classmethod
    def _get_nested(cls, dictionary: dict, key: str):
        """Obtem valor aninhado usando notacao de ponto."""
        keys = key.split(".")
        value = dictionary

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return None
            else:
                return None

        return value


# Funcoes de conveniencia
def t(key: str, *args, **kwargs) -> str:
    """Traduz uma chave."""
    return I18n.t(key, *args, **kwargs)


def set_language(lang: str):
    """Define idioma."""
    I18n.set_language(lang)


def get_language() -> str:
    """Retorna idioma atual."""
    return I18n.get_language()


def get_available_languages() -> list:
    """Retorna idiomas disponiveis."""
    return I18n.get_available_languages()
