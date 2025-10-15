@echo off
cd backend
echo ========================================
echo Starting Fortes Education Backend
echo ========================================
echo.
echo Port: 8000
echo Database: SQLite (./data/fortes.db)
echo Vector Store: ChromaDB (local)
echo Guest Mode: ENABLED (No auth required)
echo CORS: localhost:3000, 3001, 3002
echo.

set OPENAI_API_KEY=your-openai-api-key-here
set RAG_STORE=sqlite
set SQLITE_FILE=./data/fortes.db
set VECTOR_STORE_TYPE=chroma
set EMBEDDING_MODEL=text-embedding-3-small
set GENERATION_MODEL=gpt-4o-mini
set PROJECT_NAME=Fortes Education
set VERSION=1.0.0

echo Starting server (migrations will run automatically)...
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

