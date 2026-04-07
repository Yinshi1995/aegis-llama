FROM python:3.12-slim

# System dependencies: Tesseract OCR + language packs, Poppler utils
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-ukr \
        tesseract-ocr-rus \
        tesseract-ocr-eng \
        poppler-utils && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Ensure target directories exist even if COPY sources are empty
RUN mkdir -p ./app ./scripts ./knowledge_base

COPY requirements.txt* ./
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

COPY . .


ENV GRADIO_SERVER_NAME=0.0.0.0
EXPOSE 7860

CMD ["sh", "-c", "GRADIO_SERVER_PORT=${PORT:-7860} exec python -m app.main"]
