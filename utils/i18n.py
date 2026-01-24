"""
Internationalization (i18n) system for Bot COC.
Manages translations from JSON files for multiple languages.
"""
import json
import os
from pathlib import Path


class I18n:
    """
    Internationalization manager.
    Loads translations from JSON files and provides translation methods.
    """
    
    _instance = None
    _translations = {}
    _current_language = "pt-BR"
    _fallback_language = "en-US"
    _locales_dir = "locales"
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super(I18n, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._load_translations()
            self._initialized = True
    
    def _load_translations(self):
        """Load translations from JSON files"""
        locales_path = Path(self._locales_dir)
        
        if not locales_path.exists():
            # Create default locales directory
            locales_path.mkdir(exist_ok=True)
            self._create_default_translations()
            return
        
        # Load all available language files
        for lang_file in locales_path.glob("*.json"):
            lang_code = lang_file.stem
            try:
                with open(lang_file, "r", encoding="utf-8") as f:
                    self._translations[lang_code] = json.load(f)
            except Exception as e:
                print(f"Error loading translation file {lang_file}: {e}")
    
    def _create_default_translations(self):
        """Create default translation files if they don't exist"""
        default_pt_br = {
            "gui": {
                "title": "Bot COC - Painel de Controle",
                "tabs": {
                    "control": "Controle",
                    "settings": "Configurações",
                    "army": "Exército",
                    "log": "Log"
                },
                "buttons": {
                    "kill_bluestacks": "Encerrar BlueStacks",
                    "configure_bluestacks": "Configurar BlueStacks",
                    "start_bluestacks": "Iniciar BlueStacks",
                    "validate_adb": "Validar ADB",
                    "connect_device": "Conectar Dispositivo",
                    "screenshot": "Capturar Tela",
                    "init_game": "Inicializar Jogo",
                    "center_view": "Centralizar Visualização",
                    "delete_army": "Deletar Exército",
                    "create_army": "Criar Exército",
                    "train_army": "Treinar Exército",
                    "donate_castle": "Doar para Castelo",
                    "request_castle": "Solicitar do Castelo",
                    "clear_log": "Limpar Log",
                    "save_settings": "Salvar Configurações",
                    "refresh_list": "Atualizar Lista",
                    "add_selected": "Adicionar Selecionado",
                    "remove_selected": "Remover Selecionado",
                    "update_quantity": "Atualizar Quantidade",
                    "save_army_config": "Salvar Config. Exército",
                    "load_army_config": "Carregar Config. Exército"
                },
                "labels": {
                    "blue_stacks_control": "Controle BlueStacks",
                    "device_connection": "Conexão do Dispositivo",
                    "game_actions": "Ações do Jogo",
                    "bot_functions": "Funções do Bot",
                    "adb_settings": "Configurações ADB",
                    "game_settings": "Configurações do Jogo",
                    "view_settings": "Configurações de Visualização",
                    "available_troops": "Tropas Disponíveis",
                    "army_configuration": "Configuração do Exército",
                    "adb_path": "Caminho ADB:",
                    "host": "Host:",
                    "port": "Porta:",
                    "game_package": "Pacote do Jogo:",
                    "move_right": "Mover Direita:",
                    "move_down": "Mover Baixo:",
                    "quantity": "Quantidade:",
                    "troop": "Tropa",
                    "quantity_col": "Quantidade"
                },
                "messages": {
                    "warning": "Aviso",
                    "error": "Erro",
                    "success": "Sucesso",
                    "another_operation_running": "Outra operação já está em execução!",
                    "please_connect_device": "Por favor, conecte o dispositivo primeiro!",
                    "please_select_troop": "Por favor, selecione uma tropa!",
                    "please_select_troop_to_remove": "Por favor, selecione uma tropa para remover!",
                    "please_select_troop_to_update": "Por favor, selecione uma tropa para atualizar!",
                    "invalid_quantity": "Quantidade inválida!",
                    "troop_already_in_army": "{} já está no exército!",
                    "army_config_saved": "Configuração do exército salva!",
                    "settings_saved": "Configurações salvas (apenas GUI)"
                }
            },
            "logs": {
                "bs": {
                    "killing": "Encerrando BlueStacks...",
                    "killed": "BlueStacks encerrado",
                    "configuring": "Configurando BlueStacks...",
                    "configured": "BlueStacks configurado",
                    "starting": "Iniciando BlueStacks...",
                    "started": "BlueStacks iniciado"
                },
                "adb": {
                    "validating": "Validando conexão...",
                    "validation_complete": "Validação completa"
                },
                "device": {
                    "connecting": "Conectando...",
                    "connected": "Conectado a {}:{}",
                    "taking_screenshot": "Capturando tela...",
                    "screenshot_saved": "Captura de tela salva em screen.png"
                },
                "game": {
                    "initializing": "Inicializando jogo...",
                    "waiting_for_load": "Aguardando jogo carregar...",
                    "zooming_out": "Fazendo zoom out...",
                    "initialized": "Jogo inicializado",
                    "centering_view": "Centralizando visualização (right={}, down={})...",
                    "view_centered": "Visualização centralizada"
                },
                "bot": {
                    "deleting_army": "Deletando exército...",
                    "army_deleted": "Exército deletado",
                    "creating_army": "Criando exército...",
                    "army_created": "Exército criado",
                    "training_army": "Treinando exército...",
                    "army_trained": "Exército treinado",
                    "donating_castle": "Doando para castelo...",
                    "donation_complete": "Doação completa",
                    "requesting_castle": "Solicitando do castelo...",
                    "request_complete": "Solicitação completa"
                },
                "army": {
                    "loaded_troops": "Carregadas {} tropas disponíveis",
                    "added_troop": "Adicionado {}x {}",
                    "removed_troop": "Removido {}",
                    "updated_quantity": "Atualizado {} quantidade para {}",
                    "saved_config": "Salva configuração do exército com {} tipos de tropas",
                    "loaded_config": "Carregada configuração do exército com {} tipos de tropas"
                }
            }
        }
        
        default_en_us = {
            "gui": {
                "title": "Bot COC - Control Panel",
                "tabs": {
                    "control": "Control",
                    "settings": "Settings",
                    "army": "Army",
                    "log": "Log"
                },
                "buttons": {
                    "kill_bluestacks": "Kill BlueStacks",
                    "configure_bluestacks": "Configure BlueStacks",
                    "start_bluestacks": "Start BlueStacks",
                    "validate_adb": "Validate ADB",
                    "connect_device": "Connect Device",
                    "screenshot": "Screenshot",
                    "init_game": "Init Game",
                    "center_view": "Center View",
                    "delete_army": "Delete Army",
                    "create_army": "Create Army",
                    "train_army": "Train Army",
                    "donate_castle": "Donate Castle",
                    "request_castle": "Request Castle",
                    "clear_log": "Clear Log",
                    "save_settings": "Save Settings",
                    "refresh_list": "Refresh List",
                    "add_selected": "Add Selected",
                    "remove_selected": "Remove Selected",
                    "update_quantity": "Update Quantity",
                    "save_army_config": "Save Army Config",
                    "load_army_config": "Load Army Config"
                },
                "labels": {
                    "blue_stacks_control": "BlueStacks Control",
                    "device_connection": "Device Connection",
                    "game_actions": "Game Actions",
                    "bot_functions": "Bot Functions",
                    "adb_settings": "ADB Settings",
                    "game_settings": "Game Settings",
                    "view_settings": "View Settings",
                    "available_troops": "Available Troops",
                    "army_configuration": "Army Configuration",
                    "adb_path": "ADB Path:",
                    "host": "Host:",
                    "port": "Port:",
                    "game_package": "Game Package:",
                    "move_right": "Move Right:",
                    "move_down": "Move Down:",
                    "quantity": "Quantity:",
                    "troop": "Troop",
                    "quantity_col": "Quantity"
                },
                "messages": {
                    "warning": "Warning",
                    "error": "Error",
                    "success": "Success",
                    "another_operation_running": "Another operation is already running!",
                    "please_connect_device": "Please connect device first!",
                    "please_select_troop": "Please select a troop!",
                    "please_select_troop_to_remove": "Please select a troop to remove!",
                    "please_select_troop_to_update": "Please select a troop to update!",
                    "invalid_quantity": "Invalid quantity!",
                    "troop_already_in_army": "{} is already in army!",
                    "army_config_saved": "Army configuration saved!",
                    "settings_saved": "Settings saved (GUI only)"
                }
            },
            "logs": {
                "bs": {
                    "killing": "Killing BlueStacks...",
                    "killed": "BlueStacks killed",
                    "configuring": "Configuring BlueStacks...",
                    "configured": "BlueStacks configured",
                    "starting": "Starting BlueStacks...",
                    "started": "BlueStacks started"
                },
                "adb": {
                    "validating": "Validating connection...",
                    "validation_complete": "Validation complete"
                },
                "device": {
                    "connecting": "Connecting...",
                    "connected": "Connected to {}:{}",
                    "taking_screenshot": "Taking screenshot...",
                    "screenshot_saved": "Screenshot saved to screen.png"
                },
                "game": {
                    "initializing": "Initializing game...",
                    "waiting_for_load": "Waiting for game to load...",
                    "zooming_out": "Zooming out...",
                    "initialized": "Game initialized",
                    "centering_view": "Centering view (right={}, down={})...",
                    "view_centered": "View centered"
                },
                "bot": {
                    "deleting_army": "Deleting army...",
                    "army_deleted": "Army deleted",
                    "creating_army": "Creating army...",
                    "army_created": "Army created",
                    "training_army": "Training army...",
                    "army_trained": "Army trained",
                    "donating_castle": "Donating to castle...",
                    "donation_complete": "Donation complete",
                    "requesting_castle": "Requesting from castle...",
                    "request_complete": "Request complete"
                },
                "army": {
                    "loaded_troops": "Loaded {} available troops",
                    "added_troop": "Added {}x {}",
                    "removed_troop": "Removed {}",
                    "updated_quantity": "Updated {} quantity to {}",
                    "saved_config": "Saved army configuration with {} troop types",
                    "loaded_config": "Loaded army configuration with {} troop types"
                }
            }
        }
        
        # Save default translations
        pt_br_path = Path(self._locales_dir) / "pt-BR.json"
        en_us_path = Path(self._locales_dir) / "en-US.json"
        
        if not pt_br_path.exists():
            with open(pt_br_path, "w", encoding="utf-8") as f:
                json.dump(default_pt_br, f, indent=2, ensure_ascii=False)
        
        if not en_us_path.exists():
            with open(en_us_path, "w", encoding="utf-8") as f:
                json.dump(default_en_us, f, indent=2, ensure_ascii=False)
        
        # Load translations
        self._load_translations()
    
    def set_language(self, language_code):
        """
        Set the current language.
        
        Args:
            language_code: Language code (e.g., 'pt-BR', 'en-US')
        """
        if language_code in self._translations:
            self._current_language = language_code
        else:
            print(f"Warning: Language '{language_code}' not found, using fallback '{self._fallback_language}'")
            self._current_language = self._fallback_language
    
    def get_language(self):
        """Get the current language code"""
        return self._current_language
    
    def get_available_languages(self):
        """Get list of available language codes"""
        return list(self._translations.keys())
    
    def t(self, key, *args, **kwargs):
        """
        Translate a key.
        
        Args:
            key: Translation key (e.g., 'gui.buttons.kill_bluestacks')
            *args: Positional arguments for string formatting
            **kwargs: Keyword arguments for string formatting
            
        Returns:
            Translated string or the key if translation not found
        """
        # Try current language
        translation = self._get_nested_value(
            self._translations.get(self._current_language, {}),
            key
        )
        
        # Fallback to fallback language
        if translation is None:
            translation = self._get_nested_value(
                self._translations.get(self._fallback_language, {}),
                key
            )
        
        # If still not found, return the key
        if translation is None:
            return key
        
        # Format string if args or kwargs provided
        if args or kwargs:
            try:
                return translation.format(*args, **kwargs)
            except Exception:
                return translation
        
        return translation
    
    def _get_nested_value(self, dictionary, key):
        """
        Get nested value from dictionary using dot notation.
        
        Args:
            dictionary: Dictionary to search
            key: Key in dot notation (e.g., 'gui.buttons.kill_bluestacks')
            
        Returns:
            Value or None if not found
        """
        keys = key.split('.')
        value = dictionary
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return None
            else:
                return None
        
        return value


# Global instance
_i18n = I18n()


# Convenience functions
def t(key, *args, **kwargs):
    """Translate a key (convenience function)"""
    return _i18n.t(key, *args, **kwargs)


def set_language(language_code):
    """Set the current language"""
    _i18n.set_language(language_code)


def get_language():
    """Get the current language code"""
    return _i18n.get_language()


def get_available_languages():
    """Get list of available language codes"""
    return _i18n.get_available_languages()
