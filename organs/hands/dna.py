"""
Hands DNA — Concurrency, allowed actions, and auto-execution thresholds from identity.yaml.

Expected YAML (example):

organs:
  hands:
    max_concurrent_tasks: 4
    allowed_actions: ["shell.run", "github.pr"]
    auto_execute_threshold: 0.85
"""

from dataclasses import dataclass

from core.dna_loader import get_dna


@dataclass
class HandsDNA:
    max_concurrent_tasks: int
    allowed_actions: list[str]
    auto_execute_threshold: float


def get_hands_dna() -> HandsDNA:
    """Extract hands-specific config from global DNA with safe defaults."""
    dna = get_dna()
    max_tasks = dna.get("organs.hands.max_concurrent_tasks", 4)
    if not isinstance(max_tasks, int):
        max_tasks = int(max_tasks) if max_tasks is not None else 4

    raw_actions = dna.get("organs.hands.allowed_actions", ["shell.run", "github.*", "azure_devops.*"])
    if isinstance(raw_actions, list):
        allowed = [str(a) for a in raw_actions]
    else:
        allowed = ["shell.run", "github.*", "azure_devops.*"]

    threshold = dna.get("organs.hands.auto_execute_threshold", 0.85)
    try:
        threshold = float(threshold)
    except (TypeError, ValueError):
        threshold = 0.85

    return HandsDNA(
        max_concurrent_tasks=max(1, max_tasks),
        allowed_actions=allowed,
        auto_execute_threshold=max(0.0, min(1.0, threshold)),
    )
