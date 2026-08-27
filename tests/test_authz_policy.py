"""Unit tests for AuthZ Policy Enforcement Point (PEP)."""

import unittest
from src.security.policy_enforcer import AuthZPolicyEnforcer

class TestAuthZPolicy(unittest.TestCase):

    def setUp(self):
        self.enforcer = AuthZPolicyEnforcer()

    def test_greeter_permissions(self):
        # Greeter allowed tools
        self.assertTrue(self.enforcer.is_authorized("greeter", "add_prompt_to_state"))
        
        # Greeter denied tools
        self.assertFalse(self.enforcer.is_authorized("greeter", "get_animal_info"))
        self.assertFalse(self.enforcer.is_authorized("greeter", "enterprise_grounding_search"))

    def test_researcher_permissions(self):
        # Researcher allowed tools
        self.assertTrue(self.enforcer.is_authorized("comprehensive_researcher", "get_animal_info"))
        self.assertTrue(self.enforcer.is_authorized("comprehensive_researcher", "list_exhibits"))
        self.assertTrue(self.enforcer.is_authorized("comprehensive_researcher", "enterprise_grounding_search"))

        # Researcher denied tools
        self.assertFalse(self.enforcer.is_authorized("comprehensive_researcher", "add_prompt_to_state"))
        self.assertFalse(self.enforcer.is_authorized("comprehensive_researcher", "admin_execute_command"))

    def test_formatter_permissions(self):
        # Formatter should have no tool execution permissions
        self.assertFalse(self.enforcer.is_authorized("response_formatter", "get_animal_info"))
        self.assertFalse(self.enforcer.is_authorized("response_formatter", "any_random_tool"))

    def test_enforce_raises_exception(self):
        with self.assertRaises(PermissionError):
            self.enforcer.enforce("response_formatter", "get_animal_info")

if __name__ == "__main__":
    unittest.main()
