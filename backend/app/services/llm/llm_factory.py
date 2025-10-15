import logging
from typing import Optional
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from langchain_ollama import OllamaLLM
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMFactory:
    @staticmethod
    def create(
        provider: Optional[str] = None,
        temperature: float = 0.7,
        streaming: bool = True,
    ) -> BaseChatModel:
        """
        Create a LLM instance with automatic fallback to stub when API key unavailable
        """
        provider = provider or settings.CHAT_PROVIDER

        try:
            if provider.lower() == "openai":
                # Check if API key is configured
                if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your-openai-api-key-here":
                    logger.warning("⚠️  No valid OpenAI API key found. Falling back to stub LLM.")
                    from app.services.stub_services import create_stub_llm
                    return create_stub_llm()
                
                logger.info(f"✓ Using OpenAI LLM: {settings.OPENAI_MODEL}")
                return ChatOpenAI(
                    temperature=temperature,
                    streaming=streaming,
                    model=settings.OPENAI_MODEL,
                    openai_api_key=settings.OPENAI_API_KEY,
                    openai_api_base=settings.OPENAI_API_BASE
                )
            elif provider.lower() == "deepseek":
                return ChatDeepSeek(
                    temperature=temperature,
                    streaming=streaming,
                    model=settings.DEEPSEEK_MODEL,
                    api_key=settings.DEEPSEEK_API_KEY,
                    api_base=settings.DEEPSEEK_API_BASE
                )
            elif provider.lower() == "ollama":
                return OllamaLLM(
                    model=settings.OLLAMA_MODEL,
                    base_url=settings.OLLAMA_API_BASE,
                    temperature=temperature,
                    streaming=streaming
                )
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")
        
        except Exception as e:
            logger.error(f"Failed to initialize {provider} LLM: {e}")
            logger.warning("Falling back to stub LLM for development/testing")
            from app.services.stub_services import create_stub_llm
            return create_stub_llm()