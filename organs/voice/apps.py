"""
Django app configuration for the Voice organ.
"""

import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class VoiceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "organs.voice"
    verbose_name = "Voice — Notifications"

    def ready(self):
        from core.dna_loader import get_dna
        from core.bus import get_bus
        from core.pulse import register_organ_health

        from . import dna as voice_dna
        from . import events, health

        _ = get_dna()
        self.voice_dna = voice_dna.get_voice_dna()

        try:
            for event_type in events.SUBSCRIBES:
                get_bus().subscribe(event_type, events.handle_event)
        except Exception:
            logger.exception("voice: event bus subscription failed during AppConfig.ready()")

        try:
            register_organ_health("voice", health.check)
        except Exception:
            logger.exception("voice: organ health registration failed during AppConfig.ready()")
