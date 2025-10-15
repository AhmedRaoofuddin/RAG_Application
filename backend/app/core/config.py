import os
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Fortes Education")  # Project name
    VERSION: str = os.getenv("VERSION", "1.0.0")  # Project version
    API_V1_STR: str = "/api"  # API version string

    # Database Configuration
    RAG_STORE: str = os.getenv("RAG_STORE", "sqlite")  # sqlite | pinecone | mysql
    
    @property
    def SQLITE_FILE(self) -> str:
        """Get absolute path for SQLite database file."""
        sqlite_path = os.getenv("SQLITE_FILE", "./data/fortes.db")
        if not os.path.isabs(sqlite_path):
            # Make it absolute relative to project root
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            sqlite_path = os.path.join(base_dir, sqlite_path)
        # Ensure directory exists
        os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
        return sqlite_path
    
    RAG_DB_URL: str = os.getenv("RAG_DB_URL", "")

    # MySQL settings
    MYSQL_SERVER: str = os.getenv("MYSQL_SERVER", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "fortes")
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @property
    def get_database_url(self) -> str:
        if self.RAG_DB_URL:
            return self.RAG_DB_URL
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        if self.RAG_STORE == "sqlite":
            db_path = self.SQLITE_FILE
            return f"sqlite:///{db_path}"
        return (
            f"mysql+mysqlconnector://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_SERVER}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        )

    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))

    # Chat Provider settings
    CHAT_PROVIDER: str = os.getenv("CHAT_PROVIDER", "openai")

    # Embeddings settings
    EMBEDDINGS_PROVIDER: str = os.getenv("EMBEDDINGS_PROVIDER", "openai")

    # MinIO settings
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET_NAME", "documents")

    # OpenAI settings
    OPENAI_API_BASE: str = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_EMBEDDINGS_MODEL: str = os.getenv("OPENAI_EMBEDDINGS_MODEL", "text-embedding-ada-002")

    # DashScope settings
    DASH_SCOPE_API_KEY: str = os.getenv("DASH_SCOPE_API_KEY", "")
    DASH_SCOPE_EMBEDDINGS_MODEL: str = os.getenv("DASH_SCOPE_EMBEDDINGS_MODEL", "")

    # Vector Store settings
    VECTOR_STORE_TYPE: str = os.getenv("VECTOR_STORE_TYPE", "chroma")

    # Chroma DB settings
    CHROMA_DB_HOST: str = os.getenv("CHROMA_DB_HOST", "chromadb")
    CHROMA_DB_PORT: int = int(os.getenv("CHROMA_DB_PORT", "8000"))

    # Qdrant DB settings
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_PREFER_GRPC: bool = os.getenv("QDRANT_PREFER_GRPC", "true").lower() == "true"

    # Deepseek settings
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_API_BASE: str = "https://api.deepseek.com/v1"  # 默认 API 地址
    DEEPSEEK_MODEL: str = "deepseek-chat"  # 默认模型名称

    # Ollama settings
    OLLAMA_API_BASE: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "deepseek-r1:7b"
    OLLAMA_EMBEDDINGS_MODEL: str = os.getenv(
        "OLLAMA_EMBEDDINGS_MODEL", "nomic-embed-text"
    )

    # Pinecone settings
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENV: str = os.getenv("PINECONE_ENV", "")
    PINECONE_INDEX: str = os.getenv("PINECONE_INDEX", "fortes-eduction")

    # RAG Configuration
    GROUNDING_THRESHOLD: float = float(os.getenv("GROUNDING_THRESHOLD", "0.62"))
    TOP_K_RETRIEVAL: int = int(os.getenv("TOP_K_RETRIEVAL", "5"))
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "512"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "50"))

    # Guardrails Configuration
    ENABLE_PII_REDACTION: bool = os.getenv("ENABLE_PII_REDACTION", "true").lower() == "true"
    ENABLE_PROMPT_INJECTION_DETECTION: bool = os.getenv("ENABLE_PROMPT_INJECTION_DETECTION", "true").lower() == "true"
    ENABLE_GROUNDING_REFUSAL: bool = os.getenv("ENABLE_GROUNDING_REFUSAL", "true").lower() == "true"

    # Observability
    ENABLE_TOKEN_LOGGING: bool = os.getenv("ENABLE_TOKEN_LOGGING", "true").lower() == "true"
    ENABLE_COST_TRACKING: bool = os.getenv("ENABLE_COST_TRACKING", "true").lower() == "true"
    ENABLE_PROMPT_CACHE: bool = os.getenv("ENABLE_PROMPT_CACHE", "true").lower() == "true"

    # Generation Model Configuration
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    GENERATION_MODEL: str = os.getenv("GENERATION_MODEL", "gpt-4o-mini")

    class Config:
        env_file = ".env"


settings = Settings()
