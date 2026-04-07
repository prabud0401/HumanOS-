"""
Django app configuration for the Brain organ.
Injects DNA config and registers event subscriptions + health checks at startup.
"""

import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class BrainConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "organs.brain"
    verbose_name = "Brain — AI Engine"

    def ready(self):
        from core.dna_loader import get_dna
        from core.bus import get_bus
        from core.pulse import register_organ_health
        from . import events, health

        dna = get_dna()
        self.ai_config = dna.ai_engine

        try:
            for event_type in events.SUBSCRIBES:
                get_bus().subscribe(event_type, events.handle_event)
        except Exception:
            logger.exception("brain: event bus subscription failed during AppConfig.ready()")

        try:
            register_organ_health("brain", health.check)
        except Exception:
            logger.exception("brain: organ health registration failed during AppConfig.ready()")
