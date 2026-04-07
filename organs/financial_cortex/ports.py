"""
Financial Cortex ports — Banking sync and forecasting.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any


@dataclass
class TransactionRecord:
    """Normalized transaction for ports."""

    external_id: str
    account_id: str
    amount: Decimal
    currency: str
    description: str
    posted_on: date
    category: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class BalanceSnapshot:
    account_id: str
    balance: Decimal
    currency: str
    as_of: date


class BankingPort(ABC):
    """Ingest and synchronize account activity."""

    @abstractmethod
    def sync_transactions(self, account_id: str, since: date | None) -> list[TransactionRecord]:
        """Fetch new transactions since a date (inclusive boundary left to adapter)."""

    @abstractmethod
    def get_balance(self, account_id: str) -> BalanceSnapshot:
        """Current balance for an account."""


@dataclass
class CashflowForecast:
    horizon_days: int
    projected_balance: Decimal
    currency: str
    breakdown: list[dict[str, Any]] = field(default_factory=list)


class ForecastPort(ABC):
    """Analytics and projection over normalized financial data."""

    @abstractmethod
    def predict_cashflow(self, account_ids: list[str], horizon_days: int) -> CashflowForecast:
        """Simple statistical projection — not investment advice."""

    @abstractmethod
    def analyze_spending(self, account_ids: list[str], period_days: int) -> dict[str, Any]:
        """Category totals, trends, anomalies."""
