"""
Django app configuration for the Hands organ.
Loads DNA, subscribes to the event bus, and registers pulse health checks.
"""

import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class HandsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "organs.hands"
    verbose_name = "Hands — Agent Control / Task Execution"

    def ready(self):
        from core.dna_loader import get_dna
        from core.bus import get_bus
        from core.pulse import register_organ_health
        from . import events, health, dna as hands_dna

        get_dna()
        self.hands_dna = hands_dna.get_hands_dna()

        try:
            for event_type in events.SUBSCRIBES:
                get_bus().subscribe(event_type, events.handle_event)
        except Exception:
            logger.exception("hands: event bus subscription failed during AppConfig.ready()")

        try:
            register_organ_health("hands", health.check)
        except Exception:
            logger.exception("hands: organ health registration failed during AppConfig.ready()")
