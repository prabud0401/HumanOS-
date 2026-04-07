"""
Memory Celery tasks — async embedding and bulk ingest.
"""

import logging

logger = logging.getLogger("humanos.memory.tasks")

try:
    from celery import shared_task

    @shared_task(name="memory.embed_and_store")
    def embed_and_store(text: str, collection: str, metadata: dict | None = None) -> dict:
        from .services import get_memory_service

        entry_id = get_memory_service().remember(text, collection, metadata or {})
        return {"entry_id": entry_id, "collection": collection}

    @shared_task(name="memory.batch_recall")
    def batch_recall(queries: list[str], collection: str | None = None) -> list[dict]:
        from .services import get_memory_service

        svc = get_memory_service()
        out = []
        for q in queries:
            hits = svc.recall(q, collection)
            out.append({"query": q, "ids": [h.id for h in hits], "scores": [h.score for h in hits]})
        return out

except ImportError:
    logger.debug("Celery not installed — memory tasks are stubs")

    def embed_and_store(text, collection, metadata=None):
        raise RuntimeError("Celery required for async memory tasks")

    def batch_recall(queries, collection=None):
        raise RuntimeError("Celery required for async memory tasks")
