"""
Attribution and Hallucination Detection Service for Fortes Eduction
Implements sentence-level citation mapping and unsupported content flagging
"""

import re
import logging
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Citation:
    """Represents a citation for a sentence"""
    doc_id: str
    chunk_id: str
    line_start: int
    line_end: int
    similarity_score: float
    chunk_text: str


@dataclass
class AnnotatedSentence:
    """Represents a sentence with its citations"""
    text: str
    citations: List[Citation]
    is_supported: bool
    confidence: float


class AttributionService:
    """Service for sentence-level attribution and hallucination detection"""

    # Minimum similarity threshold for citation support
    CITATION_THRESHOLD = 0.65
    
    # Minimum number of citations required for support
    MIN_CITATIONS = 1

    def __init__(self):
        # Pattern for sentence splitting (handles common abbreviations)
        self.sentence_pattern = re.compile(
            r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s'
        )

    def split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences, handling common edge cases
        """
        # Handle common abbreviations
        text = text.replace("e.g.", "e~g~")
        text = text.replace("i.e.", "i~e~")
        text = text.replace("etc.", "etc~")
        text = text.replace("Dr.", "Dr~")
        text = text.replace("Mr.", "Mr~")
        text = text.replace("Mrs.", "Mrs~")
        text = text.replace("Ms.", "Ms~")
        
        sentences = self.sentence_pattern.split(text)
        
        # Restore abbreviations
        sentences = [
            s.replace("e~g~", "e.g.")
             .replace("i~e~", "i.e.")
             .replace("etc~", "etc.")
             .replace("Dr~", "Dr.")
             .replace("Mr~", "Mr.")
             .replace("Mrs~", "Mrs.")
             .replace("Ms~", "Ms.")
             .strip()
            for s in sentences if s.strip()
        ]
        
        return sentences

    def calculate_sentence_similarity(
        self, 
        sentence: str, 
        chunk: Dict[str, Any]
    ) -> float:
        """
        Calculate similarity between a sentence and a chunk
        Uses simple word overlap for now (can be replaced with embeddings)
        """
        # Normalize text
        sentence_words = set(sentence.lower().split())
        chunk_words = set(chunk.get("content", "").lower().split())
        
        if not sentence_words or not chunk_words:
            return 0.0
        
        # Jaccard similarity
        intersection = sentence_words.intersection(chunk_words)
        union = sentence_words.union(chunk_words)
        
        return len(intersection) / len(union) if union else 0.0

    def find_supporting_chunks(
        self, 
        sentence: str, 
        chunks: List[Dict[str, Any]],
        top_k: int = 3
    ) -> List[Citation]:
        """
        Find chunks that support a given sentence
        """
        citations = []
        
        for chunk in chunks:
            similarity = self.calculate_sentence_similarity(sentence, chunk)
            
            if similarity >= self.CITATION_THRESHOLD:
                citation = Citation(
                    doc_id=chunk.get("doc_id", "unknown"),
                    chunk_id=chunk.get("chunk_id", "unknown"),
                    line_start=chunk.get("line_start", 0),
                    line_end=chunk.get("line_end", 0),
                    similarity_score=similarity,
                    chunk_text=chunk.get("content", "")[:200]  # First 200 chars
                )
                citations.append(citation)
        
        # Sort by similarity and return top-k
        citations.sort(key=lambda c: c.similarity_score, reverse=True)
        return citations[:top_k]

    def annotate_response(
        self, 
        response_text: str, 
        retrieved_chunks: List[Dict[str, Any]]
    ) -> Tuple[List[AnnotatedSentence], bool, Dict[str, Any]]:
        """
        Annotate response with sentence-level citations and detect hallucinations
        
        Returns:
            Tuple of (annotated_sentences, has_hallucination, stats)
        """
        sentences = self.split_into_sentences(response_text)
        annotated_sentences = []
        unsupported_count = 0
        
        for sentence in sentences:
            if not sentence.strip():
                continue
                
            citations = self.find_supporting_chunks(sentence, retrieved_chunks)
            is_supported = len(citations) >= self.MIN_CITATIONS
            
            if not is_supported:
                unsupported_count += 1
            
            confidence = max([c.similarity_score for c in citations], default=0.0)
            
            annotated = AnnotatedSentence(
                text=sentence,
                citations=citations,
                is_supported=is_supported,
                confidence=confidence
            )
            annotated_sentences.append(annotated)
        
        has_hallucination = unsupported_count > 0
        
        stats = {
            "total_sentences": len(annotated_sentences),
            "supported_sentences": len(annotated_sentences) - unsupported_count,
            "unsupported_sentences": unsupported_count,
            "hallucination_rate": unsupported_count / len(annotated_sentences) if annotated_sentences else 0.0,
            "average_confidence": sum(s.confidence for s in annotated_sentences) / len(annotated_sentences) if annotated_sentences else 0.0
        }
        
        if has_hallucination:
            logger.warning(
                f"Hallucination detected: {unsupported_count}/{len(annotated_sentences)} "
                f"sentences lack sufficient support"
            )
        
        return annotated_sentences, has_hallucination, stats

    def format_citations_for_response(
        self, 
        annotated_sentences: List[AnnotatedSentence]
    ) -> Dict[str, Any]:
        """
        Format annotated sentences for API response
        """
        formatted_sentences = []
        
        for sent in annotated_sentences:
            formatted_citations = [
                {
                    "doc_id": c.doc_id,
                    "chunk_id": c.chunk_id,
                    "line_range": f"{c.line_start}-{c.line_end}",
                    "similarity": round(c.similarity_score, 3),
                    "preview": c.chunk_text
                }
                for c in sent.citations
            ]
            
            formatted_sentences.append({
                "text": sent.text,
                "citations": formatted_citations,
                "is_supported": sent.is_supported,
                "confidence": round(sent.confidence, 3),
                "hallucination_flag": not sent.is_supported
            })
        
        return {
            "sentences": formatted_sentences,
            "has_hallucination": any(not s.is_supported for s in annotated_sentences)
        }

    def calculate_grounding_score(
        self, 
        retrieved_chunks: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate overall grounding score based on retrieved chunks
        """
        if not retrieved_chunks:
            return 0.0
        
        # Use the maximum similarity score from top chunks
        scores = [chunk.get("score", 0.0) for chunk in retrieved_chunks]
        return max(scores) if scores else 0.0


# Singleton instance
attribution_service = AttributionService()

