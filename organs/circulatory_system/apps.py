"""
Django app configuration for the Circulatory System organ.
"""

import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class CirculatorySystemConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "organs.circulatory_system"
    verbose_name = "Circulatory System — Data transport"

    def ready(self) -> None:
        from core.bus import get_bus
        from core.dna_loader import get_dna
        from core.pulse import register_organ_health

        from . import dna as circulatory_dna
        from . import events, health

        _ = get_dna()
        self.circulatory_dna = circulatory_dna.get_circulatory_dna()

        try:
            for event_type in events.SUBSCRIBES:
                get_bus().subscribe(event_type, events.handle_event)
        except Exception:
            logger.exception("circulatory_system: event bus subscription failed during AppConfig.ready()")

        try:
            register_organ_health("circulatory_system", health.check)
        except Exception:
            logger.exception("circulatory_system: organ health registration failed during AppConfig.ready()")
