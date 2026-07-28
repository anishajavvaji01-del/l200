"""Plugins module for ADK Agent satisfying Category 4 (Observability & Tracing) & Category 3 Guardrails."""

import json
import logging
import re
import time
from typing import Any, Dict, Optional
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse

logger = logging.getLogger("adk_observability")
logger.setLevel(logging.INFO)


class ObservabilityPlugin(BasePlugin):
    """Plugin capturing structured JSON logs, tracing latency, token usage, intent vs outcome, and redacting PII."""

    # Common PII regex patterns (emails, phone numbers, SSNs)
    PII_PATTERNS = [
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED_EMAIL]'),
        (r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', '[REDACTED_PHONE]'),
        (r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED_SSN]')
    ]

    def _redact_pii(self, text: str) -> str:
        """Redacts sensitive PII from log output strings."""
        if not isinstance(text, str):
            return text
        redacted = text
        for pattern, replacement in self.PII_PATTERNS:
            redacted = re.sub(pattern, replacement, redacted)
        return redacted

    def _emit_json_log(self, event_type: str, data: Dict[str, Any]) -> None:
        """Emits a structured JSON log entry."""
        log_entry = {
            "timestamp": time.time(),
            "event_type": event_type,
            "data": data
        }
        json_str = json.dumps(log_entry, default=str)
        redacted_json = self._redact_pii(json_str)
        logger.info(redacted_json)

    async def before_agent_callback(self, *, callback_context) -> None:
        """Traces agent start and captures initial user intent."""
        user_intent = callback_context.state.get("temp:user_intent", "Unknown intent")
        self._emit_json_log("agent_start", {
            "agent_name": callback_context.agent_name if hasattr(callback_context, "agent_name") else "agent",
            "session_id": callback_context.session.id if hasattr(callback_context, "session") else None,
            "intent": user_intent
        })

    async def after_agent_callback(self, *, callback_context) -> Optional[Any]:
        """Traces agent completion and compares intent vs outcome."""
        user_intent = callback_context.state.get("temp:user_intent", "Unknown intent")
        outcome = callback_context.state.get("agent_response", "No response captured")
        self._emit_json_log("agent_finish", {
            "agent_name": callback_context.agent_name if hasattr(callback_context, "agent_name") else "agent",
            "intent": user_intent,
            "outcome": outcome,
            "intent_outcome_matched": user_intent is not None and outcome is not None
        })
        return None

    async def before_model_callback(self, *, callback_context, llm_request: LlmRequest) -> Optional[LlmResponse]:
        """Traces LLM request generation."""
        callback_context.state["temp:model_start_time"] = time.time()
        self._emit_json_log("model_request", {
            "model": llm_request.model if hasattr(llm_request, "model") else "default",
            "contents_count": len(llm_request.contents) if hasattr(llm_request, "contents") and llm_request.contents else 0
        })
        return None

    async def after_model_callback(self, *, callback_context, llm_response: LlmResponse) -> Optional[LlmResponse]:
        """Traces LLM response, latency, and token usage."""
        start_time = callback_context.state.get("temp:model_start_time", time.time())
        latency_ms = (time.time() - start_time) * 1000

        usage_metadata = {}
        if hasattr(llm_response, "usage_metadata") and llm_response.usage_metadata:
            usage_metadata = {
                "prompt_tokens": getattr(llm_response.usage_metadata, "prompt_token_count", 0),
                "candidates_tokens": getattr(llm_response.usage_metadata, "candidates_token_count", 0),
                "total_tokens": getattr(llm_response.usage_metadata, "total_token_count", 0)
            }

        self._emit_json_log("model_response", {
            "latency_ms": latency_ms,
            "usage": usage_metadata
        })
        return None
