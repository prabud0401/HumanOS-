"""
Django app configuration for the Digestive System organ.
"""

from django.apps import AppConfig


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

        for event_type in events.SUBSCRIBES:
            get_bus().subscribe(event_type, events.handle_event)

        register_organ_health("digestive_system", health.check)
