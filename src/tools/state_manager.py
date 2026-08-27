"""Enterprise Session State & Context Management."""

import logging
from typing import Any, Dict
from google.adk.tools.tool_context import ToolContext
from src.security.guardrails import GuardrailValidator

logger = logging.getLogger("agent_platform.tools.state")

def add_prompt_to_state(tool_context: ToolContext, prompt: str) -> dict[str, str]:
    """Saves and sanitizes the user's initial prompt into the shared session state."""
    # Run guardrail sanitization
    sanitized_prompt = GuardrailValidator.sanitize_input(prompt)
    redacted_prompt = GuardrailValidator.redact_pii(sanitized_prompt)
    
    tool_context.state["PROMPT"] = redacted_prompt
    logger.info(f"[State updated] Successfully stored prompt in state: '{redacted_prompt}'")
    return {"status": "success", "sanitized": True}

def get_session_state(tool_context: ToolContext, key: str, default: Any = None) -> Any:
    """Safely retrieves a value from session state."""
    return tool_context.state.get(key, default)
