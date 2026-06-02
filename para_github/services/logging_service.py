"""
Sistema de logging - LADOS 2.0
"""

import logging
import os
from datetime import datetime

def setup_logger(nome: str = "lados", nivel: str = "INFO") -> logging.Logger:
    """Configura e retorna um logger"""
    
    # Criar diretório de logs se não existir
    os.makedirs("logs", exist_ok=True)
    
    # Configurar logger
    logger = logging.getLogger(nome)
    
    # Evitar duplicação de handlers
    if logger.handlers:
        return logger
    
    # Definir nível
    niveis = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR
    }
    logger.setLevel(niveis.get(nivel, logging.INFO))
    
    # Formato do log
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para arquivo
    arquivo_log = f"logs/lados_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(arquivo_log, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler para console (opcional)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()
