"""
Guardrails service for Fortes Eduction RAG Q&A App
Implements prompt injection detection, PII redaction, and grounding score validation
"""

import re
import logging
from typing import Dict, List, Tuple, Any
from app.core.config import settings

logger = logging.getLogger(__name__)


class GuardrailsService:
    """Comprehensive guardrails for RAG Q&A system"""

    # Prompt injection patterns
    INJECTION_PATTERNS = [
        r"ignore\s+(previous|all|above)\s+instructions?",
        r"disregard\s+(previous|all|above)\s+instructions?",
        r"forget\s+(previous|all|above)\s+(instructions?|commands?)",
        r"you\s+are\s+now\s+a?\s*\w+",
        r"system\s*:\s*",
        r"<\s*system\s*>",
        r"jailbreak",
        r"sudo\s+mode",
        r"developer\s+mode",
        r"admin\s+mode",
        r"root\s+access",
        r"\[INST\]|\[/INST\]",
        r"<\|.*?\|>",
    ]

    # PII patterns
    EMAIL_PATTERN = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    
    # Phone patterns (including UAE format)
    PHONE_PATTERNS = [
        r"\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}",  # General international
        r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b",  # US format
        r"\+971[-.\s]?\d{1,2}[-.\s]?\d{3}[-.\s]?\d{4}",  # UAE format
        r"\b05\d[-.\s]?\d{3}[-.\s]?\d{4}\b",  # UAE local format
    ]

    def __init__(self):
        self.injection_regex = re.compile(
            "|".join(self.INJECTION_PATTERNS), 
            re.IGNORECASE
        )
        self.email_regex = re.compile(self.EMAIL_PATTERN)
        self.phone_regexes = [re.compile(pattern) for pattern in self.PHONE_PATTERNS]

    def detect_prompt_injection(self, text: str) -> Tuple[bool, str]:
        """
        Detect potential prompt injection or jailbreak attempts
        
        Returns:
            Tuple of (is_injection, reason)
        """
        if not settings.ENABLE_PROMPT_INJECTION_DETECTION:
            return False, ""

        match = self.injection_regex.search(text)
        if match:
            reason = f"Potential prompt injection detected: '{match.group()}'"
            logger.warning(reason)
            return True, reason

        return False, ""

    def redact_pii(self, text: str) -> Tuple[str, List[str]]:
        """
        Redact personally identifiable information (PII) from text
        
        Returns:
            Tuple of (redacted_text, list_of_redacted_items)
        """
        if not settings.ENABLE_PII_REDACTION:
            return text, []

        redacted_items = []
        redacted_text = text

        # Redact emails
        emails = self.email_regex.findall(redacted_text)
        for email in emails:
            redacted_text = redacted_text.replace(email, "[EMAIL_REDACTED]")
            redacted_items.append(f"email:{email}")

        # Redact phone numbers
        for phone_regex in self.phone_regexes:
            phones = phone_regex.findall(redacted_text)
            for phone in phones:
                # Avoid re-redacting already redacted items
                if "[PHONE_REDACTED]" not in phone and "[EMAIL_REDACTED]" not in phone:
                    redacted_text = redacted_text.replace(phone, "[PHONE_REDACTED]")
                    redacted_items.append(f"phone:{phone}")

        if redacted_items:
            logger.info(f"Redacted {len(redacted_items)} PII items")

        return redacted_text, redacted_items

    def neutralize_injection(self, text: str) -> str:
        """
        Neutralize detected injection attempts while preserving the query
        """
        # Replace injection patterns with safe alternatives
        neutralized = self.injection_regex.sub("[INSTRUCTION_REMOVED]", text)
        return neutralized

    def validate_grounding_score(
        self, 
        grounding_score: float, 
        context_chunks: List[Dict[str, Any]]
    ) -> Tuple[bool, str]:
        """
        Validate if grounding score meets the threshold
        
        Returns:
            Tuple of (is_valid, refusal_message)
        """
        if not settings.ENABLE_GROUNDING_REFUSAL:
            return True, ""

        if grounding_score < settings.GROUNDING_THRESHOLD:
            refusal_message = (
                f"I don't have enough relevant information in my knowledge base to answer this question confidently "
                f"(grounding score: {grounding_score:.2f}, threshold: {settings.GROUNDING_THRESHOLD:.2f}). "
                f"Could you try rephrasing your question or provide more context?"
            )
            logger.info(f"Query refused due to low grounding score: {grounding_score:.2f}")
            return False, refusal_message

        return True, ""

    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a user query through all guardrails
        
        Returns:
            Dictionary with processing results and flags
        """
        result = {
            "original_query": query,
            "processed_query": query,
            "is_safe": True,
            "injection_detected": False,
            "injection_reason": "",
            "pii_redacted": False,
            "redacted_items": [],
            "warnings": []
        }

        # 1. Check for prompt injection
        is_injection, injection_reason = self.detect_prompt_injection(query)
        if is_injection:
            result["injection_detected"] = True
            result["injection_reason"] = injection_reason
            result["processed_query"] = self.neutralize_injection(query)
            result["warnings"].append("Potential prompt injection neutralized")
            logger.warning(f"Injection attempt neutralized in query")

        # 2. Redact PII
        redacted_query, redacted_items = self.redact_pii(result["processed_query"])
        if redacted_items:
            result["pii_redacted"] = True
            result["redacted_items"] = redacted_items
            result["processed_query"] = redacted_query
            result["warnings"].append(f"Redacted {len(redacted_items)} PII items")

        return result

    def process_response(self, response: str) -> Dict[str, Any]:
        """
        Process a generated response through output guardrails
        
        Returns:
            Dictionary with processing results
        """
        result = {
            "original_response": response,
            "processed_response": response,
            "pii_redacted": False,
            "redacted_items": []
        }

        # Redact PII from output
        redacted_response, redacted_items = self.redact_pii(response)
        if redacted_items:
            result["pii_redacted"] = True
            result["redacted_items"] = redacted_items
            result["processed_response"] = redacted_response
            logger.info(f"Redacted {len(redacted_items)} PII items from response")

        return result

    def create_refusal_response(self, reason: str = "safety") -> str:
        """
        Create a friendly refusal message
        """
        refusals = {
            "safety": "I can't process that request. Please rephrase your question in a different way.",
            "injection": "I detected an attempt to alter my instructions. Please ask your question normally.",
            "grounding": "I don't have enough relevant information to answer this question confidently. Try rephrasing or providing more context."
        }
        return refusals.get(reason, refusals["safety"])


# Singleton instance
guardrails_service = GuardrailsService()

