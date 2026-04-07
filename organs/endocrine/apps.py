"""
Django app configuration for the Endocrine organ.
"""

from django.apps import AppConfig


class EndocrineConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "organs.endocrine"
    verbose_name = "Endocrine — Schedules & timers"

    def ready(self) -> None:
        from core.bus import get_bus
        from core.dna_loader import get_dna
        from core.pulse import register_organ_health

        from . import dna as endocrine_dna
        from . import events, health

        _ = get_dna()
        self.endocrine_dna = endocrine_dna.get_endocrine_dna()

        for event_type in events.SUBSCRIBES:
            get_bus().subscribe(event_type, events.handle_event)

        register_organ_health("endocrine", health.check)
