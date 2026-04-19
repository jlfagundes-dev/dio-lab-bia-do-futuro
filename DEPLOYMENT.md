# === DEPLOYMENT.md ===
# Guia de Deployment e Produção para o ABI

## 🚀 Opções de Deployment

### Opção 1: Streamlit Cloud (Mais fácil)

#### Passo 1: Prepare o repositório GitHub
```bash
# 1. Crie um repositório no GitHub
# 2. Faça push do código
git init
git add .
git commit -m "Initial commit: ABI Agent"
git push origin main
```

#### Passo 2: Deploy no Streamlit Cloud
1. Acesse https://streamlit.io/cloud
2. Clique em "Create app"
3. Selecione seu repositório GitHub
4. Configure:
   - Repository: seu repo
   - Branch: main
   - Main file path: src/app.py
5. Clique "Deploy"
6. Adicione a secret no Streamlit Cloud:
   - Vá em "Settings" → "Secrets"
   - Adicione: `API_KEY_GEMINI = sua_chave_aqui`

#### Resultado
- ✅ URL pública: https://seu-app-abi.streamlit.app
- ✅ Auto-deploy ao fazer push no GitHub
- ✅ SSL/HTTPS automático

### Opção 2: Heroku (Containerizado)

#### Passo 1: Crie Dockerfile
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copiar requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copiar código
COPY src/ ./src/
COPY data/ ./data/

# Expor porta
EXPOSE 8501

# Comando padrão
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### Passo 2: Crie heroku.yml
```yaml
# heroku.yml
build:
  docker:
    web: Dockerfile
run:
  web: streamlit run src/app.py --server.port=$PORT --server.address=0.0.0.0
```

#### Passo 3: Deploy
```bash
# Login no Heroku
heroku login

# Crie app
heroku create seu-app-abi

# Configure variável de ambiente
heroku config:set API_KEY_GEMINI=sua_chave

# Deploy
git push heroku main

# Ver logs
heroku logs --tail
```

#### Resultado
- ✅ URL: https://seu-app-abi.herokuapp.com
- ✅ Rodando em container
- ✅ Auto-restart em falhas

### Opção 3: Docker + AWS/GCP (Enterprise)

#### Passo 1: Build da imagem
```bash
docker build -t abi-agent:latest .
docker run -p 8501:8501 \
  -e API_KEY_GEMINI=sua_chave \
  abi-agent:latest
```

#### Passo 2: Push para registry
```bash
# AWS ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
docker tag abi-agent:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/abi-agent:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/abi-agent:latest
```

#### Passo 3: Deploy em ECS/EKS
- Use CloudFormation ou Terraform
- Configure load balancer
- Setup auto-scaling

### Opção 4: Digital Ocean App Platform

```bash
# 1. Conecte repositório GitHub
# 2. App Platform detecta Streamlit automaticamente
# 3. Configure ambiente:
API_KEY_GEMINI=sua_chave
# 4. Deploy automático
```

---

## 🔒 Segurança em Produção

### 1. Variáveis de Ambiente
```python
# ✅ Certo: Usar .env ou secrets
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY_GEMINI")

# ❌ Errado: Hardcoded
API_KEY = "abc123xyz"
```

### 2. Nunca commitar .env
```bash
# .gitignore
.env
.env.local
*.key
```

### 3. CORS (Cross-Origin)
```python
# Se expor como API
from streamlit.server.config import get_config_options

config = get_config_options()
config.server.enableCORS = False
```

### 4. Rate Limiting
```python
# Adicionar em infrastructure/gemini_service.py
from datetime import datetime, timedelta
import time

class RateLimitedGeminiService(GeminiService):
    def __init__(self, max_requests_per_minute=30):
        super().__init__()
        self.max_requests = max_requests_per_minute
        self.requests_in_minute = []
    
    def gerar_resposta(self, mensagem, contexto, system_prompt):
        # Limpar requests antigos
        now = datetime.now()
        self.requests_in_minute = [
            req_time for req_time in self.requests_in_minute
            if now - req_time < timedelta(minutes=1)
        ]
        
        # Verificar limite
        if len(self.requests_in_minute) >= self.max_requests:
            raise Exception("Rate limit exceeded")
        
        self.requests_in_minute.append(now)
        return super().gerar_resposta(mensagem, contexto, system_prompt)
```

---

## 📊 Monitoramento

### Logs Estruturados
```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        return json.dumps(log_obj)

# Usar em produção
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
```

