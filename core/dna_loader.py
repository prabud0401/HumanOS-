"""
DNA Loader — Parses identity.yaml and injects configuration into all organs.

At startup, the system reads the DNA file and builds a config object that
every organ can access. Different DNA = completely different twin behavior
with zero code changes.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any

import yaml


DNA_PATH = os.environ.get(
    "HUMANOS_DNA_PATH",
    str(Path(__file__).resolve().parent.parent / "dna" / "identity.yaml"),
)


@dataclass
class ChromosomeIdentity:
    name: str = ""
    full_name: str = ""
    nickname: str = ""
    timezone: str = "UTC"
    locale: str = "en-US"
    avatar: str | None = None


@dataclass
class ChromosomePersonality:
    communication_style: str = "direct"
    decision_speed: str = "fast"
    risk_tolerance: str = "moderate"
    work_hours: dict = field(default_factory=lambda: {"start": "09:00", "end": "18:00"})
    response_tone: str = "professional-casual"
    delegation_preference: str = "high"
    escalation_threshold: float = 0.6


@dataclass
class ChromosomeAI:
    primary_model: str = "claude-sonnet-4-5"
    adapter: str = "claude_local"
    fallback_model: str = "claude-sonnet-4-5"
    temperature: float = 0.3
    max_context_tokens: int = 200000
    speech_to_text: str = "whisper-large-v3"
    embedding_model: str = "text-embedding-3-large"
    vector_db: str = "chromadb"


@dataclass
class DNA:
    """The complete genetic code of this digital twin."""

    identity: ChromosomeIdentity = field(default_factory=ChromosomeIdentity)
    personality: ChromosomePersonality = field(default_factory=ChromosomePersonality)
    ai_engine: ChromosomeAI = field(default_factory=ChromosomeAI)
    professional: dict = field(default_factory=dict)
    connections: dict = field(default_factory=dict)
    financial: dict = field(default_factory=dict)
    knowledge: dict = field(default_factory=dict)
    agents: dict = field(default_factory=dict)
    preferences: dict = field(default_factory=dict)
    security: dict = field(default_factory=dict)
    _raw: dict = field(default_factory=dict, repr=False)

    def get(self, dotpath: str, default: Any = None) -> Any:
        """Access nested config via dot notation: dna.get('ai_engine.primary_model')"""
        keys = dotpath.split(".")
        value = self._raw
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key, default)
            else:
                return default
        return value


_dna_instance: DNA | None = None


def _parse_chromosome(raw: dict, key: str, cls: type):
    data = raw.get(key, {})
    if not isinstance(data, dict):
        return cls()
    valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
    return cls(**{k: v for k, v in data.items() if k in valid_fields})


def load_dna(path: str | None = None) -> DNA:
    """Load and parse identity.yaml into a DNA dataclass. Cached after first call."""
    global _dna_instance
    if _dna_instance is not None:
        return _dna_instance

    path = path or DNA_PATH
    if not Path(path).exists():
        _dna_instance = DNA()
        return _dna_instance

    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    _dna_instance = DNA(
        identity=_parse_chromosome(raw, "identity", ChromosomeIdentity),
        personality=_parse_chromosome(raw, "personality", ChromosomePersonality),
        ai_engine=_parse_chromosome(raw, "ai_engine", ChromosomeAI),
        professional=raw.get("professional", {}),
        connections=raw.get("connections", {}),
        financial=raw.get("financial", {}),
        knowledge=raw.get("knowledge", {}),
        agents=raw.get("agents", {}),
        preferences=raw.get("preferences", {}),
        security=raw.get("security", {}),
        _raw=raw,
    )
    return _dna_instance


def reset_dna():
    """Clear cached DNA — useful for testing."""
    global _dna_instance
    _dna_instance = None


def get_dna() -> DNA:
    """Get the current DNA instance (loads if needed)."""
    return load_dna()
