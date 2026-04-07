"""
Django app configuration for the Nervous System organ.
"""

import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class NervousSystemConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "organs.nervous_system"
    verbose_name = "Nervous System — Real-time Signals"

    def ready(self):
        from core.dna_loader import get_dna
        from core.bus import get_bus
        from core.pulse import register_organ_health
        from . import events, health, dna as ns_dna

        get_dna()
        self.nervous_dna = ns_dna.get_nervous_system_dna()

        try:
            for event_type in events.SUBSCRIBES:
                get_bus().subscribe(event_type, events.handle_event)
        except Exception:
            logger.exception("nervous_system: event bus subscription failed during AppConfig.ready()")

        try:
            register_organ_health("nervous_system", health.check)
        except Exception:
            logger.exception("nervous_system: organ health registration failed during AppConfig.ready()")
