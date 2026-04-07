"""
Circulatory organ health — transport mode and recent failure signals.
"""

from core.pulse import HealthStatus


def check() -> tuple[HealthStatus, str, dict]:
    """Verify DNA load and transport adapter sanity."""
    details: dict = {}
    try:
        from .dna import get_circulatory_dna
        from .services import get_circulatory_service

        dna = get_circulatory_dna()
        details["transport_mode"] = dna.transport_mode
        details["max_packet_size"] = dna.max_packet_size
        details["compression"] = dna.compression

        svc = get_circulatory_service()
        transport = type(svc._transport).__name__
        details["adapter"] = transport

        if dna.transport_mode == "async" and transport == "CeleryTransportAdapter":
            from .adapters.celery_transport import CeleryTransportAdapter

            adapter = svc._transport
            if isinstance(adapter, CeleryTransportAdapter) and adapter._apply_task is None:
                return (
                    HealthStatus.DEGRADED,
                    "Async mode selected but Celery task not bound",
                    details,
                )

        return HealthStatus.HEALTHY, "Circulatory transport operational", details
    except Exception as exc:
        details["error"] = str(exc)
        return HealthStatus.UNHEALTHY, f"Circulatory check failed: {exc}", details
