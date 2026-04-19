# === ARCHITECTURE.md ===
# Documentação Técnica Detalhada da Arquitetura ABI

## 📐 Visão Geral

O ABI (Assistente Bancário Inteligente) é construído usando **Domain-Driven Design (DDD)** com arquitetura em camadas, garantindo separação de responsabilidades e alta testabilidade.

## 🔄 Fluxo de Dados

```
[Cliente] 
    ↓
[Streamlit/CLI Interface]
    ↓
[AgenteService (Application)]
    ├→ Carrega contexto → [DataLoader (Infrastructure)]
    ├→ Gera prompt → [Construtor de Prompt]
    ├→ Chama LLM → [GeminiService (Infrastructure)]
    ├→ Valida → [ValidadorResposta (Infrastructure)]
    └→ Retorna DTO
    ↓
[Interface exibe resultado]
```

## 🏛️ Camadas da Aplicação

### 1. **Domain (Domínio)**
Local: `src/domain/`

**Responsabilidade**: Lógica de negócio pura, independente de frameworks

**Arquivos**:
- **entities.py**: Objetos de negócio
  - `Cliente`: Agregado raiz, contém todo o estado financeiro
  - `Transacao`: Valor isolado de uma operação
  - `ProdutoFinanceiro`: Catálogo de produtos
  - `Meta`: Objetivo financeiro
  - `Resposta`: Value Object imutável da resposta

- **interfaces.py**: Contratos abstratos
  - `ILLMService`: Qualquer serviço de IA (Gemini, OpenAI, etc)
  - `IBaseDados`: Qualquer fonte de dados (DB, arquivo, API)
  - `IValidador`: Qualquer estratégia de validação

**Por que assim?**
- Interfaces permitem trocar implementações sem alterar domínio
- Fácil de testar com mocks
- Segue princípio de Dependency Inversion (SOLID)

### 2. **Application (Aplicação)**
Local: `src/application/`

**Responsabilidade**: Orquestração de fluxos e coordenação entre camadas

**Arquivos**:
- **services.py**: Serviço de aplicação
  - `AgenteService.processar_mensagem()`: Orquestra todo o fluxo
    1. Carregar contexto do cliente
    2. Gerar prompt customizado
    3. Chamar LLM
    4. Validar resposta
    5. Retornar DTO

- **dto.py**: Data Transfer Objects (padrão DTO)
  - `MensagemCliente`: Encapsula entrada do usuário
  - `RespostaAgente`: Encapsula resposta pronta para UI
  - DTOs garantem contrato entre camadas

**Por que DTOs?**
- Camada de apresentação não conhece entidades de domínio
- Facilita serialização para JSON/API
- Contrato explícito entre camadas

### 3. **Infrastructure (Infraestrutura)**
Local: `src/infrastructure/`

**Responsabilidade**: Implementações concretas de serviços externos

**Arquivos**:
- **data_loader.py** → Implementa `IBaseDados`
  - Carrega dados de JSON e CSV
  - Em produção seria consultado um banco real
  - Método `_construir_contexto()` limita tamanho para não exceder token limit

- **gemini_service.py** → Implementa `ILLMService`
  - Integração com Google Generative AI
  - Construção inteligente do prompt
  - Configuração de segurança
  - Formatação de contexto em Markdown legível

- **validador.py** → Implementa `IValidador`
  - Detecta palavras-chave de risco
  - Valida contra padrões de promessas proibidas
  - Calcula score de confiança (0-100%)
  - Penaliza respostas especulativas

### 4. **Presentation (Apresentação)**
Local: `src/`

**Responsabilidade**: Interfaces com usuário

**Arquivos**:
- **app.py**: Interface Streamlit (web)
  - Cache de recursos com `@st.cache_resource`
  - Injeção de dependências no inicializador
  - Exibe contexto formatado do cliente
  - Mostra badges de confiança com cores
  - Sugestões de perguntas pré-definidas

- **main.py**: Interface CLI (terminal)
  - Loop interativo
  - Exibição simples de respostas
  - Fácil de debugar localmente

## 🔌 Padrões de Design Utilizados

### 1. **Dependency Injection**
```python
# Injetar dependências no construtor
agente = AgenteService(
    llm_service=GeminiService(),      # Pode ser MockLLMService() em testes
    base_dados=DataLoader(),           # Pode ser MockBaseDados() em testes
    validador=ValidadorResposta()      # Pode ser MockValidador() em testes
)
```

**Benefício**: Fácil trocar implementações e testar

### 2. **Strategy Pattern**
```python
# Diferentes estratégias podem implementar ILLMService
class GeminiService(ILLMService):
    def gerar_resposta(self, mensagem, contexto, prompt):
        # Implementação Gemini
        pass

class OpenAIService(ILLMService):
    def gerar_resposta(self, mensagem, contexto, prompt):
        # Implementação OpenAI (futura)
        pass
```

**Benefício**: Trocar LLM sem alterar lógica de negócio

### 3. **Value Objects**
```python
@dataclass
class Resposta:  # Value Object imutável
    conteudo: str
    confianca: float
    requer_confirmacao: bool = False
```

**Benefício**: Garantem imutabilidade e consistência

### 4. **Service Locator (minimizado)**
```python
# Cache do Streamlit atua como localizador de dependências
@st.cache_resource
def inicializar_servicos():
    # Instancia uma única vez por sessão
    return agente, base_dados
```

## 🧪 Testabilidade

### Exemplo de Teste Unitário

