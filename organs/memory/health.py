"""
Memory organ health — vector backend reachability.
"""

from core.pulse import HealthStatus


def check() -> tuple[HealthStatus, str, dict]:
    details: dict = {}
    try:
        from .dna import get_memory_dna
        from .services import get_memory_service, get_vector_store

        dna = get_memory_dna()
        details["vector_db_type"] = dna.vector_db_type
        details["storage_path"] = dna.storage_path
        store = get_vector_store()
        details["adapter"] = type(store).__name__
        cols = store.list_collections()
        details["collection_count"] = len(cols)

        svc = get_memory_service()
        _ = svc  # ensure service graph loads

        if type(store).__name__ == "_InMemoryVectorStore":
            return (
                HealthStatus.DEGRADED,
                "Using in-memory vector store (no persistent ChromaDB/Pinecone)",
                details,
            )

        return HealthStatus.HEALTHY, "Memory / vector store operational", details
    except Exception as exc:
        details["error"] = str(exc)
        return HealthStatus.UNHEALTHY, f"Memory check failed: {exc}", details
