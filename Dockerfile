# ==============================================================================
# FIAP Global Solution 2026/2 - Disruptive Architectures: IoT, IoB & Generative IA
# Dockerfile Multi-Stage Otimizado para Produção
# ==============================================================================

FROM python:3.11-slim

WORKDIR /app

# Variáveis de ambiente Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_PORT=8000 \
    APP_HOST=0.0.0.0

# Instalação de dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalação das dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Cópia do código-fonte e base de dados
COPY src/ ./src/
COPY data/ ./data/
COPY static/ ./static/
COPY scripts/ ./scripts/

# Treina e pré-aquecer os modelos e vetorizadores em tempo de build
RUN python scripts/generate_dataset.py

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
