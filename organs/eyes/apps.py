"""
Django app configuration for the Eyes organ.
"""

from django.apps import AppConfig


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
        get_bus().subscribe("*", events.handle_event)

        register_organ_health("eyes", health.check)
