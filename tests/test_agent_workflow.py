"""End-to-End Integration Tests for Enterprise Multi-Agent System."""

import asyncio
import unittest
from dotenv import load_dotenv

load_dotenv()

from src.agent import root_agent
from google.adk.runners import InMemoryRunner
from google.genai import types

class TestAgentWorkflow(unittest.TestCase):

    def setUp(self):
        self.runner = InMemoryRunner(agent=root_agent)

    def test_multi_agent_greeting_flow(self):
        async def _run():
            session = await self.runner.session_service.create_session(
                app_name=self.runner.app_name,
                user_id="integration_tester"
            )

            content = types.Content(
                role="user",
                parts=[types.Part.from_text(text="Hello")]
            )

            responses = []
            async for event in self.runner.run_async(
                session_id=session.id,
                user_id="integration_tester",
                new_message=content
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            responses.append(part.text)

            combined_response = " ".join(responses)
            self.assertTrue(len(combined_response) > 0)
            self.assertTrue("zoo" in combined_response.lower() or "animal" in combined_response.lower())

        asyncio.run(_run())

if __name__ == "__main__":
    unittest.main()
