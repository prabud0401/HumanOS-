"""
Django app configuration for the Brain organ.
Injects DNA config and registers event subscriptions + health checks at startup.
"""

from django.apps import AppConfig


class BrainConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "organs.brain"
    verbose_name = "Brain — AI Engine"

    def ready(self):
        from core.dna_loader import get_dna
        from core.bus import get_bus
        from core.pulse import register_organ_health
        from . import events, health

        dna = get_dna()
        self.ai_config = dna.ai_engine

        for event_type in events.SUBSCRIBES:
            get_bus().subscribe(event_type, events.handle_event)

        register_organ_health("brain", health.check)
