# Fortes Eduction - Quick Start

## System Status ✅

- **Frontend**: http://localhost:3001 (or 3000)
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: SQLite at `backend/data/fortes.db`

## Starting the Application

### Backend (Port 8000)
```powershell
cd backend
$env:OPENAI_API_KEY='your-key-here'
$env:RAG_STORE='sqlite'
$env:SQLITE_FILE='./data/fortes.db'
$env:VECTOR_STORE_TYPE='chroma'
$env:EMBEDDING_MODEL='text-embedding-3-small'
$env:GENERATION_MODEL='gpt-4o-mini'
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend (Port 3000/3001)
```powershell
cd frontend
$env:NEXT_PUBLIC_API_URL='http://localhost:8000'
npm run dev
```

## Features Verified

✅ **Knowledge Base Creation** - POST /api/knowledge-bases  
✅ **Document Upload** - Chunking, embedding, and storage  
✅ **Chat with Citations** - Streaming responses with source attribution  
✅ **Guardrails** - PII redaction, prompt injection detection  
✅ **Grounding** - Hallucination detection and confidence scoring  

## Architecture

- **Frontend**: Next.js 14 (React, TailwindCSS, TypeScript)
- **Backend**: FastAPI (Python 3.13)
- **Database**: SQLite (local file-based)
- **Vector Store**: ChromaDB (local persistent storage)
- **LLM**: OpenAI GPT-4o-mini
- **Embeddings**: OpenAI text-embedding-3-small

## CORS Configuration

The backend allows requests from:
- http://localhost:3000
- http://localhost:3001  
- http://localhost:3002

## Database Migrations

Migrations run automatically on backend startup. The database schema includes:
- users, knowledge_bases, documents, document_chunks
- chats, messages, processing_tasks, api_keys

## Troubleshooting

**404 on /api endpoints?**
- Ensure `NEXT_PUBLIC_API_URL=http://localhost:8000` is set
- Hard refresh browser (Ctrl+Shift+R)
- Check backend is running on port 8000

**Database errors?**
- Delete `backend/data/fortes.db*` and restart backend
- Migrations will recreate all tables

**CORS errors?**
- Check frontend port matches CORS whitelist in backend/app/main.py
- Restart backend after changing CORS settings

**"Not Found" errors?**
- Verify you're using correct endpoints: `/api/knowledge-bases` (plural) and `/api/chats` (plural)

