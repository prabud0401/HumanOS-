"""
Hands Events — Task lifecycle and action notifications.
"""

import logging
import uuid

from core.bus import Event, emit

from .dna import get_hands_dna
from .services import get_hands_service

logger = logging.getLogger("humanos.hands.events")

PUBLISHES = [
    "task.completed",
    "task.failed",
    "action.executed",
]

SUBSCRIBES = [
    "decision.made",
    "task.assigned",
]


def handle_event(event: Event) -> None:
    """Route bus events into the Hands execution pipeline."""
    handlers = {
        "decision.made": _on_decision_made,
        "task.assigned": _on_task_assigned,
    }
    fn = handlers.get(event.type)
    if fn:
        fn(event)
    else:
        logger.warning("Hands received unhandled event type: %s", event.type)


def _on_decision_made(event: Event) -> None:
    """When the Brain decides, optionally auto-queue execution if confidence is high enough."""
    dna = get_hands_dna()
    payload = event.payload or {}
    confidence = float(payload.get("confidence", 0))
    if confidence < dna.auto_execute_threshold:
        logger.info(
            "Decision below auto_execute threshold (%.2f < %.2f) — not auto-running",
            confidence,
            dna.auto_execute_threshold,
        )
        return
    action = payload.get("action") or payload.get("decision", "")
    if not action:
        return
    service = get_hands_service()
    task_id = f"task-{uuid.uuid4().hex[:12]}"
    service.enqueue_from_decision(
        task_id=task_id,
        title="Execute brain decision",
        action_type="brain.followup",
        payload={"decision_event": event.event_id, "action": action},
        source_event_id=event.event_id,
        decision_ref=payload.get("decision_id", ""),
    )


def _on_task_assigned(event: Event) -> None:
    """Run a task that was explicitly assigned via the bus."""
    p = event.payload or {}
    task_id = p.get("task_id") or f"task-{uuid.uuid4().hex[:12]}"
    service = get_hands_service()
    service.enqueue_from_decision(
        task_id=task_id,
        title=p.get("title", "Assigned task"),
        action_type=p.get("action_type", "generic.execute"),
        payload=p.get("payload", {}),
        source_event_id=event.event_id,
        decision_ref=p.get("decision_ref", ""),
    )
