"""
Digestive System Celery Tasks — Async ingestion jobs.
"""

import logging

logger = logging.getLogger("humanos.digestive.tasks")

try:
    from celery import shared_task

    @shared_task(name="digestive_system.process_file")
    def process_file(source_uri: str, file_format: str) -> dict:
        from .services import get_digestive_system_service

        job = get_digestive_system_service().run_job(source_uri, file_format)
        return {"job_id": job.job_id, "status": job.status}

except ImportError:
    logger.debug("Celery not installed — digestive_system tasks are stubs")

    def process_file(source_uri, file_format):
        raise RuntimeError("Celery required for digestive_system tasks")
