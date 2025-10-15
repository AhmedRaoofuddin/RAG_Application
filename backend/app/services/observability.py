"""
Observability Service for Fortes Eduction
Implements token logging, cost tracking, and prompt caching
"""

import logging
import hashlib
import time
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from app.core.config import settings

logger = logging.getLogger(__name__)


class TokenCostTracker:
    """Track token usage and estimated costs"""

    # Pricing per 1M tokens (as of 2024)
    PRICING = {
        "gpt-4o-mini": {
            "input": 0.150,   # $0.150 per 1M input tokens
            "output": 0.600,  # $0.600 per 1M output tokens
        },
        "gpt-4o": {
            "input": 2.50,
            "output": 10.00,
        },
        "gpt-4": {
            "input": 30.00,
            "output": 60.00,
        },
        "text-embedding-3-small": {
            "input": 0.020,  # $0.020 per 1M tokens
            "output": 0.0,
        },
        "text-embedding-3-large": {
            "input": 0.130,
            "output": 0.0,
        },
        "text-embedding-ada-002": {
            "input": 0.100,
            "output": 0.0,
        }
    }

    def __init__(self):
        self.session_stats = {
            "total_requests": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_cost": 0.0,
            "cache_hits": 0,
            "cache_misses": 0
        }

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count (rough approximation: ~4 chars per token)
        """
        return len(text) // 4

    def calculate_cost(
        self, 
        model: str, 
        input_tokens: int, 
        output_tokens: int = 0
    ) -> float:
        """
        Calculate estimated cost for a request
        """
        if model not in self.PRICING:
            logger.warning(f"Unknown model for pricing: {model}, using gpt-4o-mini rates")
            model = "gpt-4o-mini"

        pricing = self.PRICING[model]
        
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        return input_cost + output_cost

    def log_request(
        self,
        request_type: str,
        model: str,
        input_tokens: int,
        output_tokens: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log a request and return stats
        """
        if not settings.ENABLE_TOKEN_LOGGING:
            return {}

        cost = self.calculate_cost(model, input_tokens, output_tokens)
        
        self.session_stats["total_requests"] += 1
        self.session_stats["total_input_tokens"] += input_tokens
        self.session_stats["total_output_tokens"] += output_tokens
        self.session_stats["total_cost"] += cost

        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "request_type": request_type,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": round(cost, 6),
            "metadata": metadata or {}
        }

        if settings.ENABLE_COST_TRACKING:
            logger.info(
                f"[{request_type}] Model: {model} | "
                f"Tokens: {input_tokens} in / {output_tokens} out | "
                f"Cost: ${cost:.6f} | "
                f"Session Total: ${self.session_stats['total_cost']:.6f}"
            )

        return log_entry

    def get_session_stats(self) -> Dict[str, Any]:
        """Get cumulative session statistics"""
        return {
            **self.session_stats,
            "average_cost_per_request": (
                self.session_stats["total_cost"] / self.session_stats["total_requests"]
                if self.session_stats["total_requests"] > 0
                else 0.0
            ),
            "cache_hit_rate": (
                self.session_stats["cache_hits"] / 
                (self.session_stats["cache_hits"] + self.session_stats["cache_misses"])
                if (self.session_stats["cache_hits"] + self.session_stats["cache_misses"]) > 0
                else 0.0
            )
        }


class PromptCache:
    """Simple in-memory prompt cache"""

    def __init__(self, ttl_seconds: int = 3600, max_size: int = 1000):
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size

    def _generate_key(self, query: str, corpus_fingerprint: str) -> str:
        """Generate cache key from query and corpus fingerprint"""
        combined = f"{query.lower().strip()}:{corpus_fingerprint}"
        return hashlib.sha256(combined.encode()).hexdigest()

    def _is_expired(self, timestamp: float) -> bool:
        """Check if cache entry is expired"""
        return (time.time() - timestamp) > self.ttl_seconds

    def _evict_oldest(self):
        """Evict oldest entry if cache is full"""
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
            logger.debug(f"Evicted oldest cache entry: {oldest_key}")

    def get(
        self, 
        query: str, 
        corpus_fingerprint: str
    ) -> Optional[Any]:
        """Get cached result if available and not expired"""
        if not settings.ENABLE_PROMPT_CACHE:
            return None

        key = self._generate_key(query, corpus_fingerprint)
        
        if key in self.cache:
            result, timestamp = self.cache[key]
            
            if not self._is_expired(timestamp):
                logger.info(f"✓ Cache hit for query: {query[:50]}...")
                return result
            else:
                del self.cache[key]
                logger.debug(f"Cache entry expired for query: {query[:50]}...")
        
        return None

    def set(
        self, 
        query: str, 
        corpus_fingerprint: str, 
        result: Any
    ):
        """Store result in cache"""
        if not settings.ENABLE_PROMPT_CACHE:
            return

        self._evict_oldest()
        
        key = self._generate_key(query, corpus_fingerprint)
        self.cache[key] = (result, time.time())
        logger.debug(f"Cached result for query: {query[:50]}...")

    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
        logger.info("Prompt cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds
        }


class ObservabilityService:
    """Main observability service combining all tracking"""

    def __init__(self):
        self.token_tracker = TokenCostTracker()
        self.prompt_cache = PromptCache()

    def log_embedding_request(
        self, 
        text: str, 
        model: str
    ) -> Dict[str, Any]:
        """Log an embedding request"""
        tokens = self.token_tracker.estimate_tokens(text)
        return self.token_tracker.log_request(
            request_type="embedding",
            model=model,
            input_tokens=tokens,
            output_tokens=0,
            metadata={"text_length": len(text)}
        )

    def log_generation_request(
        self,
        prompt: str,
        response: str,
        model: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Log a generation request"""
        input_tokens = self.token_tracker.estimate_tokens(prompt)
        output_tokens = self.token_tracker.estimate_tokens(response)
        
        return self.token_tracker.log_request(
            request_type="generation",
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            metadata=metadata
        )

    def get_cached_response(
        self, 
        query: str, 
        corpus_id: str
    ) -> Optional[Dict[str, Any]]:
        """Try to get cached response"""
        cached = self.prompt_cache.get(query, corpus_id)
        if cached:
            self.token_tracker.session_stats["cache_hits"] += 1
        else:
            self.token_tracker.session_stats["cache_misses"] += 1
        return cached

    def cache_response(
        self, 
        query: str, 
        corpus_id: str, 
        response: Dict[str, Any]
    ):
        """Cache a response"""
        self.prompt_cache.set(query, corpus_id, response)

    def get_stats(self) -> Dict[str, Any]:
        """Get all observability stats"""
        return {
            "token_stats": self.token_tracker.get_session_stats(),
            "cache_stats": self.prompt_cache.get_stats()
        }


# Singleton instance
observability_service = ObservabilityService()

