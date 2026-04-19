# === Serviço Gemini ===
# Implementação concreta de integração com a API do Google Gemini
# Segue a interface ILLMService

import logging
from typing import Dict, Any

import google.generativeai as genai

from config import settings
from domain.interfaces import ILLMService


logger = logging.getLogger(__name__)


class GeminiService(ILLMService):
    """
    Implementação concreta do serviço de LLM usando Google Gemini.
    Encapsula a integração com a API do Gemini.
    """
    
    def __init__(self, api_key: str = None):
        """
        Inicializa o serviço Gemini.
        
        Args:
            api_key: Chave da API do Gemini (usa config se não fornecido)
        """
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        
        # Configurar a API
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
        
        logger.info(f"Gemini Service inicializado com modelo {self.model_name}")
    
    def gerar_resposta(
        self,
        mensagem: str,
        contexto: Dict[str, Any],
        system_prompt: str
    ) -> str:
        """
        Gera uma resposta usando o Gemini.
        
        Args:
            mensagem: Pergunta do cliente
            contexto: Informações do cliente em formato dict
            system_prompt: Instruções de sistema para o modelo
            
        Returns:
            str: Resposta gerada pelo Gemini
        """
        
        try:
            # Construir prompt completo
            prompt_completo = self._construir_prompt(
                system_prompt,
                contexto,
                mensagem
            )
            
            logger.debug(f"Enviando prompt para Gemini (tamanho: {len(prompt_completo)} chars)")
            
            # Chamar o modelo
            response = self.model.generate_content(
                prompt_completo,
                generation_config=genai.types.GenerationConfig(
                    temperature=settings.LLM_TEMPERATURE,
                    max_output_tokens=500,
                ),
                safety_settings=self._obter_safety_settings()
            )
            
            resposta = response.text
            logger.info("Resposta recebida do Gemini com sucesso")
            
            return resposta
            
        except Exception as e:
            logger.error(f"Erro ao chamar Gemini: {str(e)}")
            raise
    
    def _construir_prompt(
        self,
        system_prompt: str,
        contexto: Dict[str, Any],
        mensagem: str
    ) -> str:
        """
        Constrói o prompt final que será enviado ao Gemini.
        Combina instruções de sistema, contexto do cliente e mensagem.
        """
        
        # Formatar contexto de forma legível
        contexto_formatado = self._formatar_contexto(contexto)
        
        prompt_final = f"""{system_prompt}

## Contexto Atual do Cliente
{contexto_formatado}

## Pergunta do Cliente
{mensagem}

## Instruções Finais
- Responda de forma direta e amigável
- Use os dados do contexto para personalizar a resposta
- Se não tiver informação, admita explicitamente
- Não invente dados
- Mantenha a resposta concisa (máximo 3-4 linhas)
"""
        
        return prompt_final
    
    def _formatar_contexto(self, contexto: Dict[str, Any]) -> str:
        """Formata o dicionário de contexto em texto legível."""
        
        linhas = []
        
        # Informações do cliente
        if 'cliente' in contexto:
            cliente_info = contexto['cliente']
            linhas.append("### Cliente")
            linhas.append(f"- Nome: {cliente_info.get('nome', 'N/A')}")
            linhas.append(f"- Perfil: {cliente_info.get('perfil_investidor', 'N/A')}")
            linhas.append(f"- Renda Mensal: R$ {cliente_info.get('renda_mensal', 0):.2f}")
            linhas.append(f"- Reserva Emergência: R$ {cliente_info.get('reserva_emergencia', 0):.2f}")
            linhas.append(f"- Saúde Financeira: {cliente_info.get('saude_financeira', 'N/A')}")
            linhas.append("")
        
        # Objetivo
        if contexto.get('objetivo_principal'):
            linhas.append(f"### Objetivo: {contexto['objetivo_principal']}")
            linhas.append("")
        
        # Últimas transações
        if contexto.get('ultimas_transacoes'):
            linhas.append("### Últimas Transações")
            for t in contexto['ultimas_transacoes'][:3]:
                linhas.append(f"- {t['data']}: {t['tipo']} ({t['categoria']}) R$ {t['valor']:.2f}")
            linhas.append("")
        
        # Produtos recomendados
        if contexto.get('produtos_recomendados'):
            linhas.append("### Produtos Recomendados")
            for p in contexto['produtos_recomendados']:
                linhas.append(f"- {p['nome']}: {p['rentabilidade']} (aporte mín: R$ {p['aporte_minimo']:.2f})")
            linhas.append("")
        
        return "\n".join(linhas)
    
    def _obter_safety_settings(self):
        """Retorna configurações de segurança para o Gemini."""
        
        return [
            {
                "category": genai.types.HarmCategory.HARM_CATEGORY_UNSPECIFIED,
                "threshold": genai.types.HarmBlockThreshold.BLOCK_NONE,
            },
        ]
