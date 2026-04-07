"""
Django app configuration for the Lungs organ.
"""

from django.apps import AppConfig


class LungsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "organs.lungs"
    verbose_name = "Lungs — Data Ingestion"

    def ready(self):
        from core.dna_loader import get_dna
        from core.bus import get_bus
        from core.pulse import register_organ_health

        from . import dna as lungs_dna
        from . import events, health

        _ = get_dna()
        self.lungs_dna = lungs_dna.get_lungs_dna()

        for event_type in events.SUBSCRIBES:
            get_bus().subscribe(event_type, events.handle_event)

        register_organ_health("lungs", health.check)
