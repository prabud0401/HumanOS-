"""
Django app configuration for the Ears organ.
"""

from django.apps import AppConfig


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

        for event_type in events.SUBSCRIBES:
            get_bus().subscribe(event_type, events.handle_event)

        register_organ_health("ears", health.check)
