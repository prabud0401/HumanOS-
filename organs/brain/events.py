"""
Brain Events — Declares what events the Brain publishes and subscribes to.
"""

import logging
from core.bus import Event, emit

logger = logging.getLogger("humanos.brain.events")

PUBLISHES = [
    "decision.made",
    "decision.failed",
    "analysis.complete",
    "brain.overloaded",
]

SUBSCRIBES = [
    "knowledge.extracted",
    "task.requested",
    "meeting.summarized",
    "financial.anomaly",
]


def handle_event(event: Event) -> None:
    """Central event handler — routes incoming events to appropriate logic."""
    handlers = {
        "knowledge.extracted": _on_knowledge_extracted,
        "task.requested": _on_task_requested,
        "meeting.summarized": _on_meeting_summarized,
        "financial.anomaly": _on_financial_anomaly,
    }
    handler = handlers.get(event.type)
    if handler:
        handler(event)
    else:
        logger.warning("Brain received unhandled event type: %s", event.type)


def _on_knowledge_extracted(event: Event) -> None:
    """Process newly extracted knowledge — analyze and decide on actions."""
    logger.info("Brain processing knowledge: %s", event.event_id)
    # TODO: Wire to decision pipeline once adapters are configured
    emit("analysis.complete", "brain", payload={
        "source_event": event.event_id,
        "status": "acknowledged",
    })


def _on_task_requested(event: Event) -> None:
    """Evaluate a task request — decide priority and routing."""
    logger.info("Brain evaluating task request: %s", event.payload.get("task", "unknown"))


def _on_meeting_summarized(event: Event) -> None:
    """Process a meeting summary — extract decisions and action items."""
    logger.info("Brain processing meeting summary: %s", event.event_id)


def _on_financial_anomaly(event: Event) -> None:
    """Evaluate a financial anomaly — decide if action needed."""
    logger.info("Brain evaluating financial anomaly: %s", event.payload.get("type", "unknown"))
