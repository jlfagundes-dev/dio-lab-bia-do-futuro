# === Interfaces (Abstrações) de Domínio ===
# Define contatos entre camadas, independente de implementação
# Facilita testes e desacoplamento

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from domain.entities import Cliente, ProdutoFinanceiro, Resposta


class ILLMService(ABC):
    """Interface para serviços de LLM (qualquer IA generativa)."""
    
    @abstractmethod
    def gerar_resposta(
        self,
        mensagem: str,
        contexto: Dict[str, Any],
        system_prompt: str
    ) -> str:
        """
        Gera uma resposta baseada na mensagem e contexto.
        
        Args:
            mensagem: Pergunta ou comando do cliente
            contexto: Dicionário com informações do cliente
            system_prompt: Instruções de sistema para o LLM
            
        Returns:
            str: Resposta gerada pelo LLM
        """
        pass


class IBaseDados(ABC):
    """Interface para acesso aos dados (clientes, transações, etc)."""
    
    @abstractmethod
    def carregar_cliente(self, cliente_id: str) -> Cliente:
        """Carrega dados de um cliente específico."""
        pass
    
    @abstractmethod
    def carregar_produtos(self) -> List[ProdutoFinanceiro]:
        """Carrega lista de produtos financeiros disponíveis."""
        pass


class IValidador(ABC):
    """Interface para validar respostas e aplicar regras de negócio."""
    
    @abstractmethod
    def validar_resposta(self, resposta: str, contexto: Dict[str, Any]) -> Resposta:
        """
        Valida uma resposta antes de enviá-la ao cliente.
        Aplica regras de segurança e anti-alucinação.
        """
        pass
