"""
Nervous Reflex Arcs — Synchronous fast-path communication.

For time-critical operations that can't wait for the event bus.
Like pulling your hand from fire — the signal goes straight to the muscle
without waiting for the brain to process it.

Organs register reflex handlers for urgent situations. These are direct
synchronous calls that bypass the async event bus.
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable
from datetime import datetime, timezone

logger = logging.getLogger("humanos.reflex")


@dataclass
class ReflexResult:
    success: bool
    data: Any = None
    error: str | None = None
    response_time_ms: float = 0.0


@dataclass
class ReflexArc:
    """A registered reflex — a direct synchronous call between organs."""
    name: str
    source_organ: str
    target_organ: str
    handler: Callable[..., Any]
    priority: int = 0
    description: str = ""
    registered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ReflexRegistry:
    """
    Registry for synchronous reflex arcs.

    Usage:
        # In the target organ's apps.py:
        registry.register("emergency.shutdown", "immune_system", "hands", handler_fn)

        # In the calling organ:
        result = registry.trigger("emergency.shutdown", context={"reason": "breach"})
    """

    def __init__(self):
        self._arcs: dict[str, list[ReflexArc]] = {}

    def register(
        self,
        reflex_name: str,
        source_organ: str,
        target_organ: str,
        handler: Callable[..., Any],
        priority: int = 0,
        description: str = "",
    ) -> None:
        arc = ReflexArc(
            name=reflex_name,
            source_organ=source_organ,
            target_organ=target_organ,
            handler=handler,
            priority=priority,
            description=description,
        )
        self._arcs.setdefault(reflex_name, []).append(arc)
        # Higher priority runs first
        self._arcs[reflex_name].sort(key=lambda a: a.priority, reverse=True)
        logger.debug(
            "Reflex registered: %s (%s -> %s, priority=%d)",
            reflex_name, source_organ, target_organ, priority,
        )

    def unregister(self, reflex_name: str, target_organ: str | None = None) -> None:
        if target_organ:
            arcs = self._arcs.get(reflex_name, [])
            self._arcs[reflex_name] = [a for a in arcs if a.target_organ != target_organ]
        else:
            self._arcs.pop(reflex_name, None)

    def trigger(self, reflex_name: str, **kwargs) -> list[ReflexResult]:
        """
        Trigger a reflex arc synchronously. All registered handlers
        run in priority order. Returns a list of results.
        """
        arcs = self._arcs.get(reflex_name, [])
        if not arcs:
            logger.warning("No reflex handlers for '%s'", reflex_name)
            return []

        results = []
        for arc in arcs:
            start = time.monotonic()
            try:
                data = arc.handler(**kwargs)
                elapsed = (time.monotonic() - start) * 1000
                results.append(ReflexResult(success=True, data=data, response_time_ms=round(elapsed, 2)))
                logger.info(
                    "Reflex %s -> %s: OK (%.1fms)",
                    reflex_name, arc.target_organ, elapsed,
                )
            except Exception as exc:
                elapsed = (time.monotonic() - start) * 1000
                results.append(ReflexResult(success=False, error=str(exc), response_time_ms=round(elapsed, 2)))
                logger.exception("Reflex %s -> %s: FAILED", reflex_name, arc.target_organ)
        return results

    def trigger_first(self, reflex_name: str, **kwargs) -> ReflexResult:
        """Trigger and return only the highest-priority handler's result."""
        results = self.trigger(reflex_name, **kwargs)
        if not results:
            return ReflexResult(success=False, error=f"No handlers for reflex '{reflex_name}'")
        return results[0]

    @property
    def registered_reflexes(self) -> dict[str, list[str]]:
        """Map of reflex names to their target organs."""
        return {name: [a.target_organ for a in arcs] for name, arcs in self._arcs.items()}


# Global instance
_registry = ReflexRegistry()


def get_reflex_registry() -> ReflexRegistry:
    return _registry


def register_reflex(
    reflex_name: str,
    source_organ: str,
    target_organ: str,
    handler: Callable[..., Any],
    priority: int = 0,
    description: str = "",
) -> None:
    _registry.register(reflex_name, source_organ, target_organ, handler, priority, description)


def trigger_reflex(reflex_name: str, **kwargs) -> list[ReflexResult]:
    return _registry.trigger(reflex_name, **kwargs)
