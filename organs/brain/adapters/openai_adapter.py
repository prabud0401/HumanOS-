"""
OpenAI Adapter — Fallback LLM adapter using OpenAI's GPT API.
"""

import time
import logging
import os

from ..ports import LLMPort, LLMRequest, LLMResponse

logger = logging.getLogger("humanos.brain.openai")


class OpenAIAdapter(LLMPort):
    """Adapter for OpenAI GPT models (fallback)."""

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o"):
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self._model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import openai
                self._client = openai.OpenAI(api_key=self._api_key)
            except ImportError:
                raise ImportError("openai package required: pip install openai")
        return self._client

    def generate(self, request: LLMRequest) -> LLMResponse:
        client = self._get_client()
        model = request.model or self._model
        start = time.monotonic()

        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )
        elapsed = (time.monotonic() - start) * 1000

        choice = response.choices[0]
        usage = response.usage

        return LLMResponse(
            content=choice.message.content or "",
            model=model,
            tokens_input=usage.prompt_tokens if usage else 0,
            tokens_output=usage.completion_tokens if usage else 0,
            latency_ms=round(elapsed, 2),
        )

    def is_available(self) -> bool:
        return bool(self._api_key)

    def get_model_name(self) -> str:
        return self._model
