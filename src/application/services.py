# === Serviços de Aplicação ===
# Orquestram o fluxo da aplicação, coordenando domain e infrastructure
# Implementam os casos de uso do sistema

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from domain.entities import Cliente, Resposta
from domain.interfaces import ILLMService, IBaseDados, IValidador
from application.dto import MensagemCliente, RespostaAgente


logger = logging.getLogger(__name__)


class AgenteService:
    """
    Serviço de aplicação do Agente ABI.
    Coordena a interação entre o cliente, LLM, validação e regras de negócio.
    """
    
    def __init__(
        self,
        llm_service: ILLMService,
        base_dados: IBaseDados,
        validador: IValidador
    ):
        """
        Inicializa o serviço do agente com suas dependências.
        Usa Injeção de Dependência para facilitar testes.
        """
        self.llm_service = llm_service
        self.base_dados = base_dados
        self.validador = validador
    
    def processar_mensagem(
        self,
        mensagem: MensagemCliente,
        cliente_id: str
    ) -> RespostaAgente:
        """
        Processa uma mensagem do cliente e retorna uma resposta.
        
        Fluxo:
        1. Carregar contexto do cliente
        2. Preparar prompt do sistema
        3. Chamar LLM
        4. Validar resposta
        5. Retornar ao cliente
        
        Args:
            mensagem: Mensagem do cliente
            cliente_id: ID único do cliente
            
        Returns:
            RespostaAgente: Resposta validada pronta para envio
        """
        
        try:
            # 1. Carregar contexto do cliente
            cliente = self.base_dados.carregar_cliente(cliente_id)
            contexto = self._construir_contexto(cliente)
            
            # 2. Preparar prompt do sistema
            system_prompt = self._gerar_system_prompt(cliente)
            
            # 3. Chamar LLM
            logger.info(f"Enviando mensagem para LLM: {mensagem.texto[:100]}")
            resposta_llm = self.llm_service.gerar_resposta(
                mensagem=mensagem.texto,
                contexto=contexto,
                system_prompt=system_prompt
            )
            
            # 4. Validar resposta
            resposta_validada = self.validador.validar_resposta(
                resposta_llm,
                contexto
            )
            
            # 5. Converter para DTO e retornar
            return RespostaAgente(
                mensagem=resposta_validada.conteudo,
                confianca=resposta_validada.confianca,
                requer_confirmacao=resposta_validada.requer_confirmacao
            )
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {str(e)}")
            return RespostaAgente(
                mensagem="Desculpe, ocorreu um erro ao processar sua solicitação. Tente novamente.",
                confianca=0.0
            )
    
    def _construir_contexto(self, cliente: Cliente) -> Dict[str, Any]:
        """
        Constrói um dicionário com todas as informações relevantes do cliente
        para passar ao LLM. Limita tamanho para não exceder contexto do modelo.
        """
        
        # Produtos recomendados baseado no perfil
        todos_produtos = self.base_dados.carregar_produtos()
        produtos_filtrados = [
            p for p in todos_produtos
            if p.risco == cliente.perfil_investidor
        ]
        
        contexto = {
            "cliente": {
                "nome": cliente.nome,
                "idade": cliente.idade,
                "profissao": cliente.profissao,
                "renda_mensal": cliente.renda_mensal,
                "perfil_investidor": cliente.perfil_investidor,
                "patrimonio_total": cliente.patrimonio_total,
                "reserva_emergencia": cliente.reserva_emergencia_atual,
                "meses_cobertura": cliente.obter_meses_reserva(),
                "saude_financeira": cliente.calcular_saude_financeira(),
            },
            "objetivo_principal": cliente.objetivo_principal,
            "metas": [
                {
                    "meta": m.meta,
                    "valor_necessario": m.valor_necessario,
                    "prazo": m.prazo
                }
                for m in cliente.metas
            ],
            "ultimas_transacoes": [
                {
                    "data": t.data,
                    "tipo": t.tipo,
                    "categoria": t.categoria,
                    "valor": t.valor,
                    "descricao": t.descricao
                }
                for t in cliente.transacoes_recentes[:5]  # Últimas 5
            ],
            "produtos_recomendados": [
                {
                    "nome": p.nome,
                    "categoria": p.categoria,
                    "risco": p.risco,
                    "rentabilidade": p.rentabilidade,
                    "aporte_minimo": p.aporte_minimo,
                    "indicado_para": p.indicado_para
                }
                for p in produtos_filtrados[:3]  # Top 3
            ]
        }
        
        return contexto
    
    def _gerar_system_prompt(self, cliente: Cliente) -> str:
        """
        Gera o prompt de sistema que instrui o LLM sobre como se comportar.
        Define tom, limitações e contexto de negócio.
        """
        
        saude = cliente.calcular_saude_financeira()
        
        system_prompt = f"""
# Você é ABI (Assistente Bancário Inteligente)

## Contexto do Cliente
- Nome: {cliente.nome}
- Perfil: {cliente.perfil_investidor}
- Saúde Financeira: {saude}
- Renda Mensal: R$ {cliente.renda_mensal:.2f}

## Instruções de Comportamento

### Tom e Linguagem
- Use linguagem acessível e clara, sem jargão bancário
- Estilo levemente informal, como no WhatsApp
- Seja didático quando explicar conceitos
- Sempre educativo e consultivo

### O que VOCÊ FAZ
✓ Responde perguntas sobre finanças pessoais
✓ Analisa transações e ajuda a entender gastos
✓ Recomenda produtos de acordo com o perfil
✓ Explica conceitos financeiros
✓ Ajuda a planejar metas
✓ Reconhece limitações e admite quando não sabe

### O que VOCÊ NÃO FAZ
✗ Não executa transações (PIX, transferências, etc)
✗ Não fornece aconselhamento de investimento regulado
✗ Não inventa dados ou faz promessas
✗ Não acessa dados sensíveis como senhas
✗ Não substitui profissionais qualificados
✗ Não faz recomendações sobre investimentos complexos

## Exemplo de Resposta
"Entendi! Você tem R$ {cliente.patrimonio_total:.2f} de patrimônio e uma reserva de emergência que cobre {cliente.obter_meses_reserva():.1f} meses. Isso é {saude.lower()}!"

---
Responda sempre de forma clara, concisa e amigável.
"""
        
        return system_prompt
