# === Exemplos de Testes Unitários ===
# Como testar a arquitetura com Dependency Injection e Mocks

import pytest
from unittest.mock import Mock, MagicMock
from typing import Dict, Any

# Imports do projeto (assumindo que está no PYTHONPATH)
# from domain.entities import Cliente, Resposta
# from domain.interfaces import ILLMService, IBaseDados, IValidador
# from application.services import AgenteService
# from application.dto import MensagemCliente, RespostaAgente


# === Fixtures (Setup reutilizável) ===

@pytest.fixture
def cliente_mock():
    """Cria um cliente mock para testes."""
    from domain.entities import Cliente, Meta
    
    return Cliente(
        nome="João Silva",
        idade=32,
        profissao="Analista de Sistemas",
        renda_mensal=5000.0,
        perfil_investidor="moderado",
        objetivo_principal="Construir reserva",
        patrimonio_total=15000.0,
        reserva_emergencia_atual=10000.0,
        aceita_risco=False,
        metas=[],
        transacoes_recentes=[]
    )


@pytest.fixture
def llm_service_mock():
    """Mock do serviço de LLM."""
    mock = Mock()
    mock.gerar_resposta = Mock(return_value="Sua saúde financeira está boa!")
    return mock


@pytest.fixture
def base_dados_mock(cliente_mock):
    """Mock da base de dados."""
    from domain.entities import ProdutoFinanceiro
    
    mock = Mock()
    mock.carregar_cliente = Mock(return_value=cliente_mock)
    mock.carregar_produtos = Mock(return_value=[
        ProdutoFinanceiro(
            nome="Tesouro Selic",
            categoria="renda_fixa",
            risco="baixo",
            rentabilidade="100% da Selic",
            aporte_minimo=30.0,
            indicado_para="Iniciantes"
        )
    ])
    return mock


@pytest.fixture
def validador_mock():
    """Mock do validador."""
    from domain.entities import Resposta
    
    mock = Mock()
    mock.validar_resposta = Mock(
        return_value=Resposta(
            conteudo="Sua saúde financeira está boa!",
            confianca=0.95,
            requer_confirmacao=False,
            tags=[]
        )
    )
    return mock


# === Testes de AgenteService ===

class TestAgenteService:
    """Testes do serviço principal do agente."""
    
    def test_processar_mensagem_sucesso(
        self,
        llm_service_mock,
        base_dados_mock,
        validador_mock
    ):
        """Testa processamento bem-sucedido de uma mensagem."""
        
        from application.services import AgenteService
        from application.dto import MensagemCliente
        
        # Arrange (Preparar)
        agente = AgenteService(
            llm_service=llm_service_mock,
            base_dados=base_dados_mock,
            validador=validador_mock
        )
        
        msg = MensagemCliente(
            texto="Como está minha saúde financeira?",
            tipo="texto"
        )
        
        # Act (Agir)
        resposta = agente.processar_mensagem(msg, "cliente_1")
        
        # Assert (Afirmar)
        assert resposta.confianca > 0
        assert len(resposta.mensagem) > 0
        assert llm_service_mock.gerar_resposta.called
        assert base_dados_mock.carregar_cliente.called
        assert validador_mock.validar_resposta.called
    
    def test_processar_mensagem_erro_carregamento_cliente(
        self,
        llm_service_mock,
        validador_mock
    ):
        """Testa tratamento de erro ao carregar cliente."""
        
        from application.services import AgenteService
        from application.dto import MensagemCliente
        
        # Arrange
        base_dados_mock = Mock()
        base_dados_mock.carregar_cliente = Mock(
            side_effect=Exception("Erro ao carregar cliente")
        )
        
        agente = AgenteService(
            llm_service=llm_service_mock,
            base_dados=base_dados_mock,
            validador=validador_mock
        )
        
        msg = MensagemCliente(texto="Teste", tipo="texto")
        
        # Act
        resposta = agente.processar_mensagem(msg, "cliente_1")
        
        # Assert - Deve retornar erro gracioso
        assert resposta.confianca == 0.0
        assert "erro" in resposta.mensagem.lower()


