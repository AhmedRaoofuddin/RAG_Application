# Configuration Guide

## Environment Variables

### Core Application Settings

```bash
# Application Identity
PROJECT_NAME=Fortes Eduction
VERSION=1.0.0
API_V1_STR=/api
```

### Database Configuration

```bash
# Database Type: sqlite | mysql | pinecone
RAG_STORE=sqlite

# SQLite (Default)
SQLITE_FILE=./fortes.db
RAG_DB_URL=sqlite:///./fortes.db

# MySQL (XAMPP Compatible)
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=fortes

# Pinecone (Cloud Vector Database)
PINECONE_API_KEY=
PINECONE_ENV=
PINECONE_INDEX=fortes-eduction
```

### OpenAI Configuration

```bash
# OpenAI API
OPENAI_API_KEY=sk-...
OPENAI_API_BASE=https://api.openai.com/v1

# Models
EMBEDDING_MODEL=text-embedding-3-small
GENERATION_MODEL=gpt-4o-mini
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDINGS_MODEL=text-embedding-3-small
```

### Vector Store Configuration

```bash
# Vector Store Type
VECTOR_STORE_TYPE=chroma

# ChromaDB
CHROMA_DB_HOST=localhost
CHROMA_DB_PORT=8000

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_PREFER_GRPC=false
```

### RAG Parameters

```bash
# Retrieval Configuration
GROUNDING_THRESHOLD=0.62
TOP_K_RETRIEVAL=5
CHUNK_SIZE=512
CHUNK_OVERLAP=50
```

### Guardrails Configuration

```bash
# Enable/Disable Guardrails
ENABLE_PII_REDACTION=true
ENABLE_PROMPT_INJECTION_DETECTION=true
ENABLE_GROUNDING_REFUSAL=true
```

### Observability Configuration

```bash
# Monitoring and Logging
ENABLE_TOKEN_LOGGING=true
ENABLE_COST_TRACKING=true
ENABLE_PROMPT_CACHE=true
```

### Storage Configuration

```bash
# MinIO Object Storage
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=fortes-documents
```

## Configuration Profiles

### Development Profile

Optimized for local development with stubs:

```bash
RAG_STORE=sqlite
VECTOR_STORE_TYPE=chroma
OPENAI_API_KEY=  # Empty = uses stubs
ENABLE_TOKEN_LOGGING=true
ENABLE_COST_TRACKING=false
ENABLE_PROMPT_CACHE=true
```

### Production Profile

Production-ready configuration:

```bash
RAG_STORE=mysql
VECTOR_STORE_TYPE=qdrant
OPENAI_API_KEY=sk-real-key-here
ENABLE_TOKEN_LOGGING=true
ENABLE_COST_TRACKING=true
ENABLE_PROMPT_CACHE=true
GROUNDING_THRESHOLD=0.65
```

### Testing Profile

Optimized for automated testing:

```bash
RAG_STORE=sqlite
VECTOR_STORE_TYPE=chroma
OPENAI_API_KEY=  # Uses stubs
ENABLE_PII_REDACTION=true
ENABLE_PROMPT_INJECTION_DETECTION=true
GROUNDING_THRESHOLD=0.50  # Lower for tests
```

## Switching Configurations

### At Runtime

Some settings can be changed without restart:
- Grounding threshold (affects future queries)
- Guardrail enables/disables
- Cache settings

### Requires Restart

These settings require application restart:
- Database type (RAG_STORE)
- Vector store type
- Model selection
- API credentials

## Performance Tuning

### Chunk Size

- **Small (256)**: Better precision, more chunks, higher costs
- **Medium (512)**: Balanced (recommended)
- **Large (1024)**: Better context, fewer chunks, may miss details

### Top-K Retrieval

- **Low (3)**: Faster, less context
- **Medium (5)**: Balanced (recommended)
- **High (10)**: More context, slower, higher costs

### Grounding Threshold

- **0.5-0.6**: Lenient, fewer refusals
- **0.62-0.7**: Balanced (recommended)
- **0.7-0.8**: Strict, more refusals, higher quality

## Troubleshooting

### Database Connection Issues

If using MySQL:
```bash
# Test connection
mysql -h localhost -u root -p

# Verify database exists
SHOW DATABASES;
```

### Vector Store Issues

ChromaDB:
```bash
# Check if ChromaDB is running
curl http://localhost:8000/api/v1/heartbeat
```

### OpenAI API Issues

Test your API key:
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

