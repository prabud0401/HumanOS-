"""
Memory DNA — Vector store dimensions, thresholds, and paths from identity.yaml.
"""

from dataclasses import dataclass

from core.dna_loader import get_dna


@dataclass
class MemoryDNA:
    vector_db_type: str
    embedding_dimensions: int
    max_results: int
    similarity_threshold: float
    storage_path: str


def get_memory_dna() -> MemoryDNA:
    """Extract memory / vector config from global DNA."""
    dna = get_dna()
    raw = getattr(dna, "_raw", {}) or {}
    mem = raw.get("memory")
    if not isinstance(mem, dict):
        organs = raw.get("organs")
        if isinstance(organs, dict):
            mem = organs.get("memory", {})
        if not isinstance(mem, dict):
            mem = {}
    knowledge = raw.get("knowledge") if isinstance(raw.get("knowledge"), dict) else {}
    ai = dna.ai_engine
    return MemoryDNA(
        vector_db_type=str(mem.get("vector_db_type", ai.vector_db)),
        embedding_dimensions=int(mem.get("embedding_dimensions", 1536)),
        max_results=int(mem.get("max_results", 20)),
        similarity_threshold=float(mem.get("similarity_threshold", 0.72)),
        storage_path=str(mem.get("storage_path", knowledge.get("storage_path", "./var/chromadb"))),
    )
