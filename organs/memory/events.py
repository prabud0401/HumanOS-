"""
Memory events — knowledge lifecycle on the bus.
"""

import logging

from core.bus import Event, emit

logger = logging.getLogger("humanos.memory.events")

PUBLISHES = [
    "knowledge.stored",
    "knowledge.recalled",
    "memory.full",
]

SUBSCRIBES = [
    "knowledge.extracted",
    "search.requested",
]


def handle_event(event: Event) -> None:
    handlers = {
        "knowledge.extracted": _on_knowledge_extracted,
        "search.requested": _on_search_requested,
    }
    fn = handlers.get(event.type)
    if fn:
        fn(event)
    else:
        logger.warning("Memory received unhandled event: %s", event.type)


def _on_knowledge_extracted(event: Event) -> None:
    from .services import get_memory_service

    text = (event.payload or {}).get("text", "")
    collection = (event.payload or {}).get("collection", "default")
    meta = (event.payload or {}).get("metadata") or {}
    meta.setdefault("source_event_id", event.event_id)
    entry_id = get_memory_service().remember(text, collection, meta)
    emit(
        "knowledge.stored",
        "memory",
        payload={"entry_id": entry_id, "collection": collection},
    )


def _on_search_requested(event: Event) -> None:
    from .services import get_memory_service

    query = (event.payload or {}).get("query", "")
    collection = (event.payload or {}).get("collection")
    limit = (event.payload or {}).get("limit")
    results = get_memory_service().recall(query, collection, limit)
    emit(
        "knowledge.recalled",
        "memory",
        payload={
            "query": query,
            "hits": [r.id for r in results],
            "scores": [r.score for r in results],
        },
    )
