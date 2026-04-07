"""
Django app configuration for the Skeleton organ.
"""

from django.apps import AppConfig


class SkeletonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "organs.skeleton"
    verbose_name = "Skeleton — Framework / Project Structure"

    def ready(self):
        from core.dna_loader import get_dna
        from core.bus import get_bus
        from core.pulse import register_organ_health
        from . import events, health, dna as skeleton_dna

        get_dna()
        self.skeleton_dna = skeleton_dna.get_skeleton_dna()

        for event_type in events.SUBSCRIBES:
            get_bus().subscribe(event_type, events.handle_event)

        register_organ_health("skeleton", health.check)
