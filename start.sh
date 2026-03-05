#!/bin/bash
# KakaoTalk CS Chatbot - Startup Script
# Usage: ./start.sh

set -e
cd "$(dirname "$0")"
source .venv/bin/activate

# Ensure Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "Starting Ollama..."
    /Applications/Ollama.app/Contents/Resources/ollama serve &
    sleep 3
fi

# Initialize DB if not exists
python -c "
import os
from app.database import DB_PATH, init_db, seed_sample_orders
if not os.path.exists(DB_PATH):
    init_db()
    seed_sample_orders()
    print('Database initialized')
"

# Ingest data if chroma_db is empty
python -c "
import os
if not os.listdir('chroma_db'):
    from app.ingest import load_documents, create_vectorstore
    docs = load_documents('data/')
    create_vectorstore(docs)
    print('Vectorstore created')
"

echo "Starting FastAPI server on port 8000..."
uvicorn app.main:app --host 0.0.0.0 --port 8000
