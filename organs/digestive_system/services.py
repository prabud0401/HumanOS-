"""
Digestive System Service — Parsing, transformation, and knowledge persistence.
"""

from __future__ import annotations

import logging
import uuid
from pathlib import Path

from django.db import transaction

from core.bus import emit

from .dna import get_digestive_system_dna
from .models import ExtractedKnowledge, ProcessingJob, TransformationRule
from .ports import ParseResult, ParserPort, TransformPort, TransformResult
from .adapters.nlp_adapter import NlpTransformAdapter
from .adapters.pdf_parser import PdfParserAdapter
from .adapters.vtt_parser import VttParserAdapter

logger = logging.getLogger("humanos.digestive.services")


class CompositeParserPort(ParserPort):
    def __init__(self):
        self._vtt = VttParserAdapter()
        self._pdf = PdfParserAdapter()

    def parse_vtt(self, path: Path | str) -> ParseResult:
        return self._vtt.parse_vtt(path)

    def parse_pdf(self, path: Path | str) -> ParseResult:
        return self._pdf.parse_pdf(path)

    def parse_email(self, path: Path | str) -> ParseResult:
        return self._vtt.parse_email(path)


class DigestiveSystemService:
    def __init__(self, parser: ParserPort | None = None, transformer: TransformPort | None = None):
        self._parser = parser or CompositeParserPort()
        self._transformer = transformer or NlpTransformAdapter(model_name="stub")

    def _ensure_format_allowed(self, fmt: str) -> None:
        dna = get_digestive_system_dna()
        if fmt.lower() not in dna.supported_formats:
            raise ValueError(f"Format {fmt} not in DNA supported_formats")

    def _ensure_size(self, path: Path) -> None:
        dna = get_digestive_system_dna()
        sz = path.stat().st_size
        if sz > dna.max_file_size:
            raise ValueError(f"File exceeds max_file_size ({sz} > {dna.max_file_size})")

    def parse_source(self, path: Path | str, fmt: str) -> ParseResult:
        p = Path(path)
        self._ensure_format_allowed(fmt)
        self._ensure_size(p)
        fmt = fmt.lower()
        if fmt in ("vtt", "srt"):
            return self._parser.parse_vtt(p)
        if fmt == "pdf":
            return self._parser.parse_pdf(p)
        if fmt in ("eml", "email", "mime"):
            return self._parser.parse_email(p)
        raise ValueError(f"Unsupported format for parser: {fmt}")

    def run_job(self, source_uri: str, fmt: str) -> ProcessingJob:
        dna = get_digestive_system_dna()
        self._transformer = NlpTransformAdapter(model_name=dna.nlp_model)

        job_id = f"job-{uuid.uuid4().hex[:12]}"
        with transaction.atomic():
            job = ProcessingJob.objects.create(
                job_id=job_id,
                source_uri=source_uri,
                format=fmt,
                status=ProcessingJob.Status.RUNNING,
            )
        try:
            result = self.parse_source(source_uri, fmt)
            enriched = self._transformer.enrich(
                {"text": result.text, "segments": result.segments},
                {"rules": dna.extraction_rules},
            )
            if not enriched.valid:
                raise RuntimeError(enriched.errors)

            chunks = self._split_knowledge(enriched.data.get("text", result.text))
            for i, chunk in enumerate(chunks):
                kid = f"k-{job_id}-{i}"
                ExtractedKnowledge.objects.create(
                    knowledge_id=kid,
                    job=job,
                    kind=ExtractedKnowledge.Kind.TRANSCRIPT_CHUNK,
                    title=f"chunk-{i}",
                    content=chunk,
                    confidence=0.9,
                    metadata={"entities": enriched.data.get("entities", [])},
                )

            job.status = ProcessingJob.Status.SUCCEEDED
            job.stats = {
                "segments": len(result.segments),
                "knowledge_chunks": len(chunks),
                "format": result.format,
            }
            job.save(update_fields=["status", "stats", "updated_at"])

            emit(
                "knowledge.extracted",
                "digestive_system",
                payload={"job_id": job.job_id, "chunks": len(chunks)},
            )
            emit(
                "data.transformed",
                "digestive_system",
                payload={"job_id": job.job_id, "metadata": result.metadata},
            )
        except Exception as exc:
            logger.exception("Processing job failed")
            job.status = ProcessingJob.Status.FAILED
            job.error_message = str(exc)
            job.save(update_fields=["status", "error_message", "updated_at"])
            emit(
                "processing.failed",
                "digestive_system",
                payload={"job_id": job.job_id, "error": str(exc)},
            )
        return job

    def _split_knowledge(self, text: str, max_chars: int = 4000) -> list[str]:
        text = text.strip()
        if not text:
            return []
        return [text[i : i + max_chars] for i in range(0, len(text), max_chars)]

    def apply_rules(self, data: dict) -> TransformResult:
        qs = TransformationRule.objects.filter(is_active=True).order_by("priority")
        current = dict(data)
        errors: list[str] = []
        for rule in qs:
            if rule.rule_type == "map" and isinstance(rule.config, dict):
                for src, dst in rule.config.items():
                    if src in current:
                        current[dst] = current.pop(src)
            elif rule.rule_type == "validate":
                res = self._transformer.validate(current, rule.config)
                if not res.valid:
                    errors.extend(res.errors)
        return TransformResult(data=current, valid=len(errors) == 0, errors=errors)


_service: DigestiveSystemService | None = None


def get_digestive_system_service() -> DigestiveSystemService:
    global _service
    if _service is None:
        _service = DigestiveSystemService()
    return _service
