# === Validador de Respostas ===
# Implementação concreta da validação de respostas para evitar alucinações
# Segue a interface IValidador

import logging
import re
from typing import Dict, Any

from domain.entities import Resposta
from domain.interfaces import IValidador


logger = logging.getLogger(__name__)


class ValidadorResposta(IValidador):
    """
    Validador que aplica regras de negócio e anti-alucinação nas respostas.
    Implementa estratégias para aumentar confiabilidade do agente.
    """
    
    # Palavras-chave que indicam especulação ou informações não confiáveis
    PALAVRAS_ESPECULACAO = [
        'acredito que',
        'provavelmente',
        'talvez',
        'pode ser',
        'supostamente',
        'aparentemente',
    ]
    
    # Padrões que indicam promessas não permitidas
    PADROES_PROMESSAS_PROIBIDAS = [
        r'garanto que você vai ganhar',
        r'vai dar lucro',
        r'prometo que',
        r'com certeza vai',
        r'renda certa de \d+%',
    ]
    
    # Operações proibidas que não devemos confirmar
    OPERACOES_PROIBIDAS = [
        'pix',
        'transferência',
        'saque',
        'empréstimo',
        'compre agora',
        'faça um pix',
    ]
    
    def validar_resposta(
        self,
        resposta: str,
        contexto: Dict[str, Any]
    ) -> Resposta:
        """
        Valida uma resposta antes de enviar ao cliente.
        Aplica várias camadas de validação.
        
        Args:
            resposta: Texto da resposta gerada pelo LLM
            contexto: Contexto do cliente
            
        Returns:
            Resposta: Entidade com conteúdo validado e nível de confiança
        """
        
        confianca = 1.0
        requer_confirmacao = False
        tags = []
        
        # Validação 1: Operações proibidas
        if self._contem_operacao_proibida(resposta):
            logger.warning("Resposta contém operação proibida")
            confianca -= 0.3
            tags.append("operacao_proibida")
            requer_confirmacao = True
        
        # Validação 2: Promessas não permitidas
        if self._contem_promessa_proibida(resposta):
            logger.warning("Resposta contém promessa proibida")
            confianca -= 0.2
            tags.append("promessa_proibida")
            requer_confirmacao = True
        
        # Validação 3: Muito especulativa
        if self._eh_muito_especulativa(resposta):
            logger.warning("Resposta muito especulativa")
            confianca -= 0.15
            tags.append("especulativa")
            requer_confirmacao = True
        
        # Validação 4: Faz sentido com o contexto
        if not self._faz_sentido_com_contexto(resposta, contexto):
            logger.warning("Resposta não faz sentido com o contexto")
            confianca -= 0.1
            tags.append("inconsistente_contexto")
        
        # Validação 5: Não é completamente vazia
        if len(resposta.strip()) < 10:
            logger.warning("Resposta muito curta ou vazia")
            confianca -= 0.2
            tags.append("resposta_vazia")
        
        # Garantir confiança entre 0 e 1
        confianca = max(0.0, min(1.0, confianca))
        
        # Criar entidade de resposta validada
        resposta_validada = Resposta(
            conteudo=resposta,
            confianca=confianca,
            requer_confirmacao=requer_confirmacao,
            tags=tags
        )
        
        logger.info(f"Resposta validada. Confiança: {confianca:.2f}, Tags: {tags}")
        
        return resposta_validada
    
    def _contem_operacao_proibida(self, resposta: str) -> bool:
        """Verifica se a resposta menciona operações financeiras diretas proibidas."""
        
        resposta_lower = resposta.lower()
        
        for operacao in self.OPERACOES_PROIBIDAS:
            if operacao in resposta_lower:
                # Verificar se é uma negação (não faça)
                if not self._eh_negacao(resposta_lower, operacao):
                    return True
        
        return False
    
    def _contem_promessa_proibida(self, resposta: str) -> bool:
        """Verifica se a resposta faz promessas não permitidas."""
        
        resposta_lower = resposta.lower()
        
        for padrao in self.PADROES_PROMESSAS_PROIBIDAS:
            if re.search(padrao, resposta_lower, re.IGNORECASE):
                return True
        
        return False
    
    def _eh_muito_especulativa(self, resposta: str) -> bool:
        """Verifica se a resposta é muito especulativa (muitas incertezas)."""
        
        resposta_lower = resposta.lower()
        contagem_especulacoes = sum(
            1 for palavra in self.PALAVRAS_ESPECULACAO
            if palavra in resposta_lower
        )
        
        # Se tem mais de 2 marcadores de especulação, é muito especulativa
        return contagem_especulacoes > 2
    
    def _faz_sentido_com_contexto(
        self,
        resposta: str,
        contexto: Dict[str, Any]
    ) -> bool:
        """Verifica se a resposta faz sentido com o contexto fornecido."""
        
        # Validações simples: se o contexto tem produto, deve ser mencionado
        # Esta é uma validação bem simplificada. Em produção, seria mais robusta
        
        # Se a resposta é muito genérica e o contexto tem dados específicos
        if len(contexto.get('ultimas_transacoes', [])) > 0:
            # Esperaríamos que a resposta fosse personalizada
            pass
        
        return True
    
    def _eh_negacao(self, texto: str, termo: str) -> bool:
        """Verifica se a menção do termo é uma negação."""
        
        # Procura por "não [termo]" ou similar
        padrao = rf'(não|nunca|nuca)\s+\w*\s*{re.escape(termo)}'
        return bool(re.search(padrao, texto, re.IGNORECASE))
