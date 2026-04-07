"""
Financial Cortex Celery tasks — sync and rollup jobs.
"""

import logging
from datetime import date

logger = logging.getLogger("humanos.financial_cortex.tasks")

try:
    from celery import shared_task

    @shared_task(name="financial_cortex.monthly_budget_check")
    def monthly_budget_check(year: int | None = None, month: int | None = None) -> str:
        from .services import get_financial_cortex_service

        today = date.today()
        y = year or today.year
        m = month or today.month
        get_financial_cortex_service().check_budgets(y, m)
        return f"checked-{y}-{m:02d}"

    @shared_task(name="financial_cortex.sync_all_accounts")
    def sync_all_accounts(account_ids: list[str]) -> dict:
        from .services import get_financial_cortex_service

        svc = get_financial_cortex_service()
        out = {}
        for aid in account_ids:
            out[aid] = len(svc.sync_account(aid, since=None))
        return out

except ImportError:
    logger.debug("Celery not installed — financial_cortex tasks are stubs")

    def monthly_budget_check(year=None, month=None):
        raise RuntimeError("Celery required for financial cortex tasks")

    def sync_all_accounts(account_ids):
        raise RuntimeError("Celery required for financial cortex tasks")
