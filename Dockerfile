# Use uma imagem Python leve baseada no Debian
FROM python:3.11-slim

# Variáveis de ambiente para evitar prompts durante instalação
ENV DEBIAN_FRONTEND=noninteractive

# Instala dependências do sistema e o Firefox + Geckodriver
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    unzip \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libasound2 \
    libnss3 \
    libxss1 \
    libxtst6 \
    fonts-liberation \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Instala o Firefox ESR
RUN apt-get update && apt-get install -y firefox-esr

# Instala o Geckodriver
RUN GECKODRIVER_VERSION=0.34.0 && \
    wget -q "https://github.com/mozilla/geckodriver/releases/download/v${GECKODRIVER_VERSION}/geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz" && \
    tar -xzf "geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz" -C /usr/local/bin && \
    rm "geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz"

# Cria diretório da aplicação
WORKDIR /app

# Copia os arquivos do projeto
COPY . /app

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Comando padrão para rodar o script principal
CMD ["python", "src/main.py"]
