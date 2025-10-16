# 🐳 Docker Setup for Fortes Education

This document explains how to run Fortes Education using Docker.

## 📋 Prerequisites

- Docker 20.10+
- Docker Compose 1.29+
- 8GB+ RAM recommended
- OpenAI API key (optional for development)

## 🚀 Quick Start

### Option 1: Simplified Setup (Recommended for Quick Start)

Uses SQLite + Local File Storage + ChromaDB

```bash
# 1. Set your OpenAI API key (optional but recommended)
export OPENAI_API_KEY=your-api-key-here

# 2. Start all services
docker-compose -f docker-compose.simple.yml up -d

# 3. Wait for services to start (30-60 seconds)
docker-compose -f docker-compose.simple.yml logs -f backend

# 4. Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# ChromaDB: http://localhost:8001
```

**Windows (PowerShell):**
```powershell
# 1. Set your OpenAI API key
$env:OPENAI_API_KEY="your-api-key-here"

# 2. Start all services
docker-compose -f docker-compose.simple.yml up -d

# 3. View logs
docker-compose -f docker-compose.simple.yml logs -f backend
```

### Option 2: Full Setup (Production-Ready)

Uses MySQL + MinIO + ChromaDB

```bash
# 1. Copy and configure environment file
cp env.example .env
# Edit .env and set your OPENAI_API_KEY and other settings

# 2. Start all services
docker-compose up -d

# 3. Wait for database initialization
docker-compose logs -f db

# 4. Access the application
# Frontend: http://localhost
# Backend API: http://localhost/api
# MinIO Console: http://localhost:9001
```

## 📦 Services Overview

### Simplified Setup (`docker-compose.simple.yml`)

| Service    | Port | Description                    |
|------------|------|--------------------------------|
| backend    | 8000 | FastAPI backend server         |
| frontend   | 3000 | Next.js frontend application   |
| chromadb   | 8001 | Vector database for embeddings |

**Data Storage:**
- Database: SQLite (`./data/fortes.db`)
- Uploaded Files: Local filesystem (`./uploads/`)
- Vector Store: ChromaDB (`chroma_data` volume)

### Full Setup (`docker-compose.yml`)

| Service    | Port      | Description                    |
|------------|-----------|--------------------------------|
| nginx      | 80        | Reverse proxy                  |
| frontend   | (proxied) | Next.js frontend               |
| backend    | (proxied) | FastAPI backend                |
| db         | 3306      | MySQL database                 |
| chromadb   | 8001      | Vector database                |
| minio      | 9000,9001 | Object storage                 |

## 🛠️ Common Commands

### Start Services
```bash
# Simplified setup
docker-compose -f docker-compose.simple.yml up -d

# Full setup
docker-compose up -d
```

### Stop Services
```bash
# Simplified setup
docker-compose -f docker-compose.simple.yml down

# Full setup
docker-compose down
```

### View Logs
```bash
# All services
docker-compose -f docker-compose.simple.yml logs -f

# Specific service
docker-compose -f docker-compose.simple.yml logs -f backend
docker-compose -f docker-compose.simple.yml logs -f frontend
```

### Rebuild After Code Changes
```bash
# Rebuild all services
docker-compose -f docker-compose.simple.yml up -d --build

# Rebuild specific service
docker-compose -f docker-compose.simple.yml up -d --build backend
```

### Reset Everything (Clean Start)
```bash
# Simplified setup
docker-compose -f docker-compose.simple.yml down -v
rm -rf data/ uploads/
docker-compose -f docker-compose.simple.yml up -d --build

# Full setup
docker-compose down -v
docker-compose up -d --build
```

## 🐛 Troubleshooting

### Backend Won't Start

**Check logs:**
```bash
docker-compose -f docker-compose.simple.yml logs backend
```

**Common issues:**
- Port 8000 already in use → Stop other services on port 8000
- ChromaDB not ready → Wait 30 seconds and restart: `docker-compose restart backend`

### Frontend Won't Start

