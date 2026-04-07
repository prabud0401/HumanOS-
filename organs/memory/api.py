"""
Memory REST API — Django Ninja routes for recall and ingest.
"""

import logging

from core.bus import emit

logger = logging.getLogger("humanos.memory.api")

try:
    from ninja import Router

    router = Router(tags=["memory"])

    @router.post("/remember")
    def remember(request, body: dict):
        from .services import get_memory_service

        text = body.get("text", "")
        collection = body.get("collection", "default")
        meta = body.get("metadata") or {}
        entry_id = get_memory_service().remember(text, collection, meta)
        emit(
            "knowledge.stored",
            "memory",
            payload={"entry_id": entry_id, "collection": collection, "via": "api"},
        )
        return {"entry_id": entry_id}

    @router.post("/recall")
    def recall(request, body: dict):
        from .services import get_memory_service

        query = body.get("query", "")
        collection = body.get("collection")
        limit = body.get("limit")
        results = get_memory_service().recall(query, collection, limit)
        emit(
            "knowledge.recalled",
            "memory",
            payload={
                "query": query[:500],
                "hits": [r.id for r in results],
                "scores": [r.score for r in results],
                "via": "api",
            },
        )
        return {
            "results": [
                {"id": r.id, "score": r.score, "document": r.document, "metadata": r.metadata}
                for r in results
            ]
        }

    @router.get("/collections")
    def collections(request):
        from .services import get_vector_store

        return {"collections": get_vector_store().list_collections()}

    @router.get("/health")
    def health(request):
        from .health import check

        status, message, details = check()
        return {"status": status.value, "message": message, **details}

except ImportError:
    logger.debug("django-ninja not installed — memory API not registered")
    router = None
