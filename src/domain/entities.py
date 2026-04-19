# === Entidades de Domínio ===
# Objetos que representam conceitos do domínio de negócio bancário
# Cada entidade tem identidade única e ciclo de vida

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Transacao:
    """Representa uma transação financeira do cliente."""
    
    id: str
    data: str
    tipo: str  # entrada, saída, transferência
    categoria: str
    valor: float
    descricao: str
    saldo_after: Optional[float] = None


@dataclass
class Meta:
    """Representa uma meta financeira do cliente."""
    
    meta: str
    valor_necessario: float
    prazo: str
    progresso: float = 0.0


@dataclass
class Cliente:
    """
    Entidade Cliente - representa um cliente do banco.
    Agrupa informações financeiras e perfil do cliente.
    """
    
    nome: str
    idade: int
    profissao: str
    renda_mensal: float
    perfil_investidor: str  # conservador, moderado, agressivo
    objetivo_principal: str
    patrimonio_total: float
    reserva_emergencia_atual: float
    aceita_risco: bool
    metas: List[Meta] = field(default_factory=list)
    transacoes_recentes: List[Transacao] = field(default_factory=list)
    
    def calcular_saude_financeira(self) -> str:
        """Calcula um score simples de saúde financeira."""
        if self.reserva_emergencia_atual >= self.renda_mensal * 3:
            return "Boa"
        elif self.reserva_emergencia_atual >= self.renda_mensal:
            return "Moderada"
        else:
            return "Frágil"
    
    def obter_meses_reserva(self) -> float:
        """Calcula quantos meses de vida a reserva cobre."""
        if self.renda_mensal == 0:
            return 0
        return self.reserva_emergencia_atual / self.renda_mensal


@dataclass
class ProdutoFinanceiro:
    """Representa um produto financeiro disponível."""
    
    nome: str
    categoria: str  # renda_fixa, renda_variavel, fundo, etc
    risco: str  # baixo, medio, alto
    rentabilidade: str
    aporte_minimo: float
    indicado_para: str
    descricao: Optional[str] = None


@dataclass
class Resposta:
    """Value Object que encapsula a resposta do agente."""
    
    conteudo: str
    confianca: float  # 0.0 a 1.0, indica o grau de confiança na resposta
    requer_confirmacao: bool = False
    tags: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
