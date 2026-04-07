"""
Django app configuration for the Heart organ.
"""

import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class HeartConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "organs.heart"
    verbose_name = "Heart — Event Bus"

    def ready(self):
        from core.dna_loader import get_dna
        from core.bus import get_bus
        from core.pulse import register_organ_health

        from . import dna as heart_dna
        from . import events, health

        _ = get_dna()
        self.heart_dna = heart_dna.get_heart_dna()

        try:
            for event_type in events.SUBSCRIBES:
                get_bus().subscribe(event_type, events.handle_event)
        except Exception:
            logger.exception("heart: event bus subscription failed during AppConfig.ready()")

        try:
            register_organ_health("heart", health.check)
        except Exception:
            logger.exception("heart: organ health registration failed during AppConfig.ready()")
