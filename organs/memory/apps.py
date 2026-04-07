"""
Django app configuration for the Memory organ.
"""

from django.apps import AppConfig


class MemoryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "organs.memory"
    verbose_name = "Memory — Vector / knowledge store"

    def ready(self) -> None:
        from core.bus import get_bus
        from core.dna_loader import get_dna
        from core.pulse import register_organ_health

        from . import dna as memory_dna
        from . import events, health

        _ = get_dna()
        self.memory_dna = memory_dna.get_memory_dna()

        for event_type in events.SUBSCRIBES:
            get_bus().subscribe(event_type, events.handle_event)

        register_organ_health("memory", health.check)