**Check logs:**
```bash
docker-compose -f docker-compose.simple.yml logs frontend
```

**Common issues:**
- Port 3000 in use → Change port in docker-compose file
- Build failed → Rebuild: `docker-compose -f docker-compose.simple.yml up -d --build frontend`

### Database Connection Errors

**For simplified setup:**
- Ensure `data/` directory exists: `mkdir -p data`
- Check file permissions: `chmod 755 data`

**For full setup:**
- Wait for MySQL to initialize (first run takes 1-2 minutes)
- Check MySQL health: `docker-compose exec db mysqladmin ping -p`

### "No OpenAI API Key" Warning

This is expected if you haven't set your API key. The system will use stub implementations for development.

**To fix:**
```bash
# Set in environment
export OPENAI_API_KEY=your-key-here

# Or add to .env file (full setup only)
echo "OPENAI_API_KEY=your-key-here" >> .env

# Restart services
docker-compose -f docker-compose.simple.yml restart
```

## 📊 Health Checks

### Backend Health
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": {
    "status": "ok",
    "path": "/app/data/fortes.db",
    "type": "sqlite"
  }
}
```

### Frontend
```bash
curl http://localhost:3000
```

Should return HTML content.

### ChromaDB
```bash
curl http://localhost:8001/api/v1/heartbeat
```

## 🔧 Configuration

### Environment Variables

For simplified setup, edit `docker-compose.simple.yml`:

```yaml
environment:
  - OPENAI_API_KEY=your-key-here
  - EMBEDDING_MODEL=text-embedding-3-small
  - GENERATION_MODEL=gpt-4o-mini
  - TOP_K_RETRIEVAL=5
  - GROUNDING_THRESHOLD=0.62
```

For full setup, edit `.env` file.

### Persistent Data

**Simplified setup:**
- SQLite database: `./data/fortes.db`
- Uploaded files: `./uploads/`
- ChromaDB: Docker volume `chroma_data`

**To backup:**
```bash
# Backup database
cp data/fortes.db data/fortes.db.backup

# Backup uploads
tar -czf uploads-backup.tar.gz uploads/

# Backup ChromaDB
docker-compose -f docker-compose.simple.yml exec chromadb tar -czf /tmp/chroma-backup.tar.gz /chroma/chroma
docker cp fortes-chromadb:/tmp/chroma-backup.tar.gz ./chroma-backup.tar.gz
```

## 🔄 Updates and Maintenance

### Pull Latest Changes
```bash
git pull origin main
docker-compose -f docker-compose.simple.yml up -d --build
```

### Update Docker Images
```bash
docker-compose -f docker-compose.simple.yml pull
docker-compose -f docker-compose.simple.yml up -d
```

### Clean Up Old Images
```bash
docker image prune -a
```

## 📝 Notes

- **Development Mode**: Both setups run in development mode with hot-reload enabled
- **Production**: For production, use full setup with proper SSL certificates via nginx
- **Performance**: First build takes 5-10 minutes; subsequent builds are faster
- **Ports**: Ensure ports 3000, 8000, 8001 (and 9000, 9001, 3306 for full setup) are available

## 🆘 Getting Help

If you encounter issues:

1. Check logs: `docker-compose -f docker-compose.simple.yml logs -f`
2. Verify all containers are running: `docker-compose -f docker-compose.simple.yml ps`
3. Check the troubleshooting guide above
4. Review backend logs: `docker-compose -f docker-compose.simple.yml logs backend`
5. Review frontend logs: `docker-compose -f docker-compose.simple.yml logs frontend`

## ✅ Success Checklist

- [ ] Docker and Docker Compose installed
- [ ] OpenAI API key set (or using stub mode)
- [ ] All services started: `docker-compose -f docker-compose.simple.yml ps`
- [ ] Backend health check passes: `curl http://localhost:8000/api/health`
- [ ] Frontend accessible: Open http://localhost:3000
- [ ] Can create knowledge base
- [ ] Can upload documents
- [ ] Can chat and get responses

---

**Happy Building with Fortes Education! 🚀**

