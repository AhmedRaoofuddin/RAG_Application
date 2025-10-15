import logging
from app.core.config import settings
from langchain_openai import OpenAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_community.embeddings import DashScopeEmbeddings

logger = logging.getLogger(__name__)


class EmbeddingsFactory:
    @staticmethod
    def create():
        """
        Factory method to create an embeddings instance with automatic fallback to stub.
        Falls back to stub embeddings if API key is missing or invalid.
        """
        embeddings_provider = settings.EMBEDDINGS_PROVIDER.lower()

        try:
            if embeddings_provider == "openai":
                # Check if API key is configured
                if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your-openai-api-key-here":
                    logger.warning("⚠️  No valid OpenAI API key found. Falling back to stub embeddings.")
                    from app.services.stub_services import create_stub_embeddings
                    return create_stub_embeddings()
                
                logger.info(f"✓ Using OpenAI embeddings: {settings.OPENAI_EMBEDDINGS_MODEL}")
                return OpenAIEmbeddings(
                    openai_api_key=settings.OPENAI_API_KEY,
                    openai_api_base=settings.OPENAI_API_BASE,
                    model=settings.OPENAI_EMBEDDINGS_MODEL
                )
            elif embeddings_provider == "dashscope":
                return DashScopeEmbeddings(
                    model=settings.DASH_SCOPE_EMBEDDINGS_MODEL,
                    dashscope_api_key=settings.DASH_SCOPE_API_KEY
                )
            elif embeddings_provider == "ollama":
                return OllamaEmbeddings(
                    model=settings.OLLAMA_EMBEDDINGS_MODEL,
                    base_url=settings.OLLAMA_API_BASE
                )
            else:
                raise ValueError(f"Unsupported embeddings provider: {embeddings_provider}")
        
        except Exception as e:
            logger.error(f"Failed to initialize {embeddings_provider} embeddings: {e}")
            logger.warning("Falling back to stub embeddings for development/testing")
            from app.services.stub_services import create_stub_embeddings
            return create_stub_embeddings()
