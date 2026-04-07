"""
Immune System Celery Tasks — Key rotation and audit compaction.
"""

import logging

logger = logging.getLogger("humanos.immune.tasks")

try:
    from celery import shared_task

    @shared_task(name="immune_system.rotate_keys")
    def rotate_keys() -> dict:
        from .dna import get_immune_system_dna
        from .services import FernetEncryptionPort

        dna = get_immune_system_dna()
        enc = FernetEncryptionPort(algorithm=dna.encryption_algorithm)
        new_id = enc.rotate_key()
        return {"key_id": new_id}

    @shared_task(name="immune_system.purge_old_audit")
    def purge_old_audit() -> dict:
        from datetime import timedelta

        from django.utils import timezone as dj_tz

        from .dna import get_immune_system_dna
        from .models import AuditLog

        dna = get_immune_system_dna()
        cutoff = dj_tz.now() - timedelta(days=dna.audit_retention_days)
        n, _ = AuditLog.objects.filter(created_at__lt=cutoff).delete()
        return {"deleted": n}

except ImportError:
    logger.debug("Celery not installed — immune_system tasks are stubs")

    def rotate_keys():
        raise RuntimeError("Celery required for immune_system tasks")

    def purge_old_audit():
        raise RuntimeError("Celery required for immune_system tasks")
