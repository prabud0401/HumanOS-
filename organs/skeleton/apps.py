"""
Django app configuration for the Skeleton organ.
"""

import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class SkeletonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "organs.skeleton"
    verbose_name = "Skeleton — Framework / Project Structure"

    def ready(self):
        from core.dna_loader import get_dna
        from core.bus import get_bus
        from core.pulse import register_organ_health
        from . import events, health, dna as skeleton_dna

        get_dna()
        self.skeleton_dna = skeleton_dna.get_skeleton_dna()

        try:
            for event_type in events.SUBSCRIBES:
                get_bus().subscribe(event_type, events.handle_event)
        except Exception:
            logger.exception("skeleton: event bus subscription failed during AppConfig.ready()")

        try:
            register_organ_health("skeleton", health.check)
        except Exception:
            logger.exception("skeleton: organ health registration failed during AppConfig.ready()")
