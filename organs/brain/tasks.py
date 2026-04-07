"""
Brain Celery Tasks — Async background processing for AI operations.

Heavy AI work (multi-step reasoning, batch analysis) runs as Celery tasks
so the main event loop stays responsive.
"""

import logging

logger = logging.getLogger("humanos.brain.tasks")

# Celery app will be configured in the Django settings.
# For now, define task signatures that can be wired up later.

try:
    from celery import shared_task

    @shared_task(name="brain.analyze_context")
    def analyze_context(context: str, knowledge_ids: list[str] | None = None) -> dict:
        """Analyze a context string with optional knowledge references."""
        from .services import get_brain_service
        service = get_brain_service()
        return service.analyze(context, knowledge_ids or [])

    @shared_task(name="brain.make_decision")
    def make_decision(analysis: dict, constraints: dict | None = None) -> dict:
        """Make a decision based on an analysis result."""
        from .services import get_brain_service
        service = get_brain_service()
        return service.decide(analysis, constraints)

    @shared_task(name="brain.batch_summarize")
    def batch_summarize(texts: list[str]) -> list[str]:
        """Summarize a batch of texts (e.g., meeting transcripts)."""
        from .services import get_brain_service
        service = get_brain_service()
        return [service.summarize(text) for text in texts]

except ImportError:
    logger.debug("Celery not installed — brain tasks registered as stubs")

    def analyze_context(context, knowledge_ids=None):
        raise RuntimeError("Celery required for async brain tasks")

    def make_decision(analysis, constraints=None):
        raise RuntimeError("Celery required for async brain tasks")

    def batch_summarize(texts):
        raise RuntimeError("Celery required for async brain tasks")
