# === Configurações da Aplicação ===
# Arquivo centralizado para variáveis de ambiente e configurações do projeto

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """
    Classe de configuração que centraliza todas as variáveis de ambiente.
    Segue o padrão de configuração por ambiente (desenvolvimento, staging, produção).
    """
    
    # === API Gemini ===
    GEMINI_API_KEY: str = os.getenv("API_KEY_GEMINI", "")
    GEMINI_MODEL: str = "gemini-2.0-flash"
    
    # === Caminhos de Dados ===
    DATA_PATH: str = os.path.join(os.path.dirname(__file__), "..", "data")
    PERFIL_INVESTIDOR_PATH: str = os.path.join(DATA_PATH, "perfil_investidor.json")
    PRODUTOS_FINANCEIROS_PATH: str = os.path.join(DATA_PATH, "produtos_financeiros.json")
    TRANSACOES_PATH: str = os.path.join(DATA_PATH, "transacoes.csv")
    ATENDIMENTOS_PATH: str = os.path.join(DATA_PATH, "historico_atendimento.csv")
    
    # === Streamlit Config ===
    APP_TITLE: str = "ABI - Assistente Bancário Inteligente"
    APP_ICON: str = "🤖"
    
    # === Temperatura do LLM (criatividade vs determinismo) ===
    LLM_TEMPERATURE: float = 0.7
    
    # === Tamanho máximo do contexto enviado para o LLM ===
    MAX_CONTEXT_LENGTH: int = 3000


settings = Settings()
