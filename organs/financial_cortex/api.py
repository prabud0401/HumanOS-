"""
Financial Cortex REST API.
"""

import logging

logger = logging.getLogger("humanos.financial_cortex.api")

try:
    from ninja import Router

    router = Router(tags=["financial_cortex"])

    @router.get("/balance/{account_id}")
    def get_balance(request, account_id: str):
        from .services import get_financial_cortex_service

        b = get_financial_cortex_service().balance(account_id)
        return {
            "account_id": b.account_id,
            "balance": float(b.balance),
            "currency": b.currency,
            "as_of": str(b.as_of),
        }

    @router.post("/forecast")
    def forecast(request, body: dict):
        from .services import get_financial_cortex_service

        ids = body.get("account_ids", [])
        days = int(body.get("horizon_days", 30))
        fc = get_financial_cortex_service().forecast_cashflow(ids, days)
        return {
            "horizon_days": fc.horizon_days,
            "projected_balance": float(fc.projected_balance),
            "currency": fc.currency,
            "breakdown": fc.breakdown,
        }

    @router.get("/health")
    def health(request):
        from .health import check

        status, message, details = check()
        return {"status": status.value, "message": message, **details}

except ImportError:
    logger.debug("django-ninja not installed — financial_cortex API not registered")
    router = None
