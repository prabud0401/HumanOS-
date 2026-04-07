"""
Memory service — orchestrates vector store, knowledge port, and ORM metadata.
"""

from __future__ import annotations

import hashlib
import logging
import time
import uuid
from typing import Any

from .dna import get_memory_dna
from .models import Collection, KnowledgeEntry, SearchLog
from .ports import KnowledgePort, SearchResult, VectorRecord, VectorStorePort

logger = logging.getLogger("humanos.memory.services")


class _InMemoryVectorStore(VectorStorePort):
    """Fallback when ChromaDB / Pinecone clients are not installed."""

    def __init__(self) -> None:
        self._collections: dict[str, dict[str, VectorRecord]] = {}

    def store(self, collection: str, records: list[VectorRecord]) -> list[str]:
        bucket = self._collections.setdefault(collection, {})
        ids = []
        for r in records:
            rid = r.id or f"mem-{uuid.uuid4().hex}"
            bucket[rid] = VectorRecord(id=rid, vector=r.vector, metadata=r.metadata, document=r.document)
            ids.append(rid)
        return ids

    def search(
        self, collection: str, query_vector: list[float], limit: int
    ) -> list[SearchResult]:
        bucket = self._collections.get(collection, {})
        scored: list[tuple[float, VectorRecord]] = []
        for rec in bucket.values():
            if len(rec.vector) != len(query_vector):
                continue
            dot = sum(a * b for a, b in zip(rec.vector, query_vector))
            scored.append((dot, rec))
        scored.sort(key=lambda x: x[0], reverse=True)
        out: list[SearchResult] = []
        for score, rec in scored[:limit]:
            sim = max(0.0, min(1.0, (score + 1) / 2))
            out.append(SearchResult(id=rec.id, score=sim, metadata=dict(rec.metadata), document=rec.document))
        return out

    def delete(self, collection: str, ids: list[str]) -> int:
        bucket = self._collections.get(collection, {})
        n = 0
        for i in ids:
            if i in bucket:
                del bucket[i]
                n += 1
        return n

    def list_collections(self) -> list[str]:
        return list(self._collections.keys())


def _pseudo_embedding(text: str, dimensions: int) -> list[float]:
    """Deterministic pseudo-vector for dev when no embedding model is wired."""
    vec: list[float] = []
    seed = hashlib.sha256(text.encode()).digest()
    while len(vec) < dimensions:
        seed = hashlib.sha256(seed).digest()
        for b in seed:
            vec.append((b / 255.0) * 2.0 - 1.0)
    return vec[:dimensions]


class MemoryService(KnowledgePort):
    """Knowledge operations backed by a VectorStorePort."""

    def __init__(self, store: VectorStorePort):
        self._store = store

    def remember(self, text: str, collection: str, metadata: dict[str, Any] | None = None) -> str:
        dna = get_memory_dna()
        meta = dict(metadata or {})
        coll, _ = Collection.objects.get_or_create(
            slug=collection,
            defaults={"name": collection.replace("_", " ").title()},
        )
        vector = _pseudo_embedding(text, dna.embedding_dimensions)
        entry_id = meta.get("entry_id") or f"k-{uuid.uuid4().hex}"
        record = VectorRecord(
            id=entry_id,
            vector=vector,
            metadata={**meta, "title": meta.get("title", "")},
            document=text[:32000],
        )
        self._store.store(collection, [record])
        KnowledgeEntry.objects.update_or_create(
            entry_id=entry_id,
            defaults={
                "collection": coll,
                "title": meta.get("title", "")[:512],
                "source_organ": meta.get("source_organ", ""),
                "source_event_id": meta.get("source_event_id", ""),
                "content_preview": text[:2000],
                "extra": {k: v for k, v in meta.items() if k not in ("title", "source_organ", "source_event_id")},
            },
        )
        coll.record_count = KnowledgeEntry.objects.filter(collection=coll).count()
        coll.save(update_fields=["record_count", "updated_at"])
        return entry_id

    def recall(self, query: str, collection: str | None, limit: int | None = None) -> list[SearchResult]:
        dna = get_memory_dna()
        lim = limit if limit is not None else dna.max_results
        coll_name = collection or "default"
        start = time.monotonic()
        qvec = _pseudo_embedding(query, dna.embedding_dimensions)
        results = self._store.search(coll_name, qvec, lim)
        filtered = [r for r in results if r.score >= dna.similarity_threshold]
        elapsed_ms = (time.monotonic() - start) * 1000
        coll = Collection.objects.filter(slug=coll_name).first()
        top = filtered[0].score if filtered else None
        SearchLog.objects.create(
            query_text=query[:4000],
            collection=coll,
            result_count=len(filtered),
            top_score=top,
            latency_ms=round(elapsed_ms, 2),
            requested_by="memory_service",
        )
        return filtered

    def forget(self, entry_ids: list[str], collection: str | None = None) -> int:
        coll_name = collection or "default"
        return self._store.delete(coll_name, entry_ids)


_service: MemoryService | None = None


def get_vector_store() -> VectorStorePort:
    dna = get_memory_dna()
    vtype = (dna.vector_db_type or "").lower()
    if vtype == "pinecone":
        try:
            from .adapters.pinecone_adapter import PineconeAdapter

            return PineconeAdapter()
        except Exception as exc:
            logger.warning("Pinecone unavailable (%s); using in-memory vector store", exc)
            return _InMemoryVectorStore()
    try:
        from .adapters.chromadb_adapter import ChromaDBAdapter

        return ChromaDBAdapter(persist_path=dna.storage_path)
    except ImportError as exc:
        logger.warning("ChromaDB unavailable (%s); using in-memory vector store", exc)
        return _InMemoryVectorStore()


def get_memory_service() -> MemoryService:
    global _service
    if _service is None:
        _service = MemoryService(store=get_vector_store())
    return _service
