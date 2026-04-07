"""
Financial Cortex DNA — Currency, pay cycle, accounts, and targets from identity.yaml.
"""

from dataclasses import dataclass, field

from core.dna_loader import get_dna


@dataclass
class FinancialCortexDNA:
    currency: str
    salary_day: int
    accounts: list[dict]
    loan_details: list[dict]
    budget_categories: list[str]
    savings_targets: dict


def get_financial_cortex_dna() -> FinancialCortexDNA:
    dna = get_dna()
    fin = dna.financial if isinstance(dna.financial, dict) else {}
    raw = getattr(dna, "_raw", {}) or {}
    fc = raw.get("financial_cortex")
    if not isinstance(fc, dict):
        organs = raw.get("organs")
        if isinstance(organs, dict):
            fc = organs.get("financial_cortex", {})
        if not isinstance(fc, dict):
            fc = {}
    accounts = fc.get("accounts")
    if not isinstance(accounts, list):
        accounts = fin.get("accounts", []) if isinstance(fin.get("accounts"), list) else []
    loans = fc.get("loan_details")
    if not isinstance(loans, list):
        loans = fin.get("loans", []) if isinstance(fin.get("loans"), list) else []
    cats = fc.get("budget_categories")
    if not isinstance(cats, list):
        cats = fin.get("budget_categories", []) if isinstance(fin.get("budget_categories"), list) else []
    targets = fc.get("savings_targets")
    if not isinstance(targets, dict):
        targets = fin.get("savings_targets", {}) if isinstance(fin.get("savings_targets"), dict) else {}

    return FinancialCortexDNA(
        currency=str(fc.get("currency", fin.get("currency", "USD"))),
        salary_day=int(fc.get("salary_day", fin.get("salary_day", 1))),
        accounts=list(accounts),
        loan_details=list(loans),
        budget_categories=[str(c) for c in cats],
        savings_targets=dict(targets),
    )
