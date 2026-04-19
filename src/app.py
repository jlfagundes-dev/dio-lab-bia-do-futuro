# === Aplicação Streamlit - ABI ===
# Interface web interativa para o Agente Bancário Inteligente
# Execute com: streamlit run app.py

import streamlit as st
import sys
from pathlib import Path

# Adicionar src ao path para importações
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from utils import configurar_logging
from infrastructure.data_loader import DataLoader
from infrastructure.gemini_service import GeminiService
from infrastructure.validador import ValidadorResposta
from application.services import AgenteService
from application.dto import MensagemCliente


# === Configuração de Logging ===
logger = configurar_logging("ABI")


# === Configuração da Página Streamlit ===
st.set_page_config(
    page_title=settings.APP_TITLE,
    page_icon=settings.APP_ICON,
    layout="centered",
    initial_sidebar_state="expanded"
)


# === Estilo customizado ===
st.markdown("""
<style>
    .header-main {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 30px;
    }
    .response-box {
        background-color: #f0f2f6;
        border-left: 4px solid #1f77b4;
        padding: 15px;
        border-radius: 5px;
        margin: 20px 0;
    }
    .confidence-badge {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
    }
    .confidence-high {
        background-color: #90EE90;
        color: #333;
    }
    .confidence-medium {
        background-color: #FFD700;
        color: #333;
    }
    .confidence-low {
        background-color: #FFB6C1;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)


# === Inicializar Session State ===
@st.cache_resource
def inicializar_servicos():
    """
    Inicializa os serviços da aplicação usando cache do Streamlit.
    Executa apenas uma vez por sessão.
    """
    
    logger.info("Inicializando serviços da aplicação...")
    
    try:
        # Injetar dependências - padrão de Design Pattern "Dependency Injection"
        base_dados = DataLoader()
        llm_service = GeminiService()
        validador = ValidadorResposta()
        
        # Criar serviço do agente
        agente = AgenteService(
            llm_service=llm_service,
            base_dados=base_dados,
            validador=validador
        )
        
        logger.info("Serviços inicializados com sucesso!")
        return agente, base_dados
        
    except Exception as e:
        logger.error(f"Erro ao inicializar serviços: {str(e)}")
        st.error(f"❌ Erro ao inicializar aplicação: {str(e)}")
        st.stop()


# === Função para formatar a confiança ===
def obter_badge_confianca(confianca: float) -> str:
    """Retorna HTML de badge com cor baseada no nível de confiança."""
    
    if confianca >= 0.8:
        classe = "confidence-high"
        nivel = "Alta"
    elif confianca >= 0.5:
        classe = "confidence-medium"
        nivel = "Média"
    else:
        classe = "confidence-low"
        nivel = "Baixa"
    
    return f'<span class="confidence-badge {classe}">{nivel} ({confianca:.0%})</span>'


# === Interface Principal ===
def main():
    """Função principal da aplicação Streamlit."""
    
    # Header
    col1, col2, col3 = st.columns(3)
    with col2:
        st.markdown("# 🤖 ABI")
        st.markdown("*Assistente Bancário Inteligente*")
    
    # Barra lateral com informações
    with st.sidebar:
        st.header("ℹ️ Informações")
        st.write("""
        **ABI** é um assistente bancário inteligente que ajuda você a:
        
        ✅ Entender suas finanças  
        ✅ Analisar suas transações  
        ✅ Explorar produtos financeiros  
        ✅ Planejar metas financeiras  
        
        ---
        
        **Como usar:**
        1. Selecione seu perfil
        2. Faça uma pergunta
        3. Receba uma resposta personalizada
        
        ---
        
        ⚠️ **Limites:**
        - Não executa operações financeiras
        - Não substitui apps oficiais
        - Não aconselhamento regulado
        """)
        
        st.divider()
        
        st.subheader("⚙️ Configurações")
        temperatura = st.slider(
            "Criatividade do LLM",
            min_value=0.0,
            max_value=1.0,
            value=settings.LLM_TEMPERATURE,
            step=0.1,
            help="Menor = mais previsível, Maior = mais criativo"
        )
    
    # Inicializar serviços
    agente, base_dados = inicializar_servicos()
    
    # Carregar dados do cliente
    try:
        cliente = base_dados.carregar_cliente()
        
        # Mostrar perfil do cliente
        with st.expander(f"👤 Perfil do Cliente: {cliente.nome}", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Idade", cliente.idade)
                st.metric("Perfil", cliente.perfil_investidor)
            
            with col2:
                st.metric("Renda Mensal", f"R$ {cliente.renda_mensal:,.2f}")
                st.metric("Patrimônio Total", f"R$ {cliente.patrimonio_total:,.2f}")
            
            with col3:
                saude = cliente.calcular_saude_financeira()
                meses = cliente.obter_meses_reserva()
                st.metric("Saúde Financeira", saude)
                st.metric("Meses Cobertos", f"{meses:.1f}")
            
            st.write(f"**Objetivo Principal:** {cliente.objetivo_principal}")
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar cliente: {str(e)}")
        logger.error(f"Erro ao carregar cliente: {str(e)}")
        st.stop()
    
    # Área de entrada de mensagem
    st.divider()
    
    st.subheader("💬 Sua Pergunta")
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        mensagem_usuario = st.text_input(
            "Digite sua pergunta sobre suas finanças:",
            placeholder="Ex: Qual é meu melhor produto para investir agora?",
            label_visibility="collapsed"
        )
    
    with col2:
        botao_enviar = st.button("Enviar ✈️", use_container_width=True)
    
    # Processar mensagem quando enviada
    if botao_enviar and mensagem_usuario.strip():
        
        # Mostrar status de processamento
        with st.spinner("🔄 ABI está analisando sua pergunta..."):
            
            try:
                # Criar DTO da mensagem
                msg_cliente = MensagemCliente(
                    texto=mensagem_usuario,
                    tipo="texto"
                )
                
                # Processar mensagem através do agente
                resposta = agente.processar_mensagem(msg_cliente, "default")
                
                # Exibir resposta
                st.markdown("---")
                st.subheader("📝 Resposta da ABI")
                
                with st.container():
                    st.markdown(
                        f'<div class="response-box">{resposta.mensagem}</div>',
                        unsafe_allow_html=True
                    )
                
                # Mostrar confiança
                col1, col2, col3 = st.columns([2, 2, 2])
                
                with col1:
                    st.markdown(
                        "**Confiança:**  " + 
                        obter_badge_confianca(resposta.confianca),
                        unsafe_allow_html=True
                    )
                
                with col2:
                    if resposta.requer_confirmacao:
                        st.warning("⚠️ Requer verificação")
                
                with col3:
                    st.info(f"🕐 {resposta.confianca:.0%} confiável")
                
                # Log da interação
                logger.info(
                    f"Pergunta: {mensagem_usuario[:100]} | "
                    f"Confiança: {resposta.confianca:.2f}"
                )
                
            except Exception as e:
                logger.error(f"Erro ao processar mensagem: {str(e)}")
                st.error(f"❌ Erro ao processar sua pergunta: {str(e)}")
    
    elif botao_enviar:
        st.warning("⚠️ Digite uma pergunta antes de enviar!")
    
    # Sugestões de perguntas
    st.divider()
    st.subheader("💡 Perguntas Sugeridas")
    
    sugestoes = [
        "Como está minha saúde financeira?",
        "Quais produtos você recomenda para mim?",
        "Qual é o status das minhas metas?",
        "Como fiz meus gastos no mês passado?",
    ]
    
    col1, col2 = st.columns(2)
    
    for idx, sugestao in enumerate(sugestoes):
        if idx % 2 == 0:
            if col1.button(sugestao, use_container_width=True, key=f"sugestao_{idx}"):
                st.session_state.mensagem = sugestao
        else:
            if col2.button(sugestao, use_container_width=True, key=f"sugestao_{idx}"):
                st.session_state.mensagem = sugestao
    
    # Footer
    st.divider()
    st.caption(
        "🏦 ABI v1.0 | Assistente Bancário Inteligente | "
        "Desenvolvido para Bradesco-DIO"
    )


if __name__ == "__main__":
    main()



