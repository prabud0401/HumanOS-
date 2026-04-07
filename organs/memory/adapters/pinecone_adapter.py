"""
Pinecone vector store adapter — managed similarity index in the cloud.
"""

from __future__ import annotations

import logging
import os
import uuid
from typing import Any

from ..ports import SearchResult, VectorRecord, VectorStorePort

logger = logging.getLogger("humanos.memory.pinecone")


class PineconeAdapter(VectorStorePort):
    """Pinecone index per collection name (index must exist or be created externally)."""

    def __init__(self, api_key: str | None = None, environment: str | None = None) -> None:
        from pinecone import Pinecone

        key = api_key or os.environ.get("PINECONE_API_KEY", "")
        if not key:
            raise ValueError("Pinecone API key required")
        self._pc = Pinecone(api_key=key)
        self._environment = environment

    def _index(self, collection: str):
        return self._pc.Index(collection)

    def store(self, collection: str, records: list[VectorRecord]) -> list[str]:
        idx = self._index(collection)
        ids = [r.id or f"id-{uuid.uuid4().hex}" for r in records]
        vectors = [{"id": i, "values": rec.vector, "metadata": rec.metadata} for i, rec in zip(ids, records)]
        idx.upsert(vectors=vectors)
        return ids

    def search(
        self, collection: str, query_vector: list[float], limit: int
    ) -> list[SearchResult]:
        idx = self._index(collection)
        res = idx.query(vector=query_vector, top_k=limit, include_metadata=True)
        out: list[SearchResult] = []
        for m in res.get("matches") or []:
            mid = m.get("id", "")
            score = float(m.get("score", 0.0))
            meta = dict(m.get("metadata") or {})
            out.append(SearchResult(id=mid, score=score, metadata=meta, document=meta.pop("_document", "")))
        return out

    def delete(self, collection: str, ids: list[str]) -> int:
        idx = self._index(collection)
        idx.delete(ids=ids)
        return len(ids)

    def list_collections(self) -> list[str]:
        li = self._pc.list_indexes()
        if hasattr(li, "names"):
            return list(li.names())
        return [getattr(i, "name", str(i)) for i in (li or [])]
