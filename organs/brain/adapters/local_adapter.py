"""
Local / Paperclip Adapter — Routes LLM calls through a local proxy.

Paperclip allows using Claude and other models through a local MCP server,
which means the API key stays local and requests don't leave the machine
unless explicitly configured.
"""

import time
import logging
import os

from ..ports import LLMPort, LLMRequest, LLMResponse

logger = logging.getLogger("humanos.brain.local")


class LocalAdapter(LLMPort):
    """Adapter for local LLM proxy (Paperclip, LM Studio, Ollama, etc.)."""

    def __init__(self, base_url: str | None = None, model: str = "claude-sonnet-4-5"):
        self._base_url = base_url or os.environ.get("LOCAL_LLM_URL", "http://localhost:8080/v1")
        self._model = model

    def generate(self, request: LLMRequest) -> LLMResponse:
        import requests as http

        model = request.model or self._model
        start = time.monotonic()

        payload = {
            "model": model,
            "messages": [],
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
        }
        if request.system_prompt:
            payload["messages"].append({"role": "system", "content": request.system_prompt})
        payload["messages"].append({"role": "user", "content": request.prompt})

        resp = http.post(
            f"{self._base_url}/chat/completions",
            json=payload,
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        elapsed = (time.monotonic() - start) * 1000

        choice = data.get("choices", [{}])[0]
        usage = data.get("usage", {})

        return LLMResponse(
            content=choice.get("message", {}).get("content", ""),
            model=model,
            tokens_input=usage.get("prompt_tokens", 0),
            tokens_output=usage.get("completion_tokens", 0),
            latency_ms=round(elapsed, 2),
        )

    def is_available(self) -> bool:
        import requests as http
        try:
            resp = http.get(f"{self._base_url}/models", timeout=3)
            return resp.status_code == 200
        except Exception:
            return False

    def get_model_name(self) -> str:
        return f"local:{self._model}"
