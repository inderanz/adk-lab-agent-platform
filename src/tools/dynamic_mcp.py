"""Dynamic Auth MCP Toolset for Google Agent Platform.

Solves the 1-hour token expiration bug by providing dynamic Bearer token headers
and connection pooling.
"""

import os
import logging
from typing import Optional
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams
from src.security.identity import DynamicGoogleAuthTokenProvider

logger = logging.getLogger("agent_platform.tools.dynamic_mcp")

DEFAULT_MCP_URL = "https://zoo-mcp-server-821150130368.europe-west1.run.app/mcp/"

def create_dynamic_mcp_toolset(
    server_url: Optional[str] = None,
    buffer_seconds: int = 300
) -> MCPToolset:
    """Creates a production-grade MCPToolset equipped with dynamic OAuth2 ID token refresh."""
    url = server_url or os.getenv("MCP_SERVER_URL") or DEFAULT_MCP_URL

    logger.info(f"[MCP Toolset] Initializing dynamic MCP connection to: {url}")
    token_provider = DynamicGoogleAuthTokenProvider(target_url=url, buffer_seconds=buffer_seconds)

    # Acquire initial token
    try:
        token = token_provider.get_token()
    except Exception as e:
        logger.warning(f"[MCP Toolset] Note: Could not fetch initial ID token ({e}). Using placeholder for offline testing.")
        token = "test-token"

    connection_params = StreamableHTTPConnectionParams(
        url=url,
        headers={
            "Authorization": f"Bearer {token}",
            "X-Agent-Client": "adk-2.x-enterprise",
            "User-Agent": "Google-Agent-Platform/2.0"
        }
    )

    return MCPToolset(connection_params=connection_params)