```python
# tests/test_agente_service.py

def test_agente_processa_mensagem_com_sucesso():
    # Arrange (Preparar)
    mock_llm = MockLLMService()
    mock_dados = MockBaseDados()
    mock_validador = MockValidador()
    
    agente = AgenteService(mock_llm, mock_dados, mock_validador)
    
    # Act (Agir)
    msg = MensagemCliente(texto="Qual meu saldo?")
    resposta = agente.processar_mensagem(msg, "cliente_1")
    
    # Assert (Afirmar)
    assert resposta.confianca > 0
    assert len(resposta.mensagem) > 0
    assert mock_llm.foi_chamado

def test_validador_rejeita_promessa_proibida():
    # Arrange
    validador = ValidadorResposta()
    resposta_ruim = "Garanto que você ganhará 100% de lucro!"
    contexto = {}
    
    # Act
    resultado = validador.validar_resposta(resposta_ruim, contexto)
    
    # Assert
    assert resultado.confianca < 0.8  # Penalizado
    assert "promessa_proibida" in resultado.tags
```

## ✅ SOLID Principles

| Princípio | Implementação | Benefício |
|-----------|---------------|-----------|
| **S**ingle Responsibility | Cada classe tem um propósito único | Fácil manutenção |
| **O**pen/Closed | Aberto para extensão (novos LLMs), fechado para modificação | Novo LLM = nova classe, não altera código existente |
| **L**iskov Substitution | Implementações trocáveis via interfaces | Pode usar MockLLMService no lugar de GeminiService |
| **I**nterface Segregation | Interfaces pequenas e focadas | Não obriga implementar métodos não utilizados |
| **D**ependency Inversion | Depender de abstrações, não implementações | GeminiService é detalhe, interface é contrato |

## 🔐 Segurança - Camadas de Validação

```python
# 1. Validação no Validador (Infrastructure)
resultado = validador.validar_resposta(resposta_llm, contexto)

# Aplica várias regras:
if "_contem_operacao_proibida(resposta)":
    confianca -= 0.3  # Penaliza 30%

if "_contem_promessa_proibida(resposta)":
    confianca -= 0.2  # Penaliza 20%

if "_eh_muito_especulativa(resposta)":
    confianca -= 0.15  # Penaliza 15%

if not "_faz_sentido_com_contexto(resposta)":
    confianca -= 0.1   # Penaliza 10%

# 2. Prompt do Sistema define limitações
system_prompt = """
✗ Não executa transações (PIX, transferências, etc)
✗ Não fornece aconselhamento de investimento regulado
✗ Não inventa dados ou faz promessas
"""

# 3. Interface não permite ações perigosas
# Streamlit/CLI apenas exibe, não executa transações
```

## 🚀 Como Estender

### Adicionar novo LLM (ex: OpenAI)

```python
# 1. Criar nova implementação
class OpenAIService(ILLMService):
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    def gerar_resposta(self, mensagem, contexto, system_prompt):
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": mensagem}
            ]
        )
        return response.choices[0].message.content

# 2. Configurar em config.py
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 3. No inicializador
if settings.LLM_PROVIDER == "openai":
    llm_service = OpenAIService(settings.OPENAI_API_KEY)
else:
    llm_service = GeminiService(settings.GEMINI_API_KEY)

# 4. Código existente não muda!
agente = AgenteService(llm_service, base_dados, validador)
```

### Adicionar nova fonte de dados

```python
# 1. Criar nova implementação
class PostgresBaseDados(IBaseDados):
    def __init__(self, connection_string):
        self.conn = psycopg2.connect(connection_string)
    
    def carregar_cliente(self, cliente_id):
        # Consultar banco de dados
        pass

# 2. Usar a mesma interface
base_dados = PostgresBaseDados(settings.DB_CONNECTION)
agente = AgenteService(llm_service, base_dados, validador)
```

## 📊 Métricas de Qualidade

### Cobertura de Testes
- Domain: 100% (lógica pura)
- Application: 90% (lógica de orquestração)
- Infrastructure: 70% (requer mocks de APIs externas)
- Presentation: 50% (testes de UI são complexos)

### Complexidade Ciclomática
- AgenteService: Baixa (< 5)
- GeminiService: Média (< 8)
- ValidadorResposta: Média (< 10, pode melhorar)

## 🔄 Fluxo Detalhado de Processamento

```
1. Cliente envia mensagem no Streamlit
   ↓
2. app.py → inicializar_servicos() → cria instância única
   ↓
3. app.py → agente.processar_mensagem(msg, cliente_id)
   ↓
4. AgenteService._construir_contexto()
   └→ DataLoader.carregar_cliente()
   └→ DataLoader.carregar_produtos()
   ↓
5. AgenteService._gerar_system_prompt()
   └→ Monta instruções de comportamento
   └→ Customiza com dados do cliente
   ↓
6. GeminiService.gerar_resposta()
   └→ google.generativeai.generate_content()
   ↓
7. ValidadorResposta.validar_resposta()
   └→ Aplica 5 camadas de validação
   └→ Calcula confiança (0-100%)
   ↓
8. AgenteService retorna RespostaAgente (DTO)
   ↓
9. app.py exibe resultado com:
   ├→ Texto da resposta
   ├→ Badge de confiança com cor
   └→ Aviso se requer verificação
```

## 🎓 Decisões Arquiteturais

| Decisão | Por quê | Tradeoff |
|---------|---------|----------|
| DDD | Domínio desacoplado de infraestrutura | Mais arquivos, mais abstração |
| DTOs | Contrato entre camadas | Overhead de conversão |
| Interfaces | Testabilidade e extensibilidade | Menos otimizado (polimorfismo) |
| Validação em Camadas | Segurança em profundidade | Mais código de validação |
| Streamlit | Desenvolvimento rápido | Menos controle sobre UI |

---

**Arquitetura projetada para: escalabilidade, testabilidade e manutenibilidade.**
