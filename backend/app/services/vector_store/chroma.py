from typing import List, Any
import os
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_chroma import Chroma
import chromadb 
from app.core.config import settings

from .base import BaseVectorStore

class ChromaVectorStore(BaseVectorStore):
    """Chroma vector store implementation"""
    
    def __init__(self, collection_name: str, embedding_function: Embeddings, **kwargs):
        """Initialize Chroma vector store"""
        try:
            # Try HTTP client first for production use
            chroma_client = chromadb.HttpClient(
                host=settings.CHROMA_DB_HOST,
                port=settings.CHROMA_DB_PORT,
            )
        except Exception:
            # Fall back to persistent local storage for development
            persist_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "chroma_db")
            os.makedirs(persist_directory, exist_ok=True)
            chroma_client = chromadb.PersistentClient(path=persist_directory)
        
        self._store = Chroma(
            client=chroma_client,
            collection_name=collection_name,
            embedding_function=embedding_function,
        )
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to Chroma"""
        self._store.add_documents(documents)
    
    def delete(self, ids: List[str]) -> None:
        """Delete documents from Chroma"""
        self._store.delete(ids)
    
    def as_retriever(self, **kwargs: Any):
        """Return a retriever interface"""
        return self._store.as_retriever(**kwargs)
    
    def similarity_search(self, query: str, k: int = 4, **kwargs: Any) -> List[Document]:
        """Search for similar documents in Chroma"""
        return self._store.similarity_search(query, k=k, **kwargs)
    
    def similarity_search_with_score(self, query: str, k: int = 4, **kwargs: Any) -> List[Document]:
        """Search for similar documents in Chroma with score"""
        return self._store.similarity_search_with_score(query, k=k, **kwargs)

    def delete_collection(self) -> None:
        """Delete the entire collection"""
        self._store._client.delete_collection(self._store._collection.name) 