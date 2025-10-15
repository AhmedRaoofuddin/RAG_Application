"""
Tests for Retrieval System
"""

import pytest
from app.services.enhanced_chunker import enhanced_chunker
from app.services.stub_services import create_stub_embeddings


class TestRetriever:
    """Test suite for retrieval functionality"""

    def setup_method(self):
        """Setup for each test"""
        self.embeddings = create_stub_embeddings()

    def test_embedding_generation(self):
        """Test that embeddings are generated correctly"""
        text = "This is a test query"
        embedding = self.embeddings.embed_query(text)

        assert embedding is not None, "Should generate embedding"
        assert len(embedding) > 0, "Embedding should have dimensions"
        assert all(isinstance(x, float) for x in embedding), "Embedding values should be floats"

    def test_embedding_consistency(self):
        """Test that same text produces same embedding"""
        text = "Consistent text"

        embedding1 = self.embeddings.embed_query(text)
        embedding2 = self.embeddings.embed_query(text)

        assert embedding1 == embedding2, "Same text should produce identical embeddings"

    def test_embedding_difference(self):
        """Test that different texts produce different embeddings"""
        text1 = "First text"
        text2 = "Second text"

        embedding1 = self.embeddings.embed_query(text1)
        embedding2 = self.embeddings.embed_query(text2)

        assert embedding1 != embedding2, "Different texts should produce different embeddings"

    def test_batch_embeddings(self):
        """Test batch embedding generation"""
        texts = ["Text 1", "Text 2", "Text 3"]
        embeddings = self.embeddings.embed_documents(texts)

        assert len(embeddings) == 3, "Should generate embeddings for all texts"
        assert all(len(emb) > 0 for emb in embeddings), "All embeddings should have dimensions"

    def test_chunk_retrieval_preparation(self):
        """Test that chunks are prepared for retrieval"""
        text = """
        Fortes Education is an advanced RAG system.
        It includes guardrails and attribution.
        The system is designed for Q&A applications.
        """

        chunks = enhanced_chunker.chunk_text(text, "test.md")

        assert len(chunks) > 0, "Should create chunks"

        # Verify chunks can be embedded
        for chunk in chunks[:3]:  # Test first 3 chunks
            embedding = self.embeddings.embed_query(chunk.content)
            assert embedding is not None, "Each chunk should be embeddable"

    def test_similarity_calculation(self):
        """Test basic similarity calculation"""
        import numpy as np

        emb1 = self.embeddings.embed_query("machine learning")
        emb2 = self.embeddings.embed_query("machine learning")
        emb3 = self.embeddings.embed_query("cooking recipes")

        # Calculate cosine similarity
        def cosine_sim(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        sim_identical = cosine_sim(emb1, emb2)
        sim_different = cosine_sim(emb1, emb3)

        assert sim_identical == 1.0, "Identical embeddings should have similarity 1.0"
        assert sim_different < 1.0, "Different embeddings should have similarity < 1.0"


class TestAttributionRetrieval:
    """Test retrieval for attribution purposes"""

    def setup_method(self):
        """Setup for each test"""
        self.embeddings = create_stub_embeddings()

    def test_chunk_metadata_preservation(self):
        """Test that chunk metadata is preserved for citations"""
        text = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"

        chunks = enhanced_chunker.chunk_text(text, "test.txt")

        # Verify metadata needed for citations
        for chunk in chunks:
            assert hasattr(chunk, 'doc_id'), "Should have doc_id"
            assert hasattr(chunk, 'chunk_id'), "Should have chunk_id"
            assert hasattr(chunk, 'line_start'), "Should have line_start"
            assert hasattr(chunk, 'line_end'), "Should have line_end"
            assert chunk.line_start > 0, "Line numbers should be positive"

    def test_document_dict_for_vector_store(self):
        """Test that chunks can be converted to dict for vector store"""
        text = "Test content for vector storage"

        chunk_dicts = enhanced_chunker.chunk_document(text, "test.md")

        assert len(chunk_dicts) > 0, "Should create chunk dicts"

        for chunk_dict in chunk_dicts:
            # Verify required fields for vector store
            assert "doc_id" in chunk_dict, "Should have doc_id"
            assert "content" in chunk_dict, "Should have content"
            assert "line_start" in chunk_dict, "Should have line_start"
            assert "line_end" in chunk_dict, "Should have line_end"
            assert "metadata" in chunk_dict, "Should have metadata"

            # Verify content is embeddable
            embedding = self.embeddings.embed_query(chunk_dict["content"])
            assert len(embedding) > 0, "Content should be embeddable"


def test_retrieval_integration():
    """Integration test for retrieval pipeline"""
    # Create sample documents
    documents = [
        ("Fortes Education is a RAG system with advanced features.", "doc1.md"),
        ("The system includes guardrails and attribution.", "doc2.md"),
        ("Installation requires Python 3.9 and Node.js 18.", "doc3.md")
    ]

    embeddings = create_stub_embeddings()
    all_chunks = []

    # Process documents
    for content, filename in documents:
        chunks = enhanced_chunker.chunk_text(content, filename)
        all_chunks.extend(chunks)

    assert len(all_chunks) > 0, "Should create chunks from documents"

    # Simulate retrieval
    query = "What is Fortes Education?"
    query_embedding = embeddings.embed_query(query)

    assert query_embedding is not None, "Query should be embeddable"

    # In real implementation, would calculate similarity and retrieve top-k
    # For test, just verify chunks have necessary data
    for chunk in all_chunks:
        chunk_embedding = embeddings.embed_query(chunk.content)
        assert chunk_embedding is not None, "Each chunk should be embeddable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

