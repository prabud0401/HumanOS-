"""
HumanOS URL Configuration.

Central URL router that wires all organ API endpoints together
using Django Ninja.
"""

from django.contrib import admin
from django.urls import path
from django.http import JsonResponse

try:
    from ninja import NinjaAPI

    api = NinjaAPI(
        title="HumanOS API",
        version="0.1.0",
        description="Digital Twin REST API — Every organ exposes endpoints here.",
    )

    # Wire organ routers
    def _mount_organ_router(module_path: str, prefix: str, tag: str):
        try:
            import importlib
            mod = importlib.import_module(module_path)
            router = getattr(mod, "router", None)
            if router:
                api.add_router(f"/{prefix}/", router, tags=[tag])
        except (ImportError, AttributeError):
            pass

    _mount_organ_router("organs.brain.api", "brain", "Brain")
    _mount_organ_router("organs.heart.api", "heart", "Heart")
    _mount_organ_router("organs.lungs.api", "lungs", "Lungs")
    _mount_organ_router("organs.ears.api", "ears", "Ears")
    _mount_organ_router("organs.eyes.api", "eyes", "Eyes")
    _mount_organ_router("organs.voice.api", "voice", "Voice")
    _mount_organ_router("organs.hands.api", "hands", "Hands")
    _mount_organ_router("organs.skeleton.api", "skeleton", "Skeleton")
    _mount_organ_router("organs.nervous_system.api", "nervous-system", "Nervous System")
    _mount_organ_router("organs.immune_system.api", "immune-system", "Immune System")
    _mount_organ_router("organs.digestive_system.api", "digestive-system", "Digestive System")
    _mount_organ_router("organs.circulatory_system.api", "circulatory-system", "Circulatory System")
    _mount_organ_router("organs.memory.api", "memory", "Memory")
    _mount_organ_router("organs.endocrine.api", "endocrine", "Endocrine")
    _mount_organ_router("organs.financial_cortex.api", "financial-cortex", "Financial Cortex")
    _mount_organ_router("organs.reproductive.api", "reproductive", "Reproductive")

    api_urls = [path("api/", api.urls)]

except ImportError:
    api_urls = []


def _system_health(request):
    """Root health check — returns overall system pulse."""
    from core.pulse import get_pulse
    pulse = get_pulse()
    report = pulse.check_all()
    return JsonResponse({
        "status": report.status.value,
        "healthy": report.healthy_count,
        "degraded": report.degraded_count,
        "unhealthy": report.unhealthy_count,
        "checked_at": report.checked_at,
        "organs": {
            name: {"status": oh.status.value, "message": oh.message, "ms": oh.response_time_ms}
            for name, oh in report.organs.items()
        },
    })


def _index(request):
    """Root endpoint."""
    return JsonResponse({
        "name": "HumanOS",
        "version": "0.1.0",
        "status": "alive",
        "docs": "/api/docs",
        "health": "/health/",
        "admin": "/admin/",
    })


urlpatterns = [
    path("", _index),
    path("health/", _system_health),
    path("admin/", admin.site.urls),
] + api_urls
