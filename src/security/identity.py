"""Enterprise Agent Identity & Dynamic Token Provider.

Eliminates the 1-hour static token bug by implementing cached, proactive token
renewal using Google OAuth2 ID token fetchers.
"""

import time
import logging
import threading
from typing import Optional
import google.auth
import google.auth.transport.requests
import google.oauth2.id_token

logger = logging.getLogger("agent_platform.security.identity")

class DynamicGoogleAuthTokenProvider:
    """Proactively refreshes Google OAuth2 ID tokens for downstream MCP services."""

    def __init__(self, target_url: str, buffer_seconds: int = 300):
        """
        Args:
            target_url: The full or base URL of the target service.
            buffer_seconds: Seconds before expiration to trigger a token refresh (default 5 mins).
        """
        self.target_url = target_url
        self.audience = target_url.split('/mcp/')[0] if '/mcp/' in target_url else target_url
        self.buffer_seconds = buffer_seconds
        
        self._cached_token: Optional[str] = None
        self._token_expiry_timestamp: float = 0.0
        self._lock = threading.Lock()
        self._request = google.auth.transport.requests.Request()

    def get_token(self) -> str:
        """Returns a valid Google ID token, refreshing automatically if expired or expiring soon."""
        now = time.time()
        
        # Fast path if token is valid and not within the refresh buffer window
        if self._cached_token and (now < (self._token_expiry_timestamp - self.buffer_seconds)):
            return self._cached_token

        with self._lock:
            # Re-check under lock in case another thread refreshed it
            if self._cached_token and (now < (self._token_expiry_timestamp - self.buffer_seconds)):
                return self._cached_token

            logger.info(f"[Identity] Fetching fresh Google ID token for audience: {self.audience}")
            try:
                fresh_token = google.oauth2.id_token.fetch_id_token(self._request, self.audience)
                self._cached_token = fresh_token
                # Standard GCP ID tokens are valid for 3600 seconds (1 hour)
                self._token_expiry_timestamp = now + 3600
                logger.info("[Identity] Successfully acquired and cached fresh Google ID token.")
                return self._cached_token
            except Exception as e:
                logger.error(f"[Identity] Failed to fetch Google ID token: {e}")
                # If we have an existing token, try fallback if within hard expiry
                if self._cached_token and (now < self._token_expiry_timestamp):
                    logger.warning("[Identity] Using existing cached token as fallback.")
                    return self._cached_token
                raise

    def get_auth_header(self) -> dict[str, str]:
        """Returns authorization header dict with a valid Bearer token."""
        return {"Authorization": f"Bearer {self.get_token()}"}
