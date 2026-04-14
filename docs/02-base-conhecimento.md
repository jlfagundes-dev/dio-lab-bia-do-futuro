# Base de Conhecimento

## Dados Utilizados

Descreva se usou os arquivos da pasta `data`, por exemplo:

| Arquivo | Formato | Utilização no Agente |
|---------|---------|---------------------|
| `historico_atendimento.csv` | CSV | Contextualizar interações anteriores |
| `perfil_investidor.json` | JSON | Personalizar recomendações |
| `produtos_financeiros.json` | JSON | Sugerir produtos adequados ao perfil |
| `transacoes.csv` | CSV | Analisar padrão de gastos do cliente |

---

## Adaptações nos Dados

> Você modificou ou expandiu os dados mockados? Descreva aqui.

Não modifiquei, nem expandi os dados mockados neste primeiro momento

---

## Estratégia de Integração

### Como os dados são carregados?
> Descreva como seu agente acessa a base de conhecimento.

Os arquivos CSV e JSON são carregados pela camada de orquestração no início da execução da aplicação.

Pega só as últimas 5 transações para manter o contexto relevante.

```python
import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any


class DataLoader:
    def __init__(self, data_path: str = "data"):
        self.data_path = Path(data_path)

        self.historico = None
        self.transacoes = None
        self.perfil = None
        self.produtos = None

    def load_all(self) -> None:
        """Carrega todos os dados na memória"""
        self._load_csvs()
        self._load_jsons()

    def _load_csvs(self) -> None:
        """Carrega arquivos CSV"""
        try:
            self.historico = pd.read_csv(self.data_path / "historico_atendimento.csv")
            self.transacoes = pd.read_csv(self.data_path / "transacoes.csv")
        except Exception as e:
            print(f"[ERRO] Falha ao carregar CSVs: {e}")

    def _load_jsons(self) -> None:
        """Carrega arquivos JSON"""
        try:
            with open(self.data_path / "perfil_investidor.json", "r", encoding="utf-8") as f:
                self.perfil = json.load(f)

            with open(self.data_path / "produtos_financeiros.json", "r", encoding="utf-8") as f:
                self.produtos = json.load(f)

        except Exception as e:
            print(f"[ERRO] Falha ao carregar JSONs: {e}")

    def get_context(self) -> Dict[str, Any]:
        """Retorna os dados organizados para uso no prompt"""
        return {
            "perfil": self.perfil,
            "transacoes": self._get_transacoes_recentes(),
            "historico": self._get_historico_resumido(),
            "produtos": self.produtos
        }

    def _get_transacoes_recentes(self, limite: int = 5):
        """Retorna as últimas transações"""
        if self.transacoes is not None:
            return self.transacoes.tail(limite).to_dict(orient="records")
        return []

    def _get_historico_resumido(self, limite: int = 5):
        """Retorna últimas interações"""
        if self.historico is not None:
            return self.historico.tail(limite).to_dict(orient="records")
        return []
```

### Como os dados são usados no prompt?
> Os dados vão no system prompt? São consultados dinamicamente?

Os dados são organizados dinamicamente em um texto consolidado antes de serem enviados ao LLM. Isso mantém o contexto objetivo e facilita a leitura das informações do cliente.

No perfil o formato JSON e nas outras variaveis serão arrays.

```python
def montar_contexto_texto(contexto: dict) -> str:
    perfil = contexto.get("perfil", {})
    transacoes = contexto.get("transacoes", [])
    historico = contexto.get("historico", [])
    produtos = contexto.get("produtos", [])

    texto = "DADOS DO CLIENTE:\n\n"

    # PERFIL
    texto += "PERFIL DO CLIENTE:\n"
    if perfil:
        texto += f"- Nome: {perfil.get('nome')}\n"
        texto += f"- Idade: {perfil.get('idade')}\n"
        texto += f"- Profissão: {perfil.get('profissao')}\n"
        texto += f"- Renda mensal: R$ {perfil.get('renda_mensal')}\n"
        texto += f"- Perfil de investidor: {perfil.get('perfil_investidor')}\n"
        texto += f"- Objetivo principal: {perfil.get('objetivo_principal')}\n"
        texto += f"- Patrimônio total: R$ {perfil.get('patrimonio_total')}\n"
        texto += f"- Reserva de emergência atual: R$ {perfil.get('reserva_emergencia_atual')}\n"
        texto += f"- Aceita risco: {'Sim' if perfil.get('aceita_risco') else 'Não'}\n"
    else:
        texto += "- Não disponível\n"

    # METAS
    texto += "\nMETAS FINANCEIRAS:\n"
    metas = perfil.get("metas", []) if perfil else []
    if metas:
        for m in metas:
            texto += f"- {m.get('meta')}: R$ {m.get('valor_necessario')} até {m.get('prazo')}\n"
    else:
        texto += "- Nenhuma meta definida\n"

    # TRANSAÇÕES
    texto += "\nTRANSAÇÕES RECENTES:\n"
    if transacoes:
        for t in transacoes:
            data = t.get("data") or t.get("Data")
            desc = t.get("descricao") or t.get("descricao") or t.get("categoria")
            valor = t.get("valor") or t.get("Valor")

            texto += f"- {data}: {desc} - R$ {valor}\n"
    else:
        texto += "- Nenhuma transação encontrada\n"

    # HISTÓRICO
    texto += "\nHISTÓRICO DE INTERAÇÕES:\n"
    if historico:
        for h in historico:
            texto += f"- {h}\n"
    else:
        texto += "- Nenhum histórico disponível\n"

    # PRODUTOS
    texto += "\nPRODUTOS FINANCEIROS DISPONÍVEIS:\n"
    if produtos:
        for p in produtos:
            texto += f"- {p.get('nome')} ({p.get('risco')}, {p.get('indicado_para')})\n"
    else:
        texto += "- Nenhum produto disponível\n"

    # INSTRUÇÕES
    texto += "\nINSTRUÇÕES:\n"
    texto += "- Responder apenas com base nos dados fornecidos\n"
    texto += "- Não inventar informações\n"
    texto += "- Não recomendar produtos incompatíveis com o perfil\n"

    return texto
```

---

## Exemplo de Contexto Montado

> Mostre um exemplo de como os dados são formatados para o agente.

```
DADOS DO CLIENTE:

PERFIL DO CLIENTE:
- Nome: João Silva
- Idade: 32
- Profissão: Analista de Sistemas
- Renda mensal: R$ 5.000
- Perfil de investidor: Moderado
- Objetivo principal: Construir reserva de emergência
- Patrimônio total: R$ 15.000
- Reserva de emergência atual: R$ 10.000
- Aceita risco: Não

METAS FINANCEIRAS:
- Completar reserva de emergência: R$ 15.000 até 2026-06
- Entrada do apartamento: R$ 50.000 até 2027-12

TRANSAÇÕES RECENTES:
- 01/11: Supermercado - R$ 450
- 03/11: Streaming - R$ 55
- 05/11: Restaurante - R$ 120
- 07/11: Transporte - R$ 80

PRODUTOS FINANCEIROS DISPONÍVEIS:
- Tesouro Selic (baixo risco, indicado para reserva de emergência)
- CDB Liquidez Diária (baixo risco, rendimento diário)
- LCI/LCA (baixo risco, isento de IR após 90 dias)
- Fundo Multimercado (risco médio, diversificação)
- Fundo de Ações (alto risco, longo prazo)

INSTRUÇÕES:
- Responder com base apenas nos dados fornecidos
- Não inventar informações
- Não recomendar produtos sem considerar o perfil
```
