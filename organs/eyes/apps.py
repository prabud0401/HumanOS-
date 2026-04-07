"""
Django app configuration for the Eyes organ.
"""

import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class EyesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "organs.eyes"
    verbose_name = "Eyes — Dashboard"

    def ready(self):
        from core.dna_loader import get_dna
        from core.bus import get_bus
        from core.pulse import register_organ_health

        from . import dna as eyes_dna
        from . import events, health

        _ = get_dna()
        self.eyes_dna = eyes_dna.get_eyes_dna()

        # Bus matches literal types only; completion-style updates use one wildcard subscription.
        try:
            get_bus().subscribe("*", events.handle_event)
        except Exception:
            logger.exception("eyes: event bus subscription failed during AppConfig.ready()")

        try:
            register_organ_health("eyes", health.check)
        except Exception:
            logger.exception("eyes: organ health registration failed during AppConfig.ready()")
