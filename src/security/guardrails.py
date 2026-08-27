"""Vertex AI Model Armor & Safety Guardrails Validator."""

import re
import logging

logger = logging.getLogger("agent_platform.security.guardrails")

class GuardrailValidator:
    """Provides prompt-injection defenses, PII masking, and safety filters."""

    # Patterns for basic PII masking
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    PHONE_PATTERN = re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b')
    SSN_PATTERN = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')

    # Common injection keywords
    SUSPICIOUS_INJECTIONS = [
        "ignore previous instructions",
        "system prompt override",
        "act as root admin",
        "drop table",
        "jailbreak enabled"
    ]

    @classmethod
    def sanitize_input(cls, user_prompt: str) -> str:
        """Validates user input against prompt injection signatures."""
        lower_prompt = user_prompt.lower()
        for pattern in cls.SUSPICIOUS_INJECTIONS:
            if pattern in lower_prompt:
                logger.warning(f"[Guardrails] Prompt injection attempt detected: '{pattern}'")
                raise ValueError("Input blocked by Model Armor security guardrails: Prohibited pattern detected.")
        return user_prompt.strip()

    @classmethod
    def redact_pii(cls, text: str) -> str:
        """Masks sensitive PII patterns (emails, phone numbers, SSNs) from logs/state."""
        text = cls.EMAIL_PATTERN.sub("[REDACTED_EMAIL]", text)
        text = cls.PHONE_PATTERN.sub("[REDACTED_PHONE]", text)
        text = cls.SSN_PATTERN.sub("[REDACTED_SSN]", text)
        return text
