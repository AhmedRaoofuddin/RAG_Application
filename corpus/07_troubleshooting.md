# Troubleshooting Guide

## Common Issues and Solutions

### Installation Issues

#### Python Dependencies Fail to Install

**Problem**: `pip install -r requirements.txt` fails

**Solutions**:
1. Upgrade pip: `pip install --upgrade pip`
2. Install build tools (Windows): Install Microsoft C++ Build Tools
3. Use virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate  # Windows
   ```

#### Node Modules Installation Fails

**Problem**: `npm install` or `pnpm install` fails

**Solutions**:
1. Clear cache: `npm cache clean --force`
2. Delete `node_modules` and `package-lock.json`
3. Try different package manager: `pnpm install` or `yarn install`

### Runtime Issues

#### "No OpenAI API Key" Warning

**Problem**: System shows stub mode warnings

**Solution**: This is expected if no API key is configured. Set `OPENAI_API_KEY` in `.env` for production use.

**Stub Mode**: The system will still work for development/testing with deterministic responses.

#### Database Connection Failed

**Problem**: Cannot connect to MySQL

**Solutions**:
1. Verify MySQL is running: `sudo service mysql status`
2. Check credentials in `.env`
3. For XAMPP: Start MySQL from XAMPP control panel
4. Fallback: Use SQLite by setting `RAG_STORE=sqlite`

#### ChromaDB Connection Error

**Problem**: Vector store connection fails

**Solutions**:
1. Check ChromaDB is running: `curl http://localhost:8000/api/v1/heartbeat`
2. Verify port is not in use
3. Check firewall settings
4. For local setup, ChromaDB should start automatically

### Document Processing Issues

#### Upload Hangs or Fails

**Problem**: Document upload doesn't complete

**Solutions**:
1. Check file format is supported (PDF, DOCX, MD, TXT)
2. Verify file size is reasonable (< 50MB recommended)
3. Check disk space available
4. Review backend logs for errors

#### No Chunks Created

**Problem**: Upload succeeds but no chunks are created

**Solutions**:
1. Verify document has readable text
2. Check chunking parameters in `.env`
3. For PDFs: Ensure it's text-based, not scanned image
4. Check backend logs for processing errors

### Query and Response Issues

#### Low Grounding Score Refusals

**Problem**: All queries return "not enough information" refusal

**Solutions**:
1. Lower threshold: Set `GROUNDING_THRESHOLD=0.5` in `.env`
2. Upload more relevant documents
3. Check if documents were processed successfully
4. Try rephrasing query to match document content

#### No Citations Appear

**Problem**: Responses don't include citations

**Solutions**:
1. Verify documents were chunked with line numbers
2. Check attribution service is enabled
3. Review chunk metadata in database
4. Ensure using enhanced chat service

#### Responses Too Slow

**Problem**: Queries take too long to respond

**Solutions**:
1. Reduce `TOP_K_RETRIEVAL` in `.env`
2. Use smaller embedding model
3. Optimize chunk size
4. Enable prompt caching
5. Use faster vector store (e.g., FAISS)

### Memory and Performance

#### High Memory Usage

**Problem**: System consumes too much memory

**Solutions**:
1. Reduce number of loaded documents
2. Decrease `CHUNK_SIZE` to create smaller chunks
3. Use lighter models
4. Limit concurrent requests

#### Cache Not Working

**Problem**: Identical queries don't hit cache

**Solutions**:
1. Verify `ENABLE_PROMPT_CACHE=true` in `.env`
2. Check cache TTL settings
3. Review cache statistics in logs
4. Ensure corpus hasn't changed between queries

## Error Messages

### "Unsupported embeddings provider"

**Cause**: Invalid `EMBEDDINGS_PROVIDER` value

**Fix**: Set to `openai`, `dashscope`, or `ollama`

### "Vector store collection not found"

**Cause**: Knowledge base hasn't been indexed

**Fix**: Re-upload documents or reinitialize vector store

### "Token limit exceeded"

**Cause**: Context or response too large

**Fix**: 
1. Reduce `TOP_K_RETRIEVAL`
2. Decrease `CHUNK_SIZE`
3. Use model with larger context window

## Logging and Debugging

### Enable Debug Logging

Add to `.env`:
```bash
LOG_LEVEL=DEBUG
```

### View Backend Logs

```bash
# If running with uvicorn
tail -f logs/app.log

# If using Docker
docker logs -f fortes-backend
```

### View Frontend Logs

Open browser console (F12) and check:
- Network tab for API errors
- Console tab for JavaScript errors

## Getting Help

If issues persist:

1. Check GitHub issues: Search for similar problems
2. Review documentation: Ensure correct configuration
3. Collect logs: Gather error messages and logs
4. Create detailed bug report with:
   - Error message
   - Steps to reproduce
   - Environment details
   - Relevant logs

## Reset to Clean State

If all else fails, reset to clean state:

```bash
# Stop all services
docker-compose down

# Remove database
rm fortes.db

# Clear vector store
rm -rf chroma_data/

# Restart
docker-compose up --build
```

