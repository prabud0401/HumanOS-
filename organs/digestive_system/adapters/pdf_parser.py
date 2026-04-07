"""
PDF text extraction — uses pypdf when available, else raises with clear message.
"""

from __future__ import annotations

from pathlib import Path

from ..ports import ParseResult, ParserPort


class PdfParserAdapter(ParserPort):
    def parse_vtt(self, path: Path | str) -> ParseResult:
        raise NotImplementedError("Use VTT adapter")

    def parse_pdf(self, path: Path | str) -> ParseResult:
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError("pypdf required for PDF parsing") from exc

        reader = PdfReader(str(path))
        texts: list[str] = []
        for page in reader.pages:
            t = page.extract_text() or ""
            texts.append(t)
        full = "\n".join(texts)
        return ParseResult(
            format="pdf",
            text=full,
            segments=[{"page": i, "text": t} for i, t in enumerate(texts)],
            metadata={"pages": len(reader.pages)},
        )

    def parse_email(self, path: Path | str) -> ParseResult:
        from .vtt_parser import VttParserAdapter

        return VttParserAdapter().parse_email(path)
