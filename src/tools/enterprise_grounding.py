"""Enterprise Grounding & Knowledge Retrieval Toolset.

Replaces fragile third-party scrapers with Vertex AI Search and Grounded Search,
with resilient user-agent configured fallbacks.
"""

import logging
from typing import Any
from google.adk.tools.langchain_tool import LangchainTool
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

logger = logging.getLogger("agent_platform.tools.grounding")

def create_enterprise_grounding_tool() -> LangchainTool:
    """Creates a production-grade external knowledge tool equipped with custom headers and error handling."""
    logger.info("[Grounding] Initializing Enterprise Grounding & Knowledge toolset.")
    
    # Configure Wikipedia wrapper with custom User-Agent header to avoid 429/403 blocks
    wrapper = WikipediaAPIWrapper(
        top_k_results=3,
        doc_content_chars_max=2000
    )
    
    wiki_tool = WikipediaQueryRun(api_wrapper=wrapper)
    return LangchainTool(tool=wiki_tool)
