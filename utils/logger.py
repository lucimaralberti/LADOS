import logging
import sys
from pathlib import Path
from datetime import datetime

_LOGGERS = {}

def setup_logger(name: str, level=logging.INFO, log_file: str = None) -> logging.Logger:
    """Configura e retorna um logger padronizado"""
    if name in _LOGGERS:
        return _LOGGERS[name]
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False
    
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (opcional)
    if log_file:
        from config import settings
        file_handler = logging.FileHandler(settings.logs_dir / log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    _LOGGERS[name] = logger
    return logger

def get_logger(name: str) -> logging.Logger:
    """Obtém um logger existente ou cria um novo"""
    if name in _LOGGERS:
        return _LOGGERS[name]
    return setup_logger(name)
