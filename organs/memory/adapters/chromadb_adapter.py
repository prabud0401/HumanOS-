"""
ChromaDB vector store adapter — local persistent embeddings.
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

from ..ports import SearchResult, VectorRecord, VectorStorePort

logger = logging.getLogger("humanos.memory.chromadb")


def _chroma_metadata(meta: dict[str, Any]) -> dict[str, Any]:
    flat: dict[str, Any] = {}
    for k, v in meta.items():
        if isinstance(v, (str, int, float, bool)) or v is None:
            flat[k] = v
        else:
            flat[k] = json.dumps(v, default=str)
    return flat


class ChromaDBAdapter(VectorStorePort):
    """ChromaDB implementation of VectorStorePort."""

    def __init__(self, persist_path: str) -> None:
        import chromadb
        from chromadb.config import Settings

        self._client = chromadb.PersistentClient(
            path=persist_path,
            settings=Settings(anonymized_telemetry=False),
        )

    def store(self, collection: str, records: list[VectorRecord]) -> list[str]:
        coll = self._client.get_or_create_collection(collection)
        ids = [r.id or f"id-{uuid.uuid4().hex}" for r in records]
        embeddings = [r.vector for r in records]
        documents = [r.document or "" for r in records]
        metadatas: list[dict[str, Any]] | None = [_chroma_metadata(r.metadata) for r in records]
        coll.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
        return ids

    def search(
        self, collection: str, query_vector: list[float], limit: int
    ) -> list[SearchResult]:
        coll = self._client.get_or_create_collection(collection)
        raw = coll.query(query_embeddings=[query_vector], n_results=limit, include=["metadatas", "documents", "distances"])
        out: list[SearchResult] = []
        ids_list = raw.get("ids") or [[]]
        metas = raw.get("metadatas") or [[]]
        docs = raw.get("documents") or [[]]
        dists = raw.get("distances") or [[]]
        for i, eid in enumerate(ids_list[0] or []):
            dist = (dists[0] or [0.0])[i] if dists and dists[0] else 0.0
            score = 1.0 / (1.0 + float(dist))
            meta = (metas[0] or [{}])[i] if metas and metas[0] else {}
            doc = (docs[0] or [""])[i] if docs and docs[0] else ""
            out.append(SearchResult(id=eid, score=score, metadata=meta or {}, document=doc or ""))
        return out

    def delete(self, collection: str, ids: list[str]) -> int:
        coll = self._client.get_or_create_collection(collection)
        coll.delete(ids=ids)
        return len(ids)

    def list_collections(self) -> list[str]:
        return [c.name for c in self._client.list_collections()]
