# 1. Imagem base leve do Python
FROM python:3.11-slim

# 2. Define o diretório de trabalho dentro do container
WORKDIR /app

# 3. Instala dependências do sistema necessárias para o driver do Postgres (psycopg2)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Copia o arquivo de dependências e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copia todos os seus arquivos (app.py, database.py, ai_service.py)
COPY . .

# 6. Expõe a porta padrão do Streamlit
EXPOSE 8501

# 7. Comando para rodar a aplicação
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]