"""Tools module for ADK Agent satisfying Category 1 (Tool & Interface Design)."""

import json
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from google.adk.tools import ToolContext


class AnalysisInput(BaseModel):
    query: str = Field(description="The user input query or topic to analyze.")
    max_results: int = Field(default=5, description="Maximum number of results to extract.")


class CalculationInput(BaseModel):
    expression: str = Field(description="Mathematical expression to evaluate safely.")


def analyze_user_query(query: str, max_results: int = 5, tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """Analyzes user input queries and extracts structured intent and keywords.

    Args:
        query: The user input query string to analyze.
        max_results: Maximum number of key topics or entities to extract.

    Returns:
        A dictionary containing:
            - status: "success" or "error"
            - data: dict of extracted keywords and query metadata
            - error: error details if status is "error"
    """
    try:
        if not query or not query.strip():
            return {
                "status": "error",
                "data": None,
                "error": "Query parameter cannot be empty."
            }

        # Simulated analysis logic
        tokens = query.strip().split()
        keywords = list(set(tokens))[:max_results]
        
        # Access session state if tool_context is present
        user_id = "unknown"
        if tool_context and hasattr(tool_context, "state"):
            user_id = tool_context.state.get("user_id", "anonymous")
            tool_context.state["temp:last_query_analyzed"] = query

        return {
            "status": "success",
            "data": {
                "user_id": user_id,
                "original_query": query,
                "keywords": keywords,
                "word_count": len(tokens)
            },
            "error": None
        }
    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": f"Failed to analyze query: {str(e)}"
        }


def safe_calculator(expression: str, tool_context: Optional[ToolContext] = None) -> Dict[str, Any]:
    """Evaluates basic mathematical expressions safely.

    Args:
        expression: Simple mathematical string expression (e.g. '12 * 4 + 7').

    Returns:
        A dictionary containing:
            - status: "success" or "error"
            - data: dict with calculated numerical value
            - error: error details if evaluation fails
    """
    try:
        # Sanitization check
        allowed_chars = set("0123456789+-*/(). ")
        if not set(expression).issubset(allowed_chars):
            return {
                "status": "error",
                "data": None,
                "error": "Invalid characters in mathematical expression."
            }

        # Safe evaluation
        result = eval(expression, {"__builtins__": None}, {})
        
        if tool_context and hasattr(tool_context, "state"):
            tool_context.state["temp:last_calculation"] = result

        return {
            "status": "success",
            "data": {
                "expression": expression,
                "result": result
            },
            "error": None
        }
    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "error": f"Calculation error: {str(e)}"
        }
