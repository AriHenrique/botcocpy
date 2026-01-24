"""
Robust logging system for Bot COC.
Provides standardized logging with file rotation and multiple log levels.
"""
import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path


class BotLogger:
    """
    Centralized logging system for the bot.
    Provides standardized logging with file rotation and console output.
    """
    
    _initialized = False
    _loggers = {}
    
    # Log format padrão
    LOG_FORMAT = "[%(asctime)s] [%(levelname)-8s] [%(module)s.%(name)s] %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    # Diretório de logs
    LOG_DIR = "logs"
    
    @classmethod
    def initialize(cls, log_level=logging.INFO, log_to_file=True, log_to_console=True):
        """
        Initialize the logging system.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_file: Whether to save logs to file
            log_to_console: Whether to output logs to console
        """
        if cls._initialized:
            return
            
        # Cria diretório de logs
        if log_to_file:
            os.makedirs(cls.LOG_DIR, exist_ok=True)
        
        # Configura root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # Remove handlers existentes
        root_logger.handlers.clear()
        
        # Formatter padrão
        formatter = logging.Formatter(cls.LOG_FORMAT, cls.DATE_FORMAT)
        
        # Console handler
        if log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
        
        # File handler com rotação
        if log_to_file:
            log_file = os.path.join(cls.LOG_DIR, "bot_coc.log")
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        cls._initialized = True
        
    @classmethod
    def get_logger(cls, name, module_prefix=None):
        """
        Get a logger instance for a specific module.
        
        Args:
            name: Logger name (usually __name__)
            module_prefix: Optional prefix for log messages (e.g., "BOT", "ADB", "BS")
            
        Returns:
            Logger instance with custom formatting
        """
        if not cls._initialized:
            cls.initialize()
        
        # Usa cache de loggers
        cache_key = f"{name}_{module_prefix}"
        if cache_key in cls._loggers:
            return cls._loggers[cache_key]
        
        logger = logging.getLogger(name)
        
        # Adiciona handler customizado se necessário
        if module_prefix:
            # Cria handler customizado com prefixo
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(cls.LOG_FORMAT, cls.DATE_FORMAT))
            
            # Adiciona filtro para prefixo
            class PrefixFilter(logging.Filter):
                def __init__(self, prefix):
                    super().__init__()
                    self.prefix = prefix
                    
                def filter(self, record):
                    record.msg = f"[{self.prefix}] {record.msg}"
                    return True
            
            handler.addFilter(PrefixFilter(module_prefix))
            logger.addHandler(handler)
        
        cls._loggers[cache_key] = logger
        return logger


# Funções de conveniência para diferentes módulos
def get_bot_logger(name=__name__):
    """Get logger for bot operations"""
    return BotLogger.get_logger(name, "BOT")


def get_adb_logger(name=__name__):
    """Get logger for ADB operations"""
    return BotLogger.get_logger(name, "ADB")


def get_bs_logger(name=__name__):
    """Get logger for BlueStacks operations"""
    return BotLogger.get_logger(name, "BS")


def get_vision_logger(name=__name__):
    """Get logger for vision/template matching operations"""
    return BotLogger.get_logger(name, "VISION")


def get_army_logger(name=__name__):
    """Get logger for army operations"""
    return BotLogger.get_logger(name, "ARMY")


def get_device_logger(name=__name__):
    """Get logger for device operations"""
    return BotLogger.get_logger(name, "DEVICE")


def get_game_logger(name=__name__):
    """Get logger for game operations"""
    return BotLogger.get_logger(name, "GAME")


def get_donate_logger(name=__name__):
    """Get logger for donation operations"""
    return BotLogger.get_logger(name, "DONATE")


# Inicializa o sistema de logs ao importar
BotLogger.initialize()


# Logger genérico para uso geral
def get_logger(name=__name__, prefix=None):
    """Get a generic logger"""
    return BotLogger.get_logger(name, prefix)
