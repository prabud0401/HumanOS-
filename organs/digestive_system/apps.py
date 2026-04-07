"""
Django app configuration for the Digestive System organ.
"""

import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class DigestiveSystemConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "organs.digestive_system"
    verbose_name = "Digestive System — Data Processing / Transformation"

    def ready(self):
        from core.dna_loader import get_dna
        from core.bus import get_bus
        from core.pulse import register_organ_health
        from . import events, health, dna as digestive_dna

        get_dna()
        self.digestive_dna = digestive_dna.get_digestive_system_dna()

        try:
            for event_type in events.SUBSCRIBES:
                get_bus().subscribe(event_type, events.handle_event)
        except Exception:
            logger.exception("digestive_system: event bus subscription failed during AppConfig.ready()")

        try:
            register_organ_health("digestive_system", health.check)
        except Exception:
            logger.exception("digestive_system: organ health registration failed during AppConfig.ready()")
