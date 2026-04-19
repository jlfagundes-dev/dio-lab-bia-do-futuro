# === ARCHITECTURE_DIAGRAM.md ===
# Diagramas Visuais da Arquitetura ABI

## 🔄 Fluxo Completo de Processamento

```mermaid
graph TD
    A[👤 Cliente no Streamlit] -->|Digita pergunta| B[app.py]
    B -->|Inicializa| C{Cache verificado?}
    C -->|Sim| D[Serviços carregados]
    C -->|Não| E[Criar instâncias]
    E --> D
    D -->|Chama| F[AgenteService]
    F -->|1. Carrega| G[Cliente do banco]
    F -->|2. Carrega| H[Produtos financeiros]
    G -->|Retorna| I{Contexto montado}
    H -->|Retorna| I
    I -->|3. Gera| J[System Prompt]
    J -->|4. Envia| K[GeminiService]
    K -->|Chama API| L[Google Gemini API]
    L -->|Gera| M[Resposta texto]
    M -->|5. Valida| N[ValidadorResposta]
    N -->|Aplica regras| O{Passou validação?}
    O -->|Não| P[Reduz confiança]
    O -->|Sim| Q[Máxima confiança]
    P --> R[RespostaAgente DTO]
    Q --> R
    R -->|Retorna| S[app.py exibe]
    S -->|Mostra com cor| T[👤 Resposta formatada]
```

## 🏛️ Arquitetura em Camadas

```mermaid
graph TB
    subgraph Presentation["🖥️ PRESENTATION"]
        A[app.py - Streamlit]
        B[main.py - CLI]
    end
    
    subgraph Application["📋 APPLICATION"]
        C[AgenteService]
        D["DTO<br/>MensagemCliente<br/>RespostaAgente"]
    end
    
    subgraph Domain["🎯 DOMAIN"]
        E["Entidades<br/>Cliente<br/>Transacao<br/>ProdutoFinanceiro<br/>Resposta"]
        F["Interfaces<br/>ILLMService<br/>IBaseDados<br/>IValidador"]
    end
    
    subgraph Infrastructure["🔧 INFRASTRUCTURE"]
        G["DataLoader<br/>carregar_cliente<br/>carregar_produtos"]
        H["GeminiService<br/>gerar_resposta<br/>formatar_contexto"]
        I["ValidadorResposta<br/>validar_resposta<br/>calcular_confianca"]
    end
    
    subgraph External["☁️ EXTERNAL"]
        J["Google Gemini API"]
        K["JSON/CSV Files"]
    end
    
    A -->|Usa| C
    B -->|Usa| C
    C -->|Coordena| D
    C -->|Implementa| E
    C -->|Usa| F
    G -->|Implementa| F
    H -->|Implementa| F
    I -->|Implementa| F
    G -->|Consulta| K
    H -->|Consulta| J
    E -->|Contém| F
    
    style Presentation fill:#e1f5ff
    style Application fill:#f3e5f5
    style Domain fill:#fff3e0
    style Infrastructure fill:#f1f8e9
    style External fill:#ffe0b2
```

## 📊 Dependências de Componentes

```mermaid
graph LR
    A[app.py]
    B[main.py]
    C[AgenteService]
    D[DataLoader]
    E[GeminiService]
    F[ValidadorResposta]
    G[config.py]
    H[utils.py]
    
    A -->|Cria| C
    B -->|Cria| C
    C -->|Usa| D
    C -->|Usa| E
    C -->|Usa| F
    D -->|Lê| G
    E -->|Lê| G
    F -->|Lê| G
    A -->|Usa| H
    B -->|Usa| H
    C -->|Usa| H
    
    style C fill:#ff6b6b
    style D fill:#4ecdc4
    style E fill:#45b7d1
    style F fill:#f7b731
```

## 🔐 Fluxo de Validação

```mermaid
graph TD
    A["📝 Resposta gerada<br/>pelo LLM"] -->|Passa para| B[ValidadorResposta]
    B -->|Verifica| C{Operação<br/>proibida?}
    C -->|Sim| D["❌ confianca -= 0.3<br/>requer_confirmacao=true"]
    C -->|Não| E{Promessa<br/>proibida?}
    E -->|Sim| F["❌ confianca -= 0.2<br/>tag: promessa_proibida"]
    E -->|Não| G{Muito<br/>especulativa?}
    G -->|Sim| H["⚠️ confianca -= 0.15<br/>tag: especulativa"]
    G -->|Não| I{Faz sentido<br/>com contexto?}
    I -->|Não| J["⚠️ confianca -= 0.1"]
    I -->|Sim| K{"Resposta<br/>vazia?"}
    K -->|Sim| L["⚠️ confianca -= 0.2"]
    K -->|Não| M["✅ Confiança final"]
    D --> N["📊 Resposta Validada"]
    F --> N
    H --> N
    J --> N
    L --> N
    M --> N
    N -->|Retorna| O["RespostaAgente<br/>com badge de cor"]
```

## 📈 Lifecycle do Cliente

```mermaid
sequenceDiagram
    participant Cliente as 👤 Cliente
    participant Streamlit as 🖥️ Streamlit
    participant AgenteService as 📋 Agente
    participant DataLoader as 📂 Dados
    participant Gemini as ☁️ Gemini
    participant Validador as ✅ Validador

    Cliente->>Streamlit: Digite pergunta
    Streamlit->>AgenteService: processar_mensagem()
    AgenteService->>DataLoader: carregar_cliente()
    DataLoader-->>AgenteService: Cliente obj
    AgenteService->>DataLoader: carregar_produtos()
    DataLoader-->>AgenteService: Produtos lista
    AgenteService->>AgenteService: _construir_contexto()
    AgenteService->>AgenteService: _gerar_system_prompt()
    AgenteService->>Gemini: gerar_resposta()
    Gemini-->>AgenteService: Texto resposta
    AgenteService->>Validador: validar_resposta()
    Validador-->>AgenteService: Resposta validada
    AgenteService-->>Streamlit: RespostaAgente DTO
    Streamlit-->>Cliente: Exibe resposta+confiança
```

