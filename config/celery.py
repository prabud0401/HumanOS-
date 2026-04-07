"""
Celery configuration for HumanOS.

Auto-discovers tasks from all organ apps.
"""

import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("humanos")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
