# 🤖 ABI - Assistente Bancário Inteligente

Uma aplicação inteligente que oferece assistência bancária proativa e consultiva via interface web.

## 🏗️ Arquitetura

A aplicação segue **Domain-Driven Design (DDD)** com separação em camadas:

```
src/
├── domain/              # Lógica de negócio pura
│   ├── entities.py      # Entidades: Cliente, Transação, Produto, etc
│   └── interfaces.py    # Abstrações: ILLMService, IBaseDados, IValidador
├── application/         # Orquestração e casos de uso
│   ├── services.py      # AgenteService (coordenação do fluxo)
│   └── dto.py           # Data Transfer Objects
├── infrastructure/      # Implementações concretas
│   ├── data_loader.py   # Carregamento de dados (CSV, JSON)
│   ├── gemini_service.py # Integração com Google Gemini
│   └── validador.py     # Validação de respostas (anti-alucinação)
├── config.py            # Configurações centralizadas
├── utils.py             # Funções auxiliares (logging)
├── app.py               # Interface Streamlit (web)
└── main.py              # Interface CLI (terminal)
```

## 🎯 Princípios de Design

1. **DDD (Domain-Driven Design)**: Domínio separado de infraestrutura
2. **Clean Code**: Código legível, autodocumentado e bem organizado
3. **SOLID Principles**: Componentes reutilizáveis e testáveis
4. **Dependency Injection**: Componentes recebem dependências no construtor

## 🚀 Como Executar

### Pré-requisitos
- Python 3.10+
- pip

### 1. Instalação de Dependências
```bash
cd src
pip install -r requirements.txt
```

### 2. Interface Web (Streamlit) - Recomendado
```bash
cd src
streamlit run app.py
```

Acesse: http://localhost:8501

### 3. Interface CLI (Terminal)
```bash
cd src
python main.py
```

## 💡 Exemplos de Uso

**No Streamlit:**
1. Abra http://localhost:8501
2. Visualize seu perfil na seção expansível
3. Digite uma pergunta
4. Receba uma resposta personalizada

**Na CLI:**
```
$ python main.py
✅ Bem-vindo, João Silva!
👤 Você: Como está minha saúde financeira?
🤖 ABI: Sua saúde financeira está boa!
```

## 📊 Dados Utilizados

- **perfil_investidor.json**: Perfil e objetivos do cliente
- **produtos_financeiros.json**: Catálogo de produtos bancários
- **transacoes.csv**: Histórico de transações
- **historico_atendimento.csv**: Histórico de atendimentos

## 🛡️ Segurança e Anti-Alucinação

Validações implementadas:
- ✅ Detecta operações proibidas
- ✅ Verifica promessas não permitidas
- ✅ Penaliza respostas especulativas
- ✅ Valida consistência com contexto
- ✅ Retorna nível de confiança (0-100%)

## 📝 Limitações Declaradas

- ❌ Não executa operações financeiras reais
- ❌ Não substitui aplicativos bancários oficiais
- ❌ Não acessa dados bancários sensíveis
- ❌ Não aconselhamento de investimentos regulado

## 📚 Estrutura de Logs

Os logs são salvos em `logs/ABI.log` e exibidos no console.

---

**Desenvolvido com ❤️ para Bradesco-DIO Bootcamp**

## Como Rodar

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar a aplicação
streamlit run app.py
```
