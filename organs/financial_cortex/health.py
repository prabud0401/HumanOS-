"""
Financial Cortex health.
"""

from core.pulse import HealthStatus


def check() -> tuple[HealthStatus, str, dict]:
    details: dict = {}
    try:
        from .dna import get_financial_cortex_dna
        from .models import Account
        from .services import get_financial_cortex_service

        dna = get_financial_cortex_dna()
        details["currency"] = dna.currency
        details["accounts_configured"] = len(dna.accounts)
        details["account_rows"] = Account.objects.filter(is_active=True).count()

        svc = get_financial_cortex_service()
        _ = svc

        return HealthStatus.HEALTHY, "Financial Cortex operational", details
    except Exception as exc:
        details["error"] = str(exc)
        return HealthStatus.UNHEALTHY, f"Financial Cortex check failed: {exc}", details
