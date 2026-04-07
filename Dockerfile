FROM ollama/ollama:latest AS ollama-base

FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-ukr \
        tesseract-ocr-rus \
        tesseract-ocr-eng \
        poppler-utils \
        curl && \
    rm -rf /var/lib/apt/lists/*

# Copy Ollama binary from the official image
COPY --from=ollama-base /bin/ollama /usr/local/bin/ollama

WORKDIR /app

RUN mkdir -p ./app ./scripts ./knowledge_base

COPY requirements.txt* ./
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Pre-pull models at build time
RUN ollama serve & \
    sleep 5 && \
    ollama pull qwen2.5:1.5b && \
    ollama pull nomic-embed-text && \
    pkill ollama || true

COPY . .
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 7860

CMD ["/app/start.sh"]
