# === Ponto de Entrada Alternativo ===
# Execute com: python main.py
# Oferece uma interface CLI simples para testar o agente

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from utils import configurar_logging
from infrastructure.data_loader import DataLoader
from infrastructure.gemini_service import GeminiService
from infrastructure.validador import ValidadorResposta
from application.services import AgenteService
from application.dto import MensagemCliente


logger = configurar_logging("ABI-CLI")


def main():
    """Interface CLI para o ABI."""
    
    print("\n" + "=" * 60)
    print("🤖  ABI - Assistente Bancário Inteligente")
    print("=" * 60 + "\n")
    
    print("Inicializando serviços...\n")
    
    try:
        # Inicializar componentes (Injeção de Dependência)
        base_dados = DataLoader()
        llm_service = GeminiService()
        validador = ValidadorResposta()
        agente = AgenteService(
            llm_service=llm_service,
            base_dados=base_dados,
            validador=validador
        )
        
        # Carregar dados do cliente
        cliente = base_dados.carregar_cliente()
        
        print(f"✅ Bem-vindo, {cliente.nome}!")
        print(f"   Perfil: {cliente.perfil_investidor}")
        print(f"   Saúde Financeira: {cliente.calcular_saude_financeira()}")
        print(f"   Reserva de Emergência: R$ {cliente.reserva_emergencia_atual:,.2f}\n")
        
        # Loop de conversação
        print("Você pode fazer perguntas (digite 'sair' para encerrar):\n")
        
        while True:
            pergunta = input("👤 Você: ").strip()
            
            if pergunta.lower() in ['sair', 'quit', 'exit', 'q']:
                print("\n👋 Até logo!")
                break
            
            if not pergunta:
                print("⚠️  Digite uma pergunta...\n")
                continue
            
            # Processar mensagem
            print("\n🤖 ABI: ", end="", flush=True)
            
            try:
                msg = MensagemCliente(texto=pergunta)
                resposta = agente.processar_mensagem(msg, "default")
                
                print(resposta.mensagem)
                print(f"   [Confiança: {resposta.confianca:.0%}]\n")
                
            except Exception as e:
                print(f"❌ Erro ao processar: {str(e)}\n")
                logger.error(f"Erro: {str(e)}")
    
    except Exception as e:
        print(f"❌ Erro ao inicializar: {str(e)}")
        logger.error(f"Erro fatal: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
