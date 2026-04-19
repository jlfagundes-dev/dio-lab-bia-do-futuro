# === Carregador de Dados ===
# Implementação concreta de acesso aos dados (JSON, CSV, etc)
# Segue a interface IBaseDados

import json
import csv
import logging
from typing import List, Dict, Any
from pathlib import Path

from config import settings
from domain.entities import Cliente, ProdutoFinanceiro, Meta, Transacao
from domain.interfaces import IBaseDados


logger = logging.getLogger(__name__)


class DataLoader(IBaseDados):
    """
    Carregador de dados que implementa a interface IBaseDados.
    Lê dados de arquivos JSON e CSV.
    """
    
    def __init__(self):
        """Inicializa o loader verificando que os arquivos existem."""
        self._validar_arquivos()
    
    def _validar_arquivos(self) -> None:
        """Valida se os arquivos de dados existem."""
        arquivos = [
            settings.PERFIL_INVESTIDOR_PATH,
            settings.PRODUTOS_FINANCEIROS_PATH,
            settings.TRANSACOES_PATH,
            settings.ATENDIMENTOS_PATH,
        ]
        
        for arquivo in arquivos:
            if not Path(arquivo).exists():
                logger.warning(f"Arquivo não encontrado: {arquivo}")
    
    def carregar_cliente(self, cliente_id: str = "default") -> Cliente:
        """
        Carrega dados do cliente. Por enquanto, carrega do perfil_investidor.json.
        Em produção, seria consultado um banco de dados real.
        """
        
        try:
            with open(settings.PERFIL_INVESTIDOR_PATH, 'r', encoding='utf-8') as f:
                dados_cliente = json.load(f)
            
            # Mapear metas
            metas = [
                Meta(
                    meta=m['meta'],
                    valor_necessario=m['valor_necessario'],
                    prazo=m['prazo']
                )
                for m in dados_cliente.get('metas', [])
            ]
            
            # Carregar transações recentes
            transacoes = self._carregar_transacoes()
            
            # Criar entidade Cliente
            cliente = Cliente(
                nome=dados_cliente['nome'],
                idade=dados_cliente['idade'],
                profissao=dados_cliente['profissao'],
                renda_mensal=dados_cliente['renda_mensal'],
                perfil_investidor=dados_cliente['perfil_investidor'],
                objetivo_principal=dados_cliente['objetivo_principal'],
                patrimonio_total=dados_cliente['patrimonio_total'],
                reserva_emergencia_atual=dados_cliente['reserva_emergencia_atual'],
                aceita_risco=dados_cliente['aceita_risco'],
                metas=metas,
                transacoes_recentes=transacoes
            )
            
            logger.info(f"Cliente {cliente.nome} carregado com sucesso")
            return cliente
            
        except Exception as e:
            logger.error(f"Erro ao carregar cliente: {str(e)}")
            raise
    
    def carregar_produtos(self) -> List[ProdutoFinanceiro]:
        """Carrega lista de produtos financeiros disponíveis."""
        
        try:
            with open(settings.PRODUTOS_FINANCEIROS_PATH, 'r', encoding='utf-8') as f:
                dados_produtos = json.load(f)
            
            produtos = [
                ProdutoFinanceiro(
                    nome=p['nome'],
                    categoria=p['categoria'],
                    risco=p['risco'],
                    rentabilidade=p['rentabilidade'],
                    aporte_minimo=p['aporte_minimo'],
                    indicado_para=p['indicado_para'],
                    descricao=p.get('descricao')
                )
                for p in dados_produtos
            ]
            
            logger.info(f"{len(produtos)} produtos financeiros carregados")
            return produtos
            
        except Exception as e:
            logger.error(f"Erro ao carregar produtos: {str(e)}")
            return []
    
    def _carregar_transacoes(self, limite: int = 10) -> List[Transacao]:
        """Carrega as últimas transações do cliente."""
        
        try:
            transacoes = []
            with open(settings.TRANSACOES_PATH, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    transacao = Transacao(
                        id=row.get('id', ''),
                        data=row.get('data', ''),
                        tipo=row.get('tipo', ''),
                        categoria=row.get('categoria', ''),
                        valor=float(row.get('valor', 0)),
                        descricao=row.get('descricao', ''),
                        saldo_after=float(row.get('saldo_after', 0)) if row.get('saldo_after') else None
                    )
                    transacoes.append(transacao)
                    if len(transacoes) >= limite:
                        break
            
            logger.info(f"{len(transacoes)} transações carregadas")
            return transacoes
            
        except Exception as e:
            logger.warning(f"Erro ao carregar transações: {str(e)}")
            return []
