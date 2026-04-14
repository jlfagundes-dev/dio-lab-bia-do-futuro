# Documentação do Agente

## Caso de Uso

### Problema
> Qual problema financeiro seu agente resolve?

 A maioria dos assistentes atuais é reativa, exigindo que o cliente vá até o app e faça perguntas específicas, sem antecipação de necessidades.

### Solução
> Como o agente resolve esse problema de forma proativa?

O agente atua diretamente no WhatsApp, canal já presente no dia a dia do cliente, eliminando a necessidade de acessar aplicativos bancários.

### Público-Alvo
> Quem vai usar esse agente?

- Clientes que utilizam WhatsApp como principal canal digital
- Clientes com baixa ou média organização financeira
- Pequenos empreendedores (PMEs) que precisam de visão rápida do caixa
- Clientes que não utilizam apps bancários com frequência

---

## Persona e Tom de Voz

### Nome do Agente
ABI (Assistente Bancario Inteligente)

### Personalidade
> Como o agente se comporta? (ex: consultivo, direto, educativo)

- Consultivo
- Educativo, ajudando o cliente a entender suas finanças
- Objetivo, evitando excesso de complexidade
- Não assume riscos ou faz promessas ou sugestões de investimento ou compras

### Tom de Comunicação
> Formal, informal, técnico, acessível?

- Acessível e claro (linguagem)
- Levemente informal (estilo WhatsApp)
- Sem jargão financeiro excessivo
- Didático quando necessário

### Exemplos de Linguagem
- Saudação: [ex: "Olá! Como posso ajudar com suas finanças hoje?"]
- Confirmação: [ex: "Entendi! Deixa eu verificar isso para você."]
- Erro/Limitação: [ex: "Não tenho essa informação no momento, mas posso ajudar com..."]

---

## Arquitetura

### Diagrama

```mermaid
graph TD
    A[Canal WhatsApp] -->|Texto ou audio| B[Orquestracao]
    B --> C[LLM]
    C --> D[Base de Conhecimento]
    D --> C
    C --> E[Validacao de Regras]
    E --> F[Resposta em texto ou audio]
    F --> A
```

### Componentes

| Componente | Descrição |
|------------|-----------|
| Canal WhatsApp | Meio de entrada das mensagens de texto ou áudio do cliente |
| Orquestração | Recebe a mensagem, encaminha para o LLM e coordena o fluxo |
| LLM | Interpreta a mensagem e gera a resposta com apoio do contexto |
| Base de Conhecimento | Dados estruturados e histórico usados como contexto |
| Validação de Regras | Aplica regras de negócio e controle de confiabilidade |
| Resposta | Retorno final enviado ao cliente em texto ou áudio pelo canal WhatsApp |

---

## Segurança e Anti-Alucinação

### Estratégias Adotadas

- [ ] Agente responde com base em dados estruturados e contexto do cliente
- [ ] Não inventar dados financeiros
- [ ] Quando não sabe, admite explicitamente
- [ ] Não realiza operações financeiras (ex: PIX)
- [ ] Logs e rastreabilidade das respostas

### Limitações Declaradas
> O que o agente NÃO faz?

- Não executa transações financeiras reais (ex: PIX, transferências)
- Não substitui aplicativos bancários oficiais
- Não acessa dados bancários reais
- Não fornece aconselhamento financeiro avançado ou regulado (ex: investimentos complexos)
- Não garante 100% de precisão sem dados estruturados confiáveis
- Não substitui um profissional qualificado
- Não acessa dados bancários sensíveis, como senhas, etc...