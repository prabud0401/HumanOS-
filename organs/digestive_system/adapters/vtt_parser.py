"""
VTT/SRT parser — builds ParseResult with timed cues.
Also provides a minimal .eml parser via stdlib.
"""

from __future__ import annotations

import email
import re
from email import policy
from pathlib import Path

from ..ports import ParseResult, ParserPort

TIMING_RE = re.compile(
    r"(?P<start>\d{2}:\d{2}:\d{2}[.,]\d{3})\s*-->\s*(?P<end>\d{2}:\d{2}:\d{2}[.,]\d{3})"
)


def _read(path: Path | str) -> str:
    p = Path(path)
    return p.read_text(encoding="utf-8", errors="replace")


class VttParserAdapter(ParserPort):
    def parse_vtt(self, path: Path | str) -> ParseResult:
        raw = _read(path)
        segments: list[dict] = []
        current: dict | None = None
        text_buf: list[str] = []

        for line in raw.splitlines():
            line = line.strip()
            m = TIMING_RE.search(line)
            if m:
                if current and text_buf:
                    current["text"] = " ".join(text_buf).strip()
                    segments.append(current)
                current = {"start": m.group("start"), "end": m.group("end")}
                text_buf = []
                continue
            if line.startswith("WEBVTT") or line.isdigit() or not line:
                continue
            if current is not None:
                text_buf.append(line)

        if current and text_buf:
            current["text"] = " ".join(text_buf).strip()
            segments.append(current)

        full_text = "\n".join(s["text"] for s in segments if s.get("text"))
        return ParseResult(
            format="vtt",
            text=full_text,
            segments=segments,
            metadata={"cues": len(segments)},
        )

    def parse_pdf(self, path: Path | str) -> ParseResult:
        raise NotImplementedError("Use PDF adapter")

    def parse_email(self, path: Path | str) -> ParseResult:
        raw = Path(path).read_bytes()
        msg = email.message_from_bytes(raw, policy=policy.default)
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_content()
                    break
        else:
            body = msg.get_body(preferencelist=("plain", "html"))
            body = body.get_content() if body else ""
        return ParseResult(
            format="eml",
            text=str(body),
            segments=[{"header": k, "value": v} for k, v in msg.items()],
            metadata={"subject": msg.get("subject", "")},
        )
