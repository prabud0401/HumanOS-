"""
Eyes Service Layer — dashboard layout and widget rendering.
"""

from __future__ import annotations

import logging
from typing import Any

from .dna import get_eyes_dna
from .models import DashboardWidget, UserPreference
from .ports import DashboardPort

logger = logging.getLogger("humanos.eyes.services")


class EyesDashboardService(DashboardPort):
    def render_widget(self, slug: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        try:
            w = DashboardWidget.objects.get(slug=slug, is_active=True)
        except DashboardWidget.DoesNotExist:
            return {
                "slug": slug,
                "error": "not_found",
                "title": slug,
                "widget_type": "custom",
                "body": {},
            }
        ctx = context or {}
        return {
            "slug": w.slug,
            "title": w.title,
            "widget_type": w.widget_type,
            "body": {**w.config, **ctx},
        }

    def get_layout(self, user_id: int | None = None) -> dict[str, Any]:
        dna = get_eyes_dna()
        theme = dna.theme
        order = list(dna.default_layout)
        if user_id is not None:
            try:
                pref = UserPreference.objects.get(user_id=user_id)
                theme = pref.theme or theme
                if pref.layout_json.get("order"):
                    order = list(pref.layout_json["order"])
            except UserPreference.DoesNotExist:
                pass

        widgets = []
        for slug in order:
            widgets.append(self.render_widget(slug))
        return {
            "theme": theme,
            "refresh_interval_sec": dna.refresh_interval,
            "widgets": widgets,
        }


_service: EyesDashboardService | None = None


def get_eyes_service() -> EyesDashboardService:
    global _service
    if _service is None:
        _service = EyesDashboardService()
    return _service
