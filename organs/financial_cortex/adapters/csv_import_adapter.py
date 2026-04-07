"""
CSV import adapter — parses common bank export columns into Transaction records.
"""

from __future__ import annotations

import csv
import io
import logging
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from hashlib import sha256
from typing import BinaryIO

from ..models import Account, Transaction
from ..ports import BalanceSnapshot, BankingPort, TransactionRecord

logger = logging.getLogger("humanos.financial_cortex.csv")


class CsvImportBankingAdapter(BankingPort):
    """
    ``sync_transactions`` returns rows parsed from last imported CSV for account.

    Use ``ingest_csv`` to load file content into the database first.
    """

    def __init__(self, account_id: str):
        self._account_id = account_id

    def ingest_csv(self, fileobj: BinaryIO | str, encoding: str = "utf-8") -> int:
        """Parse CSV and create Transaction rows. Returns count inserted."""
        acc = Account.objects.get(account_id=self._account_id)
        if isinstance(fileobj, str):
            text = fileobj
        else:
            text = fileobj.read().decode(encoding, errors="replace")
        reader = csv.DictReader(io.StringIO(text))
        n = 0
        for row in reader:
            parsed = _parse_csv_row(acc, row)
            if parsed is None:
                continue
            Transaction.objects.update_or_create(
                account=acc,
                external_id=parsed.external_id,
                defaults={
                    "amount": parsed.amount,
                    "direction": parsed.direction,
                    "description": parsed.description,
                    "category": parsed.category,
                    "posted_on": parsed.posted_on,
                    "extra": parsed.metadata,
                },
            )
            n += 1
        return n

    def sync_transactions(self, account_id: str, since: date | None) -> list[TransactionRecord]:
        from .manual_adapter import ManualBankingAdapter

        return ManualBankingAdapter().sync_transactions(account_id, since)

    def get_balance(self, account_id: str) -> BalanceSnapshot:
        from .manual_adapter import ManualBankingAdapter

        return ManualBankingAdapter().get_balance(account_id)


@dataclass
class _ParsedCsvRow:
    external_id: str
    amount: Decimal
    direction: str
    description: str
    posted_on: date
    category: str
    metadata: dict


def _parse_csv_row(acc: Account, row: dict) -> _ParsedCsvRow | None:
    date_keys = ("date", "posted", "posted_on", "transaction_date")
    amount_keys = ("amount", "value", "debit", "credit")
    desc_keys = ("description", "memo", "narrative", "details")
    posted_on = None
    for k in date_keys:
        if k in row and row[k]:
            try:
                posted_on = datetime.strptime(row[k].strip()[:10], "%Y-%m-%d").date()
            except ValueError:
                try:
                    posted_on = datetime.strptime(row[k].strip()[:10], "%m/%d/%Y").date()
                except ValueError:
                    continue
            break
    if not posted_on:
        return None

    amount = None
    raw_amount_key = None
    for k in amount_keys:
        if k in row and row[k] not in ("", None):
            try:
                amount = Decimal(str(row[k]).replace(",", "").replace("$", ""))
                raw_amount_key = k
                break
            except InvalidOperation:
                continue
    if amount is None:
        return None

    direction = Transaction.Direction.OUT
    if amount < 0:
        amount = abs(amount)
        direction = Transaction.Direction.IN
    if raw_amount_key == "credit" and amount > 0:
        direction = Transaction.Direction.IN
    if raw_amount_key == "debit" and amount > 0:
        direction = Transaction.Direction.OUT

    desc = ""
    for k in desc_keys:
        if k in row and row[k]:
            desc = str(row[k])
            break

    external_id = sha256(f"{acc.account_id}:{posted_on}:{amount}:{desc}".encode()).hexdigest()[:32]

    return _ParsedCsvRow(
        external_id=external_id,
        amount=amount,
        direction=direction,
        description=desc,
        posted_on=posted_on,
        category=str(row.get("category", "")),
        metadata={"raw": row},
    )