# === Testes de ValidadorResposta ===

class TestValidadorResposta:
    """Testes do validador de respostas."""
    
    def test_valida_resposta_normal(self):
        """Testa validação de resposta normal."""
        
        from infrastructure.validador import ValidadorResposta
        
        # Arrange
        validador = ValidadorResposta()
        resposta = "Sua saúde financeira está boa!"
        contexto = {}
        
        # Act
        resultado = validador.validar_resposta(resposta, contexto)
        
        # Assert
        assert resultado.confianca >= 0.7
        assert len(resultado.tags) == 0
    
    def test_rejeita_promessa_proibida(self):
        """Testa que promessas proibidas reduzem confiança."""
        
        from infrastructure.validador import ValidadorResposta
        
        # Arrange
        validador = ValidadorResposta()
        resposta = "Garanto que você ganhará 100% de lucro com esse produto!"
        contexto = {}
        
        # Act
        resultado = validador.validar_resposta(resposta, contexto)
        
        # Assert
        assert resultado.confianca < 0.8
        assert "promessa_proibida" in resultado.tags
        assert resultado.requer_confirmacao
    
    def test_rejeita_operacao_proibida(self):
        """Testa que operações proibidas são detectadas."""
        
        from infrastructure.validador import ValidadorResposta
        
        # Arrange
        validador = ValidadorResposta()
        resposta = "Vou fazer um PIX para você agora!"
        contexto = {}
        
        # Act
        resultado = validador.validar_resposta(resposta, contexto)
        
        # Assert
        assert resultado.confianca < 0.7
        assert "operacao_proibida" in resultado.tags
    
    def test_penaliza_resposta_especulativa(self):
        """Testa que respostas especulativas demais são penalizadas."""
        
        from infrastructure.validador import ValidadorResposta
        
        # Arrange
        validador = ValidadorResposta()
        resposta = (
            "Acredito que provavelmente talvez você pudesse "
            "supostamente investir em algo que pode dar retorno"
        )
        contexto = {}
        
        # Act
        resultado = validador.validar_resposta(resposta, contexto)
        
        # Assert
        assert resultado.confianca < 0.7
        assert "especulativa" in resultado.tags
    
    def test_valida_negacao_corretamente(self):
        """Testa que negações não são penalizadas."""
        
        from infrastructure.validador import ValidadorResposta
        
        # Arrange
        validador = ValidadorResposta()
        resposta = "Não posso fazer um PIX porque isso não é permitido"
        contexto = {}
        
        # Act
        resultado = validador.validar_resposta(resposta, contexto)
        
        # Assert - Negação não deve penalizar
        assert resultado.confianca >= 0.7
        assert "operacao_proibida" not in resultado.tags


# === Testes de DataLoader ===

class TestDataLoader:
    """Testes do carregador de dados."""
    
    def test_carregar_cliente_existe(self):
        """Testa carregamento de cliente existente."""
        
        from infrastructure.data_loader import DataLoader
        
        # Arrange
        loader = DataLoader()
        
        # Act
        cliente = loader.carregar_cliente("default")
        
        # Assert
        assert cliente is not None
        assert cliente.nome == "João Silva"
        assert cliente.idade == 32
        assert cliente.perfil_investidor == "moderado"
    
    def test_carregar_produtos(self):
        """Testa carregamento de produtos financeiros."""
        
        from infrastructure.data_loader import DataLoader
        
        # Arrange
        loader = DataLoader()
        
        # Act
        produtos = loader.carregar_produtos()
        
        # Assert
        assert len(produtos) > 0
        assert produtos[0].nome is not None
        assert produtos[0].categoria is not None


# === Testes de Entidades ===

