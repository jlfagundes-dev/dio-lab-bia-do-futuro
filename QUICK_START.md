# === QUICK START ===
# Guia Passo-a-Passo para Executar o ABI

## 🚀 Início Rápido (2 minutos)

### Passo 1: Preparar o Ambiente
```bash
# Abra o terminal/CMD e vá até a pasta do projeto
cd "c:\projects_learn\Bootcamp Bradesco-DIO\dio-lab-bia-do-futuro"

# Verifique que tem Python 3.10+
python --version

# Crie um ambiente virtual (opcional mas recomendado)
python -m venv venv
venv\Scripts\activate  # Windows
```

### Passo 2: Instalar Dependências
```bash
# Navegue até a pasta src
cd src

# Instale as dependências do projeto
pip install -r requirements.txt
```

### Passo 3: Executar o ABI

#### **Opção A: Interface Web (RECOMENDADO)**
```bash
# No terminal, ainda em src/
streamlit run app.py

# Vai abrir automaticamente em: http://localhost:8501
```

#### **Opção B: Interface CLI**
```bash
# No terminal, ainda em src/
python main.py

# Aparecerá um menu interativo no terminal
```

---

## 🎯 Usando a Interface Web

### Tela Inicial
1. Vê o título "🤖 ABI"
2. Clique em "👤 Perfil do Cliente: João Silva" para expandir
3. Visualize os dados do cliente

### Fazer uma Pergunta
1. Digite sua pergunta em "Digite sua pergunta sobre suas finanças"
2. Exemplos:
   - "Como está minha saúde financeira?"
   - "Quais produtos você recomenda?"
   - "Qual é o status das minhas metas?"
3. Clique no botão "Enviar ✈️"

### Visualizar Resposta
1. A resposta aparece em um box cinza
2. Mostra o nível de confiança (Alta/Média/Baixa)
3. Se houver ⚠️, a resposta requer verificação

### Usar Sugestões
1. Clique em uma das "💡 Perguntas Sugeridas"
2. A resposta será processada automaticamente

---

## 🔧 Configuração Avançada

### Mudar a Chave da API
1. Abra `src/.env` em um editor de texto
2. Procure por `API_KEY_GEMINI=`
3. Substitua por sua chave real do Gemini

### Ajustar Criatividade do LLM
1. Na barra lateral do Streamlit
2. Encontre o slider "Criatividade do LLM"
3. Mova para ajustar (0.0 = determinístico, 1.0 = criativo)

### Visualizar Logs
1. Logs aparecem na pasta `logs/ABI.log`
2. Também aparecem no console do terminal

---

## 🧪 Testando Diferentes Cenários

### Teste 1: Consultar Saúde Financeira
```
Pergunta: "Como está minha saúde financeira?"
Resposta esperada: Analisa reserva de emergência e patrimônio
Confiança esperada: Alta (> 80%)
```

### Teste 2: Questão sobre Produtos
```
Pergunta: "Quais produtos você recomenda para meu perfil?"
Resposta esperada: Lista produtos conforme perfil moderado
Confiança esperada: Alta (> 80%)
```

### Teste 3: Pergunta Especulativa
```
Pergunta: "Você garante que vou ganhar dinheiro?"
Resposta esperada: Recusa promessa; confiança baixa
Confiança esperada: Baixa (< 60%)
Nota: ⚠️ Requer verificação
```

### Teste 4: Operação Proibida
```
Pergunta: "Pode fazer um PIX para fulano?"
Resposta esperada: Explica que não executa operações
Confiança esperada: Muito Baixa (< 40%)
```

---

## ❌ Resolvendo Problemas

### Erro: "ModuleNotFoundError"
```
Solução:
1. Verifique que está em src/
2. Rode: pip install -r requirements.txt
3. Se mesmo assim falhar, rode:
   pip install streamlit google-generativeai python-dotenv
```

### Erro: "API key not found"
```
Solução:
1. Verifique que .env existe em src/
2. Verifique que tem conteúdo:
   API_KEY_GEMINI=sua_chave_real_aqui
3. Reinicie o streamlit: Ctrl+C e streamlit run app.py
```

### Erro: "Port 8501 already in use"
```
Solução:
1. Feche qualquer outra janela do Streamlit
2. Ou especifique outra porta:
   streamlit run app.py --server.port 8502
```

### Resposta muito genérica
```
Solução:
1. Verifique que perfil_investidor.json existe
2. Verifique que os dados estão corretos
3. Tente ajustar a temperatura (criatividade)
```

---

## 📁 Estrutura de Arquivos Importante

```
src/
├── app.py                    # ← Inicie daqui (streamlit run app.py)
├── main.py                   # ← Ou daqui (python main.py)
├── .env                       # ← Sua API key fica aqui
├── requirements.txt           # ← Dependências
├── config.py                 # ← Configurações
├── utils.py                  # ← Logging
├── domain/
│   ├── entities.py
│   └── interfaces.py
├── application/
│   ├── services.py
│   └── dto.py
└── infrastructure/
    ├── data_loader.py
    ├── gemini_service.py
    └── validador.py

data/
├── perfil_investidor.json    # ← Dados do cliente
├── produtos_financeiros.json # ← Catálogo de produtos
├── transacoes.csv            # ← Histórico de transações
└── historico_atendimento.csv # ← Histórico de atendimentos
```

---

## 💡 Dicas de Uso

### Pergunta Eficaz
✅ "Como está minha saúde financeira?"
❌ "Me faça ficar rico"

### Próximos Passos Recomendados
1. Explore todas as perguntas sugeridas
2. Teste com perguntas customizadas
3. Ajuste a criatividade e observe diferenças
4. Verifique os logs em `logs/ABI.log`

### Entendendo a Confiança
- 🟢 **Verde (Alta 80%+)**: Resposta bem fundamentada
- 🟡 **Amarelo (Média 50-80%)**: Resposta razoável
- 🔴 **Vermelho (Baixa <50%)**: Resposta questionável, verificar

---

## 🎓 Estrutura do Código

O código está organizado em **camadas** (DDD):

1. **Domain** (entities.py, interfaces.py)
   - Lógica pura de negócio
   - Não depende de nada externo

2. **Application** (services.py, dto.py)
   - Orquestra o fluxo
   - Coordena domain + infrastructure

3. **Infrastructure** (data_loader.py, gemini_service.py, validador.py)
   - Fala com sistemas externos (APIs, arquivos)
   - Implementa interfaces

4. **Presentation** (app.py, main.py)
   - Interface com usuário
   - Não contém lógica de negócio

**Isso permite:**
- ✅ Trocar LLM (Gemini → OpenAI → Claude)
- ✅ Trocar fonte de dados (JSON → Banco de dados)
- ✅ Fácil testar com mocks
- ✅ Código muito legível e manutenível

---

## 📞 Próximos Passos

1. **Entender o código**: Leia ARCHITECTURE.md
2. **Estender**: Adicione novas validações em validador.py
3. **Integrar**: Conecte a um banco de dados real
4. **Deploy**: Use Docker/Heroku para colocar online

---

**Aproveite o ABI! 🤖**
