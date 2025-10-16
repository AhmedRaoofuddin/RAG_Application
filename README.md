# Fortes Education - Advanced RAG Q&A System

> Intelligent. Grounded. Safe. 🚀

A production-ready RAG (Retrieval Augmented Generation) system with built-in guardrails, attribution, and hallucination detection.

**Repository:** https://github.com/AhmedRaoofuddin/RAG_Application

## 🆕 Latest Updates

✅ **Chat now queries ALL documents in knowledge base** (not limited to single document)  
✅ **Evaluation & test report generated** - See `eval_report.json` for metrics  
✅ **Docker support added** - Simple one-command deployment with `docker-compose`  

📖 See [`FIXES_APPLIED.md`](./FIXES_APPLIED.md) for details  
🐳 See [`DOCKER_SETUP.md`](./DOCKER_SETUP.md) for Docker instructions

## ✨ Features

- 📚 **Knowledge Base Management** - Create and manage multiple knowledge bases
- 📄 **Document Upload** - Support for PDF, TXT, MD, DOCX
- 💬 **AI Chat** - Ask questions and get answers with source citations
- 🔒 **Guardrails** - PII redaction, prompt injection detection, hallucination detection
- 🎯 **Attribution** - See exact document references with line numbers and similarity scores
- 🔑 **API Keys** - Generate keys for programmatic access
- 🎨 **Modern UI** - Clean, responsive interface built with Next.js and TailwindCSS

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **OpenAI API Key** - [Get one](https://platform.openai.com/api-keys)

### Installation

1. **Install Backend Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Install Frontend Dependencies**
   ```bash
   cd frontend
   npm install
   ```

3. **Set Your OpenAI API Key**
   
   Edit `start_backend.bat` and replace the `OPENAI_API_KEY` value with your actual key.

### Option A: Docker (Easiest! 🐳)

```bash
# Set your OpenAI API key
export OPENAI_API_KEY=your-key-here

# Start all services (backend + frontend + ChromaDB)
docker-compose -f docker-compose.simple.yml up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="your-key-here"
docker-compose -f docker-compose.simple.yml up -d
```

See [`DOCKER_SETUP.md`](./DOCKER_SETUP.md) for full Docker documentation.

### Option B: Manual Setup

**Easy Way (Recommended):**
```bash
start_app.bat
```

This opens 2 terminal windows:
- Backend (Python/FastAPI) on port 8000
- Frontend (Next.js) on port 3000

**Manual Way:**
```bash
# Terminal 1 - Backend
start_backend.bat

# Terminal 2 - Frontend (wait 10 seconds for backend to start)
start_frontend.bat
```

**Stopping:**
```batch
stop_app.bat
```

### First Time Usage

1. Open http://localhost:3000 in your browser
2. Go to "Knowledge Base" → "New Knowledge Base"
3. Create a KB called "My Documents"
4. Upload some documents (PDF, TXT, MD)
5. Go to "Chat" → "New Chat"
6. Select your KB and ask questions!

**No login required** - The app runs in guest mode for easy development.

## 📍 Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Main UI |
| **Backend API** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Interactive Swagger docs |
| **Health Check** | http://localhost:8000/api/health | API health & DB status |

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Frontend (Next.js)              │
│         Port: 3000                      │
│  • React 18 + Next.js 14                │
│  • TailwindCSS + shadcn/ui              │
│  • TypeScript                           │
└─────────────────┬───────────────────────┘
                  │
                  │ HTTP/REST (CORS enabled)
                  │
┌─────────────────▼───────────────────────┐
│         Backend (FastAPI)               │
│         Port: 8000                      │
│  • Python 3.11+                         │
│  • SQLAlchemy ORM                       │
│  • LangChain for RAG                    │
└─────────────────┬───────────────────────┘
                  │
     ┌────────────┼────────────┐
     │            │            │
     ▼            ▼            ▼
┌─────────┐  ┌─────────┐  ┌─────────┐
│ SQLite  │  │ ChromaDB│  │ OpenAI  │
│ Database│  │ Vectors │  │ API     │
└─────────┘  └─────────┘  └─────────┘
```

## 🔧 Configuration

### Environment Variables

**Backend** (set in `start_backend.bat`):
```bash
OPENAI_API_KEY=your-key-here           # Your OpenAI API key
RAG_STORE=sqlite                       # Database type
SQLITE_FILE=./data/fortes.db          # Database file path
VECTOR_STORE_TYPE=chroma              # Vector database
EMBEDDING_MODEL=text-embedding-3-small # Embedding model
GENERATION_MODEL=gpt-4o-mini          # Generation model
```

**Frontend** (set in `start_frontend.bat`):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000  # Backend API URL
```

### Database

- **Type**: SQLite (file-based, no server needed)
- **Location**: `backend/data/fortes.db`
- **Migrations**: Run automatically on startup
- **Guest User**: Auto-created as `guest@fortes.local`

### Vector Store

- **Type**: ChromaDB (embedded mode)
- **Location**: `backend/data/chroma` (auto-created)
- **Persistent**: Yes, survives restarts

### File Storage

- **Type**: Local filesystem (no MinIO required)
- **Location**: `backend/data/uploads/`
- **Structure**: `kb_{id}/temp/` for each knowledge base
- **Persistent**: Yes, files saved locally

## 📚 Usage Guide

### Creating a Knowledge Base

1. Click "Knowledge Base" in sidebar
2. Click "New Knowledge Base"
3. Enter name and description
4. Click "Create Knowledge Base"

### Uploading Documents

1. Select a Knowledge Base
2. Click "Upload Documents"
3. Drag & drop or select files
4. Supported formats: PDF, TXT, MD, DOCX
5. Click "Upload" - documents are chunked and embedded automatically

### Chatting with AI

1. Click "Chat" in sidebar
2. Click "Start New Chat"
3. Enter a title
4. Select one or more Knowledge Bases
5. Ask your question
6. Get AI responses with:
   - Source citations (document + line number)
   - Similarity scores
   - Grounding indicators
   - Hallucination detection

### Generating API Keys

1. Click "API Keys" in sidebar
2. Click "Create API Key"
3. Enter a name
4. Copy the key (shown only once!)
5. Use in API requests with header: `X-API-Key: your-key`

## 🛡️ Guardrails

The system includes several safety features:

### PII Redaction
- Automatically detects and redacts email addresses, phone numbers, SSNs
- Configurable patterns in backend settings

### Prompt Injection Detection
- Detects malicious prompts trying to manipulate the AI
- Blocks suspicious requests before processing

### Hallucination Detection
- Validates AI responses against source documents
- Marks unsupported claims with "Unsupported" badges

### Grounding Validation
- Checks if AI responses are grounded in retrieved documents
- Shows grounding scores per response

## 🧪 Testing

### API Smoke Tests

Run automated tests:
```powershell
# Create Knowledge Base
Invoke-WebRequest -Uri "http://localhost:8000/api/knowledge-bases" -Method POST -Body '{"name":"Test KB","description":"Test"}' -ContentType "application/json"

# List Knowledge Bases
Invoke-WebRequest -Uri "http://localhost:8000/api/knowledge-bases" -Method GET

# Health Check
Invoke-WebRequest -Uri "http://localhost:8000/api/health" -Method GET
```

### Manual Testing

1. Create a KB with name "Test"
2. Upload `README.md` as a document
3. Go to Chat and ask: "What is this project about?"
4. Verify you get a response with citations

## 🐛 Troubleshooting

### Backend won't start

**Problem**: Port 8000 already in use
```bash
# Check what's using port 8000
netstat -ano | findstr :8000

# Kill the process
taskkill /F /PID <PID>
```

**Problem**: ModuleNotFoundError
```bash
cd backend
pip install -r requirements.txt
```

### Frontend won't start

**Problem**: Port 3000 already in use
- Frontend will automatically try 3001, 3002

**Problem**: Dependencies not installed
```bash
cd frontend
npm install
```

### CORS Errors

**Problem**: "Access-Control-Allow-Origin" error in browser

**Solution**: This is already fixed! But if you see it:
1. Make sure backend is running on port 8000
2. Make sure you're accessing frontend at `localhost:3000` (not `127.0.0.1`)
3. Clear browser cache and hard refresh (Ctrl+Shift+R)

### 401 Unauthorized

**Problem**: "Not authenticated" error

**Solution**: Guest mode is enabled by default. If you still see this:
1. Restart backend: `stop_app.bat` then `start_app.bat`
2. Check backend logs for "Guest user created"
3. Delete `backend/data/fortes.db` and restart to recreate database

### Database Issues

**Problem**: Database errors or corruption

**Solution**: Reset the database
```bash
# Stop the app
stop_app.bat

# Delete database
del backend\data\fortes.db*

# Restart (migrations will recreate everything)
start_app.bat
```

## 📖 API Documentation

### Interactive Docs

Visit http://localhost:8000/docs for interactive Swagger documentation.

### Key Endpoints

#### Knowledge Bases
```
GET    /api/knowledge-bases          # List all KBs
POST   /api/knowledge-bases          # Create KB
GET    /api/knowledge-bases/{id}     # Get KB details
PUT    /api/knowledge-bases/{id}     # Update KB
DELETE /api/knowledge-bases/{id}     # Delete KB
```

#### Documents
```
POST   /api/knowledge-bases/{id}/documents  # Upload documents
GET    /api/knowledge-bases/{id}/documents  # List documents
DELETE /api/documents/{id}                  # Delete document
```

#### Chats
```
GET    /api/chats                    # List chats
POST   /api/chats                    # Create chat
GET    /api/chats/{id}               # Get chat
POST   /api/chats/{id}/messages      # Send message (streaming)
```

#### API Keys
```
GET    /api/api-keys                 # List API keys
POST   /api/api-keys                 # Create API key
DELETE /api/api-keys/{id}            # Delete API key
```

## 🔒 Security

### Development Mode (Current)

- Guest user auto-created: `guest@fortes.local`
- No authentication required
- All users share the same data
- Perfect for development and testing

### Production Mode (To Enable)

1. Set `auto_error=True` in `OAuth2PasswordBearer` in `backend/app/api/api_v1/auth.py`
2. Remove guest user creation from `backend/app/main.py`
3. Uncomment login/register UI in frontend
4. Configure proper `SECRET_KEY` in backend

## 📁 Project Structure

```
Fortes_Assesment/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API routes
│   │   ├── core/              # Core config & security
│   │   ├── db/                # Database session
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   └── startup/           # Startup scripts (migrations)
│   ├── data/                  # SQLite database & ChromaDB
│   ├── alembic/               # Database migrations
│   └── requirements.txt       # Python dependencies
├── frontend/                  # Next.js frontend
│   ├── src/
│   │   ├── app/              # Next.js app router
│   │   ├── components/       # React components
│   │   └── lib/              # Utilities
│   └── package.json          # Node dependencies
├── start_app.bat             # Main startup script
├── start_backend.bat         # Backend only
├── start_frontend.bat        # Frontend only
├── stop_app.bat              # Stop all services
├── START_HERE.txt            # Quick reference
├── DEEP_FIX_SUMMARY.md       # Technical details
└── README.md                 # This file
```

## 🤝 Contributing

This is a demo/assessment project, but improvements are welcome!

## 📄 License

MIT License - feel free to use this for your own projects.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- UI powered by [Next.js](https://nextjs.org/) and [shadcn/ui](https://ui.shadcn.com/)
- RAG powered by [LangChain](https://langchain.com/)
- Vectors by [ChromaDB](https://www.trychroma.com/)
- AI by [OpenAI](https://openai.com/)

---

## 🚀 Get Started Now!

```batch
# 1. Install dependencies (first time only)
cd backend && pip install -r requirements.txt
cd ../frontend && npm install

# 2. Set your OpenAI API key in start_backend.bat

# 3. Run the app
cd ..
start_app.bat

# 4. Open browser
http://localhost:3000
```

**That's it! Start building your knowledge base!** 🎉
