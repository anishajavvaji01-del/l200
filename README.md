# Enterprise Intelligence & Data Operations Agent

A production-grade Python Agent Development Kit (ADK) enterprise assistant for multi-modal data processing, user query triage, and automated analytics synthesis.

---

## 🏗️ System Architecture & Engineering Highlights

This codebase implements a modern, production-grade agent architecture following enterprise design patterns:

### 1. Robust Tool Design & Error Handling (`app/tools.py`)
- **Explicit Schemas & Types**: Utilizes strict Pydantic models (`AnalysisInput`, `CalculationInput`) and Google-style docstrings for transparent parameter contracts.
- **Guided Error Recovery**: Implements structured JSON dictionary returns (`{"status": "success"|"error", ...}`) to guide LLMs through error handling without breaking execution.
- **Session State Access**: Tools accept `tool_context: ToolContext` to inspect and update session/user-scoped variables cleanly.

### 2. Context Management & Memory (`app/memory.py`)
- **Dynamic Prompt Constitutions**: System prompts dynamically resolve session, user-scoped, and application state placeholders.
- **History Compaction & Summarization**: Configured with `EventsCompactionConfig` and `LlmEventSummarizer` to handle long multi-turn interactions efficiently.
- **Multi-Scoped State & Async Memory Persistence**: Manages state across `user:`, `app:`, and `temp:` namespaces, integrated with async memory consolidation hooks.

### 3. Multi-Agent Orchestration & Logic (`app/agent.py`)
- **Sequential Multi-Agent Pipeline**: Chains a fast Flash-powered `TriageAgent` (`gemini-flash-latest`) for intent classification into a high-capacity Pro-powered `SynthesisAgent` (`gemini-pro-latest`) for complex reasoning.
- **Strategic Model Routing**: Optimizes latency and token cost by assigning sub-tasks to the appropriate model tier.
- **Human-In-The-Loop (HITL)**: Supports explicit execution pauses for human approval via `request_input` and resumable session state.

### 4. Observability, Security & Tracing (`app/plugins.py`)
- **Structured JSON Logging**: Implements a custom `ObservabilityPlugin` capturing lifecycle events, execution latency (ms), and token usage.
- **Intent vs. Outcome Capture**: Explicitly logs user intent alongside final agent output to simplify accuracy auditing.
- **Automated PII Redaction**: Regex-based redaction of emails, phone numbers, and SSNs prior to log storage.

### 5. Quality Assurance & Evaluation (`tests/`)
- **Unit Test Suite**: Full `pytest` unit coverage in `tests/unit/test_tools.py`.
- **Evaluation Harness**: Configured with `tests/eval/eval_config.yaml` and golden evaluation dataset `tests/eval/datasets/eval_dataset.json`.

---

## 📁 Repository Layout

```
.
├── pyproject.toml
├── .env.example
├── README.md
├── app/
│   ├── __init__.py
│   ├── agent.py
│   ├── tools.py
│   ├── plugins.py
│   └── memory.py
└── tests/
    ├── unit/
    │   └── test_tools.py
    └── eval/
        ├── eval_config.yaml
        └── datasets/
            └── eval_dataset.json
```

---

## ⚙️ Quickstart & Setup

1. **Install Dependencies**:
   ```bash
   pip install -e .
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Add your GEMINI_API_KEY
   ```

3. **Run Unit Tests**:
   ```bash
   pytest
   ```
