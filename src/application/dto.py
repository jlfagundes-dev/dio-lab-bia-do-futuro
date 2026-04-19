# === Data Transfer Objects (DTOs) ===
# Estruturas para transferência de dados entre camadas
# Desacoplam a representação interna da API

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class MensagemCliente:
    """DTO que encapsula uma mensagem do cliente."""
    
    texto: str
    tipo: str = "texto"  # texto, audio, etc
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class RespostaAgente:
    """DTO que encapsula a resposta do agente."""
    
    mensagem: str
    confianca: float
    requer_confirmacao: bool = False
    sugestoes: Optional[list] = None
