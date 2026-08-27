"""Tests for Dynamic Token Provider and MCP Connectivity."""

import os
import unittest
from dotenv import load_dotenv

load_dotenv()

from src.security.identity import DynamicGoogleAuthTokenProvider

class TestDynamicMCP(unittest.TestCase):

    def setUp(self):
        self.mcp_url = os.getenv(
            "MCP_SERVER_URL",
            "https://zoo-mcp-server-821150130368.europe-west1.run.app/mcp/"
        )

    def test_dynamic_token_acquisition_and_cache(self):
        provider = DynamicGoogleAuthTokenProvider(target_url=self.mcp_url, buffer_seconds=300)
        
        # 1. First token fetch
        token_1 = provider.get_token()
        self.assertIsNotNone(token_1)
        self.assertTrue(len(token_1) > 20)
        
        # 2. Second fetch should return cached token
        token_2 = provider.get_token()
        self.assertEqual(token_1, token_2)

        # 3. Verify Auth header format
        auth_header = provider.get_auth_header()
        self.assertIn("Authorization", auth_header)
        self.assertTrue(auth_header["Authorization"].startswith("Bearer "))

if __name__ == "__main__":
    unittest.main()
