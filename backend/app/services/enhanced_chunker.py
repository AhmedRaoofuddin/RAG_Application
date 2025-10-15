"""
Enhanced Chunking Service for Fortes Eduction
Implements chunking with doc_id and line number tracking for citations
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import hashlib
from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """Represents a chunk with full citation metadata"""
    doc_id: str
    chunk_id: str
    content: str
    line_start: int
    line_end: int
    char_start: int
    char_end: int
    metadata: Dict[str, Any]


class EnhancedChunker:
    """Enhanced text chunker with citation tracking"""

    def __init__(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None
    ):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    def _generate_doc_id(self, filename: str, content: str) -> str:
        """Generate a unique document ID"""
        # Use filename + content hash for uniqueness
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        clean_filename = filename.replace(" ", "_").replace("/", "_")
        return f"{clean_filename}_{content_hash}"

    def _generate_chunk_id(self, doc_id: str, chunk_index: int) -> str:
        """Generate a unique chunk ID"""
        return f"{doc_id}_chunk_{chunk_index}"

    def _count_lines_up_to(self, text: str, position: int) -> int:
        """Count number of lines up to a given character position"""
        return text[:position].count('\n') + 1

    def chunk_text(
        self,
        text: str,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[DocumentChunk]:
        """
        Chunk text into overlapping segments with line tracking
        
        Args:
            text: The text to chunk
            filename: Original filename for doc_id generation
            metadata: Additional metadata to attach to chunks
        
        Returns:
            List of DocumentChunk objects with citation metadata
        """
        if not text.strip():
            logger.warning(f"Empty text provided for chunking: {filename}")
            return []

        doc_id = self._generate_doc_id(filename, text)
        chunks = []
        chunk_metadata = metadata or {}
        chunk_metadata["filename"] = filename
        chunk_metadata["doc_length"] = len(text)

        # Split into words for token approximation
        words = text.split()
        current_pos = 0
        chunk_index = 0

        while current_pos < len(words):
            # Get chunk window
            chunk_end = min(current_pos + self.chunk_size, len(words))
            chunk_words = words[current_pos:chunk_end]
            chunk_text = " ".join(chunk_words)

            # Find character positions in original text
            # This is approximate but good enough for line tracking
            char_start = text.find(chunk_words[0], 0 if chunk_index == 0 else chunks[-1].char_start)
            if char_start == -1:
                char_start = 0
            
            # Find end of last word in chunk
            if chunk_end < len(words):
                # Find the end of the last word in this chunk
                last_word = chunk_words[-1]
                char_end = text.find(last_word, char_start) + len(last_word)
            else:
                char_end = len(text)

            # Calculate line numbers
            line_start = self._count_lines_up_to(text, char_start)
            line_end = self._count_lines_up_to(text, char_end)

            # Create chunk
            chunk = DocumentChunk(
                doc_id=doc_id,
                chunk_id=self._generate_chunk_id(doc_id, chunk_index),
                content=chunk_text,
                line_start=line_start,
                line_end=line_end,
                char_start=char_start,
                char_end=char_end,
                metadata={
                    **chunk_metadata,
                    "chunk_index": chunk_index,
                    "word_count": len(chunk_words)
                }
            )
            chunks.append(chunk)

            # Move to next chunk with overlap
            current_pos += (self.chunk_size - self.chunk_overlap)
            chunk_index += 1

        logger.info(
            f"Chunked '{filename}' into {len(chunks)} chunks "
            f"(size={self.chunk_size}, overlap={self.chunk_overlap})"
        )

        return chunks

    def chunk_document(
        self,
        content: str,
        filename: str,
        doc_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Chunk a document and return as dictionaries for storage
        
        Returns:
            List of chunk dictionaries ready for vector store
        """
        chunks = self.chunk_text(content, filename, metadata)
        
        return [
            {
                "doc_id": chunk.doc_id,
                "chunk_id": chunk.chunk_id,
                "content": chunk.content,
                "line_start": chunk.line_start,
                "line_end": chunk.line_end,
                "char_start": chunk.char_start,
                "char_end": chunk.char_end,
                "metadata": {
                    **chunk.metadata,
                    "doc_type": doc_type
                }
            }
            for chunk in chunks
        ]

    def chunk_by_lines(
        self,
        text: str,
        filename: str,
        lines_per_chunk: int = 10,
        overlap_lines: int = 2,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[DocumentChunk]:
        """
        Alternative chunking strategy: by lines instead of tokens
        Useful for maintaining structure in code or structured text
        """
        doc_id = self._generate_doc_id(filename, text)
        lines = text.split('\n')
        chunks = []
        chunk_index = 0
        chunk_metadata = metadata or {}
        chunk_metadata["filename"] = filename

        current_line = 0
        while current_line < len(lines):
            chunk_end_line = min(current_line + lines_per_chunk, len(lines))
            chunk_lines = lines[current_line:chunk_end_line]
            chunk_text = '\n'.join(chunk_lines)

            # Calculate character positions
            char_start = sum(len(line) + 1 for line in lines[:current_line])  # +1 for \n
            char_end = char_start + len(chunk_text)

            chunk = DocumentChunk(
                doc_id=doc_id,
                chunk_id=self._generate_chunk_id(doc_id, chunk_index),
                content=chunk_text,
                line_start=current_line + 1,  # 1-indexed
                line_end=chunk_end_line,  # 1-indexed
                char_start=char_start,
                char_end=char_end,
                metadata={
                    **chunk_metadata,
                    "chunk_index": chunk_index,
                    "line_count": len(chunk_lines)
                }
            )
            chunks.append(chunk)

            current_line += (lines_per_chunk - overlap_lines)
            chunk_index += 1

        logger.info(
            f"Line-chunked '{filename}' into {len(chunks)} chunks "
            f"({lines_per_chunk} lines per chunk, {overlap_lines} overlap)"
        )

        return chunks


# Singleton instance
enhanced_chunker = EnhancedChunker()

