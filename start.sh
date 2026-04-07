#!/bin/sh
set -e

echo "Starting Ollama server..."
ollama serve &
OLLAMA_PID=$!

# Wait until Ollama is ready
echo "Waiting for Ollama to be ready..."
for i in $(seq 1 30); do
    if curl -sf http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "Ollama is ready."
        break
    fi
    sleep 1
done

echo "Starting application on port ${PORT:-7860}..."
exec python -m app.main
