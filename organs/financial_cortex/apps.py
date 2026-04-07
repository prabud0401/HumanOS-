"""
Django app configuration for the Financial Cortex organ.
"""

from django.apps import AppConfig


class FinancialCortexConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "organs.financial_cortex"
    verbose_name = "Financial Cortex — Personal finance"

    def ready(self) -> None:
        from core.bus import get_bus
        from core.dna_loader import get_dna
        from core.pulse import register_organ_health

        from . import dna as fc_dna
        from . import events, health

        _ = get_dna()
        self.financial_cortex_dna = fc_dna.get_financial_cortex_dna()

        for event_type in events.SUBSCRIBES:
            get_bus().subscribe(event_type, events.handle_event)

        register_organ_health("financial_cortex", health.check)
