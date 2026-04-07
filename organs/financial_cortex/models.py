"""
Financial Cortex models — accounts through snapshots.
"""

from django.db import models


class Account(models.Model):
    """Bank account, wallet, or logical money bucket."""

    class Kind(models.TextChoices):
        CHECKING = "checking", "Checking"
        SAVINGS = "savings", "Savings"
        CREDIT = "credit", "Credit"
        CASH = "cash", "Cash"
        INVESTMENT = "investment", "Investment"
        OTHER = "other", "Other"

    account_id = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=256)
    kind = models.CharField(max_length=32, choices=Kind.choices, default=Kind.CHECKING)
    currency = models.CharField(max_length=8, default="USD")
    institution = models.CharField(max_length=256, blank=True, default="")
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"Account({self.account_id})"


class Transaction(models.Model):
    """Single money movement."""

    class Direction(models.TextChoices):
        IN = "in", "Income"
        OUT = "out", "Expense"

    external_id = models.CharField(max_length=128, blank=True, default="", db_index=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    direction = models.CharField(max_length=8, choices=Direction.choices)
    description = models.TextField(blank=True, default="")
    category = models.CharField(max_length=128, blank=True, default="")
    posted_on = models.DateField()
    extra = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-posted_on", "-pk"]
        indexes = [models.Index(fields=["account", "posted_on"])]

    def __str__(self) -> str:
        return f"Transaction({self.account.account_id}, {self.amount})"


class Loan(models.Model):
    """Loan or structured debt."""

    loan_id = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=256)
    principal = models.DecimalField(max_digits=14, decimal_places=2)
    remaining = models.DecimalField(max_digits=14, decimal_places=2)
    apr = models.DecimalField(max_digits=6, decimal_places=3, default=0)
    due_day = models.PositiveSmallIntegerField(default=1)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"Loan({self.loan_id})"


class Budget(models.Model):
    """Monthly envelope per category."""

    year = models.PositiveSmallIntegerField()
    month = models.PositiveSmallIntegerField()
    category = models.CharField(max_length=128)
    limit_amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=8, default="USD")
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-year", "-month", "category"]
        unique_together = ["year", "month", "category", "currency"]

    def __str__(self) -> str:
        return f"Budget({self.year}-{self.month:02d} {self.category})"


class RecurringPayment(models.Model):
    """Rent, subscriptions, predictable bills."""

    name = models.CharField(max_length=256)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=8, default="USD")
    cadence = models.CharField(max_length=32, default="monthly")
    next_due = models.DateField()
    account = models.ForeignKey(
        Account, on_delete=models.SET_NULL, null=True, blank=True, related_name="recurring"
    )
    metadata = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["next_due"]

    def __str__(self) -> str:
        return f"RecurringPayment({self.name})"


class SavingsGoal(models.Model):
    """Target balance or milestone."""

    goal_id = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=256)
    target_amount = models.DecimalField(max_digits=14, decimal_places=2)
    current_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    currency = models.CharField(max_length=8, default="USD")
    deadline = models.DateField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"SavingsGoal({self.goal_id})"


class FinancialSnapshot(models.Model):
    """Point-in-time rollup for dashboards."""

    as_of = models.DateField()
    net_worth = models.DecimalField(max_digits=16, decimal_places=2)
    currency = models.CharField(max_length=8, default="USD")
    breakdown = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-as_of"]
        unique_together = ["as_of", "currency"]

    def __str__(self) -> str:
        return f"FinancialSnapshot({self.as_of})"
