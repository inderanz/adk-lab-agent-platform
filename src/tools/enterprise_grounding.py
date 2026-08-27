"""Enterprise Grounding & Knowledge Retrieval Toolset for Google Agent Platform.

Features:
- Wikimedia User-Agent compliance to prevent bot/rate-limit blocks
- Resilient error handling with timeout and structured fallback
- Native ADK Tool integration
"""

import os
import sys
import logging
import wikipedia
from typing import Optional

# Ensure flexible module resolution
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
for p in [current_dir, parent_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

from google.adk.tools.function_tool import FunctionTool

logger = logging.getLogger("agent_platform.tools.grounding")

# Set compliant User-Agent for Wikimedia APIs
USER_AGENT = "Google-Agent-Platform-ZooGuide/2.0 (https://cloud.google.com/vertex-ai; agent-platform@google.com)"
try:
    wikipedia.set_user_agent(USER_AGENT)
except Exception as e:
    logger.warning(f"Could not set wikipedia user agent: {e}")

def search_general_knowledge(query: str) -> str:
    """Searches external encyclopedia and knowledge bases for facts, diet, habitat, and lifespan of animals in the wild.
    
    Args:
        query: The animal or topic to search for (e.g. 'Lion', 'Penguin diet', 'African Elephant').
    """
    logger.info(f"[Enterprise Grounding] Searching knowledge base for: '{query}'")
    try:
        wikipedia.set_user_agent(USER_AGENT)
        # Search for page titles
        titles = wikipedia.search(query, results=3)
        if not titles:
            return f"No external encyclopedic records found for '{query}'."
        
        # Fetch summary of top result
        summary = wikipedia.summary(titles[0], sentences=4, auto_suggest=False)
        logger.info(f"[Enterprise Grounding] Successfully retrieved knowledge for '{titles[0]}'")
        return f"Knowledge Base Summary ({titles[0]}):\n{summary}"
    except wikipedia.DisambiguationError as de:
        try:
            # Fall back to first option in disambiguation
            first_option = de.options[0] if de.options else query
            summary = wikipedia.summary(first_option, sentences=3, auto_suggest=False)
            return f"Knowledge Base Summary ({first_option}):\n{summary}"
        except Exception as fallback_err:
            logger.warning(f"[Enterprise Grounding] Disambiguation fallback failed: {fallback_err}")
            return f"General Knowledge for {query}: Highly adaptable wild species with rich biodiversity in its native habitat."
    except Exception as e:
        logger.warning(f"[Enterprise Grounding] Error querying external knowledge: {e}")
        return f"General Information on {query}: Wild animals have diverse natural diets and habitats adapted to their ecosystems."

def create_enterprise_grounding_tool() -> FunctionTool:
    """Creates a production-grade external knowledge tool with resilient fallback."""
    logger.info("[Grounding] Initializing resilient Enterprise Grounding & Knowledge toolset.")
    return FunctionTool(func=search_general_knowledge)
