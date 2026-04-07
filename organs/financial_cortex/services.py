"""
Financial Cortex service — banking + forecasting orchestration.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from django.db.models import Sum

from core.bus import emit

from .dna import get_financial_cortex_dna
from .models import Budget, Transaction
from .ports import (
    BalanceSnapshot,
    BankingPort,
    CashflowForecast,
    ForecastPort,
    TransactionRecord,
)

logger = logging.getLogger("humanos.financial_cortex.services")


class DjangoForecastAdapter(ForecastPort):
    """Rolling averages from ORM data — illustrative, not financial advice."""

    def predict_cashflow(self, account_ids: list[str], horizon_days: int) -> CashflowForecast:
        dna = get_financial_cortex_dna()
        end = date.today()
        start = end - timedelta(days=30)
        qs = Transaction.objects.filter(account__account_id__in=account_ids, posted_on__gte=start)
        net = Decimal("0")
        for t in qs:
            if t.direction == Transaction.Direction.IN:
                net += t.amount
            else:
                net -= t.amount
        daily = net / Decimal("30") if qs.exists() else Decimal("0")
        projected = daily * Decimal(str(horizon_days))
        return CashflowForecast(
            horizon_days=horizon_days,
            projected_balance=projected,
            currency=dna.currency,
            breakdown=[{"label": "30d_net_daily_estimate", "value": float(daily)}],
        )

    def analyze_spending(self, account_ids: list[str], period_days: int) -> dict[str, Any]:
        end = date.today()
        start = end - timedelta(days=period_days)
        qs = Transaction.objects.filter(
            account__account_id__in=account_ids,
            posted_on__gte=start,
            direction=Transaction.Direction.OUT,
        )
        by_cat: dict[str, Decimal] = {}
        for t in qs:
            cat = t.category or "uncategorized"
            by_cat[cat] = by_cat.get(cat, Decimal("0")) + t.amount
        return {
            "period_days": period_days,
            "categories": {k: float(v) for k, v in sorted(by_cat.items(), key=lambda x: -x[1])},
            "total_spend": float(sum(by_cat.values(), start=Decimal("0"))),
        }


class FinancialCortexService:
    def __init__(self, banking: BankingPort, forecast: ForecastPort):
        self._banking = banking
        self._forecast = forecast

    def sync_account(self, account_id: str, since: date | None = None) -> list[TransactionRecord]:
        return self._banking.sync_transactions(account_id, since)

    def balance(self, account_id: str) -> BalanceSnapshot:
        return self._banking.get_balance(account_id)

    def check_budgets(self, year: int, month: int) -> None:
        dna = get_financial_cortex_dna()
        for b in Budget.objects.filter(year=year, month=month, currency=dna.currency):
            spent = (
                Transaction.objects.filter(
                    posted_on__year=year,
                    posted_on__month=month,
                    category=b.category,
                    direction=Transaction.Direction.OUT,
                ).aggregate(s=Sum("amount"))["s"]
                or Decimal("0")
            )
            if spent > b.limit_amount:
                emit(
                    "budget.exceeded",
                    "financial_cortex",
                    payload={
                        "category": b.category,
                        "limit": float(b.limit_amount),
                        "spent": float(spent),
                    },
                )

    def flag_anomaly(self, description: str, amount: float) -> None:
        emit(
            "financial.anomaly",
            "financial_cortex",
            payload={"description": description, "amount": amount},
        )

    def forecast_cashflow(self, account_ids: list[str], days: int = 30) -> CashflowForecast:
        fc = self._forecast.predict_cashflow(account_ids, days)
        emit(
            "cashflow.forecast",
            "financial_cortex",
            payload={
                "horizon_days": fc.horizon_days,
                "projected": float(fc.projected_balance),
                "currency": fc.currency,
            },
        )
        return fc


_service: FinancialCortexService | None = None


def get_financial_cortex_service() -> FinancialCortexService:
    global _service
    if _service is None:
        from .adapters.manual_adapter import ManualBankingAdapter

        _service = FinancialCortexService(
            banking=ManualBankingAdapter(),
            forecast=DjangoForecastAdapter(),
        )
    return _service
