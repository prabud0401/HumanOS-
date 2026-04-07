"""
Tests for Brain LLM adapters.
"""

import pytest
from organs.brain.ports import LLMRequest, LLMResponse


class TestClaudeAdapter:
    def test_adapter_requires_api_key(self):
        from organs.brain.adapters.claude_adapter import ClaudeAdapter
        adapter = ClaudeAdapter(api_key="")
        assert not adapter.is_available()

    def test_adapter_model_name(self):
        from organs.brain.adapters.claude_adapter import ClaudeAdapter
        adapter = ClaudeAdapter(model="claude-opus-4-6")
        assert adapter.get_model_name() == "claude-opus-4-6"


class TestOpenAIAdapter:
    def test_adapter_requires_api_key(self):
        from organs.brain.adapters.openai_adapter import OpenAIAdapter
        adapter = OpenAIAdapter(api_key="")
        assert not adapter.is_available()


class TestLocalAdapter:
    def test_adapter_model_name(self):
        from organs.brain.adapters.local_adapter import LocalAdapter
        adapter = LocalAdapter(model="llama3")
        assert adapter.get_model_name() == "local:llama3"
