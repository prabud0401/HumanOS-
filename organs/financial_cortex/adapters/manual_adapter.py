"""
Manual banking adapter — reads/writes Django models only (no external bank API).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db.models import Q, Sum

from ..models import Account, Transaction
from ..ports import BalanceSnapshot, BankingPort, TransactionRecord


class ManualBankingAdapter(BankingPort):
    """Source of truth is the local Transaction table."""

    def sync_transactions(self, account_id: str, since: date | None) -> list[TransactionRecord]:
        qs = Transaction.objects.filter(account__account_id=account_id)
        if since:
            qs = qs.filter(posted_on__gte=since)
        out: list[TransactionRecord] = []
        for t in qs.order_by("posted_on"):
            out.append(
                TransactionRecord(
                    external_id=t.external_id or str(t.pk),
                    account_id=account_id,
                    amount=abs(t.amount),
                    currency=t.account.currency,
                    description=t.description,
                    posted_on=t.posted_on,
                    category=t.category,
                    metadata=dict(t.extra),
                )
            )
        return out

    def get_balance(self, account_id: str) -> BalanceSnapshot:
        acc = Account.objects.get(account_id=account_id)
        agg = Transaction.objects.filter(account=acc).aggregate(
            income=Sum("amount", filter=Q(direction=Transaction.Direction.IN)),
            expense=Sum("amount", filter=Q(direction=Transaction.Direction.OUT)),
        )
        income = agg["income"] or Decimal("0")
        expense = agg["expense"] or Decimal("0")
        balance = income - expense
        return BalanceSnapshot(
            account_id=account_id,
            balance=balance,
            currency=acc.currency,
            as_of=date.today(),
        )
