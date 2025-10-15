"""
Tests for Enhanced Chunker
"""

import pytest
from app.services.enhanced_chunker import EnhancedChunker, DocumentChunk


class TestEnhancedChunker:
    """Test suite for enhanced chunking functionality"""

    def setup_method(self):
        """Setup for each test"""
        self.chunker = EnhancedChunker(chunk_size=50, chunk_overlap=10)

    def test_simple_chunking(self):
        """Test basic text chunking"""
        text = "This is a test. " * 100  # Create text that needs chunking
        filename = "test.txt"

        chunks = self.chunker.chunk_text(text, filename)

        assert len(chunks) > 0, "Should create at least one chunk"
        assert all(isinstance(c, DocumentChunk) for c in chunks), "All chunks should be DocumentChunk instances"
        assert all(c.doc_id.startswith("test.txt") for c in chunks), "All chunks should have correct doc_id"

    def test_doc_id_generation(self):
        """Test document ID generation is consistent"""
        text = "Same text content"
        filename = "test.txt"

        chunks1 = self.chunker.chunk_text(text, filename)
        chunks2 = self.chunker.chunk_text(text, filename)

        assert chunks1[0].doc_id == chunks2[0].doc_id, "Same content should generate same doc_id"

    def test_chunk_id_unique(self):
        """Test that chunk IDs are unique within a document"""
        text = "This is a test. " * 100
        filename = "test.txt"

        chunks = self.chunker.chunk_text(text, filename)
        chunk_ids = [c.chunk_id for c in chunks]

        assert len(chunk_ids) == len(set(chunk_ids)), "All chunk IDs should be unique"

    def test_line_number_tracking(self):
        """Test line number tracking"""
        text = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
        filename = "test.txt"

        chunks = self.chunker.chunk_text(text, filename)

        # First chunk should start at line 1
        assert chunks[0].line_start == 1, "First chunk should start at line 1"
        assert chunks[0].line_end >= 1, "Line end should be >= line start"

        # All chunks should have valid line numbers
        for chunk in chunks:
            assert chunk.line_start > 0, "Line numbers should be positive"
            assert chunk.line_end >= chunk.line_start, "Line end should be >= line start"

    def test_chunk_overlap(self):
        """Test that chunk overlap works correctly"""
        text = " ".join([f"word{i}" for i in range(200)])  # 200 words
        filename = "test.txt"

        chunker = EnhancedChunker(chunk_size=50, chunk_overlap=10)
        chunks = chunker.chunk_text(text, filename)

        # Should have multiple chunks due to size
        assert len(chunks) > 1, "Should create multiple chunks"

    def test_empty_text(self):
        """Test handling of empty text"""
        text = ""
        filename = "empty.txt"

        chunks = self.chunker.chunk_text(text, filename)

        assert len(chunks) == 0, "Empty text should produce no chunks"

    def test_metadata_preservation(self):
        """Test that metadata is preserved in chunks"""
        text = "Test content"
        filename = "test.txt"
        metadata = {"author": "Test Author", "date": "2024-01-01"}

        chunks = self.chunker.chunk_text(text, filename, metadata)

        assert len(chunks) > 0, "Should create chunks"
        assert chunks[0].metadata["author"] == "Test Author", "Metadata should be preserved"
        assert chunks[0].metadata["filename"] == filename, "Filename should be in metadata"

    def test_chunk_document_dict_output(self):
        """Test chunk_document returns proper dictionaries"""
        text = "Test content for chunking"
        filename = "test.txt"

        chunk_dicts = self.chunker.chunk_document(text, filename, doc_type="text")

        assert len(chunk_dicts) > 0, "Should create chunks"
        assert isinstance(chunk_dicts[0], dict), "Should return dictionaries"
        assert "doc_id" in chunk_dicts[0], "Should have doc_id"
        assert "chunk_id" in chunk_dicts[0], "Should have chunk_id"
        assert "content" in chunk_dicts[0], "Should have content"
        assert "line_start" in chunk_dicts[0], "Should have line_start"
        assert "line_end" in chunk_dicts[0], "Should have line_end"

    def test_line_chunking(self):
        """Test line-based chunking strategy"""
        text = "\n".join([f"Line {i}" for i in range(50)])
        filename = "test.txt"

        chunks = self.chunker.chunk_by_lines(
            text, filename, lines_per_chunk=10, overlap_lines=2
        )

        assert len(chunks) > 0, "Should create chunks"
        # Each chunk should have approximately 10 lines
        for chunk in chunks[:-1]:  # Skip last chunk which might be shorter
            line_count = chunk.metadata.get("line_count", 0)
            assert line_count <= 10, f"Chunk should have <= 10 lines, got {line_count}"


def test_chunker_integration():
    """Integration test for chunker"""
    chunker = EnhancedChunker()

    # Test with realistic document
    text = """
# Fortes Education Overview

Fortes Education is an advanced RAG system.

## Features

- Document management
- Advanced guardrails
- Attribution system
- Observability

## Installation

To install, run:
pip install -r requirements.txt
"""

    chunks = chunker.chunk_text(text, "overview.md")

    assert len(chunks) > 0, "Should create chunks from realistic document"

    # Verify all chunks have required fields
    for chunk in chunks:
        assert chunk.doc_id, "Should have doc_id"
        assert chunk.chunk_id, "Should have chunk_id"
        assert chunk.content, "Should have content"
        assert chunk.line_start > 0, "Should have valid line_start"
        assert chunk.line_end > 0, "Should have valid line_end"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

