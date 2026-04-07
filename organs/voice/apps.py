"""
Django app configuration for the Voice organ.
"""

from django.apps import AppConfig


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

        for event_type in events.SUBSCRIBES:
            get_bus().subscribe(event_type, events.handle_event)

        register_organ_health("voice", health.check)
