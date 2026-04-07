"""
NLP enrichment — optional spaCy/transformers; deterministic fallback when absent.
"""

from __future__ import annotations

import re
from typing import Any

from ..ports import TransformPort, TransformResult


class NlpTransformAdapter(TransformPort):
    def __init__(self, model_name: str = "stub"):
        self._model_name = model_name

    def transform(self, data: dict[str, Any], ruleset: str | None = None) -> TransformResult:
        return TransformResult(data=dict(data), valid=True, metadata={"ruleset": ruleset})

    def validate(self, data: dict[str, Any], schema: dict[str, Any]) -> TransformResult:
        required = schema.get("required", [])
        missing = [k for k in required if k not in data]
        return TransformResult(data=data, valid=len(missing) == 0, errors=[f"missing:{k}" for k in missing])

    def enrich(self, data: dict[str, Any], context: dict[str, Any]) -> TransformResult:
        text = data.get("text") or context.get("text") or ""
        entities = self._extract_entities(text)
        out = {**data, "entities": entities, "nlp_model": self._model_name}
        return TransformResult(data=out, valid=True, metadata={"entity_count": len(entities)})

    def _extract_entities(self, text: str) -> list[dict[str, Any]]:
        try:
            import spacy

            nlp = spacy.load(self._model_name)
            doc = nlp(text[:100000])
            return [{"text": e.text, "label": e.label_} for e in doc.ents]
        except Exception:
            # Capitalized token heuristic fallback
            caps = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", text)
            return [{"text": c, "label": "HEURISTIC"} for c in caps[:50]]
