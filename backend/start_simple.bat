@echo off
set OPENAI_API_KEY=your-openai-api-key-here
set RAG_STORE=sqlite
set SQLITE_FILE=./data/fortes.db
set VECTOR_STORE_TYPE=chroma
set EMBEDDING_MODEL=text-embedding-3-small
set GENERATION_MODEL=gpt-4o-mini
set PROJECT_NAME=Fortes Eduction
set VERSION=1.0.0

echo Starting Fortes Eduction Backend...
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