### Métricas Importantes
```python
# Adicionar tracking
import time
from functools import wraps

def rastrear_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        inicio = time.time()
        try:
            resultado = func(*args, **kwargs)
            duracao = time.time() - inicio
            logger.info(f"{func.__name__} levou {duracao:.2f}s")
            return resultado
        except Exception as e:
            logger.error(f"{func.__name__} falhou em {time.time() - inicio:.2f}s")
            raise
    return wrapper

@rastrear_performance
def processar_mensagem(msg):
    # ...
    pass
```

### Health Check
```python
# Adicionar endpoint de saúde
from streamlit import write

def health_check():
    # Verificar dependências
    try:
        gemini = GeminiService()
        loader = DataLoader()
        cliente = loader.carregar_cliente()
        return {"status": "healthy", "timestamp": datetime.now()}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

---

## 🔄 CI/CD Pipeline (GitHub Actions)

Criar `.github/workflows/deploy.yml`:

```yaml
name: Deploy ABI

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt pytest pytest-cov
      
      - name: Run tests
        run: |
          pytest src/tests/ --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to Streamlit Cloud
        run: |
          # Trigger redeployment (if linked to GitHub)
          # Ou push manualmente para Heroku
          git push heroku main
        env:
          HEROKU_API_KEY: ${{ secrets.HEROKU_API_KEY }}
```

---

## 🎯 Checklist de Deployment

- [ ] Testes passando (100% em domain)
- [ ] Não há secrets no repositório (.env não commited)
- [ ] Arquivo requirements.txt atualizado
- [ ] README.md e QUICK_START.md presentes
- [ ] ARCHITECTURE.md documentado
- [ ] Logs configurados corretamente
- [ ] Error handling implementado
- [ ] Validação de dados (ValidadorResposta)
- [ ] Rate limiting configurado
- [ ] Monitoramento em produção
- [ ] Backup automático de dados
- [ ] SSL/HTTPS ativado
- [ ] CORS configurado corretamente
- [ ] Database backups (se aplicável)
- [ ] Disaster recovery plan documentado

---

## 📈 Escala em Produção

### Problema: Múltiplos usuários simultâneos

#### Solução 1: Load Balancer
```yaml
# Nginx config (nginx.conf)
upstream streamlit_backend {
    server localhost:8501;
    server localhost:8502;
    server localhost:8503;
}

server {
    listen 80;
    location / {
        proxy_pass http://streamlit_backend;
        proxy_set_header Host $host;
    }
}
```

#### Solução 2: Caching de Respostas
```python
# Adicionar em infrastructure/gemini_service.py
from functools import lru_cache

class CachedGeminiService(GeminiService):
    @lru_cache(maxsize=1000)
    def gerar_resposta(self, mensagem, contexto, system_prompt):
        # Já calcula hash de argumentos
        return super().gerar_resposta(mensagem, contexto, system_prompt)
```

#### Solução 3: Message Queue (Redis)
```python
# Para processamento assíncrono de mensagens pesadas
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379)

def processar_mensagem_async(msg):
    # Enfilar processamento
    redis_client.rpush("mensagens_fila", json.dumps(msg))
    return {"status": "processing", "queue_position": redis_client.llen("mensagens_fila")}
```

---

## 💰 Estimativa de Custos

| Serviço | Plano Grátis | Profissional | Observações |
|---------|-------------|-------------|-------------|
| Streamlit Cloud | ✅ Sim | - | Melhor para começar |
| Heroku | ✅ 1000 horas/mês | $7+/mês | Depois foi descontinuado |
| Digital Ocean | ✅ $5/mês | - | Boa relação custo/benefício |
| AWS Lightsail | - | $3.50+/mês | Escalável |
| Google Cloud Run | ✅ 2M requisições/mês | - | Pay-as-you-go |
| Gemini API | ✅ 60 req/min | - | Sempre incluso |

---

## 🔧 Troubleshooting

### "Memory exceeded"
```bash
# Aumentar limite
heroku config:set WEB_CONCURRENCY=1
heroku ps:scale web=1
```

### "Timeout na API do Gemini"
```python
# Adicionar retry logic
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential())
def gerar_resposta_com_retry(self, mensagem, contexto, system_prompt):
    return super().gerar_resposta(mensagem, contexto, system_prompt)
```

---

**Parabéns! ABI está pronto para o mundo! 🚀**
