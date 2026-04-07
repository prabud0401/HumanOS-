"""
Django app configuration for the Financial Cortex organ.
"""

import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


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

        try:
            for event_type in events.SUBSCRIBES:
                get_bus().subscribe(event_type, events.handle_event)
        except Exception:
            logger.exception("financial_cortex: event bus subscription failed during AppConfig.ready()")

        try:
            register_organ_health("financial_cortex", health.check)
        except Exception:
            logger.exception("financial_cortex: organ health registration failed during AppConfig.ready()")