## 🎯 Injeção de Dependência

```mermaid
graph LR
    A["AgenteService<br/>(recebe interfaces)"]
    B["Implementações<br/>Concretas"]
    C["Testes<br/>Mocks"]
    
    A -->|ILLMService| D["GeminiService"]
    A -->|ILLMService| E["MockLLMService"]
    A -->|IBaseDados| F["DataLoader"]
    A -->|IBaseDados| G["MockBaseDados"]
    A -->|IValidador| H["ValidadorResposta"]
    A -->|IValidador| I["MockValidador"]
    
    D --> B
    F --> B
    H --> B
    E --> C
    G --> C
    I --> C
    
    style A fill:#ff6b6b
    style B fill:#90EE90
    style C fill:#FFA500
```

## 📊 Contexto do Cliente (Estrutura de Dados)

```mermaid
graph TD
    A["Cliente<br/>Contexto"]
    
    A --> B["cliente"]
    B --> B1["nome"]
    B --> B2["idade"]
    B --> B3["perfil_investidor"]
    B --> B4["renda_mensal"]
    B --> B5["patrimonio_total"]
    B --> B6["reserva_emergencia"]
    B --> B7["saude_financeira"]
    
    A --> C["objetivo_principal"]
    
    A --> D["metas"]
    D --> D1["meta 1: valor + prazo"]
    D --> D2["meta 2: valor + prazo"]
    
    A --> E["ultimas_transacoes"]
    E --> E1["Transação 1"]
    E --> E2["Transação 2"]
    E --> E3["...últimas 5"]
    
    A --> F["produtos_recomendados"]
    F --> F1["Produto 1"]
    F --> F2["Produto 2"]
    F --> F3["Top 3"]
```

## 🔐 Camadas de Segurança

```
┌─────────────────────────────────────────────────────────┐
│ 1️⃣ PROMPT DO SISTEMA                                    │
│    ✗ Não execute transações                             │
│    ✗ Não faça promessas de retorno garantido            │
│    ✗ Admita limitações                                  │
└──────────────────┬──────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────┐
│ 2️⃣ RESPOSTA DO LLM (Google Gemini)                      │
│    Segue instruções do system prompt                     │
└──────────────────┬──────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────┐
│ 3️⃣ VALIDADOR - Detecta Risco                           │
│    ✅ Operações proibidas                              │
│    ✅ Promessas não permitidas                         │
│    ✅ Respostas especulativas                          │
│    ✅ Consistência com contexto                        │
└──────────────────┬──────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────┐
│ 4️⃣ CONFIANÇA (0-100%) - Penalizações aplicadas        │
│    -30% = Operação proibida                             │
│    -20% = Promessa proibida                             │
│    -15% = Muito especulativa                            │
│    -10% = Inconsistente                                 │
└──────────────────┬──────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────────┐
│ 5️⃣ INTERFACE                                            │
│    Exibe com badges de cor:                             │
│    🟢 Verde (>80%): Alta confiança                     │
│    🟡 Amarelo (50-80%): Média confiança                │
│    🔴 Vermelho (<50%): Baixa confiança                 │
│    ⚠️ Aviso se requer_confirmacao=true                 │
└─────────────────────────────────────────────────────────┘
```

## 📂 Estrutura de Diretórios

```
abi-agente/
├── src/                           # Código-fonte
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── entities.py            # ✅ Cliente, Transacao, etc
│   │   └── interfaces.py          # ✅ ILLMService, IBaseDados
│   ├── application/
│   │   ├── __init__.py
│   │   ├── services.py            # ✅ AgenteService
│   │   └── dto.py                 # ✅ MensagemCliente, RespostaAgente
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── data_loader.py         # ✅ DataLoader
│   │   ├── gemini_service.py      # ✅ GeminiService
│   │   └── validador.py           # ✅ ValidadorResposta
│   ├── config.py                  # ✅ Configurações
│   ├── utils.py                   # ✅ Logging
│   ├── app.py                     # ✅ Streamlit UI
│   ├── main.py                    # ✅ CLI
│   ├── requirements.txt            # ✅ Dependências
│   └── README.md                  # ✅ Documentação
│
├── data/                          # Dados do cliente
│   ├── perfil_investidor.json
│   ├── produtos_financeiros.json
│   ├── transacoes.csv
│   └── historico_atendimento.csv
│
├── docs/                          # Documentação do projeto
│   ├── 01-documentacao-agente.md
│   ├── 02-base-conhecimento.md
│   ├── 03-prompts.md
│   ├── 04-metricas.md
│   └── 05-pitch.md
│
├── tests_examples.py              # 🧪 Exemplos de testes
├── ARCHITECTURE.md                # 📐 Documentação técnica
├── QUICK_START.md                 # 🚀 Guia de início rápido
├── DEPLOYMENT.md                  # 🌍 Guia de produção
├── .env                           # 🔑 Variáveis de ambiente
├── .gitignore                     # 📝 Git ignore
└── README.md                      # 📖 README principal
```

---

**Visualizações Mermaid renderizadas acima! 📊**
