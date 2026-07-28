"""Memory and Session module satisfying Category 2 (Context & Memory)."""

from typing import Optional
from google.adk.memory import InMemoryMemoryService
from google.adk.sessions import InMemorySessionService
from google.adk.apps import App, ResumabilityConfig
from google.adk.apps.app import EventsCompactionConfig
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
from google.adk.models import Gemini
from google.adk.agents.callback_context import CallbackContext


# Dynamic System Instruction template with state placeholders
DYNAMIC_SYSTEM_INSTRUCTION = """You are an intelligent assistant for user {user_id}.
Preferred language: {user:preferred_language}
Current Session Topic: {session_topic}

Rules:
1. Always utilize available tools for mathematical operations or query analysis.
2. Adhere to safety policies and maintain structured outputs.
"""


def setup_memory_service() -> InMemoryMemoryService:
    """Instantiates and configures the async long-term memory service."""
    return InMemoryMemoryService()


def setup_session_service() -> InMemorySessionService:
    """Instantiates the session service handling persistent and scoped state."""
    return InMemorySessionService()


async def async_save_memory_callback(callback_context: CallbackContext) -> None:
    """Async callback to persist session events to Memory Bank upon agent completion."""
    if hasattr(callback_context, "add_session_to_memory"):
        await callback_context.add_session_to_memory()


def create_configured_app(root_agent, app_name: str = "app") -> App:
    """Configures the main ADK App with compaction and resumability for HITL."""
    compaction_config = EventsCompactionConfig(
        compaction_interval=10,
        overlap_size=2,
        summarizer=LlmEventSummarizer(llm=Gemini(model="gemini-flash-latest"))
    )

    resumability_config = ResumabilityConfig(is_resumable=True)

    return App(
        name=app_name,
        root_agent=root_agent,
        events_compaction_config=compaction_config,
        resumability_config=resumability_config
    )
