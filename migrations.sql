-- Fortes Education Database Schema
-- This file documents the database schema for reference
-- Actual migrations run automatically via Alembic on application startup

-- ============================================================
-- USERS TABLE (Auth system - currently unused in guest mode)
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- ============================================================
-- API KEYS TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_hash VARCHAR(512) NOT NULL,
    name VARCHAR(255) NOT NULL,
    user_id INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    last_used_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_api_keys_user ON api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_active ON api_keys(is_active);

-- ============================================================
-- KNOWLEDGE BASES TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS knowledge_bases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_kb_user ON knowledge_bases(user_id);
CREATE INDEX IF NOT EXISTS idx_kb_created ON knowledge_bases(created_at);

-- ============================================================
-- DOCUMENTS TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(128),
    knowledge_base_id INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',  -- pending, processing, completed, failed
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    error_message TEXT,
    chunk_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_documents_kb ON documents(knowledge_base_id);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_created ON documents(created_at);

-- ============================================================
-- DOCUMENT UPLOADS TABLE (Processing Queue)
-- ============================================================

CREATE TABLE IF NOT EXISTS document_uploads (
    id VARCHAR(255) PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    knowledge_base_id INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    document_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id) ON DELETE CASCADE,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_uploads_kb ON document_uploads(knowledge_base_id);
CREATE INDEX IF NOT EXISTS idx_uploads_status ON document_uploads(status);

-- ============================================================
-- CHUNKS TABLE (Document Chunks for RAG)
-- ============================================================

CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    doc_id VARCHAR(255) NOT NULL,  -- Unique document identifier
    chunk_id VARCHAR(255) NOT NULL UNIQUE,  -- Unique chunk identifier
    content TEXT NOT NULL,
    line_start INTEGER NOT NULL,
    line_end INTEGER NOT NULL,
    char_start INTEGER NOT NULL,
    char_end INTEGER NOT NULL,
    chunk_metadata TEXT,  -- JSON metadata
    embedding_id VARCHAR(255),  -- Reference to vector store
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_chunks_document ON chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_doc_id ON chunks(doc_id);
CREATE INDEX IF NOT EXISTS idx_chunks_chunk_id ON chunks(chunk_id);

-- ============================================================
-- CHATS TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255),
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_chats_user ON chats(user_id);
CREATE INDEX IF NOT EXISTS idx_chats_created ON chats(created_at);

-- ============================================================
-- CHAT_KNOWLEDGE_BASES TABLE (Many-to-Many)
-- ============================================================

CREATE TABLE IF NOT EXISTS chat_knowledge_bases (
    chat_id INTEGER NOT NULL,
    knowledge_base_id INTEGER NOT NULL,
    PRIMARY KEY (chat_id, knowledge_base_id),
    FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE,
    FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_chat_kb_chat ON chat_knowledge_bases(chat_id);
CREATE INDEX IF NOT EXISTS idx_chat_kb_kb ON chat_knowledge_bases(knowledge_base_id);

-- ============================================================
-- MESSAGES TABLE
-- ============================================================

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    role VARCHAR(50) NOT NULL,  -- user, assistant, system
    chat_id INTEGER NOT NULL,
    metadata TEXT,  -- JSON metadata (citations, grounding score, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_messages_chat ON messages(chat_id);
CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at);

-- ============================================================
-- VECTOR STORE METADATA (Optional - for SQLite vector index)
-- ============================================================

-- Note: If using FAISS/HNSWlib with SQLite, vectors are stored
-- in separate binary files, referenced by embedding_id in chunks table

-- ============================================================
-- EXAMPLE QUERIES
-- ============================================================

-- Get all knowledge bases for a user
-- SELECT * FROM knowledge_bases WHERE user_id = ?;

-- Get all documents in a knowledge base with processing status
-- SELECT * FROM documents WHERE knowledge_base_id = ? ORDER BY created_at DESC;

-- Get chunks for a document with citation metadata
-- SELECT doc_id, chunk_id, content, line_start, line_end 
-- FROM chunks WHERE document_id = ? ORDER BY chunk_id;

-- Get chat history with messages
-- SELECT m.* FROM messages m 
-- JOIN chats c ON m.chat_id = c.id 
-- WHERE c.id = ? ORDER BY m.created_at;

-- ============================================================
-- MIGRATION NOTES
-- ============================================================

-- This schema is automatically applied via Alembic migrations
-- located in backend/alembic/versions/
--
-- To apply migrations manually (not recommended):
-- cd backend
-- alembic upgrade head
--
-- To create a new migration:
-- alembic revision --autogenerate -m "description"
--
-- Database auto-initializes on first application startup
-- No manual SQL execution required

-- ============================================================
-- SQLITE OPTIMIZATIONS
-- ============================================================

-- Enable WAL mode for better concurrency
PRAGMA journal_mode=WAL;

-- Increase cache size (64MB)
PRAGMA cache_size=-64000;

-- Enable foreign keys
PRAGMA foreign_keys=ON;

