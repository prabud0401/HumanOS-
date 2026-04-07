"""
Django app configuration for the Nervous System organ.
"""

from django.apps import AppConfig


class NervousSystemConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "organs.nervous_system"
    verbose_name = "Nervous System — Real-time Signals"

    def ready(self):
        from core.dna_loader import get_dna
        from core.bus import get_bus
        from core.pulse import register_organ_health
        from . import events, health, dna as ns_dna

        get_dna()
        self.nervous_dna = ns_dna.get_nervous_system_dna()

        for event_type in events.SUBSCRIBES:
            get_bus().subscribe(event_type, events.handle_event)

        register_organ_health("nervous_system", health.check)
