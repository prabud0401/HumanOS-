"""
Brain Service Layer — Orchestrates ports, adapters, and business logic.

The service layer is the "grey matter" — it ties together the LLM port,
decision port, and domain models without coupling to any specific adapter.
"""

import logging
from typing import Any

from core.dna_loader import get_dna
from core.bus import emit

from .ports import LLMPort, LLMRequest, DecisionPort

logger = logging.getLogger("humanos.brain.services")


class BrainService:
    """High-level brain operations — used by events, tasks, and API."""

    def __init__(self, llm: LLMPort):
        self._llm = llm

    def analyze(self, context: str, knowledge_ids: list[str] | None = None) -> dict[str, Any]:
        dna = get_dna()
        system = (
            f"You are the AI brain of {dna.identity.name}'s digital twin. "
            f"Analyze the following context and provide structured insights."
        )
        request = LLMRequest(
            prompt=f"Context:\n{context}\n\nProvide a structured analysis with key_points, risks, and recommended_actions.",
            system_prompt=system,
            temperature=dna.ai_engine.temperature,
        )
        response = self._llm.generate(request)
        return {
            "analysis": response.content,
            "model": response.model,
            "tokens": response.tokens_input + response.tokens_output,
            "latency_ms": response.latency_ms,
        }

    def decide(self, analysis: dict, constraints: dict | None = None) -> dict[str, Any]:
        prompt = f"Based on this analysis:\n{analysis.get('analysis', '')}\n"
        if constraints:
            prompt += f"\nConstraints: {constraints}\n"
        prompt += "\nMake a decision. Return: action, reasoning, confidence (0-1)."

        request = LLMRequest(prompt=prompt, temperature=0.2)
        response = self._llm.generate(request)

        decision = {
            "action": response.content,
            "reasoning": "LLM-generated",
            "confidence": 0.7,
            "model": response.model,
        }
        emit("decision.made", "brain", payload=decision)
        return decision

    def summarize(self, text: str) -> str:
        request = LLMRequest(
            prompt=f"Summarize concisely:\n\n{text}",
            temperature=0.1,
            max_tokens=1024,
        )
        return self._llm.generate(request).content


_service: BrainService | None = None


def get_brain_service() -> BrainService:
    """Get or create the brain service with the configured LLM adapter."""
    global _service
    if _service is not None:
        return _service

    dna = get_dna()
    adapter_name = dna.ai_engine.adapter

    if adapter_name == "openai":
        from .adapters.openai_adapter import OpenAIAdapter
        llm = OpenAIAdapter(model=dna.ai_engine.primary_model)
    elif adapter_name == "local":
        from .adapters.local_adapter import LocalAdapter
        llm = LocalAdapter(model=dna.ai_engine.primary_model)
    else:
        from .adapters.claude_adapter import ClaudeAdapter
        llm = ClaudeAdapter(model=dna.ai_engine.primary_model)

    _service = BrainService(llm=llm)
    return _service
