# Fortes Eduction - Quick Start Guide

## 🚀 Running the Application

### Easy Way (Recommended)
Just double-click: **`start_app.bat`**

This will:
- ✅ Start the backend on port 8000
- ✅ Start the frontend on port 3000/3001
- ✅ Open in 2 separate terminal windows
- ✅ Wait 5 seconds between starts for proper initialization

### Manual Way
If you prefer to start them separately:

1. **Start Backend**: Double-click `start_backend.bat`
2. **Wait 10 seconds** for backend to fully initialize
3. **Start Frontend**: Double-click `start_frontend.bat`

### Stopping the Application
Double-click: **`stop_app.bat`**

This will safely stop both frontend and backend.

---

## 🌐 Access Points

Once running:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Main UI |
| **Backend API** | http://localhost:8000 | REST API |
| **API Documentation** | http://localhost:8000/docs | Interactive Swagger docs |
| **Health Check** | http://localhost:8000/api/health | API health status |

---

## 📁 Project Structure

```
Fortes_Assesment/
├── backend/                 # FastAPI backend
│   ├── data/               # SQLite database & ChromaDB
│   ├── app/                # Application code
│   └── requirements.txt    # Python dependencies
├── frontend/               # Next.js frontend
│   ├── src/               # React components
│   └── package.json       # Node dependencies
├── start_app.bat          # 🎯 Main startup script
├── start_backend.bat      # Backend only
├── start_frontend.bat     # Frontend only
└── stop_app.bat           # Stop everything
```

---

## ⚙️ Configuration

### Environment Variables (Already Set in .bat files)

**Backend:**
- `OPENAI_API_KEY` - Your OpenAI API key
- `RAG_STORE=sqlite` - Database type
- `SQLITE_FILE=./data/fortes.db` - Database path
- `VECTOR_STORE_TYPE=chroma` - Vector database
- `EMBEDDING_MODEL=text-embedding-3-small`
- `GENERATION_MODEL=gpt-4o-mini`

**Frontend:**
- `NEXT_PUBLIC_API_URL=http://localhost:8000` - Backend API URL

---

## ✅ Features

1. **Knowledge Base Management**
   - Create multiple knowledge bases
   - Upload documents (PDF, TXT, MD, DOCX)
   - Automatic chunking and embedding

2. **RAG Chat**
   - Ask questions about your documents
   - Get AI responses with source citations
   - See document references and line numbers

3. **Guardrails**
   - PII redaction
   - Prompt injection detection
   - Hallucination detection

4. **API Keys**
   - Generate API keys for programmatic access
   - Use OpenAPI endpoints

---

## 🔧 Troubleshooting

### Backend won't start?
- Make sure Python 3.11+ is installed: `python --version`
- Install dependencies: `cd backend && pip install -r requirements.txt`
- Check port 8000 is not in use: `netstat -ano | findstr :8000`

### Frontend won't start?
- Make sure Node.js 18+ is installed: `node --version`
- Install dependencies: `cd frontend && npm install`
- Check port 3000 is not in use: `netstat -ano | findstr :3000`

### 404 Errors in Frontend?
1. Make sure backend is running first
2. Hard refresh browser: `Ctrl + Shift + R`
3. Check console for errors (F12)
4. Verify `NEXT_PUBLIC_API_URL=http://localhost:8000` is set

### Database Issues?
1. Stop the app: `stop_app.bat`
2. Delete database: `del backend\data\fortes.db*`
3. Restart: `start_app.bat`
4. Migrations will recreate everything

### CORS Errors?
- Make sure you're accessing frontend at http://localhost:3000 (not 127.0.0.1)
- Backend allows: localhost:3000, localhost:3001, localhost:3002

---

## 📝 First Time Setup

1. **Clone the repository** (you've already done this)

2. **Install Python dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Install Node dependencies:**
   ```bash
   cd frontend
   npm install
   ```

4. **Set your OpenAI API key:**
   - Edit `start_backend.bat`
   - Replace the `OPENAI_API_KEY` value with your actual key

5. **Run the app:**
   ```bash
   start_app.bat
   ```

6. **Open browser:** http://localhost:3000

7. **Create your first Knowledge Base!**

---

## 🎯 Quick Test

After starting the app:

1. Go to http://localhost:3000
2. Click "Knowledge Base" → "New Knowledge Base"
3. Create a KB called "Test"
4. Upload a document
5. Go to "Chat" → "Start New Chat"
6. Select your KB and ask a question

You should see:
- ✅ AI response with citations
- ✅ Source documents with line numbers
- ✅ Confidence scores
- ✅ Grounding indicators

---

## 📚 More Info

- Frontend: Next.js 14 + React + TailwindCSS
- Backend: FastAPI + SQLAlchemy + LangChain
- Database: SQLite (file-based, no server needed)
- Vector DB: ChromaDB (embedded, no server needed)
- LLM: OpenAI GPT-4o-mini
- Embeddings: OpenAI text-embedding-3-small

---

**Ready to go!** Just run `start_app.bat` and visit http://localhost:3000 🚀

