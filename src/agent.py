"""Enterprise Multi-Agent Workflow for Google Agent Platform (ADK 2.x).

Coordinates:
- Greeter Root Agent (Welcome & Triage)
- Comprehensive Researcher (Dynamic MCP + Enterprise Grounding + AuthZ)
- Response Formatter (Presentation & Grounding synthesis)
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Ensure flexible module resolution
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
for p in [current_dir, parent_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

from google.adk import Agent
from google.adk.agents import SequentialAgent

try:
    from src.telemetry.tracing import init_telemetry, trace_span
    from src.tools.dynamic_mcp import create_dynamic_mcp_toolset
    from src.tools.enterprise_grounding import create_enterprise_grounding_tool
    from src.tools.state_manager import add_prompt_to_state
    from src.security.policy_enforcer import AuthZPolicyEnforcer
except ImportError:
    from telemetry.tracing import init_telemetry, trace_span
    from tools.dynamic_mcp import create_dynamic_mcp_toolset
    from tools.enterprise_grounding import create_enterprise_grounding_tool
    from tools.state_manager import add_prompt_to_state
    from security.policy_enforcer import AuthZPolicyEnforcer

# Load environment configuration
load_dotenv()

# Initialize Telemetry (Cloud Logging & Cloud Trace)
project_id = os.getenv("PROJECT_ID")
init_telemetry(project_id=project_id)

logger = logging.getLogger("agent_platform.agent")

# Configure Model
model_name = os.getenv("MODEL", "gemini-3.7-flash")
logger.info(f"[Agent Platform] Starting Agent with model: {model_name}")

# --- Initialize Tools & Policy Enforcement ---

authz_enforcer = AuthZPolicyEnforcer()

# 1. Dynamic MCP Toolset
mcp_tools = create_dynamic_mcp_toolset()

# 2. Enterprise Grounding Toolset
grounding_tool = create_enterprise_grounding_tool()

# --- Define Specialist Agents ---

# 1. Researcher Specialist Agent
comprehensive_researcher = Agent(
    name="comprehensive_researcher",
    model=model_name,
    description="The primary researcher that accesses internal zoo MCP data and external knowledge via Enterprise Grounding.",
    instruction="""
    You are a helpful research assistant for the Zoo Tour Guide system. Your goal is to fully answer the user's PROMPT.
    You have access to two tools:
    1. A tool for getting specific data about animals AT OUR ZOO (names, ages, locations, exhibits).
    2. A tool for searching general knowledge (facts, lifespan, diet, habitat).

    First, analyze the user's PROMPT.
    - If the prompt can be answered by only one tool, use that tool.
    - If the prompt is complex and requires information from both the zoo's database AND external knowledge,
      you MUST use both tools to gather all necessary information.
    - Synthesize the results from the tool(s) you use into preliminary data outputs.

    PROMPT:
    {{ PROMPT }}
    """,
    tools=[
        mcp_tools,
        grounding_tool
    ],
    output_key="research_data"
)

# 2. Response Formatter Specialist Agent
response_formatter = Agent(
    name="response_formatter",
    model=model_name,
    description="Synthesizes all information into a friendly, readable, and grounded response.",
    instruction="""
    You are the friendly voice of the Zoo Tour Guide. Your task is to take the
    RESEARCH_DATA and present it to the user in a complete, engaging, and helpful answer.

    - First, present the specific information from the zoo (like animal names, ages, and where to find their exhibit).
    - Then, add the interesting general facts from the research.
    - If some information is missing from the zoo directory, clearly inform the visitor what is available.
    - Be conversational, warm, and engaging.

    RESEARCH_DATA:
    {{ research_data }}
    """
)

# --- Define Sequential Workflow ---

tour_guide_workflow = SequentialAgent(
    name="tour_guide_workflow",
    description="The main orchestrator workflow for handling visitor requests about zoo animals.",
    sub_agents=[
        comprehensive_researcher,  # Step 1: Research & retrieve facts
        response_formatter,        # Step 2: Format & synthesize final guide response
    ]
)

# --- Define Root Triage Agent (Welcome Desk) ---

root_agent = Agent(
    name="greeter",
    model=model_name,
    description="The main entry point for the Zoo Tour Guide.",
    instruction="""
    - Let the user know you will help them learn about the animals we have in the zoo.
    - When the user responds, use the 'add_prompt_to_state' tool to save their response.
    - After using the tool, transfer control to the 'tour_guide_workflow' agent.
    """,
    tools=[add_prompt_to_state],
    sub_agents=[tour_guide_workflow]
)
