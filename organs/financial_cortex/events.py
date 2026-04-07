"""
Financial Cortex events — budgets, bills, and income signals.
"""

import logging
from datetime import date
from decimal import Decimal

from core.bus import Event, emit

logger = logging.getLogger("humanos.financial_cortex.events")

PUBLISHES = [
    "financial.anomaly",
    "budget.exceeded",
    "payment.due",
    "cashflow.forecast",
]

SUBSCRIBES = [
    "transaction.recorded",
    "salary.received",
    "bill.reminder",
]


def handle_event(event: Event) -> None:
    handlers = {
        "transaction.recorded": _on_transaction_recorded,
        "salary.received": _on_salary_received,
        "bill.reminder": _on_bill_reminder,
    }
    fn = handlers.get(event.type)
    if fn:
        fn(event)
    else:
        logger.warning("Financial Cortex received unhandled event: %s", event.type)


def _on_transaction_recorded(event: Event) -> None:
    from .models import Account, Transaction
    from .services import get_financial_cortex_service

    p = event.payload or {}
    account_id = p.get("account_id")
    if not account_id:
        return
    acc, _ = Account.objects.get_or_create(
        account_id=account_id,
        defaults={"name": p.get("account_name", account_id), "currency": p.get("currency", "USD")},
    )
    amount = Decimal(str(p.get("amount", "0")))
    direction = p.get("direction", Transaction.Direction.OUT)
    raw_date = p.get("posted_on")
    if isinstance(raw_date, str):
        posted_on = date.fromisoformat(raw_date[:10])
    elif isinstance(raw_date, date):
        posted_on = raw_date
    else:
        posted_on = date.today()
    Transaction.objects.create(
        account=acc,
        external_id=p.get("external_id", ""),
        amount=abs(amount),
        direction=direction,
        description=p.get("description", ""),
        category=p.get("category", ""),
        posted_on=posted_on,
        extra=p.get("metadata") or {},
    )
    if abs(amount) > Decimal(str(p.get("anomaly_threshold", "10000"))):
        get_financial_cortex_service().flag_anomaly(p.get("description", "large tx"), float(amount))


def _on_salary_received(event: Event) -> None:
    from .services import get_financial_cortex_service

    p = event.payload or {}
    account_ids = p.get("account_ids") or []
    if not account_ids and p.get("account_id"):
        account_ids = [p["account_id"]]
    if account_ids:
        get_financial_cortex_service().forecast_cashflow(account_ids, days=int(p.get("horizon_days", 30)))


def _on_bill_reminder(event: Event) -> None:
    p = event.payload or {}
    emit(
        "payment.due",
        "financial_cortex",
        payload={
            "name": p.get("name", "bill"),
            "amount": p.get("amount"),
            "due": p.get("due_date"),
        },
    )
