"""
Django app configuration for the Ears organ.
"""

import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class EarsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "organs.ears"
    verbose_name = "Ears — Listeners"

    def ready(self):
        from core.dna_loader import get_dna
        from core.bus import get_bus
        from core.pulse import register_organ_health

        from . import dna as ears_dna
        from . import events, health

        _ = get_dna()
        self.ears_dna = ears_dna.get_ears_dna()

        try:
            for event_type in events.SUBSCRIBES:
                get_bus().subscribe(event_type, events.handle_event)
        except Exception:
            logger.exception("ears: event bus subscription failed during AppConfig.ready()")

        try:
            register_organ_health("ears", health.check)
        except Exception:
            logger.exception("ears: organ health registration failed during AppConfig.ready()")