class TestEntidades:
    """Testes das entidades de domínio."""
    
    def test_cliente_calcula_saude_financeira_boa(self):
        """Testa cálculo de saúde financeira boa."""
        
        from domain.entities import Cliente
        
        # Arrange - Cliente com reserva >= 3 meses
        cliente = Cliente(
            nome="João",
            idade=30,
            profissao="Dev",
            renda_mensal=5000.0,
            perfil_investidor="moderado",
            objetivo_principal="Investir",
            patrimonio_total=20000.0,
            reserva_emergencia_atual=15000.0,  # 3 meses
            aceita_risco=True
        )
        
        # Act
        saude = cliente.calcular_saude_financeira()
        
        # Assert
        assert saude == "Boa"
    
    def test_cliente_calcula_saude_financeira_fragil(self):
        """Testa cálculo de saúde financeira frágil."""
        
        from domain.entities import Cliente
        
        # Arrange - Cliente com reserva < 1 mês
        cliente = Cliente(
            nome="João",
            idade=30,
            profissao="Dev",
            renda_mensal=5000.0,
            perfil_investidor="moderado",
            objetivo_principal="Investir",
            patrimonio_total=2000.0,
            reserva_emergencia_atual=1000.0,  # 0.2 meses
            aceita_risco=False
        )
        
        # Act
        saude = cliente.calcular_saude_financeira()
        
        # Assert
        assert saude == "Frágil"
    
    def test_cliente_obtem_meses_reserva(self):
        """Testa cálculo de meses de cobertura da reserva."""
        
        from domain.entities import Cliente
        
        # Arrange
        cliente = Cliente(
            nome="João",
            idade=30,
            profissao="Dev",
            renda_mensal=5000.0,
            perfil_investidor="moderado",
            objetivo_principal="Investir",
            patrimonio_total=20000.0,
            reserva_emergencia_atual=15000.0,
            aceita_risco=True
        )
        
        # Act
        meses = cliente.obter_meses_reserva()
        
        # Assert
        assert meses == 3.0


# === Como Executar os Testes ===

"""
INSTRUÇÕES:

1. Instale pytest:
   pip install pytest pytest-mock

2. No terminal, navegue até o diretório do projeto:
   cd src

3. Execute os testes:
   pytest tests/test_examples.py -v

   Flags úteis:
   -v          : Verbose (mais detalhes)
   -s          : Show print statements
   --tb=short  : Traceback curto
   -k "pattern": Executar apenas testes que correspondem ao padrão
   
   Exemplos:
   pytest tests/test_examples.py::TestValidadorResposta -v
   pytest tests/test_examples.py -k "promessa" -v

4. Ver cobertura de testes:
   pip install pytest-cov
   pytest tests/ --cov=. --cov-report=html

ESTRUTURA RECOMENDADA:

   src/
   ├── tests/
   │   ├── __init__.py
   │   ├── test_agente_service.py
   │   ├── test_validador.py
   │   ├── test_data_loader.py
   │   ├── test_entities.py
   │   └── conftest.py  (Fixtures compartilhadas)
   ├── domain/
   ├── application/
   ├── infrastructure/
   └── app.py

PADRÃO AAA (Arrange-Act-Assert):

   def test_algo():
       # Arrange (Preparar dados e mocks)
       mock_servico = Mock()
       
       # Act (Executar a ação)
       resultado = funcao_testada(mock_servico)
       
       # Assert (Verificar resultado)
       assert resultado == esperado

USANDO MOCKS:

   from unittest.mock import Mock, patch
   
   # Mock simples
   mock_llm = Mock()
   mock_llm.gerar_resposta.return_value = "Resposta"
   
   # Verificar chamadas
   assert mock_llm.gerar_resposta.called
   assert mock_llm.gerar_resposta.call_count == 1
   mock_llm.gerar_resposta.assert_called_once()
   
   # Mock com erro
   mock_llm.gerar_resposta.side_effect = Exception("Erro!")
"""
