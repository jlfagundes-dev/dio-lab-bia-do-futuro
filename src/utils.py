# === Utilidades e Configuração de Logging ===
# Funções auxiliares e setup de logging para toda a aplicação

import logging
import sys
from pathlib import Path


def configurar_logging(nome_app: str = "ABI") -> logging.Logger:
    """
    Configura logging centralizado para toda a aplicação.
    
    Args:
        nome_app: Nome da aplicação para identificar nos logs
        
    Returns:
        Logger: Logger configurado
    """
    
    # Criar diretório de logs se não existir
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configurar logger
    logger = logging.getLogger(nome_app)
    logger.setLevel(logging.DEBUG)
    
    # Handler para arquivo
    arquivo_handler = logging.FileHandler(
        log_dir / f"{nome_app}.log",
        encoding='utf-8'
    )
    arquivo_handler.setLevel(logging.DEBUG)
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Formato dos logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    arquivo_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Adicionar handlers
    logger.addHandler(arquivo_handler)
    logger.addHandler(console_handler)
    
    return logger
