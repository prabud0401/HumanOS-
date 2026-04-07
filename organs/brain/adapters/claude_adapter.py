"""
Claude Adapter — Primary LLM adapter using Anthropic's Claude API.
Supports both direct API calls and local Paperclip proxy.
"""

import time
import logging
import os

from ..ports import LLMPort, LLMRequest, LLMResponse

logger = logging.getLogger("humanos.brain.claude")


class ClaudeAdapter(LLMPort):
    """Adapter for Anthropic Claude models."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None, model: str = "claude-sonnet-4-5"):
        self._api_key = api_key or os.environ.get("CLAUDE_API_KEY", "")
        self._base_url = base_url or os.environ.get("CLAUDE_BASE_URL", "https://api.anthropic.com")
        self._model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(
                    api_key=self._api_key,
                    base_url=self._base_url if self._base_url != "https://api.anthropic.com" else None,
                )
            except ImportError:
                raise ImportError("anthropic package required: pip install anthropic")
        return self._client

    def generate(self, request: LLMRequest) -> LLMResponse:
        client = self._get_client()
        model = request.model or self._model
        start = time.monotonic()

        kwargs = {
            "model": model,
            "max_tokens": request.max_tokens,
            "messages": [{"role": "user", "content": request.prompt}],
        }
        if request.system_prompt:
            kwargs["system"] = request.system_prompt
        if request.temperature is not None:
            kwargs["temperature"] = request.temperature

        response = client.messages.create(**kwargs)
        elapsed = (time.monotonic() - start) * 1000

        return LLMResponse(
            content=response.content[0].text,
            model=model,
            tokens_input=response.usage.input_tokens,
            tokens_output=response.usage.output_tokens,
            latency_ms=round(elapsed, 2),
        )

    def is_available(self) -> bool:
        try:
            client = self._get_client()
            return client is not None and bool(self._api_key)
        except Exception:
            return False

    def get_model_name(self) -> str:
        return self._model
