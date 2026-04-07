"""
Django app configuration for the Reproductive organ.
"""

from django.apps import AppConfig


class ReproductiveConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "organs.reproductive"
    verbose_name = "Reproductive — Cloning & migration"

    def ready(self) -> None:
        from core.bus import get_bus
        from core.dna_loader import get_dna
        from core.pulse import register_organ_health

        from . import dna as reproductive_dna
        from . import events, health

        _ = get_dna()
        self.reproductive_dna = reproductive_dna.get_reproductive_dna()

        for event_type in events.SUBSCRIBES:
            get_bus().subscribe(event_type, events.handle_event)

        register_organ_health("reproductive", health.check)
