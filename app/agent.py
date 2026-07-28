"""Main Agent definition module satisfying Category 3 (Orchestration & Logic)."""

from google.adk.agents import Agent, SequentialAgent
from google.adk.tools import request_input
from app.tools import analyze_user_query, safe_calculator
from app.memory import DYNAMIC_SYSTEM_INSTRUCTION, async_save_memory_callback


# 1. Triage Agent (routed using Flash for fast extraction & classification)
triage_agent = Agent(
    name="triage_agent",
    model="gemini-flash-latest",
    instruction=(
        "You are a Triage Specialist. Extract user intent, key entities, and determine "
        "if mathematical computation or query analysis is needed. Use the analyze_user_query tool."
    ),
    description="Analyzes input queries and extracts structured intent.",
    tools=[analyze_user_query],
    output_key="triage_result"
)


# 2. Synthesis Agent (routed using Pro for complex reasoning and mathematical verification)
synthesis_agent = Agent(
    name="synthesis_agent",
    model="gemini-pro-latest",
    instruction=(
        DYNAMIC_SYSTEM_INSTRUCTION + "\n\n"
        "Review the triage results: {triage_result}. Use the safe_calculator tool if math is needed. "
        "If information is missing, ask the user using request_input tool."
    ),
    description="Synthesizes findings, performs math, and requests clarification if needed.",
    tools=[safe_calculator, request_input],
    output_key="agent_response",
    after_agent_callback=async_save_memory_callback
)


# 3. Multi-Agent Orchestration Topology (Sequential Pipeline)
root_agent = SequentialAgent(
    name="adk_pipeline_root",
    sub_agents=[triage_agent, synthesis_agent],
    description="Multi-agent pipeline carrying out triage followed by synthesis."
)
