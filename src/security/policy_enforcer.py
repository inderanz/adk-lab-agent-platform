"""Policy Enforcement Point (PEP) for Agent Platform Authorization (AuthZ)."""

import json
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("agent_platform.security.authz")

class AuthZPolicyEnforcer:
    """Enforces fine-grained tool invocation authorization policies for subagents."""

    def __init__(self, policy_path: Optional[str] = None):
        if not policy_path:
            # Check multiple candidate locations
            candidates = [
                Path(__file__).parent.parent.parent / "config" / "authz_policy.json",
                Path(__file__).parent.parent / "config" / "authz_policy.json",
                Path(__file__).parent / "config" / "authz_policy.json",
                Path("config/authz_policy.json")
            ]
            for candidate in candidates:
                if candidate.exists():
                    policy_path = str(candidate)
                    break
            if not policy_path:
                policy_path = str(candidates[0])
        
        self.policy_path = policy_path
        self._policy = self._load_policy()

    def _load_policy(self) -> dict[str, Any]:
        try:
            with open(self.policy_path, "r") as f:
                policy = json.load(f)
                logger.info(f"[AuthZ] Loaded policy from {self.policy_path}: {policy.get('policy_name', 'Unnamed')}")
                return policy
        except Exception as e:
            logger.warning(f"[AuthZ] Could not load policy from {self.policy_path}: {e}. Defaulting to STRICT mode.")
            return {"roles": {}, "default_action": "DENY"}

    def is_authorized(self, agent_name: str, tool_name: str) -> bool:
        """Evaluates whether an agent has permission to execute a specific tool."""
        roles = self._policy.get("roles", {})
        default_action = self._policy.get("default_action", "DENY")

        if agent_name not in roles:
            logger.warning(f"[AuthZ] Unknown agent '{agent_name}'. Applying default action: {default_action}")
            return default_action == "ALLOW"

        agent_permissions = roles[agent_name]
        allowed = agent_permissions.get("allowed_tools", [])
        denied = agent_permissions.get("denied_tools", [])

        # Check explicit denials
        if "*" in denied or tool_name in denied:
            logger.warning(f"[AuthZ] Access DENIED: Agent '{agent_name}' is forbidden from invoking '{tool_name}'.")
            return False

        # Check explicit allowances
        if "*" in allowed or tool_name in allowed:
            logger.debug(f"[AuthZ] Access GRANTED: Agent '{agent_name}' permitted to invoke '{tool_name}'.")
            return True

        return default_action == "ALLOW"

    def enforce(self, agent_name: str, tool_name: str):
        """Raises PermissionError if the action is unauthorized."""
        if not self.is_authorized(agent_name, tool_name):
            raise PermissionError(
                f"[AuthZ Violation] Agent '{agent_name}' does not possess authorization to execute tool '{tool_name}'."
            )
