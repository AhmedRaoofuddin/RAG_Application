"""
Stub/Fallback Services for Fortes Eduction
Provides deterministic local implementations when API keys are unavailable
"""

import logging
import hashlib
import numpy as np
from typing import List, Any, Optional
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseLLM
from langchain_core.outputs import LLMResult, Generation
from langchain_core.callbacks import CallbackManagerForLLMRun
from pydantic import Field

logger = logging.getLogger(__name__)


class StubEmbeddings(Embeddings):
    """
    Deterministic stub embeddings for development/testing when OpenAI key is unavailable
    Uses simple text hashing to create consistent embeddings
    """
    
    dimension: int = Field(default=1536, description="Embedding dimension")
    
    def __init__(self, dimension: int = 1536):
        super().__init__()
        self.dimension = dimension
        logger.warning(
            "⚠️  Using STUB embeddings (no OpenAI API key detected). "
            "Embeddings will be deterministic but NOT semantically meaningful. "
            "Set OPENAI_API_KEY for production use."
        )
    
    def _create_embedding(self, text: str) -> List[float]:
        """
        Create a deterministic embedding from text using hashing
        """
        # Create a hash of the text
        text_hash = hashlib.sha256(text.encode()).digest()
        
        # Use the hash to seed a random number generator for reproducibility
        seed = int.from_bytes(text_hash[:4], byteorder='big')
        rng = np.random.RandomState(seed)
        
        # Generate a random but deterministic vector
        embedding = rng.randn(self.dimension)
        
        # Normalize to unit length
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding.tolist()
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents"""
        return [self._create_embedding(text) for text in texts]
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a query"""
        return self._create_embedding(text)


class StubLLM(BaseLLM):
    """
    Deterministic stub LLM for development/testing when OpenAI key is unavailable
    Returns canned responses with context awareness
    """
    
    model_name: str = Field(default="stub-llm", description="Model name")
    
    def __init__(self):
        super().__init__()
        logger.warning(
            "⚠️  Using STUB LLM (no OpenAI API key detected). "
            "Responses will be canned/deterministic. "
            "Set OPENAI_API_KEY for production use."
        )
    
    @property
    def _llm_type(self) -> str:
        return "stub"
    
    def _generate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> LLMResult:
        """Generate responses for prompts"""
        generations = []
        
        for prompt in prompts:
            # Extract context if present
            context_extracted = False
            response = ""
            
            if "Context:" in prompt or "context:" in prompt:
                response = (
                    "Based on the provided context, I can help answer your question. "
                    "However, I am currently running in stub mode (no OpenAI API key detected). "
                    "This is a placeholder response. [citation:1]\n\n"
                    "For production use, please configure your OpenAI API key in the environment variables. "
                    "[citation:2]"
                )
                context_extracted = True
            elif "question" in prompt.lower() or "answer" in prompt.lower():
                response = (
                    "I understand your question, but I'm currently running in stub mode. "
                    "Please set up your OpenAI API key to get real, context-aware responses from Fortes Eduction."
                )
            else:
                # Simple echo for other cases
                response = prompt[:200] if len(prompt) > 200 else prompt
            
            generation = Generation(text=response)
            generations.append([generation])
        
        return LLMResult(generations=generations)
    
    async def _agenerate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> LLMResult:
        """Async generate - delegates to sync for stub"""
        return self._generate(prompts, stop, run_manager, **kwargs)


def create_stub_embeddings() -> StubEmbeddings:
    """Factory function for stub embeddings"""
    return StubEmbeddings()


def create_stub_llm() -> StubLLM:
    """Factory function for stub LLM"""
    return StubLLM()


def check_openai_key_available() -> bool:
    """Check if OpenAI API key is configured"""
    from app.core.config import settings
    return bool(settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your-openai-api-key-here")


def get_embeddings_with_fallback() -> Embeddings:
    """
    Get embeddings with automatic fallback to stub if OpenAI key unavailable
    """
    from app.core.config import settings
    
    if check_openai_key_available():
        try:
            from langchain_openai import OpenAIEmbeddings
            logger.info(f"✓ Using OpenAI embeddings: {settings.EMBEDDING_MODEL}")
            return OpenAIEmbeddings(
                model=settings.EMBEDDING_MODEL,
                openai_api_key=settings.OPENAI_API_KEY,
                openai_api_base=settings.OPENAI_API_BASE
            )
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI embeddings: {e}. Falling back to stub.")
            return create_stub_embeddings()
    else:
        logger.warning("No OpenAI API key configured. Using stub embeddings.")
        return create_stub_embeddings()


def get_llm_with_fallback() -> BaseLLM:
    """
    Get LLM with automatic fallback to stub if OpenAI key unavailable
    """
    from app.core.config import settings
    
    if check_openai_key_available():
        try:
            from langchain_openai import ChatOpenAI
            logger.info(f"✓ Using OpenAI LLM: {settings.GENERATION_MODEL}")
            return ChatOpenAI(
                model=settings.GENERATION_MODEL,
                openai_api_key=settings.OPENAI_API_KEY,
                openai_api_base=settings.OPENAI_API_BASE,
                streaming=True,
                temperature=0.7
            )
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI LLM: {e}. Falling back to stub.")
            return create_stub_llm()
    else:
        logger.warning("No OpenAI API key configured. Using stub LLM.")
        return create_stub_llm()

