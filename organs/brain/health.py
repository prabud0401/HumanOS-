"""
Brain Health Check — Reports the health status of the AI engine.
"""

from core.pulse import HealthStatus


def check() -> tuple[HealthStatus, str, dict]:
    """
    Check brain health:
    - Is the LLM adapter configured and reachable?
    - Are there any stuck decisions?
    """
    details = {}

    try:
        from .services import get_brain_service
        service = get_brain_service()
        llm = service._llm

        details["adapter"] = llm.get_model_name()
        details["available"] = llm.is_available()

        if not llm.is_available():
            return HealthStatus.DEGRADED, "LLM adapter configured but not reachable", details

        return HealthStatus.HEALTHY, "Brain operational", details

    except Exception as exc:
        details["error"] = str(exc)
        return HealthStatus.UNHEALTHY, f"Brain initialization failed: {exc}", details
