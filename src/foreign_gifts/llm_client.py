"""Thin wrapper over the `llm` library so every pipeline stage resolves models
(Anthropic, Ollama, or anything else `llm` supports) the same way.

Set the ANTHROPIC_API_KEY environment variable, or run `uv run llm keys set
anthropic`. For Ollama, install the model locally (e.g. `ollama pull
llama3.2`) — no API key needed. Run `uv run llm models` to list everything
`llm` currently knows about.
"""

import os

import llm

DEFAULT_MODEL = os.environ.get("GIFTS_MODEL", "claude-haiku-4.5")


def get_model(model_id: str | None = None):
    """Return an `llm` model instance, defaulting to GIFTS_MODEL / claude-haiku-4.5."""
    return llm.get_model(model_id or DEFAULT_MODEL)
