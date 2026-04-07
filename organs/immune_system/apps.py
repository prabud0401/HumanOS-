"""
Django app configuration for the Immune System organ.
"""

import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)

# Failure-shaped events from other organs (pattern *.failed expanded at startup)
_FAILURE_EVENT_TYPES = (
    "task.failed",
    "processing.failed",
    "decision.failed",
    "transport.failed",
)


class ImmuneSystemConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "organs.immune_system"
    verbose_name = "Immune System — Security / Access Control"

    def ready(self):
        from core.dna_loader import get_dna
        from core.bus import get_bus
        from core.pulse import register_organ_health
        from . import events, health, dna as immune_dna

        get_dna()
        self.immune_dna = immune_dna.get_immune_system_dna()

        try:
            bus = get_bus()
            for event_type in events.SUBSCRIBES:
                if event_type == "*.failed":
                    for et in _FAILURE_EVENT_TYPES:
                        bus.subscribe(et, events.handle_event)
                else:
                    bus.subscribe(event_type, events.handle_event)
        except Exception:
            logger.exception("immune_system: event bus subscription failed during AppConfig.ready()")

        try:
            register_organ_health("immune_system", health.check)
        except Exception:
            logger.exception("immune_system: organ health registration failed during AppConfig.ready()")
